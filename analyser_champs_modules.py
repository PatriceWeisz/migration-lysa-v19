#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALYSE DES CHAMPS DES MODULES
===============================
Compare les champs entre source et destination
"""

import sys
import os

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

afficher("="*70)
afficher("ANALYSE DES CHAMPS DES MODULES")
afficher("="*70)

conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    sys.exit(1)

afficher("OK Connexion\n")

MODULES = [
    'account.tax',
    'product.pricelist',
    'crm.team',
    'project.project',
    'account.analytic.account',
    'res.partner.category',
]

for model in MODULES:
    afficher(f"\n{'='*70}")
    afficher(f"MODULE: {model}")
    afficher(f"{'='*70}")
    
    try:
        # Récupérer les champs du modèle dans la source
        fields_src = conn.executer_source('ir.model.fields', 'search_read',
                                         [('model', '=', model)],
                                         fields=['name', 'ttype', 'required', 'readonly'])
        
        afficher(f"SOURCE: {len(fields_src)} champs")
        
        # Récupérer les champs du modèle dans la destination
        fields_dst = conn.executer_destination('ir.model.fields', 'search_read',
                                              [('model', '=', model)],
                                              fields=['name', 'ttype', 'required', 'readonly'])
        
        afficher(f"DESTINATION: {len(fields_dst)} champs")
        
        # Champs source
        src_names = {f['name'] for f in fields_src}
        dst_names = {f['name'] for f in fields_dst}
        
        # Champs manquants en destination
        missing_in_dst = src_names - dst_names
        if missing_in_dst:
            afficher(f"\nChamps dans SOURCE mais pas dans DESTINATION:")
            for fname in sorted(missing_in_dst):
                afficher(f"  - {fname}")
        
        # Champs nouveaux en destination
        new_in_dst = dst_names - src_names
        if new_in_dst:
            afficher(f"\nChamps NOUVEAUX dans DESTINATION (v19):")
            for fname in sorted(list(new_in_dst)[:10]):
                afficher(f"  - {fname}")
            if len(new_in_dst) > 10:
                afficher(f"  ... et {len(new_in_dst) - 10} autres")
        
        # Champs obligatoires en destination
        required_dst = [f for f in fields_dst if f.get('required')]
        if required_dst:
            afficher(f"\nChamps OBLIGATOIRES en destination:")
            for f in required_dst[:10]:
                afficher(f"  - {f['name']} ({f['ttype']})")
            if len(required_dst) > 10:
                afficher(f"  ... et {len(required_dst) - 10} autres")
        
    except Exception as e:
        afficher(f"ERREUR: {str(e)[:60]}")

afficher("\n" + "="*70)
afficher("FIN ANALYSE")
afficher("="*70)

