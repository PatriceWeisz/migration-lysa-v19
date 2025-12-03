#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MIGRATION PROJETS"""
import sys, os, json
from pathlib import Path

# AFFICHER IMMÉDIATEMENT
print("="*70)
print("DEMARRAGE: MIGRATION PROJETS")
print("="*70)
print("Initialisation... Chargement des modules (10-15 secondes)")
print("="*70)
sys.stdout.flush()

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19

print("OK - Modules charges")
print("="*70)

conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    sys.exit(1)

print("OK Connexion\n")

LOGS_DIR = Path('logs')
mapping_file = LOGS_DIR / 'project_mapping.json'
mapping = json.load(open(mapping_file)) if mapping_file.exists() else {}
mapping = {int(k): v for k, v in mapping.items()}
print(f"Mapping projets: {len(mapping)}")

# Charger mapping utilisateurs
user_mapping_file = LOGS_DIR / 'user_mapping.json'
if user_mapping_file.exists():
    with open(user_mapping_file, 'r') as f:
        user_mapping = json.load(f)
    print(f"Mapping utilisateurs: {len(user_mapping)}")
else:
    print("Mapping utilisateurs: AUCUN (user_id=2 par defaut)")
    user_mapping = {}

src = conn.executer_source('project.project', 'search_read', [],
                           fields=['name', 'partner_id', 'user_id', 'company_id', 'active'])
print(f"SOURCE: {len(src)}")

dst = conn.executer_destination('project.project', 'search_read', [], fields=['name'])
dst_index = {d['name']: d['id'] for d in dst if d.get('name')}
print(f"DESTINATION: {len(dst)}\n")

nouveaux = existants = 0
for idx, rec in enumerate(src, 1):
    name = rec.get('name', '')
    # Nettoyer le nom pour l'affichage Windows
    try:
        print(f"{idx}/{len(src)} - {name}")
    except UnicodeEncodeError:
        name_clean = name.encode('ascii', 'replace').decode('ascii')
        print(f"{idx}/{len(src)} - {name_clean}")
    
    if rec['id'] in mapping:
        print("  -> Deja mappe")
        existants += 1
        continue
    
    if name in dst_index:
        mapping[rec['id']] = dst_index[name]
        print(f"  -> Trouve")
        existants += 1
        continue
    
    try:
        data = {k: v for k, v in rec.items() if k != 'id' and v not in (None, False, '')}
        
        # Traiter user_id AVANT de nettoyer les many2one
        # NOTE: Tous les utilisateurs (actifs ET inactifs) sont migrés
        # en mode actif pour permettre les dépendances
        src_user_id = rec.get('user_id')
        if src_user_id:
            if isinstance(src_user_id, (list, tuple)):
                src_user_id = src_user_id[0]
            
            # Chercher dans le mapping utilisateurs
            if str(src_user_id) in user_mapping:
                data['user_id'] = user_mapping[str(src_user_id)]
            else:
                # Utilisateur pas migré -> admin par défaut
                data['user_id'] = 2
                print(f"  -> ATTENTION: user_id {src_user_id} non mappé, utilisation admin")
        else:
            data['user_id'] = 2
        
        # Nettoyer les autres relations many2one
        for k in list(data.keys()):
            if k == 'user_id':
                continue  # Déjà traité
            if isinstance(data[k], (list, tuple)) and len(data[k]) == 2:
                data[k] = data[k][0]
        
        dest_id = conn.executer_destination('project.project', 'create', data)
        mapping[rec['id']] = dest_id
        dst_index[name] = dest_id
        print(f"  -> CREE (ID: {dest_id})")
        nouveaux += 1
    except Exception as e:
        print(f"  -> ERREUR: {str(e)[:50]}")

with open(mapping_file, 'w') as f:
    json.dump({str(k): v for k, v in mapping.items()}, f, indent=2)

print(f"\nRESULTAT: {nouveaux} nouveaux, {existants} existants")
print(f"Total: {len(mapping)}/{len(src)}")

