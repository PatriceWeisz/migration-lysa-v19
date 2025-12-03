#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MIGRATION TAXES UNIQUEMENT"""

import sys
import os
import json
from pathlib import Path

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

print("="*70)
print("MIGRATION: TAXES")
print("="*70)

from connexion_double_v19 import ConnexionDoubleV19

print("Connexion...")
conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    print("ERREUR Connexion")
    sys.exit(1)

print("OK Connexion\n")

# Charger mapping
LOGS_DIR = Path('logs')
mapping_file = LOGS_DIR / 'tax_mapping.json'
if mapping_file.exists():
    with open(mapping_file, 'r') as f:
        mapping = json.load(f)
        mapping = {int(k): v for k, v in mapping.items()}
else:
    mapping = {}

print(f"Mapping existant: {len(mapping)} taxes")

# Récupérer SOURCE
print("Chargement SOURCE...")
src = conn.executer_source('account.tax', 'search_read', [],
                           fields=['name', 'amount', 'type_tax_use', 'amount_type', 
                                  'company_id', 'active'])
print(f"OK {len(src)} taxes SOURCE")

# Récupérer DESTINATION
print("Chargement DESTINATION...")
dst = conn.executer_destination('account.tax', 'search_read', [],
                                fields=['name'])
dst_index = {d['name']: d['id'] for d in dst if d.get('name')}
print(f"OK {len(dst)} taxes DESTINATION\n")

# Migrer
nouveaux = 0
existants = 0
erreurs = 0

for idx, rec in enumerate(src, 1):
    source_id = rec['id']
    name = rec.get('name', '')
    
    print(f"{idx}/{len(src)} - {name[:50]}")
    
    # Déjà mappé ?
    if source_id in mapping:
        print(f"  -> Deja mappe (ID dest: {mapping[source_id]})")
        existants += 1
        continue
    
    # Existe en destination ?
    if name in dst_index:
        dest_id = dst_index[name]
        mapping[source_id] = dest_id
        print(f"  -> Trouve en destination (ID: {dest_id})")
        existants += 1
        continue
    
    # Créer
    try:
        data = {}
        for field in ['name', 'amount', 'type_tax_use', 'amount_type', 'company_id', 'active']:
            value = rec.get(field)
            if value is not None and value is not False and value != '':
                if isinstance(value, (list, tuple)) and len(value) == 2:
                    data[field] = value[0]
                else:
                    data[field] = value
        
        dest_id = conn.executer_destination('account.tax', 'create', data)
        mapping[source_id] = dest_id
        dst_index[name] = dest_id
        print(f"  -> CREE (ID: {dest_id})")
        nouveaux += 1
        
    except Exception as e:
        print(f"  -> ERREUR: {str(e)[:50]}")
        erreurs += 1

# Sauvegarder
with open(mapping_file, 'w') as f:
    json.dump({str(k): v for k, v in mapping.items()}, f, indent=2)

print("\n" + "="*70)
print("RESULTAT")
print("="*70)
print(f"Nouveaux crees : {nouveaux}")
print(f"Existants      : {existants}")
print(f"Erreurs        : {erreurs}")
print(f"Total mappe    : {len(mapping)}/{len(src)}")
print("="*70)

