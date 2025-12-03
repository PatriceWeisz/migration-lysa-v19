#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONSTRUCTION DU MAPPING COMPLET DES PRODUITS
============================================
Crée un mapping source_id -> dest_id complet via external_id + code + nom
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
afficher("CONSTRUCTION MAPPING COMPLET PRODUITS")
afficher("="*70)
afficher(f"Debut: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Connexion
conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    afficher("ERREUR Connexion")
    sys.exit(1)

afficher("OK Connexion etablie\n")

# ÉTAPE 1 : Récupérer tous les external_id source
afficher("="*70)
afficher("ETAPE 1: External_id SOURCE")
afficher("="*70)

ext_src = conn.executer_source('ir.model.data', 'search_read',
                               [('model', '=', 'product.template')],
                               fields=['res_id', 'module', 'name'])

afficher(f"OK {len(ext_src)} external_id trouves dans SOURCE")

# Index source_id -> external_id
src_to_ext = {}
for ext in ext_src:
    src_to_ext[ext['res_id']] = f"{ext['module']}.{ext['name']}"

afficher(f"   {len(src_to_ext)} produits source avec external_id\n")

# ÉTAPE 2 : Récupérer tous les external_id destination
afficher("="*70)
afficher("ETAPE 2: External_id DESTINATION")
afficher("="*70)

ext_dst = conn.executer_destination('ir.model.data', 'search_read',
                                    [('model', '=', 'product.template')],
                                    fields=['res_id', 'module', 'name'])

afficher(f"OK {len(ext_dst)} external_id trouves dans DESTINATION")

# Index external_id -> dest_id
ext_to_dst = {}
for ext in ext_dst:
    ext_key = f"{ext['module']}.{ext['name']}"
    ext_to_dst[ext_key] = ext['res_id']

afficher(f"   {len(ext_to_dst)} produits destination avec external_id\n")

# ÉTAPE 3 : Construire mapping via external_id
afficher("="*70)
afficher("ETAPE 3: Mapping via External_id")
afficher("="*70)

mapping = {}
via_ext_id = 0

for source_id, ext_key in src_to_ext.items():
    if ext_key in ext_to_dst:
        dest_id = ext_to_dst[ext_key]
        mapping[source_id] = dest_id
        via_ext_id += 1

afficher(f"OK {via_ext_id} produits mappes via external_id\n")

# ÉTAPE 4 : Récupérer les produits source et destination
afficher("="*70)
afficher("ETAPE 4: Mapping par Code et Nom")
afficher("="*70)

afficher("Recuperation produits SOURCE...")
produits_src = conn.executer_source('product.template', 'search_read', [],
                                   fields=['name', 'default_code'])

afficher(f"OK {len(produits_src)} produits source")

afficher("Recuperation produits DESTINATION...")
produits_dst = conn.executer_destination('product.template', 'search_read', [],
                                        fields=['name', 'default_code'])

afficher(f"OK {len(produits_dst)} produits destination\n")

# Index destination
dst_by_code = {p['default_code']: p['id'] for p in produits_dst if p.get('default_code')}
dst_by_name = {p['name']: p['id'] for p in produits_dst if p.get('name')}

afficher(f"Index destination:")
afficher(f"   Par code: {len(dst_by_code)}")
afficher(f"   Par nom: {len(dst_by_name)}\n")

# Mapper les produits sans external_id
via_code = 0
via_nom = 0
non_trouves = 0

for prod in produits_src:
    source_id = prod['id']
    
    # Si déjà mappé via external_id, skip
    if source_id in mapping:
        continue
    
    # Essayer par code
    if prod.get('default_code') and prod['default_code'] in dst_by_code:
        mapping[source_id] = dst_by_code[prod['default_code']]
        via_code += 1
    # Essayer par nom
    elif prod.get('name') and prod['name'] in dst_by_name:
        mapping[source_id] = dst_by_name[prod['name']]
        via_nom += 1
    else:
        non_trouves += 1
        if non_trouves <= 10:
            afficher(f"  NON TROUVE: {prod['name'][:50]} (code: {prod.get('default_code', 'N/A')})")

afficher(f"\nMapping par code: {via_code}")
afficher(f"Mapping par nom: {via_nom}")
afficher(f"Non trouves: {non_trouves}\n")

# RÉSUMÉ FINAL
afficher("="*70)
afficher("RESULTAT FINAL")
afficher("="*70)
afficher(f"Via external_id  : {via_ext_id:>6,d}")
afficher(f"Via code         : {via_code:>6,d}")
afficher(f"Via nom          : {via_nom:>6,d}")
afficher(f"Non trouves      : {non_trouves:>6,d}")
afficher("-" * 70)
afficher(f"TOTAL MAPPES     : {len(mapping):>6,d}/{len(produits_src)}")

pourcentage = (len(mapping) / len(produits_src) * 100) if produits_src else 0
afficher(f"Taux de mapping  : {pourcentage:.1f}%")
afficher("="*70)

# Sauvegarder le mapping
mapping_file = LOGS_DIR / 'product_template_mapping.json'
with open(mapping_file, 'w') as f:
    json.dump(mapping, f, indent=2)

afficher(f"\nMapping sauvegarde dans: {mapping_file}")
afficher(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if non_trouves > 0:
    afficher(f"\nATTENTION: {non_trouves} produits source non trouves dans destination")
    afficher("Ces produits devront etre crees")
else:
    afficher("\nTOUS les produits source sont mappes ! OK")

