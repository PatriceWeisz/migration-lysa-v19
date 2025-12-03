#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEBUG PRODUITS - Analyser pourquoi ils ne sont pas mappés
"""

import sys
import os

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19
from utils.external_id_manager import ExternalIdManager

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

afficher("="*70)
afficher("DEBUG PRODUITS")
afficher("="*70)

# Connexion
conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    afficher("ERREUR: Connexion")
    sys.exit(1)

ext_mgr = ExternalIdManager(conn)

# Récupérer 50 produits de la source
afficher("\n1. Recuperation 50 produits SOURCE...")
produits_src = conn.executer_source('product.template', 'search_read', [],
                                   fields=['name', 'default_code', 'type'],
                                   limit=50)

afficher(f"OK {len(produits_src)} produits")

# Récupérer produits destination
afficher("\n2. Recuperation produits DESTINATION...")
produits_dst = conn.executer_destination('product.template', 'search_read', [],
                                        fields=['name', 'default_code'])

afficher(f"OK {len(produits_dst)} produits dans destination")

# Créer index
dst_by_code = {p['default_code']: p['id'] for p in produits_dst if p.get('default_code')}
dst_by_name = {p['name']: p['id'] for p in produits_dst}

afficher(f"   - Par code: {len(dst_by_code)}")
afficher(f"   - Par nom: {len(dst_by_name)}")

# Analyser les 50 premiers
afficher("\n3. ANALYSE DES 50 PREMIERS PRODUITS:")
afficher("="*70)

via_ext_id = 0
via_code = 0
via_nom = 0
a_creer = 0

for idx, prod in enumerate(produits_src[:50], 1):
    source_id = prod['id']
    name = prod['name']
    code = prod.get('default_code', '')
    
    # Vérifier external_id
    existe, dest_id, ext_id = ext_mgr.verifier_existe('product.template', source_id)
    
    if existe:
        via_ext_id += 1
        status = f"Existe via ext_id (ID: {dest_id})"
    elif code and code in dst_by_code:
        via_code += 1
        status = f"Existe par code {code} (ID: {dst_by_code[code]})"
    elif name in dst_by_name:
        via_nom += 1
        status = f"Existe par nom (ID: {dst_by_name[name]})"
    else:
        a_creer += 1
        status = "A CREER"
    
    if idx <= 20:
        code_str = code if code else 'sans ref'
        afficher(f"[{idx}] {name[:40]:40s} {code_str:15s} -> {status}")

afficher("\n" + "="*70)
afficher("RESUME:")
afficher(f"  Via external_id : {via_ext_id}")
afficher(f"  Via code        : {via_code}")
afficher(f"  Via nom         : {via_nom}")
afficher(f"  A creer         : {a_creer}")
afficher(f"  TOTAL           : {via_ext_id + via_code + via_nom + a_creer}/50")
afficher("="*70)

if a_creer > 0:
    afficher(f"\n{a_creer} produits devraient etre crees !")
    afficher("Si 0 sont crees, c'est qu'il y a un probleme dans le script.")
else:
    afficher("\nTous les produits existent deja !")

