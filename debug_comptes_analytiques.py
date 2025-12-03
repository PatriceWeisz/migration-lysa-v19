#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEBUG COMPTES ANALYTIQUES"""

import sys
import os
import json
from pathlib import Path

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

afficher("="*70)
afficher("DEBUG: COMPTES ANALYTIQUES")
afficher("="*70)

conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    sys.exit(1)

afficher("OK Connexion\n")

# Charger mapping
LOGS_DIR = Path('logs')
mapping_file = LOGS_DIR / 'analytic_account_mapping.json'
if mapping_file.exists():
    with open(mapping_file, 'r') as f:
        mapping = json.load(f)
        mapping = {int(k): v for k, v in mapping.items()}
else:
    mapping = {}

afficher(f"Mapping existant: {len(mapping)}\n")

# Charger mapping plans analytiques
plan_mapping_file = LOGS_DIR / 'analytic_plan_mapping.json'
if plan_mapping_file.exists():
    with open(plan_mapping_file, 'r') as f:
        plan_mapping = json.load(f)
    afficher(f"Mapping plans: {len(plan_mapping)}\n")
else:
    plan_mapping = {}
    afficher("Mapping plans: AUCUN\n")

# Récupérer SOURCE
afficher("Recuperation SOURCE...")
src = conn.executer_source('account.analytic.account', 'search_read', [],
                           fields=['name', 'code', 'plan_id', 'partner_id', 'company_id'])

afficher(f"OK {len(src)} comptes analytiques\n")

# Analyser chaque compte
for idx, rec in enumerate(src, 1):
    code = rec.get('code', 'Sans code')
    name = rec.get('name', 'Sans nom')
    plan_id = rec.get('plan_id')
    
    afficher(f"\nCompte {idx}:")
    afficher(f"  ID source : {rec['id']}")
    afficher(f"  Code      : {code}")
    afficher(f"  Nom       : {name}")
    afficher(f"  plan_id   : {plan_id}")
    
    if rec['id'] in mapping:
        afficher(f"  Status    : MAPPE (dest ID: {mapping[rec['id']]})")
    else:
        afficher(f"  Status    : NON MAPPE")
        
        # Identifier le problème
        if not plan_id:
            afficher(f"  Problème  : AUCUN plan_id dans source")
        elif isinstance(plan_id, (list, tuple)):
            src_plan_id = plan_id[0]
            if str(src_plan_id) in plan_mapping:
                afficher(f"  Plan OK   : {src_plan_id} -> {plan_mapping[str(src_plan_id)]}")
            else:
                afficher(f"  Problème  : plan_id {src_plan_id} non mappé")

afficher("\n" + "="*70)
afficher("RESUME")
afficher("="*70)
afficher(f"Total source     : {len(src)}")
afficher(f"Total mappés     : {len(mapping)}")
afficher(f"Non mappés       : {len(src) - len(mapping)}")
afficher("="*70)

