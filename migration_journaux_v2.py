#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION JOURNAUX v16 -> v19 (Version 2 avec External ID)
==========================================================
Migre les journaux en copiant les external_id de la source
"""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime
from connexion_double_v19 import ConnexionDoubleV19
from utils.external_id_manager import ExternalIdManager

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/migration_journaux_v2.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class MigrationJournauxV2:
    """Migration des journaux avec external_id"""
    
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
        self.journal_mapping = {}
        self.account_mapping = {}
        self.logs_dir = Path('logs')
        self.logs_dir.mkdir(exist_ok=True)
    
    def charger_account_mapping(self):
        """Charge le mapping des comptes"""
        mapping_file = self.logs_dir / 'account_mapping.json'
        
        if mapping_file.exists():
            with open(mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.account_mapping = {int(k): v for k, v in data.items()}
            print(f"OK {len(self.account_mapping)} comptes mappes charges")
            return True
        return False
    
    def sauvegarder_mapping(self):
        """Sauvegarde le mapping"""
        mapping_file = self.logs_dir / 'journal_mapping.json'
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.journal_mapping, f, indent=2)
        logging.info(f"OK Mapping sauvegarde : {len(self.journal_mapping)} journaux")
    
    def migrer_journaux(self):
        """Migre tous les journaux"""
        print("\n" + "="*70)
        print("MIGRATION DES JOURNAUX")
        print("="*70)
        
        # Récupérer journaux source
        journaux_source = self.conn.executer_source(
            'account.journal',
            'search_read',
            [],
            fields=['name', 'code', 'type', 'default_account_id', 
                   'suspense_account_id', 'profit_account_id', 'loss_account_id',
                   'active']
        )
        
        self.stats['total'] = len(journaux_source)
        print(f"OK {self.stats['total']} journaux a migrer")
        
        # Récupérer journaux destination
        journaux_dest = self.conn.executer_destination(
            'account.journal',
            'search_read',
            [],
            fields=['code']
        )
        
        journaux_dest_by_code = {j['code']: j['id'] for j in journaux_dest}
        print(f"OK {len(journaux_dest)} journaux existants\n")
        
        # Migrer chaque journal
        for idx, journal in enumerate(journaux_source, 1):
            source_id = journal['id']
            code = journal['code']
            name = journal['name']
            
            print(f"[{idx}/{self.stats['total']}] {code} - {name}")
            
            # 1. Vérifier via external_id
            existe, dest_id, ext_id = self.ext_id_mgr.verifier_existe('account.journal', source_id)
            
            if existe:
                self.journal_mapping[source_id] = dest_id
                self.stats['existants'] += 1
                continue
            
            # 2. Vérifier par code
            if code in journaux_dest_by_code:
                dest_id = journaux_dest_by_code[code]
                
                if ext_id:
                    self.ext_id_mgr.copier_external_id('account.journal', dest_id, source_id)
                    self.stats['external_ids_copies'] += 1
                    print(f"  OK Existe + external_id copie ({ext_id['module']}.{ext_id['name']})")
                else:
                    print(f"  OK Existe (pas d'external_id)")
                
                self.journal_mapping[source_id] = dest_id
                self.stats['existants'] += 1
                continue
            
            # 3. Créer le journal
            data = {
                'name': name,
                'code': code,
                'type': journal['type'],
                'active': journal.get('active', True),
            }
            
            # Mapper les comptes
            if journal.get('default_account_id'):
                acc_id = journal['default_account_id'][0]
                if acc_id in self.account_mapping:
                    data['default_account_id'] = self.account_mapping[acc_id]
            
            if journal.get('suspense_account_id'):
                acc_id = journal['suspense_account_id'][0]
                if acc_id in self.account_mapping:
                    data['suspense_account_id'] = self.account_mapping[acc_id]
            
            if journal.get('profit_account_id'):
                acc_id = journal['profit_account_id'][0]
                if acc_id in self.account_mapping:
                    data['profit_account_id'] = self.account_mapping[acc_id]
            
            if journal.get('loss_account_id'):
                acc_id = journal['loss_account_id'][0]
                if acc_id in self.account_mapping:
                    data['loss_account_id'] = self.account_mapping[acc_id]
            
            try:
                dest_id = self.conn.executer_destination(
                    'account.journal',
                    'create',
                    data
                )
                
                if ext_id:
                    self.ext_id_mgr.copier_external_id('account.journal', dest_id, source_id)
                    self.stats['external_ids_copies'] += 1
                    print(f"  OK Cree + external_id copie ({ext_id['module']}.{ext_id['name']})")
                else:
                    print(f"  OK Cree (pas d'external_id)")
                
                self.journal_mapping[source_id] = dest_id
                journaux_dest_by_code[code] = dest_id
                self.stats['migres'] += 1
                
            except Exception as e:
                print(f"  ERREUR: {e}")
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
    
    def executer(self):
        """Exécute la migration"""
        debut = datetime.now()
        
        print("\n" + "="*70)
        print("MIGRATION JOURNAUX v16 -> v19 (avec External ID)")
        print("="*70)
        
        if not self.conn.connecter_tout():
            print("X Echec de connexion")
            return False
        
        self.ext_id_mgr = ExternalIdManager(self.conn)
        print("OK Gestionnaire external_id initialise")
        
        self.charger_account_mapping()
        self.migrer_journaux()
        self.afficher_stats()
        
        duree = datetime.now() - debut
        print(f"\nDuree totale : {duree}")
        print("="*70)
        
        return self.stats['erreurs'] == 0


def main():
    migration = MigrationJournauxV2()
    success = migration.executer()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

