#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION UTILISATEURS v16 → v19
================================
Migre les utilisateurs (res.users)
ATTENTION: Ne pas migrer les mots de passe, les utilisateurs devront les réinitialiser
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
        logging.FileHandler('logs/migration_users.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class MigrationUsers:
    """Gestion de la migration des utilisateurs"""
    
    def __init__(self):
        self.conn = ConnexionDoubleV19()
        self.stats = {
            'total': 0,
            'migres': 0,
            'existants': 0,
            'erreurs': 0,
            'admin_skipped': 0
        }
        self.user_mapping = {}
        self.partner_mapping = {}
        self.group_mapping = {}
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
    
    def sauvegarder_user_mapping(self):
        """Sauvegarde le mapping des utilisateurs"""
        mapping_file = self.logs_dir / 'user_mapping.json'
        with open(mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.user_mapping, f, indent=2)
        logging.info(f"OK Mapping users sauvegarde : {len(self.user_mapping)}")
    
    def mapper_groupes(self):
        """Crée un mapping des groupes source -> destination via external_id"""
        print("\nMapping des groupes d'utilisateurs...")
        
        # Récupérer tous les groupes source avec leur external_id
        groups_source = self.conn.executer_source(
            'res.groups',
            'search_read',
            [],
            fields=['name', 'category_id']
        )
        
        # Récupérer les external_ids des groupes source
        ir_model_data_source = self.conn.executer_source(
            'ir.model.data',
            'search_read',
            [('model', '=', 'res.groups')],
            fields=['res_id', 'module', 'name']
        )
        
        # Créer un index externe_id -> res_id pour la source
        source_ext_to_id = {}
        for data in ir_model_data_source:
            ext_id = f"{data['module']}.{data['name']}"
            source_ext_to_id[ext_id] = data['res_id']
        
        # Récupérer les external_ids des groupes destination
        ir_model_data_dest = self.conn.executer_destination(
            'ir.model.data',
            'search_read',
            [('model', '=', 'res.groups')],
            fields=['res_id', 'module', 'name']
        )
        
        # Créer un index externe_id -> res_id pour la destination
        dest_ext_to_id = {}
        for data in ir_model_data_dest:
            ext_id = f"{data['module']}.{data['name']}"
            dest_ext_to_id[ext_id] = data['res_id']
        
        # Mapper les groupes source -> destination via external_id
        for ext_id, source_id in source_ext_to_id.items():
            if ext_id in dest_ext_to_id:
                dest_id = dest_ext_to_id[ext_id]
                self.group_mapping[source_id] = dest_id
        
        print(f"OK {len(self.group_mapping)} groupes mappes (via external_id)")
        logging.info(f"OK {len(self.group_mapping)} groupes mappes")
    
    def migrer_users(self):
        """Migre les utilisateurs"""
        print("\n" + "="*70)
        print("MIGRATION DES UTILISATEURS")
        print("="*70)
        print("ATTENTION: Les mots de passe ne sont PAS migres")
        print("Les utilisateurs devront reinitialiser leurs mots de passe")
        print("="*70)
        
        # Récupérer utilisateurs source
        users_source = self.conn.executer_source(
            'res.users',
            'search_read',
            [('id', '!=', 1)],  # Exclure l'admin (ID=1)
            fields=['name', 'login', 'email', 'partner_id', 'active',
                   'company_id', 'company_ids', 'lang', 'tz', 'groups_id']
        )
        
        self.stats['total'] = len(users_source)
        print(f"\nOK {self.stats['total']} utilisateurs a migrer (admin exclu)")
        logging.info(f"OK {self.stats['total']} utilisateurs a migrer")
        
        # Récupérer utilisateurs destination
        users_dest = self.conn.executer_destination(
            'res.users',
            'search_read',
            [],
            fields=['login', 'email']
        )
        
        # Index par login et email
        users_dest_by_login = {u['login']: u['id'] for u in users_dest}
        users_dest_by_email = {u.get('email'): u['id'] 
                               for u in users_dest if u.get('email')}
        
        print(f"OK {len(users_dest)} utilisateurs existants dans destination")
        
        # Migrer chaque utilisateur
        for idx, user in enumerate(users_source, 1):
            source_id = user['id']
            name = user['name']
            login = user['login']
            email = user.get('email', '')
            
            print(f"\n[{idx}/{self.stats['total']}] {name} ({login})")
            
            # Vérifier si existe par login
            if login in users_dest_by_login:
                dest_id = users_dest_by_login[login]
                print(f"  OK Utilisateur existant par login (ID: {dest_id})")
                self.user_mapping[source_id] = dest_id
                self.stats['existants'] += 1
                continue
            
            # Vérifier si existe par email
            if email and email in users_dest_by_email:
                dest_id = users_dest_by_email[email]
                print(f"  OK Utilisateur existant par email (ID: {dest_id})")
                self.user_mapping[source_id] = dest_id
                self.stats['existants'] += 1
                continue
            
            # Préparer données
            data = {
                'name': name,
                'login': login,
                'active': user.get('active', True),
            }
            
            # Email
            if email:
                data['email'] = email
            
            # Langue et timezone
            if user.get('lang'):
                data['lang'] = user['lang']
            if user.get('tz'):
                data['tz'] = user['tz']
            
            # Partenaire lié (si mappé)
            if user.get('partner_id'):
                partner_source_id = user['partner_id'][0]
                if partner_source_id in self.partner_mapping:
                    data['partner_id'] = self.partner_mapping[partner_source_id]
            
            # Mot de passe temporaire (à réinitialiser)
            # Les utilisateurs devront changer leur mot de passe
            data['password'] = 'ChangeMeNow123!'
            
            # Groupes d'accès
            if user.get('groups_id'):
                groups_source_ids = user['groups_id']
                groups_dest_ids = []
                
                for group_source_id in groups_source_ids:
                    if group_source_id in self.group_mapping:
                        groups_dest_ids.append(self.group_mapping[group_source_id])
                
                if groups_dest_ids:
                    # Format Odoo : [(6, 0, [ids])] pour remplacer tous les groupes
                    data['groups_id'] = [(6, 0, groups_dest_ids)]
                    print(f"     {len(groups_dest_ids)} groupe(s) d'acces ajoute(s)")
            
            try:
                # Créer utilisateur
                dest_id = self.conn.executer_destination(
                    'res.users',
                    'create',
                    data
                )
                
                print(f"  OK Utilisateur cree (ID: {dest_id})")
                print(f"     Mot de passe temporaire: ChangeMeNow123!")
                logging.info(f"  OK Utilisateur cree : {name} ({login}) (ID: {dest_id})")
                self.stats['migres'] += 1
                self.user_mapping[source_id] = dest_id
                
                users_dest_by_login[login] = dest_id
                if email:
                    users_dest_by_email[email] = dest_id
                
            except Exception as e:
                print(f"  ERREUR Creation utilisateur {name}: {e}")
                logging.error(f"  ERREUR Creation utilisateur {name} ({login}): {e}")
                self.stats['erreurs'] += 1
        
        self.sauvegarder_user_mapping()
    
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
        
        if self.stats['migres'] > 0:
            print("\n" + "="*70)
            print("IMPORTANT: REINITIALISATION DES MOTS DE PASSE")
            print("="*70)
            print(f"{self.stats['migres']} nouveaux utilisateurs crees")
            print("Mot de passe temporaire pour TOUS: ChangeMeNow123!")
            print("\nLes utilisateurs doivent:")
            print("  1. Se connecter avec ce mot de passe temporaire")
            print("  2. Changer immediatement leur mot de passe")
            print("="*70)
    
    def executer(self):
        """Exécute la migration"""
        debut = datetime.now()
        
        print("\n" + "="*70)
        print("DEBUT MIGRATION UTILISATEURS v16 -> v19")
        print("="*70)
        
        # Connexion
        if not self.conn.connecter_tout():
            print("X Echec de connexion")
            return False
        
        # Charger mapping partenaires
        self.charger_partner_mapping()
        
        # Mapper les groupes
        self.mapper_groupes()
        
        # Migrer utilisateurs
        self.migrer_users()
        
        # Stats
        self.afficher_stats()
        
        fin = datetime.now()
        duree = fin - debut
        print(f"\nDuree totale : {duree}")
        print("="*70)
        
        return self.stats['erreurs'] == 0


def main():
    migration = MigrationUsers()
    success = migration.executer()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

