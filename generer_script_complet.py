#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GÉNÉRATEUR DE SCRIPT DE MIGRATION COMPLET
=========================================
Génère automatiquement un script avec TOUS les champs migrables
"""

import sys
import os

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

def obtenir_champs_migrables(conn, model):
    """Obtient tous les champs migrables pour un modèle"""
    
    # Champs SOURCE
    fields_src = conn.executer_source('ir.model.fields', 'search_read',
                                     [('model', '=', model), ('store', '=', True)],
                                     fields=['name', 'ttype', 'readonly', 'compute'])
    
    src_dict = {f['name']: f for f in fields_src}
    
    # Champs DESTINATION
    fields_dst = conn.executer_destination('ir.model.fields', 'search_read',
                                          [('model', '=', model), ('store', '=', True)],
                                          fields=['name', 'ttype'])
    
    dst_names = {f['name'] for f in fields_dst}
    
    # Liste des champs à exclure
    EXCLUS = {
        'id', '__last_update', 'display_name',
        'create_date', 'create_uid', 'write_date', 'write_uid',
        'message_ids', 'message_follower_ids', 'activity_ids', 
        'rating_ids', 'website_message_ids', 'message_main_attachment_id'
    }
    
    # Champs migrables
    migrables = []
    for fname in src_dict.keys():
        field_info = src_dict[fname]
        
        # Exclure
        if fname in EXCLUS:
            continue
        if field_info.get('compute') and not field_info.get('store'):
            continue
        if fname not in dst_names:
            continue
        
        migrables.append(fname)
    
    return migrables

afficher("="*70)
afficher("GÉNÉRATEUR DE SCRIPT COMPLET")
afficher("="*70)

conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    sys.exit(1)

afficher("OK Connexion\n")

# Module à générer
MODEL = input("Modèle Odoo (ex: project.project): ").strip()
if not MODEL:
    afficher("Modèle requis")
    sys.exit(1)

NOM = input("Nom du module (ex: Projets): ").strip()
FICHIER = input("Nom fichier mapping (ex: project): ").strip()
UNIQUE_FIELD = input("Champ unique (ex: name): ").strip()

afficher(f"\nAnalyse de {MODEL}...")
champs = obtenir_champs_migrables(conn, MODEL)

afficher(f"OK {len(champs)} champs migrables identifiés\n")
afficher("Champs:")
for c in sorted(champs):
    afficher(f"  - {c}")

# Générer le script
afficher("\n" + "="*70)
afficher(f"GÉNÉRATION DU SCRIPT: migrer_{FICHIER}_complet.py")
afficher("="*70)

script_content = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MIGRATION {NOM.upper()} - VERSION COMPLÈTE"""

import sys
import os
import json
from pathlib import Path

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\\n')
    sys.stdout.flush()

LOGS_DIR = Path('logs')

afficher("="*70)
afficher("MIGRATION: {NOM.upper()}")
afficher("="*70)

conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    sys.exit(1)

afficher("OK Connexion\\n")

# Charger mapping
mapping_file = LOGS_DIR / '{FICHIER}_mapping.json'
if mapping_file.exists():
    with open(mapping_file, 'r') as f:
        mapping = json.load(f)
        mapping = {{int(k): v for k, v in mapping.items()}}
else:
    mapping = {{}}

afficher(f"Mapping: {{len(mapping)}}")

# TOUS les champs migrables identifiés automatiquement
CHAMPS = {sorted(champs)}

afficher("Recuperation SOURCE...")
src = conn.executer_source('{MODEL}', 'search_read', [], fields=CHAMPS)
afficher(f"OK {{len(src)}} enregistrements")

afficher("Recuperation DESTINATION...")
dst = conn.executer_destination('{MODEL}', 'search_read', [], fields=['{UNIQUE_FIELD}'])
dst_index = {{d['{UNIQUE_FIELD}']: d['id'] for d in dst if d.get('{UNIQUE_FIELD}')}}
afficher(f"OK {{len(dst)}} enregistrements\\n")

nouveaux = existants = 0

for idx, rec in enumerate(src, 1):
    unique_val = rec.get('{UNIQUE_FIELD}', '')
    
    if idx % 10 == 0 or idx == len(src):
        afficher(f"Traitement {{idx}}/{{len(src)}}...")
    
    if rec['id'] in mapping:
        existants += 1
        continue
    
    if unique_val and unique_val in dst_index:
        mapping[rec['id']] = dst_index[unique_val]
        existants += 1
        continue
    
    try:
        data = {{k: v for k, v in rec.items() if k != 'id' and v not in (None, False, '')}}
        for k in list(data.keys()):
            if isinstance(data[k], (list, tuple)) and len(data[k]) == 2:
                data[k] = data[k][0]
        
        dest_id = conn.executer_destination('{MODEL}', 'create', data)
        mapping[rec['id']] = dest_id
        if unique_val:
            dst_index[unique_val] = dest_id
        nouveaux += 1
        
    except Exception as e:
        afficher(f"ERREUR {{unique_val}}: {{str(e)[:50]}}")

with open(mapping_file, 'w') as f:
    json.dump({{str(k): v for k, v in mapping.items()}}, f, indent=2)

afficher("\\n" + "="*70)
afficher("RESULTAT")
afficher("="*70)
afficher(f"Nouveaux : {{nouveaux}}")
afficher(f"Existants: {{existants}}")
afficher(f"Total    : {{len(mapping)}}/{{len(src)}}")
afficher("="*70)
'''

# Sauvegarder le script
nom_fichier = f"migrer_{FICHIER}_complet.py"
with open(nom_fichier, 'w', encoding='utf-8') as f:
    f.write(script_content)

afficher(f"\nSCRIPT GÉNÉRÉ: {nom_fichier}")
afficher(f"Champs migrés: {len(champs)}")
afficher("="*70)

