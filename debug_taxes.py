#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DEBUG TAXES - Voir exactement ce qu'on envoie
"""

import sys
import os
import json

os.environ['PYTHONUNBUFFERED'] = '1'

def log(msg):
    print(msg)
    sys.stdout.flush()

log("="*70)
log("DEBUG TAXES")
log("="*70)

from connexion_double_v19 import ConnexionDoubleV19

conn = ConnexionDoubleV19()
conn.connecter_tout()

log("\n1. Lire UNE taxe en SOURCE avec TOUS les champs:")
log("="*70)

taxes = conn.executer_source('account.tax', 'search_read',
                             [], 
                             fields=[],  # Tous les champs
                             limit=1)

if taxes:
    tax = taxes[0]
    log(f"\nTaxe: {tax.get('name', 'N/A')}")
    log(f"\nCHAMPS PROBLÉMATIQUES:")
    
    for field in ['invoice_repartition_line_ids', 'refund_repartition_line_ids']:
        value = tax.get(field)
        log(f"\n{field}:")
        log(f"  Type: {type(value)}")
        log(f"  Valeur: {value}")
        
        if isinstance(value, list) and value:
            log(f"  Nombre éléments: {len(value)}")
            log(f"  Type premier élément: {type(value[0])}")
            
            # Lire les détails
            if isinstance(value[0], int):
                try:
                    lines = conn.executer_source(
                        'account.tax.repartition.line',
                        'read',
                        value,
                        ['repartition_type', 'factor_percent', 'account_id', 'use_in_tax_closing']
                    )
                    log(f"\n  Détails des {len(lines)} lignes:")
                    for line in lines:
                        log(f"    - {line}")
                except Exception as e:
                    log(f"  Erreur lecture lignes: {e}")

log("\n" + "="*70)
log("2. Tester création MANUELLE d'une taxe simple:")
log("="*70)

try:
    # Créer UNE taxe très simple SANS les champs problématiques
    test_data = {
        'name': 'TEST Migration',
        'amount': 20.0,
        'type_tax_use': 'sale',
        'amount_type': 'percent',
    }
    
    log(f"\nDonnées à envoyer:")
    log(json.dumps(test_data, indent=2))
    
    log("\nCréation...")
    test_id = conn.executer_destination('account.tax', 'create', test_data)
    
    log(f"✅ SUCCÈS ! ID créé: {test_id}")
    
    # Supprimer pour nettoyer
    conn.executer_destination('account.tax', 'unlink', [test_id])
    log("✅ Taxe test supprimée (nettoyage)")
    
except Exception as e:
    log(f"❌ ERREUR: {e}")

log("\n" + "="*70)
log("FIN DEBUG")
log("="*70)

