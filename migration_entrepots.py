#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION ENTREPÔTS v16 → v19
=============================
Migre les entrepôts (stock.warehouse) et emplacements de stock
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from connexion_double_v19 import ConnexionDoubleV19

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/migration_entrepots.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class MigrationEntrepots:
    """Gestion de la migration des entrepôts"""
    
    def __init__(self):
        self.conn = ConnexionDoubleV19()
        self.stats = {
            'total': 0,
            'migres': 0,
            'existants': 0,
            'erreurs': 0
        }
        self.warehouse_mapping = {}
        self.partner_mapping = {}
        self.logs_dir = Path('logs')
        self.logs_dir.mkdir(exist_ok=True)
    
    def charger_partner_mapping(self):
        """Charge le mapping des partenaires"""
        mapping_file = self.logs_dir / 'partner_mapping.json'
        
        if mapping_file.exists():
            with open(mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.partner_mapping = {int(k): v for k, v in data.items()}
            logging.info(f"OK Mapping partenaires charge : {len(self.partner_mapping)}")
            return True
        else:
            logging.warning("ATTENTION Fichier partner_mapping.json non trouve")
            return False
    
    def sauvegarder_warehouse_mapping(self):
        """Sauvegarde le mapping des entrepôts"""
        mapping_file = self.logs_dir / 'warehouse_mapping.json'
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.warehouse_mapping, f, indent=2)
        logging.info(f"OK Mapping entrepots sauvegarde : {len(self.warehouse_mapping)}")
    
    def migrer_entrepots(self):
        """Migre les entrepôts"""
        print("\n" + "="*70)
        print("MIGRATION DES ENTREPOTS")
        print("="*70)
        
        # Récupérer entrepôts source
        warehouses_source = self.conn.executer_source(
            'stock.warehouse',
            'search_read',
            [],
            fields=['name', 'code', 'partner_id', 'active']
        )
        
        self.stats['total'] = len(warehouses_source)
        print(f"OK {self.stats['total']} entrepots a migrer")
        logging.info(f"OK {self.stats['total']} entrepots a migrer")
        
        # Récupérer entrepôts destination
        warehouses_dest = self.conn.executer_destination(
            'stock.warehouse',
            'search_read',
            [],
            fields=['name', 'code']
        )
        
        # Index par code et nom
        warehouses_dest_by_code = {w['code']: w['id'] for w in warehouses_dest}
        warehouses_dest_by_name = {w['name']: w['id'] for w in warehouses_dest}
        
        print(f"OK {len(warehouses_dest)} entrepots existants dans destination")
        
        # Migrer chaque entrepôt
        for idx, wh in enumerate(warehouses_source, 1):
            source_id = wh['id']
            name = wh['name']
            code = wh.get('code', '')
            
            print(f"\n[{idx}/{self.stats['total']}] {name} ({code})")
            
            # Vérifier si existe
            dest_id = None
            if code and code in warehouses_dest_by_code:
                dest_id = warehouses_dest_by_code[code]
                print(f"  OK Entrepot existant par code (ID: {dest_id})")
                self.warehouse_mapping[source_id] = dest_id
                self.stats['existants'] += 1
                continue
            elif name in warehouses_dest_by_name:
                dest_id = warehouses_dest_by_name[name]
                print(f"  OK Entrepot existant par nom (ID: {dest_id})")
                self.warehouse_mapping[source_id] = dest_id
                self.stats['existants'] += 1
                continue
            
            # Préparer données
            data = {
                'name': name,
                'code': code or name[:5].upper(),  # Code obligatoire
                'active': wh.get('active', True),
            }
            
            # Partenaire (adresse)
            if wh.get('partner_id'):
                partner_source_id = wh['partner_id'][0]
                if partner_source_id in self.partner_mapping:
                    data['partner_id'] = self.partner_mapping[partner_source_id]
            
            try:
                # Créer entrepôt
                dest_id = self.conn.executer_destination(
                    'stock.warehouse',
                    'create',
                    data
                )
                
                print(f"  OK Entrepot cree (ID: {dest_id})")
                logging.info(f"  OK Entrepot cree : {name} (ID: {dest_id})")
                self.stats['migres'] += 1
                self.warehouse_mapping[source_id] = dest_id
                
                warehouses_dest_by_code[code] = dest_id
                warehouses_dest_by_name[name] = dest_id
                
            except Exception as e:
                print(f"  ERREUR Creation entrepot {name}: {e}")
                logging.error(f"  ERREUR Creation entrepot {name}: {e}")
                self.stats['erreurs'] += 1
        
        self.sauvegarder_warehouse_mapping()
    
    def afficher_stats(self):
        """Affiche les statistiques"""
        print("\n" + "="*70)
        print("STATISTIQUES FINALES")
        print("="*70)
        print(f"Total a migrer    : {self.stats['total']}")
        print(f"Nouveaux migres   : {self.stats['migres']}")
        print(f"Deja existants    : {self.stats['existants']}")
        print(f"Erreurs           : {self.stats['erreurs']}")
        
        if self.stats['total'] > 0:
            taux = ((self.stats['migres'] + self.stats['existants']) / self.stats['total']) * 100
            print(f"Taux de succes    : {taux:.1f}%")
    
    def executer(self):
        """Exécute la migration"""
        debut = datetime.now()
        
        print("\n" + "="*70)
        print("DEBUT MIGRATION ENTREPOTS v16 -> v19")
        print("="*70)
        
        # Connexion
        if not self.conn.connecter_tout():
            print("X Echec de connexion")
            return False
        
        # Charger mapping partenaires
        self.charger_partner_mapping()
        
        # Migrer entrepôts
        self.migrer_entrepots()
        
        # Stats
        self.afficher_stats()
        
        fin = datetime.now()
        duree = fin - debut
        print(f"\nDuree totale : {duree}")
        print("="*70)
        
        return self.stats['erreurs'] == 0


def main():
    migration = MigrationEntrepots()
    success = migration.executer()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

