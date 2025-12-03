#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION DÉPARTEMENTS v16 → v19
================================
Migre les départements (hr.department)
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
        logging.FileHandler('logs/migration_departements.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class MigrationDepartements:
    """Gestion de la migration des départements"""
    
    def __init__(self):
        self.conn = ConnexionDoubleV19()
        self.ext_id_mgr = None  # Sera initialisé après connexion
        self.stats = {
            'total': 0,
            'migres': 0,
            'existants': 0,
            'erreurs': 0
        }
        self.dept_mapping = {}
        self.logs_dir = Path('logs')
        self.logs_dir.mkdir(exist_ok=True)
    
    def sauvegarder_dept_mapping(self):
        """Sauvegarde le mapping des départements"""
        mapping_file = self.logs_dir / 'department_mapping.json'
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.dept_mapping, f, indent=2)
        logging.info(f"OK Mapping departements sauvegarde : {len(self.dept_mapping)}")
    
    def migrer_departements(self):
        """Migre les départements"""
        print("\n" + "="*70)
        print("MIGRATION DES DEPARTEMENTS")
        print("="*70)
        
        # Récupérer départements source
        depts_source = self.conn.executer_source(
            'hr.department',
            'search_read',
            [],
            fields=['name', 'parent_id', 'manager_id', 'company_id', 'active']
        )
        
        self.stats['total'] = len(depts_source)
        print(f"OK {self.stats['total']} departements a migrer")
        
        # Récupérer départements destination
        depts_dest = self.conn.executer_destination(
            'hr.department',
            'search_read',
            [],
            fields=['name', 'parent_id']
        )
        
        # Index par nom
        depts_dest_by_name = {d['name']: d['id'] for d in depts_dest}
        print(f"OK {len(depts_dest)} departements existants dans destination")
        
        # Trier pour traiter les parents d'abord
        depts_triees = sorted(depts_source, 
                             key=lambda x: (x['parent_id'][0] if x.get('parent_id') else 0))
        
        # Migrer chaque département
        for idx, dept in enumerate(depts_triees, 1):
            source_id = dept['id']
            name = dept['name']
            
            print(f"\n[{idx}/{self.stats['total']}] {name}")
            
            # Vérifier si existe via external_id
            existe, dest_id, ext_id = self.ext_id_mgr.verifier_existe('hr.department', source_id)
            if existe:
                if ext_id:
                    print(f"  OK Departement existant via external_id ({ext_id['module']}.{ext_id['name']}, ID: {dest_id})")
                else:
                    print(f"  OK Departement existant (ID: {dest_id})")
                self.dept_mapping[source_id] = dest_id
                self.stats['existants'] += 1
                continue
            
            # Sinon vérifier par nom
            if name in depts_dest_by_name:
                dest_id = depts_dest_by_name[name]
                print(f"  OK Departement existant par nom (ID: {dest_id})")
                # Copier l'external_id de la source si disponible
                if ext_id:
                    self.ext_id_mgr.copier_external_id('hr.department', dest_id, source_id)
                    print(f"     External_id copie: {ext_id['module']}.{ext_id['name']}")
                self.dept_mapping[source_id] = dest_id
                self.stats['existants'] += 1
                continue
            
            # Préparer données
            data = {
                'name': name,
                'active': dept.get('active', True),
            }
            
            # Parent (si déjà mappé)
            if dept.get('parent_id'):
                parent_source_id = dept['parent_id'][0]
                if parent_source_id in self.dept_mapping:
                    data['parent_id'] = self.dept_mapping[parent_source_id]
            
            try:
                # Créer département
                dest_id = self.conn.executer_destination(
                    'hr.department',
                    'create',
                    data
                )
                
                print(f"  OK Departement cree (ID: {dest_id})")
                logging.info(f"  OK Departement cree : {name} (ID: {dest_id})")
                
                # Copier l'external_id de la source
                ext_id = self.ext_id_mgr.get_external_id_from_source('hr.department', source_id)
                if ext_id:
                    self.ext_id_mgr.copier_external_id('hr.department', dest_id, source_id)
                    print(f"     External_id copie: {ext_id['module']}.{ext_id['name']}")
                
                self.stats['migres'] += 1
                self.dept_mapping[source_id] = dest_id
                depts_dest_by_name[name] = dest_id
                
            except Exception as e:
                print(f"  ERREUR Creation departement {name}: {e}")
                logging.error(f"  ERREUR Creation departement {name}: {e}")
                self.stats['erreurs'] += 1
        
        self.sauvegarder_dept_mapping()
    
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
        print("DEBUT MIGRATION DEPARTEMENTS v16 -> v19")
        print("="*70)
        
        # Connexion
        if not self.conn.connecter_tout():
            print("X Echec de connexion")
            return False
        
        # Initialiser le gestionnaire d'external_id
        self.ext_id_mgr = ExternalIdManager(self.conn)
        print("OK Gestionnaire external_id initialise")
        
        # Migrer départements
        self.migrer_departements()
        
        # Stats
        self.afficher_stats()
        
        fin = datetime.now()
        duree = fin - debut
        print(f"\nDuree totale : {duree}")
        print("="*70)
        
        return self.stats['erreurs'] == 0


def main():
    migration = MigrationDepartements()
    success = migration.executer()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

