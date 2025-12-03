#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONSTRUCTION DU MAPPING COMPLET DES PARTENAIRES
===============================================
Crée un mapping source_id -> dest_id complet via external_id + ref + email + nom
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
afficher("CONSTRUCTION MAPPING COMPLET PARTENAIRES")
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
                               [('model', '=', 'res.partner')],
                               fields=['res_id', 'module', 'name'])

src_to_ext = {ext['res_id']: f"{ext['module']}.{ext['name']}" for ext in ext_src}
afficher(f"OK {len(src_to_ext)} partenaires source avec external_id\n")

# ÉTAPE 2 : External_id destination
afficher("ETAPE 2: External_id DESTINATION")
ext_dst = conn.executer_destination('ir.model.data', 'search_read',
                                    [('model', '=', 'res.partner')],
                                    fields=['res_id', 'module', 'name'])

ext_to_dst = {f"{ext['module']}.{ext['name']}": ext['res_id'] for ext in ext_dst}
afficher(f"OK {len(ext_to_dst)} partenaires destination avec external_id\n")

# ÉTAPE 3 : Mapping via external_id
afficher("ETAPE 3: Mapping via External_id")
mapping = {}
via_ext_id = 0

for source_id, ext_key in src_to_ext.items():
    if ext_key in ext_to_dst:
        mapping[source_id] = ext_to_dst[ext_key]
        via_ext_id += 1

afficher(f"OK {via_ext_id} partenaires mappes via external_id\n")

# ÉTAPE 4 : Mapping par ref, email, nom
afficher("ETAPE 4: Mapping par Ref/Email/Nom")

afficher("Recuperation partenaires SOURCE...")
partners_src = conn.executer_source('res.partner', 'search_read', [],
                                   fields=['name', 'ref', 'email'])
afficher(f"OK {len(partners_src)} partenaires")

afficher("Recuperation partenaires DESTINATION...")
partners_dst = conn.executer_destination('res.partner', 'search_read', [],
                                        fields=['name', 'ref', 'email'])
afficher(f"OK {len(partners_dst)} partenaires\n")

# Index destination
dst_by_ref = {p['ref']: p['id'] for p in partners_dst if p.get('ref')}
dst_by_email = {p['email']: p['id'] for p in partners_dst if p.get('email')}
dst_by_name = {p['name']: p['id'] for p in partners_dst if p.get('name')}

afficher(f"Index destination:")
afficher(f"   Par ref: {len(dst_by_ref)}")
afficher(f"   Par email: {len(dst_by_email)}")
afficher(f"   Par nom: {len(dst_by_name)}\n")

# Mapper les non-mappés
via_ref = 0
via_email = 0
via_nom = 0
non_trouves = 0

for partner in partners_src:
    source_id = partner['id']
    
    if source_id in mapping:
        continue
    
    # Par ref
    if partner.get('ref') and partner['ref'] in dst_by_ref:
        mapping[source_id] = dst_by_ref[partner['ref']]
        via_ref += 1
    # Par email
    elif partner.get('email') and partner['email'] in dst_by_email:
        mapping[source_id] = dst_by_email[partner['email']]
        via_email += 1
    # Par nom
    elif partner.get('name') and partner['name'] in dst_by_name:
        mapping[source_id] = dst_by_name[partner['name']]
        via_nom += 1
    else:
        non_trouves += 1
        if non_trouves <= 10:
            afficher(f"  NON TROUVE: {partner.get('name', 'Sans nom')[:50]}")

afficher(f"\nMapping par ref: {via_ref}")
afficher(f"Mapping par email: {via_email}")
afficher(f"Mapping par nom: {via_nom}")
afficher(f"Non trouves: {non_trouves}\n")

# RÉSUMÉ
afficher("="*70)
afficher("RESULTAT FINAL")
afficher("="*70)
afficher(f"Via external_id  : {via_ext_id:>6,d}")
afficher(f"Via ref          : {via_ref:>6,d}")
afficher(f"Via email        : {via_email:>6,d}")
afficher(f"Via nom          : {via_nom:>6,d}")
afficher(f"Non trouves      : {non_trouves:>6,d}")
afficher("-" * 70)
afficher(f"TOTAL MAPPES     : {len(mapping):>6,d}/{len(partners_src)}")

pourcentage = (len(mapping) / len(partners_src) * 100) if partners_src else 0
afficher(f"Taux de mapping  : {pourcentage:.1f}%")
afficher("="*70)

# Sauvegarder
mapping_file = LOGS_DIR / 'partner_mapping.json'
with open(mapping_file, 'w') as f:
    json.dump(mapping, f, indent=2)

afficher(f"\nMapping sauvegarde dans: {mapping_file}")
afficher(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if non_trouves > 0:
    afficher(f"\nATTENTION: {non_trouves} partenaires a creer")
else:
    afficher("\nTOUS les partenaires mappes ! OK")

