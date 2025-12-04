#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAPPORT DES DIFFÉRENCES DE CHAMPS v16 → v19
===========================================
Analyse et affiche les différences pour tous les modules
À LANCER AVANT la migration pour identifier les problèmes potentiels
"""

import sys
import os

print("="*70, flush=True)
print("RAPPORT DIFFERENCES CHAMPS - DEMARRAGE", flush=True)
print("="*70, flush=True)
print("Import... (10-15 secondes)", flush=True)
print("="*70, flush=True)

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19
from framework.analyseur_differences_champs import AnalyseurDifferencesChamps
from framework.gestionnaire_configuration import GestionnaireConfiguration

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

afficher("\nOK - Modules charges")
afficher("="*70)
afficher("RAPPORT DES DIFFÉRENCES DE CHAMPS")
afficher("="*70)
afficher("Analyse les différences v16 → v19 pour tous les modules")
afficher("="*70)

# Connexion
afficher("\nConnexion...")
conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    sys.exit(1)

afficher("OK Connexion\n")

# Analyseur
analyseur = AnalyseurDifferencesChamps(conn)

# Modules à analyser
MODULES = [
    'account.account',
    'account.tax',
    'account.journal',
    'res.partner',
    'product.template',
    'res.users',
    'project.project',
    'account.analytic.account',
    'crm.team',
    'product.pricelist',
]

for model in MODULES:
    afficher(f"\n{'='*70}")
    afficher(f"MODULE: {model}")
    afficher(f"{'='*70}")
    
    try:
        diff = analyseur.analyser_module(model)
        
        # Champs renommés
        if diff['champs_renommes']:
            afficher("\nCHAMPS RENOMMÉS (v16 → v19):")
            for ancien, nouveau in diff['champs_renommes'].items():
                afficher(f"  {ancien:30s} → {nouveau}")
        
        # Champs disparus
        if diff['champs_disparus']:
            afficher(f"\nCHAMPS DISPARUS en v19: {len(diff['champs_disparus'])}")
            for champ in diff['champs_disparus'][:10]:
                afficher(f"  - {champ}")
            if len(diff['champs_disparus']) > 10:
                afficher(f"  ... et {len(diff['champs_disparus']) - 10} autres")
        
        # Nouveaux champs obligatoires
        if diff['nouveaux_obligatoires']:
            afficher(f"\nNOUVEAUX CHAMPS OBLIGATOIRES en v19: {len(diff['nouveaux_obligatoires'])}")
            for champ in diff['nouveaux_obligatoires']:
                default = diff['mappings_connus'].get('nouveaux_obligatoires_defaults', {}).get(champ)
                if default:
                    afficher(f"  - {champ:30s} (défaut: {default})")
                else:
                    afficher(f"  - {champ:30s} (⚠️ PAS DE DÉFAUT)")
        
        # Transformations
        if diff['transformations']:
            afficher(f"\nTRANSFORMATIONS APPLIQUÉES: {len(diff['transformations'])}")
            for champ in diff['transformations'].keys():
                afficher(f"  - {champ}")
        
        # Mapping connu ?
        if diff['mappings_connus']:
            afficher("\n✅ MAPPING CONNU - Transformations automatiques")
        else:
            afficher("\n⚠️ MAPPING INCONNU - Migration basique")
        
    except Exception as e:
        afficher(f"ERREUR: {str(e)[:60]}")

afficher("\n" + "="*70)
afficher("RÉSUMÉ")
afficher("="*70)
afficher("Ce rapport identifie les différences entre v16 et v19")
afficher("Le framework applique automatiquement les transformations connues")
afficher("")
afficher("Si vous voyez '⚠️ PAS DE DÉFAUT' :")
afficher("  → Ajouter le défaut dans framework/analyseur_differences_champs.py")
afficher("="*70)

