#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION PARTENAIRES v16 -> v19 (Version 2 avec External ID)
=============================================================
Migre les partenaires en copiant les external_id de la source
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
        logging.FileHandler('logs/migration_partenaires_v2.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class MigrationPartenairesV2:
    """Migration des partenaires avec external_id"""
    
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
        self.partner_mapping = {}
        self.logs_dir = Path('logs')
        self.logs_dir.mkdir(exist_ok=True)
    
    def sauvegarder_mapping(self):
        """Sauvegarde le mapping"""
        mapping_file = self.logs_dir / 'partner_mapping.json'
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.partner_mapping, f, indent=2)
        logging.info(f"OK Mapping sauvegarde : {len(self.partner_mapping)} partenaires")
    
    def migrer_partenaires(self):
        """Migre tous les partenaires"""
        print("\n" + "="*70)
        print("MIGRATION DES PARTENAIRES")
        if TEST_MODE:
            print(f"ATTENTION MODE TEST : Limite a {TEST_LIMIT} partenaires")
        print("="*70)
        
        # Récupérer partenaires source
        print("\nRecuperation des partenaires SOURCE...")
        
        kwargs = {
            'fields': ['name', 'email', 'phone', 'ref', 'vat', 'company_type',
                      'street', 'city', 'zip', 'country_id', 'active',
                      'customer_rank', 'supplier_rank', 'parent_id']
        }
        if TEST_MODE:
            kwargs['limit'] = TEST_LIMIT
        
        partenaires_source = self.conn.executer_source(
            'res.partner',
            'search_read',
            [],
            **kwargs
        )
        
        self.stats['total'] = len(partenaires_source)
        print(f"OK {self.stats['total']} partenaires a migrer")
        
        # Récupérer partenaires destination
        print("\nRecuperation des partenaires DESTINATION...")
        partenaires_dest = self.conn.executer_destination(
            'res.partner',
            'search_read',
            [],
            fields=['name', 'email', 'ref']
        )
        
        # Index par ref et email
        partenaires_dest_by_ref = {p['ref']: p['id'] for p in partenaires_dest if p.get('ref')}
        partenaires_dest_by_email = {p['email']: p['id'] for p in partenaires_dest if p.get('email')}
        
        print(f"OK {len(partenaires_dest)} partenaires existants dans destination")
        
        print("\n" + "="*70)
        print("MIGRATION EN COURS...")
        print("="*70)
        
        # Migrer chaque partenaire
        for idx, partner in enumerate(partenaires_source, 1):
            source_id = partner['id']
            name = partner.get('name') or f"Contact {source_id}"
            ref = partner.get('ref', '')
            email = partner.get('email', '')
            
            if idx % 10 == 0 or idx == 1:
                print(f"\n[{idx}/{self.stats['total']}] {name}")
            
            # 1. Vérifier si existe via external_id
            existe, dest_id, ext_id = self.ext_id_mgr.verifier_existe('res.partner', source_id)
            
            if existe:
                self.partner_mapping[source_id] = dest_id
                self.stats['existants'] += 1
                continue
            
            # 2. Vérifier par ref ou email
            if ref and ref in partenaires_dest_by_ref:
                dest_id = partenaires_dest_by_ref[ref]
                
                if ext_id:
                    self.ext_id_mgr.copier_external_id('res.partner', dest_id, source_id)
                    self.stats['external_ids_copies'] += 1
                
                self.partner_mapping[source_id] = dest_id
                self.stats['existants'] += 1
                continue
            
            if email and email in partenaires_dest_by_email:
                dest_id = partenaires_dest_by_email[email]
                
                if ext_id:
                    self.ext_id_mgr.copier_external_id('res.partner', dest_id, source_id)
                    self.stats['external_ids_copies'] += 1
                
                self.partner_mapping[source_id] = dest_id
                self.stats['existants'] += 1
                continue
            
            # 3. Créer le partenaire
            data = {
                'name': name,
                'active': partner.get('active', True),
            }
            
            if email:
                data['email'] = email
            if partner.get('phone'):
                data['phone'] = partner['phone']
            if ref:
                data['ref'] = ref
            if partner.get('vat'):
                data['vat'] = partner['vat']
            if partner.get('company_type'):
                data['company_type'] = partner['company_type']
            if partner.get('street'):
                data['street'] = partner['street']
            if partner.get('city'):
                data['city'] = partner['city']
            if partner.get('zip'):
                data['zip'] = partner['zip']
            if partner.get('country_id'):
                data['country_id'] = partner['country_id'][0]
            if partner.get('customer_rank'):
                data['customer_rank'] = partner['customer_rank']
            if partner.get('supplier_rank'):
                data['supplier_rank'] = partner['supplier_rank']
            
            try:
                # Créer
                dest_id = self.conn.executer_destination(
                    'res.partner',
                    'create',
                    data
                )
                
                # Copier l'external_id
                if ext_id:
                    self.ext_id_mgr.copier_external_id('res.partner', dest_id, source_id)
                    self.stats['external_ids_copies'] += 1
                
                self.partner_mapping[source_id] = dest_id
                if ref:
                    partenaires_dest_by_ref[ref] = dest_id
                if email:
                    partenaires_dest_by_email[email] = dest_id
                self.stats['migres'] += 1
                
            except Exception as e:
                print(f"  ERREUR {name}: {e}")
                logging.error(f"ERREUR {name}: {e}")
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
            print(f"\nATTENTION MODE TEST : Seulement {TEST_LIMIT} partenaires traites")
            print("   Pour tout migrer, mettre TEST_MODE = False dans le script")
    
    def executer(self):
        """Exécute la migration"""
        debut = datetime.now()
        
        print("\n" + "="*70)
        print("DEBUT MIGRATION PARTENAIRES v16 -> v19")
        print("="*70)
        
        # Connexion
        if not self.conn.connecter_tout():
            print("X Echec de connexion")
            return False
        
        # Initialiser le gestionnaire d'external_id
        self.ext_id_mgr = ExternalIdManager(self.conn)
        print("OK Gestionnaire external_id initialise")
        
        # Migrer
        self.migrer_partenaires()
        
        # Stats
        self.afficher_stats()
        
        fin = datetime.now()
        duree = fin - debut
        print(f"\nDuree totale : {duree}")
        print("="*70)
        
        return self.stats['erreurs'] == 0


def main():
    migration = MigrationPartenairesV2()
    success = migration.executer()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

