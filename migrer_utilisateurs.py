#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MIGRATION UTILISATEURS"""
import sys, os, json, traceback
from pathlib import Path
from datetime import datetime
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

# Fichier log pour les erreurs détaillées
LOG_FILE = Path('logs') / f'migration_users_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

print("="*70)
print("MIGRATION: UTILISATEURS")
print("="*70)
print("Chargement des modules... (10-15 secondes)")
print("="*70)

from connexion_double_v19 import ConnexionDoubleV19

print("OK - Modules charges")

conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    sys.exit(1)

print("OK Connexion\n")

LOGS_DIR = Path('logs')
mapping_file = LOGS_DIR / 'user_mapping.json'
mapping = json.load(open(mapping_file)) if mapping_file.exists() else {}
mapping = {int(k): v for k, v in mapping.items()}
print(f"Mapping: {len(mapping)}")

# Charger partenaires pour lier les utilisateurs
partner_mapping_file = LOGS_DIR / 'partner_mapping.json'
if partner_mapping_file.exists():
    with open(partner_mapping_file, 'r') as f:
        partner_mapping = json.load(f)
    print(f"Mapping partenaires: {len(partner_mapping)}")
else:
    partner_mapping = {}
    print("Mapping partenaires: AUCUN")

# Récupérer TOUS les utilisateurs (actifs ET inactifs)
# Important: les projets peuvent référencer des utilisateurs inactifs
src = conn.executer_source('res.users', 'search_read',
                           [('active', 'in', [True, False])],
                           fields=['name', 'login', 'email', 'active', 'partner_id', 
                                  'company_id', 'groups_id'])
print(f"SOURCE: {len(src)} utilisateurs (actifs + inactifs)")

print("\nChargement des groupes et leurs external_id...")
# Charger tous les groupes de la source avec leurs external_id
groups_src = conn.executer_source('ir.model.data', 'search_read',
                                  [('model', '=', 'res.groups')],
                                  fields=['res_id', 'module', 'name'])

# Index: group_id -> external_id
group_to_ext = {}
for g in groups_src:
    ext_id = f"{g['module']}.{g['name']}"
    group_to_ext[g['res_id']] = ext_id

print(f"OK {len(group_to_ext)} groupes avec external_id dans SOURCE")

# Charger tous les groupes de la destination avec leurs external_id
groups_dst = conn.executer_destination('ir.model.data', 'search_read',
                                       [('model', '=', 'res.groups')],
                                       fields=['res_id', 'module', 'name'])

# Index: external_id -> group_id
ext_to_group = {}
for g in groups_dst:
    ext_id = f"{g['module']}.{g['name']}"
    ext_to_group[ext_id] = g['res_id']

print(f"OK {len(ext_to_group)} groupes avec external_id dans DESTINATION")

dst = conn.executer_destination('res.users', 'search_read', [], fields=['login'])
dst_index = {d['login']: d['id'] for d in dst if d.get('login')}
print(f"DESTINATION: {len(dst)}\n")

nouveaux = existants = 0
skipped = 0

