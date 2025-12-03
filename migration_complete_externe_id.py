#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION COMPLETE AVEC EXTERNAL ID
===================================
Script d'orchestration complet de la migration v16 -> v19
Inclut la gestion des external_id pour tous les modules
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from connexion_double_v19 import ConnexionDoubleV19
from utils.external_id_manager import ExternalIdManager

# Configuration
LOGS_DIR = Path('logs')
LOGS_DIR.mkdir(exist_ok=True)

# ORDRE DE MIGRATION
MODULES = [
    'account.account',      # Plan comptable
    'res.partner',          # Partenaires
    'account.journal',      # Journaux
    'res.users',           # Utilisateurs
    'hr.department',       # Départements RH
    'hr.job',              # Postes/Fonctions
    'hr.employee',         # Employés
    'stock.warehouse',     # Entrepôts
    'product.category',    # Catégories produits
    'product.template',    # Produits
]

class MigrationCompleteExternalId:
    """Orchestrateur de migration complète"""
    
    def __init__(self):
        self.conn = ConnexionDoubleV19()
        self.ext_id_mgr = None
        self.mappings = {}
        self.stats_globales = {
            'modules_migres': 0,
            'modules_erreurs': 0,
            'total_enregistrements': 0,
            'total_migres': 0,
            'total_existants': 0,
            'total_external_ids': 0,
            'total_erreurs': 0
        }
    
    def sauvegarder_mapping(self, model, mapping):
        """Sauvegarde un mapping"""
        model_name = model.replace('.', '_')
        mapping_file = LOGS_DIR / f'{model_name}_mapping.json'
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2)
        print(f"  -> Mapping sauvegarde : {len(mapping)} enregistrements")
    
    def charger_mapping(self, model):
        """Charge un mapping existant"""
        model_name = model.replace('.', '_')
        mapping_file = LOGS_DIR / f'{model_name}_mapping.json'
        
        if mapping_file.exists():
            with open(mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {int(k): v for k, v in data.items()}
        return {}
    
    def migrer_compte_comptable(self):
        """Migre le plan comptable"""
        print("\n" + "="*70)
        print("1. PLAN COMPTABLE")
        print("="*70)
        
        # Charger si déjà fait
        mapping = self.ext_id_mgr.charger_mapping_depuis_external_ids('account.account')
        if mapping:
            print(f"OK {len(mapping)} comptes deja migres (via external_id)")
            self.mappings['account.account'] = mapping
            self.stats_globales['total_existants'] += len(mapping)
            return True
        
        # Sinon migrer
        print("Migration des comptes...")
        comptes = self.conn.executer_source('account.account', 'search_read', [], 
                                           fields=['code', 'name', 'account_type', 'reconcile'])
        
        mapping = {}
        compteur = 0
        
        for compte in comptes:
            source_id = compte['id']
            
            # Vérifier existence
            existe, dest_id, ext_id = self.ext_id_mgr.verifier_existe('account.account', source_id)
            
            if not existe:
                # Créer
                data = {
                    'code': compte['code'],
                    'name': compte['name'],
                    'account_type': compte.get('account_type', 'asset_current'),
                }
                if compte.get('reconcile') is not None:
                    data['reconcile'] = compte['reconcile']
                
                try:
                    dest_id = self.conn.executer_destination('account.account', 'create', data)
                    if ext_id:
                        self.ext_id_mgr.copier_external_id('account.account', dest_id, source_id)
                    compteur += 1
                except Exception as e:
                    print(f"  ERREUR {compte['code']}: {e}")
                    continue
            
            mapping[source_id] = dest_id
            
            if len(mapping) % 100 == 0:
                print(f"  {len(mapping)} comptes traites...")
        
        print(f"OK {compteur} comptes migres, {len(mapping)} total")
        self.mappings['account.account'] = mapping
        self.sauvegarder_mapping('account.account', mapping)
        self.stats_globales['total_migres'] += compteur
        self.stats_globales['modules_migres'] += 1
        return True
    
    def migrer_partenaires(self):
        """Migre les partenaires"""
        print("\n" + "="*70)
        print("2. PARTENAIRES")
        print("="*70)
        
        # Charger si déjà fait
        mapping = self.ext_id_mgr.charger_mapping_depuis_external_ids('res.partner')
        if mapping:
            print(f"OK {len(mapping)} partenaires deja migres")
            self.mappings['res.partner'] = mapping
            return True
        
        print("Migration des partenaires...")
        partners = self.conn.executer_source('res.partner', 'search_read', [],
                                            fields=['name', 'email', 'phone', 'ref', 'vat', 'active'])
        
        mapping = {}
        compteur = 0
        
        for partner in partners:
            source_id = partner['id']
            existe, dest_id, ext_id = self.ext_id_mgr.verifier_existe('res.partner', source_id)
            
            if not existe:
                data = {
                    'name': partner.get('name') or f"Contact {source_id}",
                    'active': partner.get('active', True),
                }
                if partner.get('email'):
                    data['email'] = partner['email']
                if partner.get('phone'):
                    data['phone'] = partner['phone']
                if partner.get('ref'):
                    data['ref'] = partner['ref']
                if partner.get('vat'):
                    data['vat'] = partner['vat']
                
                try:
                    dest_id = self.conn.executer_destination('res.partner', 'create', data)
                    if ext_id:
                        self.ext_id_mgr.copier_external_id('res.partner', dest_id, source_id)
                    compteur += 1
                except Exception as e:
                    continue
            
            mapping[source_id] = dest_id
            
            if len(mapping) % 100 == 0:
                print(f"  {len(mapping)} partenaires traites...")
        
        print(f"OK {compteur} partenaires migres, {len(mapping)} total")
        self.mappings['res.partner'] = mapping
        self.sauvegarder_mapping('res.partner', mapping)
        self.stats_globales['total_migres'] += compteur
        self.stats_globales['modules_migres'] += 1
        return True
    
    def migrer_journaux(self):
        """Migre les journaux"""
        print("\n" + "="*70)
        print("3. JOURNAUX")
        print("="*70)
        
        account_mapping = self.mappings.get('account.account', {})
        
        journaux = self.conn.executer_source('account.journal', 'search_read', [],
                                            fields=['code', 'name', 'type', 'default_account_id'])
        
        mapping = {}
        compteur = 0
        
        for journal in journaux:
            source_id = journal['id']
            existe, dest_id, ext_id = self.ext_id_mgr.verifier_existe('account.journal', source_id)
            
            if not existe:
                data = {
                    'name': journal['name'],
                    'code': journal['code'],
                    'type': journal['type'],
                }
                
                if journal.get('default_account_id') and journal['default_account_id'][0] in account_mapping:
                    data['default_account_id'] = account_mapping[journal['default_account_id'][0]]
                
                try:
                    dest_id = self.conn.executer_destination('account.journal', 'create', data)
                    if ext_id:
                        self.ext_id_mgr.copier_external_id('account.journal', dest_id, source_id)
                    compteur += 1
                except:
                    continue
            
            mapping[source_id] = dest_id
        
        print(f"OK {compteur} journaux migres, {len(mapping)} total")
        self.mappings['account.journal'] = mapping
        self.sauvegarder_mapping('account.journal', mapping)
        self.stats_globales['total_migres'] += compteur
        self.stats_globales['modules_migres'] += 1
        return True
    
    def migrer_simple(self, model, fields, name_field='name'):
        """Migre un module simple"""
        model_nom = model.split('.')[-1]
        print(f"\nMigration {model_nom}...")
        
        records = self.conn.executer_source(model, 'search_read', [], fields=fields)
        mapping = {}
        compteur = 0
        
        for record in records:
            source_id = record['id']
            existe, dest_id, ext_id = self.ext_id_mgr.verifier_existe(model, source_id)
            
            if not existe:
                data = {name_field: record.get(name_field, f"Record {source_id}")}
                for field in fields:
                    if field not in ['id', name_field] and record.get(field):
                        if isinstance(record[field], (list, tuple)) and len(record[field]) == 2:
                            continue  # Skip many2one
                        data[field] = record[field]
                
                try:
                    dest_id = self.conn.executer_destination(model, 'create', data)
                    if ext_id:
                        self.ext_id_mgr.copier_external_id(model, dest_id, source_id)
                    compteur += 1
                except:
                    continue
            
            mapping[source_id] = dest_id
        
        print(f"OK {compteur} {model_nom} migres, {len(mapping)} total")
        self.mappings[model] = mapping
        self.sauvegarder_mapping(model, mapping)
        self.stats_globales['total_migres'] += compteur
        return True
    
    def afficher_stats_globales(self):
        """Affiche les stats globales"""
        print("\n" + "="*70)
        print("STATISTIQUES GLOBALES DE MIGRATION")
        print("="*70)
        print(f"Modules migres        : {self.stats_globales['modules_migres']}")
        print(f"Modules en erreur     : {self.stats_globales['modules_erreurs']}")
        print(f"Total enregistrements : {self.stats_globales['total_enregistrements']}")
        print(f"Total migres          : {self.stats_globales['total_migres']}")
        print(f"Total existants       : {self.stats_globales['total_existants']}")
        print(f"External_ids copies   : {self.stats_globales['total_external_ids']}")
        print(f"Erreurs               : {self.stats_globales['total_erreurs']}")
    
    def executer(self):
        """Exécute la migration complète"""
        debut = datetime.now()
        
        print("\n" + "="*80)
        print(" " * 15 + "MIGRATION COMPLETE v16 -> v19")
        print(" " * 20 + "AVEC EXTERNAL ID")
        print("="*80)
        print(f"Heure de debut : {debut.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)
        
        # Connexion
        if not self.conn.connecter_tout():
            print("X Echec de connexion")
            return False
        
        # Initialiser gestionnaire external_id
        self.ext_id_mgr = ExternalIdManager(self.conn)
        print("\nOK Gestionnaire external_id initialise")
        
        # Migration dans l'ordre
        try:
            self.migrer_compte_comptable()
            self.migrer_partenaires()
            self.migrer_journaux()
            
            # Modules simples
            print("\n" + "="*70)
            print("4. DEPARTEMENTS RH")
            print("="*70)
            self.migrer_simple('hr.department', ['name', 'active'])
            self.stats_globales['modules_migres'] += 1
            
            print("\n" + "="*70)
            print("5. POSTES/FONCTIONS")
            print("="*70)
            self.migrer_simple('hr.job', ['name', 'active'])
            self.stats_globales['modules_migres'] += 1
            
            print("\n" + "="*70)
            print("6. EMPLOYES")
            print("="*70)
            self.migrer_simple('hr.employee', ['name', 'work_email', 'work_phone', 'active'])
            self.stats_globales['modules_migres'] += 1
            
            print("\n" + "="*70)
            print("7. ENTREPOTS")
            print("="*70)
            self.migrer_simple('stock.warehouse', ['name', 'code', 'active'], 'name')
            self.stats_globales['modules_migres'] += 1
            
            print("\n" + "="*70)
            print("8. CATEGORIES PRODUITS")
            print("="*70)
            self.migrer_simple('product.category', ['name', 'active'])
            self.stats_globales['modules_migres'] += 1
            
            print("\n" + "="*70)
            print("9. PRODUITS")
            print("="*70)
            produits = self.conn.executer_source('product.template', 'search_read', [],
                                                fields=['name', 'default_code', 'type', 'list_price', 'active'])
            
            mapping = {}
            compteur = 0
            
            for prod in produits:
                source_id = prod['id']
                existe, dest_id, ext_id = self.ext_id_mgr.verifier_existe('product.template', source_id)
                
                if not existe:
                    product_type = prod.get('type', 'consu')
                    is_storable = False
                    if product_type == 'product':
                        product_type = 'consu'
                        is_storable = True
                    
                    data = {
                        'name': prod['name'],
                        'type': product_type,
                        'list_price': prod.get('list_price', 0.0),
                        'active': prod.get('active', True),
                    }
                    
                    if is_storable:
                        data['is_storable'] = True
                    
                    if prod.get('default_code'):
                        data['default_code'] = prod['default_code']
                    
                    try:
                        dest_id = self.conn.executer_destination('product.template', 'create', data)
                        if ext_id:
                            self.ext_id_mgr.copier_external_id('product.template', dest_id, source_id)
                        compteur += 1
                    except:
                        continue
                
                mapping[source_id] = dest_id
                
                if len(mapping) % 100 == 0:
                    print(f"  {len(mapping)} produits traites...")
            
            print(f"OK {compteur} produits migres, {len(mapping)} total")
            self.mappings['product.template'] = mapping
            self.sauvegarder_mapping('product.template', mapping)
            self.stats_globales['total_migres'] += compteur
            self.stats_globales['modules_migres'] += 1
            
        except Exception as e:
            print(f"ERREUR MIGRATION: {e}")
            self.stats_globales['modules_erreurs'] += 1
            return False
        
        # Stats finales
        self.afficher_stats_globales()
        
        fin = datetime.now()
        duree = fin - debut
        print(f"\nHeure de fin : {fin.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duree totale : {duree}")
        print("="*80)
        
        return True


def main():
    migration = MigrationCompleteExternalId()
    success = migration.executer()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

