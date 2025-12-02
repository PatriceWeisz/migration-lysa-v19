#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION PRODUITS v16 → v19
=============================
Migre les produits (product.template et product.product) avec leurs catégories
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from connexion_double_v19 import ConnexionDoubleV19
from config_v19 import MIGRATION_PARAMS

# Constantes
BATCH_SIZE = MIGRATION_PARAMS['BATCH_SIZE']
MAX_RETRY = MIGRATION_PARAMS['MAX_RETRY']

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/migration_produits.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# MODE TEST : Limiter à 10 produits
TEST_MODE = True
TEST_LIMIT = 10

class MigrationProduits:
    """Gestion de la migration des produits"""
    
    def __init__(self):
        self.conn = ConnexionDoubleV19()
        self.stats = {
            'total': 0,
            'migres': 0,
            'existants': 0,
            'erreurs': 0
        }
        self.categorie_mapping = {}
        self.account_mapping = {}
        self.logs_dir = Path('logs')
        self.logs_dir.mkdir(exist_ok=True)
    
    def charger_account_mapping(self):
        """Charge le mapping des comptes depuis le fichier JSON"""
        mapping_file = self.logs_dir / 'account_mapping.json'
        
        if mapping_file.exists():
            with open(mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.account_mapping = {int(k): v for k, v in data.items()}
            logging.info(f"✓ Mapping des comptes chargé : {len(self.account_mapping)} comptes")
            return True
        else:
            logging.warning("⚠️ Fichier account_mapping.json non trouvé")
            return False
    
    def sauvegarder_categorie_mapping(self):
        """Sauvegarde le mapping des catégories"""
        mapping_file = self.logs_dir / 'product_category_mapping.json'
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.categorie_mapping, f, indent=2)
        logging.info(f"✓ Mapping des catégories sauvegardé : {len(self.categorie_mapping)} catégories")
    
    def migrer_categories(self):
        """Migre d'abord les catégories de produits"""
        logging.info("\n" + "="*70)
        logging.info("MIGRATION DES CATÉGORIES DE PRODUITS")
        logging.info("="*70)
        
        # Récupérer catégories source
        categories_source = self.conn.executer_source(
            'product.category',
            'search_read',
            [],
            fields=['name', 'parent_id', 'property_account_income_categ_id', 
                   'property_account_expense_categ_id', 'property_cost_method',
                   'property_valuation']
        )
        
        logging.info(f"✓ {len(categories_source)} catégories trouvées dans source")
        
        # Récupérer catégories destination
        categories_dest = self.conn.executer_destination(
            'product.category',
            'search_read',
            [],
            fields=['name', 'parent_id']
        )
        
        # Créer index par nom
        categories_dest_by_name = {c['name']: c['id'] for c in categories_dest}
        
        logging.info(f"✓ {len(categories_dest)} catégories existantes dans destination")
        
        # Migrer chaque catégorie (ordre important : parents d'abord)
        categories_triees = sorted(categories_source, 
                                   key=lambda x: (x['parent_id'][0] if x.get('parent_id') else 0))
        
        for cat in categories_triees:
            source_id = cat['id']
            name = cat['name']
            
            # Vérifier si existe déjà
            if name in categories_dest_by_name:
                dest_id = categories_dest_by_name[name]
                self.categorie_mapping[source_id] = dest_id
                logging.info(f"  Catégorie existante : {name} (ID: {dest_id})")
                continue
            
            # Préparer données
            data = {
                'name': name,
            }
            
            # Parent
            if cat.get('parent_id'):
                parent_source_id = cat['parent_id'][0]
                if parent_source_id in self.categorie_mapping:
                    data['parent_id'] = self.categorie_mapping[parent_source_id]
            
            # Comptes comptables
            if cat.get('property_account_income_categ_id'):
                income_source_id = cat['property_account_income_categ_id'][0]
                if income_source_id in self.account_mapping:
                    data['property_account_income_categ_id'] = self.account_mapping[income_source_id]
            
            if cat.get('property_account_expense_categ_id'):
                expense_source_id = cat['property_account_expense_categ_id'][0]
                if expense_source_id in self.account_mapping:
                    data['property_account_expense_categ_id'] = self.account_mapping[expense_source_id]
            
            # Méthode de coût et valorisation (si disponibles)
            if cat.get('property_cost_method'):
                data['property_cost_method'] = cat['property_cost_method']
            
            if cat.get('property_valuation'):
                data['property_valuation'] = cat['property_valuation']
            
            try:
                # Créer catégorie
                dest_id = self.conn.executer_destination(
                    'product.category',
                    'create',
                    data
                )
                
                self.categorie_mapping[source_id] = dest_id
                categories_dest_by_name[name] = dest_id
                logging.info(f"  ✓ Catégorie créée : {name} (ID: {dest_id})")
                
            except Exception as e:
                logging.error(f"  ✗ Erreur création catégorie {name}: {e}")
        
        self.sauvegarder_categorie_mapping()
        logging.info(f"\n✓ Migration catégories terminée : {len(self.categorie_mapping)} catégories")
    
    def migrer_produits(self):
        """Migre les produits (templates et variantes)"""
        logging.info("\n" + "="*70)
        logging.info("MIGRATION DES PRODUITS")
        if TEST_MODE:
            logging.info(f"⚠️  MODE TEST : Limite à {TEST_LIMIT} produits")
        logging.info("="*70)
        
        # Récupérer produits source (product.template)
        domain = []
        if TEST_MODE:
            domain = [('id', '<=', TEST_LIMIT)]
        
        produits_source = self.conn.executer_source(
            'product.template',
            'search_read',
            domain,
            fields=['name', 'default_code', 'type', 'categ_id', 'list_price', 
                   'standard_price', 'description', 'description_sale', 
                   'description_purchase', 'uom_id', 'uom_po_id', 'sale_ok',
                   'purchase_ok', 'active', 'weight', 'volume', 'barcode',
                   'taxes_id', 'supplier_taxes_id']
        )
        
        self.stats['total'] = len(produits_source)
        logging.info(f"✓ {self.stats['total']} produits à migrer")
        
        # Récupérer produits destination
        produits_dest = self.conn.executer_destination(
            'product.template',
            'search_read',
            [],
            fields=['name', 'default_code']
        )
        
        # Index par référence et nom
        produits_dest_by_ref = {p['default_code']: p['id'] 
                               for p in produits_dest if p.get('default_code')}
        produits_dest_by_name = {p['name']: p['id'] for p in produits_dest}
        
        # Migrer chaque produit
        for idx, prod in enumerate(produits_source, 1):
            source_id = prod['id']
            name = prod['name']
            ref = prod.get('default_code', '')
            
            logging.info(f"\n[{idx}/{self.stats['total']}] {name} ({ref or 'sans ref'})")
            
            # Vérifier si existe (par référence ou nom)
            dest_id = None
            if ref and ref in produits_dest_by_ref:
                dest_id = produits_dest_by_ref[ref]
                logging.info(f"  Produit existant par référence (ID: {dest_id})")
                self.stats['existants'] += 1
                continue
            elif name in produits_dest_by_name:
                dest_id = produits_dest_by_name[name]
                logging.info(f"  Produit existant par nom (ID: {dest_id})")
                self.stats['existants'] += 1
                continue
            
            # Préparer données
            data = {
                'name': name,
                'type': prod.get('type', 'consu'),
                'list_price': prod.get('list_price', 0.0),
                'standard_price': prod.get('standard_price', 0.0),
                'sale_ok': prod.get('sale_ok', True),
                'purchase_ok': prod.get('purchase_ok', True),
                'active': prod.get('active', True),
            }
            
            # Référence
            if ref:
                data['default_code'] = ref
            
            # Descriptions
            if prod.get('description'):
                data['description'] = prod['description']
            if prod.get('description_sale'):
                data['description_sale'] = prod['description_sale']
            if prod.get('description_purchase'):
                data['description_purchase'] = prod['description_purchase']
            
            # Catégorie
            if prod.get('categ_id'):
                categ_source_id = prod['categ_id'][0]
                if categ_source_id in self.categorie_mapping:
                    data['categ_id'] = self.categorie_mapping[categ_source_id]
            
            # Unités de mesure (garder celles par défaut si non trouvées)
            if prod.get('uom_id'):
                data['uom_id'] = prod['uom_id'][0]
            if prod.get('uom_po_id'):
                data['uom_po_id'] = prod['uom_po_id'][0]
            
            # Poids et volume
            if prod.get('weight'):
                data['weight'] = prod['weight']
            if prod.get('volume'):
                data['volume'] = prod['volume']
            
            # Code-barres
            if prod.get('barcode'):
                data['barcode'] = prod['barcode']
            
            # Taxes (garder les IDs si disponibles)
            if prod.get('taxes_id'):
                data['taxes_id'] = [(6, 0, prod['taxes_id'])]
            if prod.get('supplier_taxes_id'):
                data['supplier_taxes_id'] = [(6, 0, prod['supplier_taxes_id'])]
            
            try:
                # Créer produit
                dest_id = self.conn.executer_destination(
                    'product.template',
                    'create',
                    data
                )
                
                logging.info(f"  ✓ Produit créé (ID: {dest_id})")
                self.stats['migres'] += 1
                
                if ref:
                    produits_dest_by_ref[ref] = dest_id
                produits_dest_by_name[name] = dest_id
                
            except Exception as e:
                logging.error(f"  ✗ Erreur création produit {name}: {e}")
                self.stats['erreurs'] += 1
    
    def afficher_stats(self):
        """Affiche les statistiques finales"""
        logging.info("\n" + "="*70)
        logging.info("STATISTIQUES FINALES")
        logging.info("="*70)
        logging.info(f"Total à migrer    : {self.stats['total']}")
        logging.info(f"Nouveaux migrés   : {self.stats['migres']}")
        logging.info(f"Déjà existants    : {self.stats['existants']}")
        logging.info(f"Erreurs           : {self.stats['erreurs']}")
        
        if self.stats['total'] > 0:
            taux = ((self.stats['migres'] + self.stats['existants']) / self.stats['total']) * 100
            logging.info(f"Taux de succès    : {taux:.1f}%")
        
        if TEST_MODE:
            logging.info(f"\n⚠️  MODE TEST : Seulement {TEST_LIMIT} produits traités")
            logging.info("   Pour tout migrer, mettre TEST_MODE = False dans le script")
    
    def executer(self):
        """Exécute la migration complète"""
        debut = datetime.now()
        
        logging.info("\n" + "="*70)
        logging.info("DÉBUT MIGRATION PRODUITS v16 → v19")
        logging.info("="*70)
        logging.info(f"Heure de début : {debut.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Connexion
        if not self.conn.connecter_tout():
            logging.error("✗ Échec de connexion")
            return False
        
        # Charger mapping des comptes
        self.charger_account_mapping()
        
        # Migrer catégories d'abord
        self.migrer_categories()
        
        # Puis migrer produits
        self.migrer_produits()
        
        # Stats finales
        self.afficher_stats()
        
        fin = datetime.now()
        duree = fin - debut
        logging.info(f"\nDurée totale : {duree}")
        logging.info("="*70)
        
        return self.stats['erreurs'] == 0


def main():
    """Fonction principale"""
    migration = MigrationProduits()
    success = migration.executer()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

