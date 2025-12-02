#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION EMPLOYÉS v16 → v19
============================
Migre les employés (hr.employee)
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
        logging.FileHandler('logs/migration_employes.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class MigrationEmployes:
    """Gestion de la migration des employés"""
    
    def __init__(self):
        self.conn = ConnexionDoubleV19()
        self.stats = {
            'total': 0,
            'migres': 0,
            'existants': 0,
            'erreurs': 0
        }
        self.employe_mapping = {}
        self.partner_mapping = {}
        self.user_mapping = {}
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
    
    def charger_user_mapping(self):
        """Charge le mapping des utilisateurs"""
        mapping_file = self.logs_dir / 'user_mapping.json'
        
        if mapping_file.exists():
            with open(mapping_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.user_mapping = {int(k): v for k, v in data.items()}
            logging.info(f"OK Mapping utilisateurs charge : {len(self.user_mapping)}")
            return True
        else:
            logging.warning("ATTENTION Fichier user_mapping.json non trouve")
            return False
    
    def sauvegarder_employe_mapping(self):
        """Sauvegarde le mapping des employés"""
        mapping_file = self.logs_dir / 'employe_mapping.json'
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.employe_mapping, f, indent=2)
        logging.info(f"OK Mapping employes sauvegarde : {len(self.employe_mapping)}")
    
    def migrer_employes(self):
        """Migre les employés"""
        print("\n" + "="*70)
        print("MIGRATION DES EMPLOYES")
        print("="*70)
        
        # Récupérer employés source
        employes_source = self.conn.executer_source(
            'hr.employee',
            'search_read',
            [],
            fields=['name', 'work_email', 'work_phone', 'mobile_phone',
                   'job_title', 'department_id', 'parent_id', 'coach_id',
                   'address_id', 'user_id', 'active']
        )
        
        self.stats['total'] = len(employes_source)
        print(f"OK {self.stats['total']} employes a migrer")
        logging.info(f"OK {self.stats['total']} employes a migrer")
        
        # Récupérer employés destination
        employes_dest = self.conn.executer_destination(
            'hr.employee',
            'search_read',
            [],
            fields=['name', 'work_email']
        )
        
        # Index par nom et email
        employes_dest_by_name = {e['name']: e['id'] for e in employes_dest}
        employes_dest_by_email = {e.get('work_email'): e['id'] 
                                  for e in employes_dest if e.get('work_email')}
        
        # Migrer chaque employé
        for idx, emp in enumerate(employes_source, 1):
            source_id = emp['id']
            name = emp['name']
            email = emp.get('work_email', '')
            
            print(f"\n[{idx}/{self.stats['total']}] {name}")
            
            # Vérifier si existe
            dest_id = None
            if email and email in employes_dest_by_email:
                dest_id = employes_dest_by_email[email]
                print(f"  OK Employe existant par email (ID: {dest_id})")
                self.employe_mapping[source_id] = dest_id
                self.stats['existants'] += 1
                continue
            elif name in employes_dest_by_name:
                dest_id = employes_dest_by_name[name]
                print(f"  OK Employe existant par nom (ID: {dest_id})")
                self.employe_mapping[source_id] = dest_id
                self.stats['existants'] += 1
                continue
            
            # Préparer données
            data = {
                'name': name,
                'active': emp.get('active', True),
            }
            
            # Email
            if email:
                data['work_email'] = email
            
            # Téléphones
            if emp.get('work_phone'):
                data['work_phone'] = emp['work_phone']
            if emp.get('mobile_phone'):
                data['mobile_phone'] = emp['mobile_phone']
            
            # Poste
            if emp.get('job_title'):
                data['job_title'] = emp['job_title']
            
            # Adresse (partenaire lié)
            if emp.get('address_id'):
                address_source_id = emp['address_id'][0]
                if address_source_id in self.partner_mapping:
                    data['address_id'] = self.partner_mapping[address_source_id]
            
            # Utilisateur lié
            if emp.get('user_id'):
                user_source_id = emp['user_id'][0]
                if user_source_id in self.user_mapping:
                    data['user_id'] = self.user_mapping[user_source_id]
            
            try:
                # Créer employé
                dest_id = self.conn.executer_destination(
                    'hr.employee',
                    'create',
                    data
                )
                
                print(f"  OK Employe cree (ID: {dest_id})")
                logging.info(f"  OK Employe cree : {name} (ID: {dest_id})")
                self.stats['migres'] += 1
                self.employe_mapping[source_id] = dest_id
                
                employes_dest_by_name[name] = dest_id
                if email:
                    employes_dest_by_email[email] = dest_id
                
            except Exception as e:
                print(f"  ERREUR Creation employe {name}: {e}")
                logging.error(f"  ERREUR Creation employe {name}: {e}")
                self.stats['erreurs'] += 1
        
        self.sauvegarder_employe_mapping()
    
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
        print("DEBUT MIGRATION EMPLOYES v16 -> v19")
        print("="*70)
        
        # Connexion
        if not self.conn.connecter_tout():
            print("X Echec de connexion")
            return False
        
        # Charger mappings
        self.charger_partner_mapping()
        self.charger_user_mapping()
        
        # Migrer employés
        self.migrer_employes()
        
        # Stats
        self.afficher_stats()
        
        fin = datetime.now()
        duree = fin - debut
        print(f"\nDuree totale : {duree}")
        print("="*70)
        
        return self.stats['erreurs'] == 0


def main():
    migration = MigrationEmployes()
    success = migration.executer()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

