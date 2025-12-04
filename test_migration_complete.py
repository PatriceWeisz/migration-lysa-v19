#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST MIGRATION COMPLÈTE - MODE TEST
====================================
Migre 5-10 enregistrements COMPLETS de chaque module
TOUS les champs sont migrés automatiquement
"""

import sys
import os

print("="*70, flush=True)
print("TEST MIGRATION COMPLETE - DEMARRAGE", flush=True)
print("="*70, flush=True)
print("Mode: TEST (5-10 enregistrements par module)", flush=True)
print("TOUS les champs seront migrés automatiquement", flush=True)
print("="*70, flush=True)
print("Import... (10-15 secondes)", flush=True)
print("="*70, flush=True)

from datetime import datetime

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19
from framework.migrateur_generique import MigrateurGenerique
from framework.gestionnaire_configuration import GestionnaireConfiguration

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

# =============================================================================
# CONFIGURATION
# =============================================================================

MODE_TEST = True  # ✅ MODE TEST ACTIVÉ
TEST_LIMIT = 5    # 5 enregistrements par module
MODE_UPDATE = True  # Met à jour les existants aussi

afficher("\nOK - Modules charges")
afficher("="*70)
afficher("TEST MIGRATION COMPLÈTE")
afficher("="*70)
afficher(f"Mode TEST: {TEST_LIMIT} enregistrements par module")
afficher(f"Mode UPDATE: {'OUI' if MODE_UPDATE else 'NON'}")
afficher(f"Tous les champs seront migrés automatiquement")
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
# MODULES À TESTER
# =============================================================================

MODULES_TEST = [
    'account.tax',
    'account.analytic.plan',
    'account.analytic.account',
    'res.partner.category',
    'product.pricelist',
    'crm.team',
    'project.project',
]

afficher(f"Modules à tester: {len(MODULES_TEST)}")
for m in MODULES_TEST:
    config = GestionnaireConfiguration.obtenir_config_module(m)
    if config:
        afficher(f"  - {m:40s} ({config['nom']})")
    else:
        afficher(f"  - {m:40s} (CONFIG MANQUANTE)")

afficher("")

# =============================================================================
# MIGRATION TEST
# =============================================================================

stats_globales = {
    'modules_ok': 0,
    'modules_erreur': 0,
    'modules_skip': 0,
    'total_nouveaux': 0,
    'total_mis_a_jour': 0,
    'total_champs': 0
}

for model in MODULES_TEST:
    config = GestionnaireConfiguration.obtenir_config_module(model)
    
    if not config:
        afficher(f"\n{model}: CONFIG MANQUANTE - SKIP")
        stats_globales['modules_skip'] += 1
        continue
    
    # Activer mode test
    config['mode_test'] = MODE_TEST
    config['test_limit'] = TEST_LIMIT
    config['mode_update'] = MODE_UPDATE
    
    try:
        migrateur = MigrateurGenerique(conn, model, config)
        
        # Compter les champs qui seront migrés
        champs = migrateur.obtenir_champs_migrables()
        stats_globales['total_champs'] += len(champs)
        
        # Migrer
        stats = migrateur.migrer()
        
        stats_globales['total_nouveaux'] += stats['nouveaux']
        stats_globales['total_mis_a_jour'] += stats['existants'] if MODE_UPDATE else 0
        
        if stats['erreurs'] == 0:
            stats_globales['modules_ok'] += 1
        else:
            stats_globales['modules_erreur'] += 1
            
    except Exception as e:
        afficher(f"\nERREUR FATALE sur {model}: {str(e)[:80]}")
        stats_globales['modules_erreur'] += 1

# =============================================================================
# RÉSUMÉ
# =============================================================================

afficher("\n" + "="*70)
afficher("TEST TERMINÉ")
afficher("="*70)
afficher(f"Modules testés     : {len(MODULES_TEST)}")
afficher(f"  OK               : {stats_globales['modules_ok']}")
afficher(f"  Erreurs          : {stats_globales['modules_erreur']}")
afficher(f"  Skippés          : {stats_globales['modules_skip']}")
afficher("")
afficher(f"Nouveaux créés     : {stats_globales['total_nouveaux']}")
afficher(f"Mis à jour         : {stats_globales['total_mis_a_jour']}")
afficher(f"Total champs       : {stats_globales['total_champs']}")
afficher("="*70)

if stats_globales['modules_ok'] == len(MODULES_TEST) - stats_globales['modules_skip']:
    afficher("\n✅ TEST RÉUSSI !")
    afficher("Le framework fonctionne correctement")
    afficher("Vous pouvez maintenant:")
    afficher("  1. Lancer la migration complète: python migration_framework.py")
    afficher("  2. Ou compléter les existants: python completer_champs_existants.py")
else:
    afficher("\n⚠️ ATTENTION: Des erreurs ont été détectées")
    afficher("Vérifiez les messages ci-dessus")

afficher("="*70)
afficher(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

