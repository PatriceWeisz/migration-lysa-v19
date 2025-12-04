#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALYSE AVANT MIGRATION
========================
Analyse TOUS les problèmes potentiels AVANT de migrer
"""

import sys
import os

print("="*70, flush=True)
print("ANALYSE AVANT MIGRATION", flush=True)
print("="*70, flush=True)
print("Import...", flush=True)

from pathlib import Path
from datetime import datetime

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19
from framework.gestionnaire_configuration import GestionnaireConfiguration

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

LOGS_DIR = Path('logs')
RAPPORT = LOGS_DIR / f'analyse_pre_migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

afficher("\nOK - Modules charges")
afficher("="*70)
afficher("ANALYSE PRÉ-MIGRATION")
afficher("="*70)
afficher("Identifie TOUS les problèmes potentiels")
afficher(f"Rapport: {RAPPORT.name}")
afficher("="*70)

conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    sys.exit(1)

afficher("OK Connexion\n")

# Ouvrir rapport
rapport_file = open(RAPPORT, 'w', encoding='utf-8')

def ecrire_rapport(msg):
    rapport_file.write(msg + '\n')
    rapport_file.flush()

ecrire_rapport("="*70)
ecrire_rapport("ANALYSE PRÉ-MIGRATION")
ecrire_rapport(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
ecrire_rapport("="*70)

# =============================================================================
# ANALYSE PAR MODULE
# =============================================================================

phases = GestionnaireConfiguration.obtenir_modules_par_phase()

problemes = {
    'champs_renommes': [],
    'champs_disparus': [],
    'nouveaux_obligatoires_sans_default': [],
    'modules_non_installes': [],
    'relations_manquantes': [],
}

for phase_nom, modules in phases.items():
    afficher(f"\n{phase_nom}")
    ecrire_rapport(f"\n{'='*70}")
    ecrire_rapport(phase_nom)
    ecrire_rapport("="*70)
    
    for model in modules:
        afficher(f"  Analyse: {model}...", end='')
        
        # Vérifier installation
        try:
            count = conn.executer_source(model, 'search_count', [])
            if count == 0:
                afficher(" [Non installé]")
                problemes['modules_non_installes'].append(model)
                ecrire_rapport(f"\n{model}: Non installé")
                continue
            
            afficher(f" [{count} enreg]")
            ecrire_rapport(f"\n{model}: {count} enregistrements")
            
        except:
            afficher(" [ERREUR]")
            problemes['modules_non_installes'].append(model)
            continue
        
        # Analyser champs
        try:
            # Champs SOURCE
            fields_src = conn.executer_source('ir.model.fields', 'search_read',
                                             [('model', '=', model), ('store', '=', True)],
                                             fields=['name', 'ttype', 'required'])
            
            # Champs DESTINATION
            fields_dst = conn.executer_destination('ir.model.fields', 'search_read',
                                                  [('model', '=', model), ('store', '=', True)],
                                                  fields=['name', 'ttype', 'required'])
            
            src_names = {f['name']: f for f in fields_src}
            dst_names = {f['name']: f for f in fields_dst}
            
            # Champs disparus
            disparus = [f for f in src_names if f not in dst_names and f not in ['__last_update', 'display_name']]
            if disparus:
                ecrire_rapport(f"  CHAMPS DISPARUS: {', '.join(disparus)}")
                problemes['champs_disparus'].append({'module': model, 'champs': disparus})
            
            # Nouveaux obligatoires
            nouveaux_oblig = [f for f in dst_names if f not in src_names and dst_names[f].get('required')]
            if nouveaux_oblig:
                ecrire_rapport(f"  NOUVEAUX OBLIGATOIRES: {', '.join(nouveaux_oblig)}")
                problemes['nouveaux_obligatoires_sans_default'].append({'module': model, 'champs': nouveaux_oblig})
            
        except Exception as e:
            ecrire_rapport(f"  ERREUR analyse: {str(e)[:60]}")

# =============================================================================
# RÉSUMÉ DES PROBLÈMES
# =============================================================================

afficher("\n" + "="*70)
afficher("RÉSUMÉ DES PROBLÈMES POTENTIELS")
afficher("="*70)

ecrire_rapport("\n" + "="*70)
ecrire_rapport("RÉSUMÉ DES PROBLÈMES")
ecrire_rapport("="*70)

afficher(f"Modules non installés     : {len(problemes['modules_non_installes'])}")
afficher(f"Modules avec champs perdus: {len(problemes['champs_disparus'])}")
afficher(f"Nouveaux champs obligatoires: {len(problemes['nouveaux_obligatoires_sans_default'])}")

ecrire_rapport(f"\nModules non installés: {len(problemes['modules_non_installes'])}")
for m in problemes['modules_non_installes']:
    ecrire_rapport(f"  - {m}")

ecrire_rapport(f"\nChamps disparus par module:")
for p in problemes['champs_disparus']:
    ecrire_rapport(f"  {p['module']}: {', '.join(p['champs'])}")

ecrire_rapport(f"\nNouveaux champs obligatoires:")
for p in problemes['nouveaux_obligatoires_sans_default']:
    ecrire_rapport(f"  {p['module']}: {', '.join(p['champs'])}")

afficher("\n" + "="*70)
afficher("RECOMMANDATIONS")
afficher("="*70)

if len(problemes['champs_disparus']) > 0:
    afficher("⚠️ Champs disparus détectés")
    afficher("   → Vérifier framework/analyseur_differences_champs.py")
    afficher("   → Ajouter transformations si nécessaire")

if len(problemes['nouveaux_obligatoires_sans_default']) > 0:
    afficher("⚠️ Nouveaux champs obligatoires détectés")
    afficher("   → Ajouter valeurs par défaut dans gestionnaire_configuration.py")

if len(problemes['champs_disparus']) == 0 and len(problemes['nouveaux_obligatoires_sans_default']) == 0:
    afficher("✅ AUCUN PROBLÈME MAJEUR DÉTECTÉ")
    afficher("Le framework devrait fonctionner correctement")

afficher("="*70)
afficher(f"\nRapport complet sauvegardé: {RAPPORT}")
afficher("\nProchaine étape: python test_complet_framework.py")

rapport_file.close()

