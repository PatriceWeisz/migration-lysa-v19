#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION PLAN COMPTABLE v16 -> v19 (Version 2 avec External ID)
=================================================================
Migre le plan comptable en copiant les external_id de la source
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from connexion_double_v19 import ConnexionDoubleV19
from utils.external_id_manager import ExternalIdManager

# MODE TEST
TEST_MODE = True
TEST_LIMIT = 20

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/migration_plan_comptable_v2.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class MigrationPlanComptableV2:
    """Migration du plan comptable avec external_id"""
    
    def __init__(self):
        self.conn = ConnexionDoubleV19()
        self.ext_id_mgr = None
        self.stats = {
            'total': 0,
            'migres': 0,
            'existants': 0,
            'external_ids_copies': 0,
            'erreurs': 0
        }
        self.account_mapping = {}
        self.logs_dir = Path('logs')
        self.logs_dir.mkdir(exist_ok=True)
    
    def sauvegarder_mapping(self):
        """Sauvegarde le mapping"""
        mapping_file = self.logs_dir / 'account_mapping.json'
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.account_mapping, f, indent=2)
        logging.info(f"OK Mapping sauvegarde : {len(self.account_mapping)} comptes")
    
    def migrer_comptes(self):
        """Migre tous les comptes"""
        print("\n" + "="*70)
        print("MIGRATION DU PLAN COMPTABLE")
        if TEST_MODE:
            print(f"ATTENTION MODE TEST : Limite a {TEST_LIMIT} comptes")
        print("="*70)
        
        # Récupérer comptes source
        print("\nRecuperation des comptes SOURCE...")
        
        kwargs = {'fields': ['code', 'name', 'account_type', 'reconcile', 'note']}
        if TEST_MODE:
            kwargs['limit'] = TEST_LIMIT
        
        comptes_source = self.conn.executer_source(
            'account.account',
            'search_read',
            [],
            **kwargs
        )
        
        self.stats['total'] = len(comptes_source)
        print(f"OK {self.stats['total']} comptes a migrer")
        
        # Récupérer comptes destination
        print("\nRecuperation des comptes DESTINATION...")
        comptes_dest = self.conn.executer_destination(
            'account.account',
            'search_read',
            [],
            fields=['code', 'name']
        )
        
        # Index par code
        comptes_dest_by_code = {c['code']: c['id'] for c in comptes_dest}
        print(f"OK {len(comptes_dest)} comptes existants dans destination")
        
        print("\n" + "="*70)
        print("MIGRATION EN COURS...")
        print("="*70)
        
        # Migrer chaque compte
        for idx, compte in enumerate(comptes_source, 1):
            source_id = compte['id']
            code = compte['code']
            name = compte['name']
            
            if idx % 100 == 0 or idx == 1:
                print(f"\n[{idx}/{self.stats['total']}] {code} - {name}")
            
            # 1. Vérifier si existe via external_id
            existe, dest_id, ext_id = self.ext_id_mgr.verifier_existe('account.account', source_id)
            
            if existe:
                self.account_mapping[source_id] = dest_id
                self.stats['existants'] += 1
                continue
            
            # 2. Vérifier si existe par code
            if code in comptes_dest_by_code:
                dest_id = comptes_dest_by_code[code]
                
                # Copier l'external_id si disponible
                if ext_id:
                    self.ext_id_mgr.copier_external_id('account.account', dest_id, source_id)
                    self.stats['external_ids_copies'] += 1
                
                self.account_mapping[source_id] = dest_id
                self.stats['existants'] += 1
                continue
            
            # 3. Créer le compte
            # Mapper le type
            account_type = compte.get('account_type', 'asset_current')
            
            data = {
                'code': code,
                'name': name,
                'account_type': account_type,
            }
            
            if compte.get('reconcile') is not None:
                data['reconcile'] = compte['reconcile']
            
            if compte.get('note'):
                data['note'] = compte['note']
            
            try:
                # Créer
                dest_id = self.conn.executer_destination(
                    'account.account',
                    'create',
                    data
                )
                
                # Copier l'external_id
                if ext_id:
                    self.ext_id_mgr.copier_external_id('account.account', dest_id, source_id)
                    self.stats['external_ids_copies'] += 1
                
                self.account_mapping[source_id] = dest_id
                comptes_dest_by_code[code] = dest_id
                self.stats['migres'] += 1
                
            except Exception as e:
                print(f"  ERREUR {code}: {e}")
                logging.error(f"ERREUR {code}: {e}")
                self.stats['erreurs'] += 1
        
        self.sauvegarder_mapping()
    
    def afficher_stats(self):
        """Affiche les statistiques"""
        print("\n" + "="*70)
        print("STATISTIQUES FINALES")
        print("="*70)
        print(f"Total a migrer        : {self.stats['total']}")
        print(f"Nouveaux migres       : {self.stats['migres']}")
        print(f"Deja existants        : {self.stats['existants']}")
        print(f"External_ids copies   : {self.stats['external_ids_copies']}")
        print(f"Erreurs               : {self.stats['erreurs']}")
        
        if self.stats['total'] > 0:
            taux = ((self.stats['migres'] + self.stats['existants']) / self.stats['total']) * 100
            print(f"Taux de succes        : {taux:.1f}%")
        
        if TEST_MODE:
            print(f"\nATTENTION MODE TEST : Seulement {TEST_LIMIT} comptes traites")
            print("   Pour tout migrer, mettre TEST_MODE = False dans le script")
    
    def executer(self):
        """Exécute la migration"""
        debut = datetime.now()
        
        print("\n" + "="*70)
        print("DEBUT MIGRATION PLAN COMPTABLE v16 -> v19")
        print("="*70)
        
        # Connexion
        if not self.conn.connecter_tout():
            print("X Echec de connexion")
            return False
        
        # Initialiser le gestionnaire d'external_id
        self.ext_id_mgr = ExternalIdManager(self.conn)
        print("OK Gestionnaire external_id initialise")
        
        # Migrer
        self.migrer_comptes()
        
        # Stats
        self.afficher_stats()
        
        fin = datetime.now()
        duree = fin - debut
        print(f"\nDuree totale : {duree}")
        print("="*70)
        
        return self.stats['erreurs'] == 0


def main():
    migration = MigrationPlanComptableV2()
    success = migration.executer()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

