#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION COMPLETE POUR LA NUIT
================================
Script optimisé pour migration complète durant la nuit
Inclut gestion des external_id
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from connexion_double_v19 import ConnexionDoubleV19
from utils.external_id_manager import ExternalIdManager

# MODE TEST : Limiter chaque module
TEST_MODE = True
TEST_LIMIT = 10  # 10 enregistrements par module

LOGS_DIR = Path('logs')
LOGS_DIR.mkdir(exist_ok=True)

class MigrationNuit:
    """Migration complète optimisée"""
    
    def __init__(self):
        self.conn = ConnexionDoubleV19()
        self.ext_mgr = None
        self.mappings = {}
        self.log_file = LOGS_DIR / f'migration_nuit_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
    
    def log(self, message):
        """Log dans fichier et console"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[{timestamp}] {message}"
        print(msg, flush=True)  # FORCER l'affichage immédiat
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    
    def sauver_mapping(self, model, mapping):
        """Sauvegarde un mapping"""
        nom = model.replace('.', '_')
        fichier = LOGS_DIR / f'{nom}_mapping.json'
        with open(fichier, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2)
    
    def migrer_module(self, model, fields, nom_affichage):
        """Migre un module complet"""
        self.log(f"\n{'='*70}")
        self.log(f"MIGRATION: {nom_affichage}")
        self.log(f"{'='*70}")
        
        debut = time.time()
        
        # Récupérer source DIRECTEMENT (pas de chargement depuis external_id pour l'instant)
        self.log(f"  Recuperation depuis SOURCE...")
        
        kwargs = {'fields': fields}
        if TEST_MODE:
            kwargs['limit'] = TEST_LIMIT
        
        records = self.conn.executer_source(model, 'search_read', [], **kwargs)
        total = len(records)
        
        if TEST_MODE:
            self.log(f"  MODE TEST: {total} enregistrements a traiter")
        else:
            self.log(f"  OK {total} enregistrements a traiter")
        
        mapping = {}
        nouveau = 0
        erreurs = 0
        
        # Traiter chaque enregistrement
        for idx, rec in enumerate(records, 1):
            source_id = rec['id']
            
            # Vérifier via external_id
            existe, dest_id, ext_id = self.ext_mgr.verifier_existe(model, source_id)
            
            if not existe:
                # Préparer données minimales
                data = self._preparer_data(model, rec, fields)
                
                if data:
                    try:
                        dest_id = self.conn.executer_destination(model, 'create', data)
                        if ext_id:
                            self.ext_mgr.copier_external_id(model, dest_id, source_id)
                        nouveau += 1
                    except Exception as e:
                        self.log(f"  ERREUR ID {source_id}: {str(e)[:100]}")
                        erreurs += 1
                        continue
            
            if dest_id:
                mapping[source_id] = dest_id
            
            # Progression
            if TEST_MODE:
                # En mode test, afficher chaque ligne
                if dest_id:
                    status = "existant" if existe else "cree"
                    self.log(f"  [{idx}/{total}] ID {source_id} -> {dest_id} ({status})")
            elif idx % 100 == 0:
                pct = (idx / total) * 100
                self.log(f"  Progression: {idx}/{total} ({pct:.1f}%)")
        
        duree = time.time() - debut
        self.log(f"  TERMINE: {nouveau} nouveaux, {len(mapping)} total, {erreurs} erreurs en {duree:.1f}s")
        
        self.mappings[model] = mapping
        self.sauver_mapping(model, mapping)
        
        return nouveau, erreurs
    
    def _preparer_data(self, model, rec, fields):
        """Prépare les données selon le modèle"""
        data = {}
        
        if model == 'account.account':
            data = {
                'code': rec['code'],
                'name': rec['name'],
                'account_type': rec.get('account_type', 'asset_current'),
            }
            if rec.get('reconcile') is not None:
                data['reconcile'] = rec['reconcile']
        
        elif model == 'res.partner':
            data = {
                'name': rec.get('name') or f"Contact {rec['id']}",
                'active': rec.get('active', True),
            }
            for f in ['email', 'phone', 'ref', 'vat', 'street', 'city', 'zip']:
                if rec.get(f):
                    data[f] = rec[f]
        
        elif model == 'account.journal':
            account_mapping = self.mappings.get('account.account', {})
            data = {
                'name': rec['name'],
                'code': rec['code'],
                'type': rec['type'],
            }
            if rec.get('default_account_id') and rec['default_account_id'][0] in account_mapping:
                data['default_account_id'] = account_mapping[rec['default_account_id'][0]]
        
        elif model == 'hr.department':
            data = {'name': rec['name'], 'active': rec.get('active', True)}
        
        elif model == 'hr.job':
            data = {'name': rec['name'], 'active': rec.get('active', True)}
        
        elif model == 'hr.employee':
            data = {
                'name': rec['name'],
                'active': rec.get('active', True),
            }
            for f in ['work_email', 'work_phone']:
                if rec.get(f):
                    data[f] = rec[f]
        
        elif model == 'stock.warehouse':
            data = {
                'name': rec['name'],
                'code': rec.get('code') or rec['name'][:5].upper(),
                'active': rec.get('active', True),
            }
        
        elif model == 'product.category':
            data = {'name': rec['name'], 'active': rec.get('active', True)}
        
        elif model == 'product.template':
            product_type = rec.get('type', 'consu')
            is_storable = (product_type == 'product')
            if is_storable:
                product_type = 'consu'
            
            data = {
                'name': rec['name'],
                'type': product_type,
                'list_price': rec.get('list_price', 0.0),
                'active': rec.get('active', True),
            }
            if is_storable:
                data['is_storable'] = True
            if rec.get('default_code'):
                data['default_code'] = rec['default_code']
        
        return data
    
    def executer(self):
        """Exécute la migration complète"""
        debut = datetime.now()
        
        self.log("="*80)
        self.log(" " * 20 + "MIGRATION NUIT v16 -> v19")
        self.log(" " * 15 + "avec gestion des External ID")
        if TEST_MODE:
            self.log(" " * 10 + f"MODE TEST: {TEST_LIMIT} enregistrements par module")
        self.log("="*80)
        self.log(f"Debut: {debut.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log("="*80)
        
        # Connexion
        self.log("\nConnexion aux bases de donnees...")
        if not self.conn.connecter_tout():
            self.log("ERREUR: Echec de connexion")
            return False
        
        self.log("\nInitialisation du gestionnaire external_id...")
        self.ext_mgr = ExternalIdManager(self.conn)
        self.log("OK Gestionnaire external_id initialise\n")
        
        # Migration dans l'ordre
        modules = [
            ('account.account', ['code', 'name', 'account_type', 'reconcile'], 'Plan Comptable'),
            ('res.partner', ['name', 'email', 'phone', 'ref', 'vat', 'street', 'city', 'zip', 'active'], 'Partenaires'),
            ('account.journal', ['code', 'name', 'type', 'default_account_id'], 'Journaux'),
            ('hr.department', ['name', 'active'], 'Departements RH'),
            ('hr.job', ['name', 'active'], 'Postes'),
            ('hr.employee', ['name', 'work_email', 'work_phone', 'active'], 'Employes'),
            ('stock.warehouse', ['name', 'code', 'active'], 'Entrepots'),
            ('product.category', ['name', 'active'], 'Categories Produits'),
            ('product.template', ['name', 'default_code', 'type', 'list_price', 'active'], 'Produits'),
        ]
        
        total_nouveau = 0
        total_erreurs = 0
        
        for model, fields, nom in modules:
            nouveau, erreurs = self.migrer_module(model, fields, nom)
            total_nouveau += nouveau
            total_erreurs += erreurs
        
        # Résumé final
        fin = datetime.now()
        duree = fin - debut
        
        self.log("\n" + "="*80)
        self.log("MIGRATION TERMINEE")
        self.log("="*80)
        self.log(f"Debut             : {debut.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"Fin               : {fin.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log(f"Duree totale      : {duree}")
        self.log(f"Nouveaux migres   : {total_nouveau}")
        self.log(f"Erreurs           : {total_erreurs}")
        self.log("="*80)
        self.log(f"\nLog complet: {self.log_file}")
        
        return total_erreurs == 0


def main():
    migration = MigrationNuit()
    success = migration.executer()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