for idx, rec in enumerate(src, 1):
    login = rec.get('login', '')
    name = rec.get('name', '')
    is_active = rec.get('active', True)
    status = "ACTIF" if is_active else "INACTIF"
    
    try:
        print(f"{idx}/{len(src)} - {login} ({name}) [{status}]")
    except UnicodeEncodeError:
        name_clean = name.encode('ascii', 'replace').decode('ascii')
        print(f"{idx}/{len(src)} - {login} ({name_clean}) [{status}]")
    
    # Skip admin et portal users
    if login in ['admin', '__export__', 'portal']:
        print(f"  -> SKIP (utilisateur systeme)")
        skipped += 1
        continue
    
    if rec['id'] in mapping:
        print(f"  -> Deja mappe (ID dest: {mapping[rec['id']]})")
        existants += 1
        continue
    
    if login in dst_index:
        dest_user_id = dst_index[login]
        mapping[rec['id']] = dest_user_id
        
        # Mettre à jour les groupes même si l'utilisateur existe
        src_groups = rec.get('groups_id', [])
        if src_groups:
            dest_groups = []
            for src_group_id in src_groups:
                if src_group_id in group_to_ext:
                    ext_id = group_to_ext[src_group_id]
                    if ext_id in ext_to_group:
                        dest_groups.append(ext_to_group[ext_id])
            
            if dest_groups:
                try:
                    conn.executer_destination('res.users', 'write',
                                            [dest_user_id],
                                            {'groups_id': [(6, 0, dest_groups)]})
                    print(f"  -> Trouve + groupes mis a jour ({len(dest_groups)} groupes)")
                except Exception as e:
                    print(f"  -> Trouve (erreur maj groupes: {str(e)[:40]})")
            else:
                print(f"  -> Trouve en destination (ID: {dest_user_id})")
        else:
            print(f"  -> Trouve en destination (ID: {dest_user_id})")
        
        existants += 1
        continue
    
    try:
        # Préparer les données
        data = {
            'name': name or login,
            'login': login,
            'active': rec.get('active', True)
        }
        
        # Email (optionnel)
        if rec.get('email'):
            data['email'] = rec['email']
        
        # Partner
        src_partner_id = rec.get('partner_id')
        if src_partner_id:
            if isinstance(src_partner_id, (list, tuple)):
                src_partner_id = src_partner_id[0]
            
            # Chercher dans le mapping partenaires
            if str(src_partner_id) in partner_mapping:
                data['partner_id'] = partner_mapping[str(src_partner_id)]
            # Sinon on laisse Odoo créer un partenaire automatiquement
        
        # Company
        if rec.get('company_id'):
            company_id = rec['company_id']
            if isinstance(company_id, (list, tuple)):
                data['company_id'] = company_id[0]
        
        # IMPORTANT: Mot de passe temporaire
        # L'utilisateur devra le réinitialiser
        data['password'] = 'ChangeMe123!'
        
        print(f"  -> Creation...")
        dest_id = conn.executer_destination('res.users', 'create', data)
        
        # GROUPES DE PERMISSIONS (APRÈS création - via external_id)
        # On ne peut PAS définir groups_id lors de create(), il faut faire un write()
        src_groups = rec.get('groups_id', [])
        if src_groups:
            dest_groups = []
            groups_non_mappes = []
            
            for src_group_id in src_groups:
                # Chercher l'external_id du groupe source
                if src_group_id in group_to_ext:
                    ext_id = group_to_ext[src_group_id]
                    
                    # Chercher le groupe correspondant en destination
                    if ext_id in ext_to_group:
                        dest_groups.append(ext_to_group[ext_id])
                    else:
                        groups_non_mappes.append(ext_id)
                else:
                    groups_non_mappes.append(f"ID:{src_group_id}")
            
            if dest_groups:
                try:
                    # Mettre à jour les groupes
                    conn.executer_destination('res.users', 'write',
                                            [dest_id],
                                            {'groups_id': [(6, 0, dest_groups)]})
                    print(f"  -> {len(dest_groups)} groupes assignes")
                except Exception as eg:
                    print(f"  -> Erreur assignation groupes")
            
            if groups_non_mappes and len(groups_non_mappes) > 5:
                print(f"  -> {len(groups_non_mappes)} groupes non mappes")
        mapping[rec['id']] = dest_id
        dst_index[login] = dest_id
        print(f"  -> CREE (ID: {dest_id}) - Mot de passe: ChangeMe123!")
        nouveaux += 1
        
    except Exception as e:
        # Logger l'erreur complète dans un fichier
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Utilisateur: {login} - {name}\n")
            f.write(f"Erreur:\n{str(e)}\n")
            f.write(f"Traceback:\n{traceback.format_exc()}\n")
        
        # Afficher un message simple
        print(f"  -> ERREUR (voir {LOG_FILE.name})")
        
        # Si erreur "already exists", essayer de le récupérer
        if 'already exists' in error_msg.lower() or 'duplicate' in error_msg.lower():
            try:
                found = conn.executer_destination('res.users', 'search_read',
                                                 [('login', '=', login)],
                                                 fields=['id'])
                if found:
                    mapping[rec['id']] = found[0]['id']
                    dst_index[login] = found[0]['id']
                    print(f"  -> Recupere (ID: {found[0]['id']})")
                    existants += 1
            except:
                pass

with open(mapping_file, 'w') as f:
    json.dump({str(k): v for k, v in mapping.items()}, f, indent=2)

print(f"\nRESULTAT: {nouveaux} nouveaux, {existants} existants, {skipped} skippés")
print(f"Total: {len(mapping)}/{len(src)}")

if nouveaux > 0:
    print(f"\n{'='*70}")
    print("IMPORTANT: Nouveaux utilisateurs créés")
    print("="*70)
    print("Mot de passe temporaire pour tous: ChangeMe123!")
    print("Les utilisateurs devront le changer à leur première connexion")
    print("="*70)

