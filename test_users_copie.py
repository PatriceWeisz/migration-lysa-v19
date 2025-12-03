#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION UTILISATEURS
======================
Migre TOUS les utilisateurs (actifs ET inactifs) en les créant ACTIFS
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

LOGS_DIR = Path('logs')

afficher("="*70)
afficher("MIGRATION: UTILISATEURS")
afficher("="*70)
afficher(f"Debut: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
afficher("Strategie: Tous créés ACTIFS, désactivation à la fin\n")

# Connexion
conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    afficher("ERREUR Connexion")
    sys.exit(1)

afficher("OK Connexion\n")

# Charger mappings
mapping_file = LOGS_DIR / 'user_mapping.json'
if mapping_file.exists():
    with open(mapping_file, 'r') as f:
        mapping = json.load(f)
        mapping = {int(k): v for k, v in mapping.items()}
else:
    mapping = {}

afficher(f"Mapping existant: {len(mapping)}")

partner_mapping_file = LOGS_DIR / 'partner_mapping.json'
if partner_mapping_file.exists():
    with open(partner_mapping_file, 'r') as f:
        partner_mapping = json.load(f)
else:
    partner_mapping = {}

afficher(f"Mapping partenaires: {len(partner_mapping)}")

# Charger groupes
afficher("Chargement groupes...")
groups_src = conn.executer_source('ir.model.data', 'search_read',
                                  [('model', '=', 'res.groups')],
                                  fields=['res_id', 'module', 'name'])

group_to_ext = {g['res_id']: f"{g['module']}.{g['name']}" for g in groups_src}
afficher(f"OK {len(group_to_ext)} groupes SOURCE")

groups_dst = conn.executer_destination('ir.model.data', 'search_read',
                                       [('model', '=', 'res.groups')],
                                       fields=['res_id', 'module', 'name'])

ext_to_group = {f"{g['module']}.{g['name']}": g['res_id'] for g in groups_dst}
afficher(f"OK {len(ext_to_group)} groupes DESTINATION\n")

# Récupérer utilisateurs SOURCE (TOUS - actifs + inactifs)
afficher("Recuperation SOURCE...")
src = conn.executer_source('res.users', 'search_read',
                           [('active', 'in', [True, False])],
                           fields=['name', 'login', 'email', 'active', 'partner_id',
                                  'company_id', 'groups_id'])

afficher(f"OK {len(src)} utilisateurs\n")

# Récupérer DESTINATION
afficher("Recuperation DESTINATION...")
dst = conn.executer_destination('res.users', 'search_read', [], fields=['login'])
dst_index = {d['login']: d['id'] for d in dst if d.get('login')}
afficher(f"OK {len(dst)} utilisateurs\n")

# Migrer
nouveaux = 0
existants = 0
skipped = 0

for idx, rec in enumerate(src, 1):
    login = rec.get('login', '')
    name = rec.get('name', '')
    is_active = rec.get('active', True)
    
    if idx % 10 == 0 or idx == len(src):
        afficher(f"Traitement {idx}/{len(src)}...")
    
    # Skip système
    if login in ['admin', '__export__', 'portal']:
        skipped += 1
        continue
    
    # Déjà mappé
    if rec['id'] in mapping:
        existants += 1
        continue
    
    # Existe en destination
    if login in dst_index:
        dest_user_id = dst_index[login]
        mapping[rec['id']] = dest_user_id
        existants += 1
        continue
    
    # Créer
    try:
        data = {
            'name': name or login,
            'login': login,
            'active': True,  # TOUJOURS actif
            'password': 'ChangeMe123!'
        }
        
        if rec.get('email'):
            data['email'] = rec['email']
        
        # Partner
        src_partner_id = rec.get('partner_id')
        if src_partner_id and isinstance(src_partner_id, (list, tuple)):
            src_partner_id = src_partner_id[0]
            if str(src_partner_id) in partner_mapping:
                data['partner_id'] = partner_mapping[str(src_partner_id)]
        
        # Company
        if rec.get('company_id'):
            company_id = rec['company_id']
            if isinstance(company_id, (list, tuple)):
                data['company_id'] = company_id[0]
        
        dest_id = conn.executer_destination('res.users', 'create', data)
        
        # Assigner groupes
        src_groups = rec.get('groups_id', [])
        if src_groups:
            dest_groups = []
            for src_group_id in src_groups:
                if src_group_id in group_to_ext:
                    ext_id = group_to_ext[src_group_id]
                    if ext_id in ext_to_group:
                        dest_groups.append(ext_to_group[ext_id])
            
            if dest_groups:
                conn.executer_destination('res.users', 'write',
                                        [dest_id],
                                        {'groups_id': [(6, 0, dest_groups)]})
        
        mapping[rec['id']] = dest_id
        dst_index[login] = dest_id
        nouveaux += 1
        
    except Exception as e:
        afficher(f"ERREUR {login}: {str(e)[:60]}")

# Sauvegarder
with open(mapping_file, 'w') as f:
    json.dump({str(k): v for k, v in mapping.items()}, f, indent=2)

afficher("\n" + "="*70)
afficher("RESULTAT")
afficher("="*70)
afficher(f"Nouveaux : {nouveaux}")
afficher(f"Existants: {existants}")
afficher(f"Skippés  : {skipped}")
afficher(f"Total    : {len(mapping)}/{len(src)}")
afficher("="*70)
afficher(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if nouveaux > 0:
    afficher("\nIMPORTANT: Mot de passe: ChangeMe123!")
