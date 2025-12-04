#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
INVENTAIRE COMPLET DE LA BASE SOURCE
====================================
Analyse TOUS les modules, champs, paramétrages
"""

import sys
import os

# AFFICHER AVANT TOUT
print("="*70, flush=True)
print("INVENTAIRE COMPLET - DEMARRAGE", flush=True)
print("="*70, flush=True)
print("Import des modules... (10-15 secondes)", flush=True)
print("="*70, flush=True)

import json
from pathlib import Path

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

LOGS_DIR = Path('logs')
LOGS_DIR.mkdir(exist_ok=True)

afficher("\nOK - Modules charges")
afficher("="*70)
afficher("INVENTAIRE COMPLET DE LA BASE SOURCE")
afficher("="*70)

conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    sys.exit(1)

afficher("OK Connexion\n")

inventaire = {
    'modules_standard': {},
    'modules_studio': {},
    'parametrages': {},
    'total_enregistrements': 0
}

# =============================================================================
# 1. TOUS LES MODÈLES AVEC DONNÉES
# =============================================================================

afficher("="*70)
afficher("ÉTAPE 1: INVENTAIRE DES MODÈLES")
afficher("="*70)

# Récupérer tous les modèles
models = conn.executer_source('ir.model', 'search_read', [],
                              fields=['model', 'name', 'transient'])

afficher(f"Total modèles: {len(models)}\n")

modeles_avec_donnees = []

for idx, model_info in enumerate(models, 1):
    model_name = model_info['model']
    
    if idx % 50 == 0:
        afficher(f"Analyse {idx}/{len(models)}...")
    
    # Skip modèles transients (wizards)
    if model_info.get('transient'):
        continue
    
    # Skip modèles système internes
    if model_name.startswith('ir.') or model_name.startswith('base.'):
        continue
    
    try:
        count = conn.executer_source(model_name, 'search_count', [])
        if count > 0:
            is_studio = model_name.startswith('x_')
            
            modeles_avec_donnees.append({
                'model': model_name,
                'nom': model_info['name'],
                'count': count,
                'studio': is_studio
            })
            
            inventaire['total_enregistrements'] += count
            
            if is_studio:
                inventaire['modules_studio'][model_name] = count
            else:
                inventaire['modules_standard'][model_name] = count
    except:
        pass

# Trier par nombre d'enregistrements
modeles_avec_donnees.sort(key=lambda x: x['count'], reverse=True)

afficher(f"\nModèles avec données: {len(modeles_avec_donnees)}")
afficher(f"  Standard: {len(inventaire['modules_standard'])}")
afficher(f"  Studio: {len(inventaire['modules_studio'])}")
afficher(f"Total enregistrements: {inventaire['total_enregistrements']:,}\n")

# Afficher TOP 30
afficher("TOP 30 modules par volume:")
for idx, m in enumerate(modeles_avec_donnees[:30], 1):
    marker = " [STUDIO]" if m['studio'] else ""
    afficher(f"  {idx:2}. {m['model']:40s} : {m['count']:>8,d}{marker}")

# =============================================================================
# 2. PARAMÉTRAGES SYSTÈME
# =============================================================================

afficher("\n" + "="*70)
afficher("ÉTAPE 2: PARAMÉTRAGES SYSTÈME")
afficher("="*70)

# Entreprises
companies = conn.executer_source('res.company', 'search_read', [],
                                fields=['name', 'currency_id', 'country_id'])
afficher(f"\nEntreprises: {len(companies)}")
for c in companies:
    afficher(f"  - {c['name']}")

# Paramètres système
try:
    params = conn.executer_source('ir.config_parameter', 'search_read', [],
                                 fields=['key', 'value'])
    afficher(f"\nParamètres système: {len(params)}")
    inventaire['parametrages']['ir.config_parameter'] = len(params)
except:
    afficher("\nParamètres système: Non accessible")

# Séquences
sequences = conn.executer_source('ir.sequence', 'search_read', [],
                                fields=['name', 'code'])
afficher(f"Séquences: {len(sequences)}")
inventaire['parametrages']['ir.sequence'] = len(sequences)

# =============================================================================
# 3. MODULES STUDIO DÉTAILLÉS
# =============================================================================

if inventaire['modules_studio']:
    afficher("\n" + "="*70)
    afficher("ÉTAPE 3: MODULES STUDIO")
    afficher("="*70)
    
    for model_name, count in inventaire['modules_studio'].items():
        afficher(f"\n{model_name}: {count:,d} enregistrements")
        
        # Récupérer les champs
        try:
            fields = conn.executer_source('ir.model.fields', 'search_read',
                                         [('model', '=', model_name)],
                                         fields=['name', 'ttype'])
            afficher(f"  Champs: {len(fields)}")
            for f in fields[:10]:
                afficher(f"    - {f['name']} ({f['ttype']})")
            if len(fields) > 10:
                afficher(f"    ... et {len(fields) - 10} autres")
        except:
            pass

# =============================================================================
# SAUVEGARDE
# =============================================================================

output_file = LOGS_DIR / 'inventaire_complet.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump({
        'modeles_avec_donnees': modeles_avec_donnees,
        'inventaire': inventaire,
        'date': '2025-12-03'
    }, f, indent=2, ensure_ascii=False)

afficher("\n" + "="*70)
afficher("INVENTAIRE TERMINÉ")
afficher("="*70)
afficher(f"Modèles standard: {len(inventaire['modules_standard'])}")
afficher(f"Modèles Studio: {len(inventaire['modules_studio'])}")
afficher(f"Total enregistrements: {inventaire['total_enregistrements']:,}")
afficher(f"\nSauvegardé dans: {output_file}")
afficher("="*70)

