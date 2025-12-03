#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION POSTES v16 → v19
==========================
Migre les postes/fonctions (hr.job)
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
        logging.FileHandler('logs/migration_postes.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class MigrationPostes:
    """Gestion de la migration des postes"""
    
    def __init__(self):
        self.conn = ConnexionDoubleV19()
        self.stats = {
            'total': 0,
            'migres': 0,
            'existants': 0,
            'erreurs': 0
        }
        self.job_mapping = {}
        self.dept_mapping = {}
        self.logs_dir = Path('logs')
        self.logs_dir.mkdir(exist_ok=True)
    
    def charger_dept_mapping(self):
        """Charge le mapping des départements"""
        mapping_file = self.logs_dir / 'department_mapping.json'
        
        if mapping_file.exists():
            with open(mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.dept_mapping = {int(k): v for k, v in data.items()}
            logging.info(f"OK Mapping departements charge : {len(self.dept_mapping)}")
            return True
        else:
            logging.warning("ATTENTION Fichier department_mapping.json non trouve")
            return False
    
    def sauvegarder_job_mapping(self):
        """Sauvegarde le mapping des postes"""
        mapping_file = self.logs_dir / 'job_mapping.json'
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.job_mapping, f, indent=2)
        logging.info(f"OK Mapping postes sauvegarde : {len(self.job_mapping)}")
    
    def migrer_postes(self):
        """Migre les postes"""
        print("\n" + "="*70)
        print("MIGRATION DES POSTES/FONCTIONS")
        print("="*70)
        
        # Récupérer postes source
        jobs_source = self.conn.executer_source(
            'hr.job',
            'search_read',
            [],
            fields=['name', 'department_id', 'company_id', 'active', 'description']
        )
        
        self.stats['total'] = len(jobs_source)
        print(f"OK {self.stats['total']} postes a migrer")
        
        # Récupérer postes destination
        jobs_dest = self.conn.executer_destination(
            'hr.job',
            'search_read',
            [],
            fields=['name', 'department_id']
        )
        
        # Index par nom
        jobs_dest_by_name = {j['name']: j['id'] for j in jobs_dest}
        print(f"OK {len(jobs_dest)} postes existants dans destination")
        
        # Migrer chaque poste
        for idx, job in enumerate(jobs_source, 1):
            source_id = job['id']
            name = job['name']
            
            print(f"\n[{idx}/{self.stats['total']}] {name}")
            
            # Vérifier si existe
            if name in jobs_dest_by_name:
                dest_id = jobs_dest_by_name[name]
                print(f"  OK Poste existant (ID: {dest_id})")
                self.job_mapping[source_id] = dest_id
                self.stats['existants'] += 1
                continue
            
            # Préparer données
            data = {
                'name': name,
                'active': job.get('active', True),
            }
            
            # Description
            if job.get('description'):
                data['description'] = job['description']
            
            # Département (si mappé)
            if job.get('department_id'):
                dept_source_id = job['department_id'][0]
                if dept_source_id in self.dept_mapping:
                    data['department_id'] = self.dept_mapping[dept_source_id]
            
            try:
                # Créer poste
                dest_id = self.conn.executer_destination(
                    'hr.job',
                    'create',
                    data
                )
                
                print(f"  OK Poste cree (ID: {dest_id})")
                logging.info(f"  OK Poste cree : {name} (ID: {dest_id})")
                self.stats['migres'] += 1
                self.job_mapping[source_id] = dest_id
                jobs_dest_by_name[name] = dest_id
                
            except Exception as e:
                print(f"  ERREUR Creation poste {name}: {e}")
                logging.error(f"  ERREUR Creation poste {name}: {e}")
                self.stats['erreurs'] += 1
        
        self.sauvegarder_job_mapping()
    
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
        
        # Charger mapping départements
        self.charger_dept_mapping()
        
        # Migrer postes
        self.migrer_postes()
        
        # Stats
        self.afficher_stats()
        
        fin = datetime.now()
        duree = fin - debut
        print(f"\nDuree totale : {duree}")
        print("="*70)
        
        return self.stats['erreurs'] == 0


def main():
    migration = MigrationPostes()
    success = migration.executer()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

