#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MIGRATION ÉQUIPES COMMERCIALES"""
import sys, os, json
from pathlib import Path
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

print("="*70)
print("MIGRATION: EQUIPES COMMERCIALES")
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
mapping_file = LOGS_DIR / 'crm_team_mapping.json'
mapping = json.load(open(mapping_file)) if mapping_file.exists() else {}
mapping = {int(k): v for k, v in mapping.items()}
print(f"Mapping: {len(mapping)}")

src = conn.executer_source('crm.team', 'search_read', [],
                           fields=['name', 'user_id', 'company_id', 'active'])
print(f"SOURCE: {len(src)}")

dst = conn.executer_destination('crm.team', 'search_read', [], fields=['name'])
dst_index = {d['name']: d['id'] for d in dst if d.get('name')}
print(f"DESTINATION: {len(dst)}\n")

nouveaux = existants = 0
for idx, rec in enumerate(src, 1):
    name = rec.get('name', '')
    print(f"{idx}/{len(src)} - {name}")
    
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
        for k in list(data.keys()):
            if isinstance(data[k], (list, tuple)) and len(data[k]) == 2:
                data[k] = data[k][0]
        
        dest_id = conn.executer_destination('crm.team', 'create', data)
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

