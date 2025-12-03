#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONSTRUCTION DU MAPPING COMPLET DU PLAN COMPTABLE
=================================================
Crée un mapping source_id -> dest_id complet via external_id + code
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
afficher("CONSTRUCTION MAPPING COMPLET PLAN COMPTABLE")
afficher("="*70)
afficher(f"Debut: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Connexion
conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    afficher("ERREUR Connexion")
    sys.exit(1)

afficher("OK Connexion etablie\n")

# ÉTAPE 1 : External_id source
afficher("ETAPE 1: External_id SOURCE")
ext_src = conn.executer_source('ir.model.data', 'search_read',
                               [('model', '=', 'account.account')],
                               fields=['res_id', 'module', 'name'])

src_to_ext = {ext['res_id']: f"{ext['module']}.{ext['name']}" for ext in ext_src}
afficher(f"OK {len(src_to_ext)} comptes source avec external_id\n")

# ÉTAPE 2 : External_id destination
afficher("ETAPE 2: External_id DESTINATION")
ext_dst = conn.executer_destination('ir.model.data', 'search_read',
                                    [('model', '=', 'account.account')],
                                    fields=['res_id', 'module', 'name'])

ext_to_dst = {f"{ext['module']}.{ext['name']}": ext['res_id'] for ext in ext_dst}
afficher(f"OK {len(ext_to_dst)} comptes destination avec external_id\n")

# ÉTAPE 3 : Mapping via external_id
afficher("ETAPE 3: Mapping via External_id")
mapping = {}
via_ext_id = 0

for source_id, ext_key in src_to_ext.items():
    if ext_key in ext_to_dst:
        mapping[source_id] = ext_to_dst[ext_key]
        via_ext_id += 1

afficher(f"OK {via_ext_id} comptes mappes via external_id\n")

# ÉTAPE 4 : Mapping par code
afficher("ETAPE 4: Mapping par Code")

afficher("Recuperation comptes SOURCE...")
comptes_src = conn.executer_source('account.account', 'search_read', [],
                                   fields=['code', 'name'])
afficher(f"OK {len(comptes_src)} comptes")

afficher("Recuperation comptes DESTINATION...")
comptes_dst = conn.executer_destination('account.account', 'search_read', [],
                                        fields=['code', 'name'])
afficher(f"OK {len(comptes_dst)} comptes\n")

# Index destination par code
dst_by_code = {c['code']: c['id'] for c in comptes_dst if c.get('code')}

afficher(f"Index destination par code: {len(dst_by_code)}\n")

# Mapper par code
via_code = 0
a_creer = []

for compte in comptes_src:
    source_id = compte['id']
    
    if source_id in mapping:
        continue
    
    code = compte.get('code', '')
    if code and code in dst_by_code:
        mapping[source_id] = dst_by_code[code]
        via_code += 1
    else:
        a_creer.append({
            'source_id': source_id,
            'code': code,
            'name': compte['name']
        })

afficher(f"Mapping par code: {via_code}")
afficher(f"A creer: {len(a_creer)}\n")

# RÉSUMÉ
afficher("="*70)
afficher("RESULTAT FINAL")
afficher("="*70)
afficher(f"Via external_id  : {via_ext_id:>6,d}")
afficher(f"Via code         : {via_code:>6,d}")
afficher(f"A creer          : {len(a_creer):>6,d}")
afficher("-" * 70)
afficher(f"TOTAL MAPPES     : {len(mapping):>6,d}/{len(comptes_src)}")

pourcentage = (len(mapping) / len(comptes_src) * 100) if comptes_src else 0
afficher(f"Taux de mapping  : {pourcentage:.1f}%")
afficher("="*70)

# Sauvegarder
mapping_file = LOGS_DIR / 'account_mapping.json'
with open(mapping_file, 'w') as f:
    json.dump(mapping, f, indent=2)

afficher(f"\nMapping sauvegarde dans: {mapping_file}")

if a_creer:
    # Sauvegarder liste à créer
    with open(LOGS_DIR / 'comptes_a_creer.json', 'w') as f:
        json.dump(a_creer, f, indent=2)
    
    afficher(f"Liste des comptes a creer: logs/comptes_a_creer.json")
    afficher(f"\nATTENTION: {len(a_creer)} comptes doivent etre crees")
    
    if len(a_creer) <= 20:
        afficher("\nComptes a creer:")
        for c in a_creer[:20]:
            afficher(f"  - {c['code']:10s} {c['name'][:50]}")
else:
    afficher("\nTOUS les comptes sont mappes ! OK")

afficher(f"\nFin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

