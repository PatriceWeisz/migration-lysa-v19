#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OBTENIR TOUS LES CHAMPS D'UN MODULE
====================================
Récupère automatiquement tous les champs disponibles pour un modèle
"""

import sys
import os

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

def obtenir_champs_migrables(conn, model):
    """
    Obtient la liste des champs migrables pour un modèle
    Exclut les champs calculés, techniques et ceux qui n'existent plus en v19
    """
    afficher(f"\nAnalyse du modèle: {model}")
    
    # Récupérer champs SOURCE
    fields_src = conn.executer_source('ir.model.fields', 'search_read',
                                     [('model', '=', model)],
                                     fields=['name', 'ttype', 'store', 'readonly', 'compute'])
    
    src_dict = {f['name']: f for f in fields_src}
    afficher(f"  SOURCE: {len(fields_src)} champs")
    
    # Récupérer champs DESTINATION  
    fields_dst = conn.executer_destination('ir.model.fields', 'search_read',
                                          [('model', '=', model)],
                                          fields=['name', 'ttype', 'store', 'readonly', 'required'])
    
    dst_dict = {f['name']: f for f in fields_dst}
    afficher(f"  DESTINATION: {len(fields_dst)} champs")
    
    # Champs migrables
    champs_migrables = []
    champs_exclus = []
    
    for fname in src_dict.keys():
        field_info = src_dict[fname]
        
        # Exclure les champs techniques
        if fname in ['id', '__last_update', 'display_name', 'create_date', 'create_uid', 
                     'write_date', 'write_uid', 'message_ids', 'message_follower_ids',
                     'activity_ids', 'rating_ids', 'website_message_ids']:
            champs_exclus.append(f"{fname} (technique)")
            continue
        
        # Exclure les champs calculés non stockés
        if field_info.get('compute') and not field_info.get('store'):
            champs_exclus.append(f"{fname} (calculé)")
            continue
        
        # Exclure si n'existe pas en destination
        if fname not in dst_dict:
            champs_exclus.append(f"{fname} (n'existe pas en v19)")
            continue
        
        # Exclure les champs readonly
        if field_info.get('readonly') and not field_info.get('store'):
            champs_exclus.append(f"{fname} (readonly)")
            continue
        
        champs_migrables.append(fname)
    
    afficher(f"\n  MIGRABLES: {len(champs_migrables)} champs")
    afficher(f"  EXCLUS: {len(champs_exclus)} champs")
    
    return champs_migrables, champs_exclus

# =============================================================================
# MAIN
# =============================================================================

afficher("="*70)
afficher("ANALYSE DES CHAMPS MIGRABLES")
afficher("="*70)

conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    sys.exit(1)

afficher("OK Connexion")

MODULES = [
    'account.tax',
    'product.pricelist',
    'crm.team',
    'project.project',
    'account.analytic.account',
    'res.partner.category',
    'res.users',
]

for model in MODULES:
    migrables, exclus = obtenir_champs_migrables(conn, model)
    
    afficher(f"\n  Champs à migrer:")
    for f in sorted(migrables)[:20]:
        afficher(f"    - {f}")
    if len(migrables) > 20:
        afficher(f"    ... et {len(migrables) - 20} autres")

afficher("\n" + "="*70)
afficher("FIN ANALYSE")
afficher("="*70)

