#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST COMPLET DU FRAMEWORK
==========================
Teste TOUS les modules avec détection complète des erreurs
"""

import sys
import os

print("="*70, flush=True)
print("TEST COMPLET FRAMEWORK - DEMARRAGE", flush=True)
print("="*70, flush=True)
print("Import... (10-15 secondes)", flush=True)
print("="*70, flush=True)

import json
from pathlib import Path
from datetime import datetime

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19
from framework.migrateur_generique import MigrateurGenerique
from framework.gestionnaire_configuration import GestionnaireConfiguration

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

LOGS_DIR = Path('logs')
LOGS_DIR.mkdir(exist_ok=True)

# Fichier de rapport d'erreurs
RAPPORT = LOGS_DIR / f'test_complet_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'

def log_erreur(module, phase, erreur_type, details):
    """Log une erreur dans le rapport"""
    with open(RAPPORT, 'a', encoding='utf-8') as f:
        f.write(f"\n{'='*70}\n")
        f.write(f"MODULE: {module}\n")
        f.write(f"PHASE: {phase}\n")
        f.write(f"TYPE: {erreur_type}\n")
        f.write(f"DÉTAILS:\n{details}\n")

afficher("\nOK - Modules charges")
afficher("="*70)
afficher("TEST COMPLET DU FRAMEWORK")
afficher("="*70)
afficher("Mode: TEST (5 enregistrements par module)")
afficher("Détection complète des erreurs")
afficher(f"Rapport: {RAPPORT.name}")
afficher("="*70)
afficher(f"Debut: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# =============================================================================
# CONNEXION
# =============================================================================

afficher("Connexion...")
conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    afficher("ERREUR Connexion")
    sys.exit(1)

afficher("OK Connexion\n")

# =============================================================================
# TEST DE TOUS LES MODULES
# =============================================================================

phases = GestionnaireConfiguration.obtenir_modules_par_phase()

resultats = {
    'modules_testes': 0,
    'modules_ok': 0,
    'erreurs_codage': 0,
    'erreurs_champs': 0,
    'erreurs_transformation': 0,
    'erreurs_relation': 0,
    'modules_non_installes': 0,
}

erreurs_details = []

for phase_nom, modules in phases.items():
    afficher(f"\n{'='*70}")
    afficher(f"{phase_nom}")
    afficher(f"{'='*70}")
    
    for model in modules:
        config = GestionnaireConfiguration.obtenir_config_module(model)
        
        if not config:
            afficher(f"{model}: CONFIG MANQUANTE - SKIP")
            continue
        
        afficher(f"\nTest: {model} ({config['nom']})")
        resultats['modules_testes'] += 1
        
        # Configuration test
        config['mode_test'] = True
        config['test_limit'] = 5
        config['mode_update'] = False
        
        # =================================================================
        # TEST 1 : Vérifier que le module existe dans la source
        # =================================================================
        try:
            count = conn.executer_source(model, 'search_count', [])
            if count == 0:
                afficher(f"  └─ Module non installé (0 enregistrements) - SKIP")
                resultats['modules_non_installes'] += 1
                continue
            afficher(f"  ├─ Module installé: {count} enregistrements")
        except Exception as e:
            afficher(f"  └─ ERREUR accès source: {str(e)[:50]}")
            log_erreur(model, "Vérification source", "ERREUR_ACCES", str(e))
            resultats['erreurs_codage'] += 1
            erreurs_details.append({'module': model, 'type': 'ACCES_SOURCE', 'erreur': str(e)[:100]})
            continue
        
        # =================================================================
        # TEST 2 : Détection des champs
        # =================================================================
        try:
            migrateur = MigrateurGenerique(conn, model, config)
            champs = migrateur.obtenir_champs_migrables()
            afficher(f"  ├─ Champs détectés: {len(champs)}")
            
            # Vérifier champs binary (images)
            champs_binary = [c for c in champs if 'image' in c or 'file' in c or 'data' in c]
            if champs_binary:
                afficher(f"  ├─ Champs binary: {len(champs_binary)} (images/fichiers)")
            
            # Vérifier champs studio
            champs_studio = [c for c in champs if c.startswith('x_studio_')]
            if champs_studio:
                afficher(f"  ├─ Champs Studio: {len(champs_studio)}")
                
        except Exception as e:
            afficher(f"  └─ ERREUR détection champs: {str(e)[:50]}")
            log_erreur(model, "Détection champs", "ERREUR_CHAMPS", str(e))
            resultats['erreurs_champs'] += 1
            erreurs_details.append({'module': model, 'type': 'DETECTION_CHAMPS', 'erreur': str(e)[:100]})
            continue
        
        # =================================================================
        # TEST 3 : Test de transformation
        # =================================================================
        try:
            # Récupérer 1 enregistrement de test
            test_rec = conn.executer_source(model, 'search_read', [], 
                                           fields=champs, limit=1)
            if test_rec:
                rec_transforme = migrateur.analyseur.appliquer_transformations(model, test_rec[0])
                afficher(f"  ├─ Transformation: OK")
        except Exception as e:
            afficher(f"  ├─ ATTENTION transformation: {str(e)[:40]}")
            log_erreur(model, "Transformation", "ERREUR_TRANSFORMATION", str(e))
            resultats['erreurs_transformation'] += 1
        
        # =================================================================
        # TEST 4 : Migration réelle (5 enregistrements)
        # =================================================================
        try:
            stats = migrateur.migrer()
            
            if stats['erreurs'] == 0:
                afficher(f"  └─ ✅ OK: {stats['nouveaux']} créés, {stats['existants']} existants")
                resultats['modules_ok'] += 1
            else:
                afficher(f"  └─ ⚠️ ERREURS: {stats['erreurs']} erreurs")
                log_erreur(model, "Migration", "ERREURS_MIGRATION", 
                          f"{stats['erreurs']} erreurs sur 5 enregistrements")
                resultats['erreurs_relation'] += 1
                erreurs_details.append({'module': model, 'type': 'MIGRATION', 'erreur': f"{stats['erreurs']} erreurs"})
                
        except Exception as e:
            afficher(f"  └─ ❌ ERREUR FATALE: {str(e)[:50]}")
            log_erreur(model, "Migration", "ERREUR_FATALE", str(e))
            resultats['erreurs_codage'] += 1
            erreurs_details.append({'module': model, 'type': 'FATALE', 'erreur': str(e)[:100]})

# =============================================================================
# RÉSUMÉ FINAL
# =============================================================================

afficher("\n" + "="*70)
afficher("RÉSULTATS DU TEST COMPLET")
afficher("="*70)
afficher(f"Modules testés          : {resultats['modules_testes']}")
afficher(f"  ✅ OK                 : {resultats['modules_ok']}")
afficher(f"  ⏭️ Non installés      : {resultats['modules_non_installes']}")
afficher("")
afficher("ERREURS:")
afficher(f"  Erreurs codage        : {resultats['erreurs_codage']}")
afficher(f"  Erreurs champs        : {resultats['erreurs_champs']}")
afficher(f"  Erreurs transformation: {resultats['erreurs_transformation']}")
afficher(f"  Erreurs relations     : {resultats['erreurs_relation']}")
afficher("")
total_erreurs = (resultats['erreurs_codage'] + resultats['erreurs_champs'] + 
                resultats['erreurs_transformation'] + resultats['erreurs_relation'])
afficher(f"TOTAL ERREURS           : {total_erreurs}")
afficher("="*70)

if total_erreurs == 0:
    afficher("\n🎉 TOUS LES TESTS RÉUSSIS !")
    afficher("Le framework est prêt pour la production")
    afficher("\nProchaine étape: python migration_framework.py")
else:
    afficher(f"\n⚠️ {total_erreurs} ERREURS DÉTECTÉES")
    afficher(f"Voir le rapport: {RAPPORT}")
    afficher("\nErreurs par module:")
    for err in erreurs_details[:10]:
        afficher(f"  - {err['module']:40s} : {err['type']}")
    if len(erreurs_details) > 10:
        afficher(f"  ... et {len(erreurs_details) - 10} autres")
    
    afficher("\nActions recommandées:")
    if resultats['erreurs_codage'] > 0:
        afficher("  1. Corriger les erreurs de codage dans le framework")
    if resultats['erreurs_champs'] > 0:
        afficher("  2. Vérifier les champs inexistants en v19")
    if resultats['erreurs_transformation'] > 0:
        afficher("  3. Corriger les transformations v16→v19")
    if resultats['erreurs_relation'] > 0:
        afficher("  4. Vérifier les mappings de relations")

afficher("="*70)
afficher(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
afficher(f"\nRapport complet: {RAPPORT}")

