#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION AVEC FRAMEWORK GÉNÉRIQUE
===================================
Utilise le framework pour migrer tous les modules automatiquement
"""

import sys
import os

# AFFICHER AVANT TOUT
print("="*70, flush=True)
print("MIGRATION FRAMEWORK - DEMARRAGE", flush=True)
print("="*70, flush=True)
print("Import des modules... (10-15 secondes)", flush=True)
print("="*70, flush=True)

from datetime import datetime
from pathlib import Path

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19
from framework.migrateur_generique import MigrateurGenerique
from framework.gestionnaire_configuration import GestionnaireConfiguration
from framework.gestionnaire_reprise import GestionnaireReprise

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

# =============================================================================
# CONFIGURATION
# =============================================================================

MODE_TEST = False
TEST_LIMIT = 10

afficher("\nOK - Modules charges")
afficher("="*70)
afficher("MIGRATION AVEC FRAMEWORK GÉNÉRIQUE")
afficher("="*70)
afficher(f"Mode: {'TEST' if MODE_TEST else 'PRODUCTION'}")
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
# MIGRATION PAR PHASE
# =============================================================================

phases = GestionnaireConfiguration.obtenir_modules_par_phase()

stats_globales = {
    'modules_ok': 0,
    'modules_erreur': 0,
    'total_nouveaux': 0,
    'total_existants': 0,
    'total_erreurs': 0
}

for phase_nom, modules in phases.items():
    afficher(f"\n{'='*70}")
    afficher(f"{phase_nom}")
    afficher(f"{'='*70}")
    
    for model in modules:
        config = GestionnaireConfiguration.obtenir_config_module(model)
        
        if not config:
            afficher(f"\nModule {model}: Configuration manquante - SKIP")
            continue
        
        # Ajouter mode test à la config
        config['mode_test'] = MODE_TEST
        config['test_limit'] = TEST_LIMIT
        
        try:
            migrateur = MigrateurGenerique(conn, model, config)
            stats = migrateur.migrer()
            
            stats_globales['total_nouveaux'] += stats['nouveaux']
            stats_globales['total_existants'] += stats['existants']
            stats_globales['total_erreurs'] += stats['erreurs']
            
            if stats['erreurs'] == 0:
                stats_globales['modules_ok'] += 1
            else:
                stats_globales['modules_erreur'] += 1
                
        except Exception as e:
            afficher(f"\nERREUR FATALE sur {model}: {str(e)[:60]}")
            stats_globales['modules_erreur'] += 1

# =============================================================================
# RÉSUMÉ FINAL
# =============================================================================

afficher("\n" + "="*70)
afficher("MIGRATION TERMINÉE")
afficher("="*70)
afficher(f"Modules OK     : {stats_globales['modules_ok']}")
afficher(f"Modules erreur : {stats_globales['modules_erreur']}")
afficher(f"Nouveaux créés : {stats_globales['total_nouveaux']}")
afficher(f"Existants      : {stats_globales['total_existants']}")
afficher(f"Erreurs        : {stats_globales['total_erreurs']}")
afficher("="*70)
afficher(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

