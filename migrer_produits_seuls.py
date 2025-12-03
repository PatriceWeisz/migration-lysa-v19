#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION PRODUITS UNIQUEMENT
==============================
Migre SEULEMENT les produits avec affichage détaillé
"""

import sys
import os
import json
from pathlib import Path

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19
from utils.external_id_manager import ExternalIdManager
from datetime import datetime

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

LOGS_DIR = Path('logs')

afficher("="*70)
afficher("MIGRATION PRODUITS UNIQUEMENT")
afficher("="*70)
afficher(f"Debut: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Connexion
conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    afficher("ERREUR Connexion")
    sys.exit(1)

ext_mgr = ExternalIdManager(conn)
afficher("OK Connexion et external_id manager prets\n")

# Pas de préchargement, on vérifiera au fur et à mesure
afficher("Mode sans prechargement (plus rapide)\n")

# Récupérer TOUS les produits source
afficher("Recuperation TOUS les produits SOURCE...")
produits_src = conn.executer_source('product.template', 'search_read', [],
                                   fields=['name', 'default_code', 'type', 'list_price', 'active'])

afficher(f"OK {len(produits_src)} produits a traiter\n")

# Récupérer produits destination
afficher("Recuperation produits DESTINATION...")
produits_dst = conn.executer_destination('product.template', 'search_read', [],
                                        fields=['name', 'default_code'])

# Index
dst_by_code = {p['default_code']: p['id'] for p in produits_dst if p.get('default_code')}
dst_by_name = {p['name']: p['id'] for p in produits_dst if p.get('name')}

afficher(f"OK {len(produits_dst)} produits existants")
afficher(f"   Index par code: {len(dst_by_code)}")
afficher(f"   Index par nom: {len(dst_by_name)}\n")

# Migration
afficher("="*70)
afficher("MIGRATION EN COURS...")
afficher("="*70)

mapping = {}
via_ext_id = 0
via_code = 0
via_nom = 0
crees = 0
erreurs = 0

for idx, prod in enumerate(produits_src, 1):
    source_id = prod['id']
    name = prod['name']
    code = prod.get('default_code', '')
    
    # Vérifier external_id
    existe, dest_id, ext_id = ext_mgr.verifier_existe('product.template', source_id)
    
    if existe:
        via_ext_id += 1
        mapping[source_id] = dest_id
    elif code and code in dst_by_code:
        via_code += 1
        dest_id = dst_by_code[code]
        mapping[source_id] = dest_id
        # Copier external_id
        if ext_id:
            ext_mgr.copier_external_id('product.template', dest_id, source_id)
    elif name in dst_by_name:
        via_nom += 1
        dest_id = dst_by_name[name]
        mapping[source_id] = dest_id
        # Copier external_id
        if ext_id:
            ext_mgr.copier_external_id('product.template', dest_id, source_id)
    else:
        # CRÉER
        product_type = prod.get('type', 'consu')
        is_storable = (product_type == 'product')
        if is_storable:
            product_type = 'consu'
        
        data = {
            'name': name,
            'type': product_type,
            'list_price': prod.get('list_price', 0.0),
            'active': prod.get('active', True),
        }
        
        if is_storable:
            data['is_storable'] = True
        if code:
            data['default_code'] = code
        
        try:
            dest_id = conn.executer_destination('product.template', 'create', data)
            crees += 1
            mapping[source_id] = dest_id
            
            # Copier external_id
            if ext_id:
                ext_mgr.copier_external_id('product.template', dest_id, source_id)
            
            # Mettre à jour index
            if code:
                dst_by_code[code] = dest_id
            dst_by_name[name] = dest_id
            
        except Exception as e:
            afficher(f"ERREUR ID {source_id} ({name[:30]}): {str(e)[:60]}")
            erreurs += 1
    
    # Progression
    if idx % 100 == 0:
        afficher(f"  {idx}/{len(produits_src)} - Mappes: {len(mapping)} (ext_id:{via_ext_id}, code:{via_code}, nom:{via_nom}, crees:{crees})")

afficher("\n" + "="*70)
afficher("RESULTAT FINAL:")
afficher("="*70)
afficher(f"  Via external_id : {via_ext_id}")
afficher(f"  Via code        : {via_code}")
afficher(f"  Via nom         : {via_nom}")
afficher(f"  Crees           : {crees}")
afficher(f"  Erreurs         : {erreurs}")
afficher(f"  TOTAL MAPPES    : {len(mapping)}/{len(produits_src)}")
afficher("="*70)

# Sauvegarder
with open(LOGS_DIR / 'product_template_mapping.json', 'w') as f:
    json.dump(mapping, f, indent=2)

afficher(f"\nMapping sauvegarde: {len(mapping)} produits")
afficher(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

