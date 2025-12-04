#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST SIMPLE - TAXES UNIQUEMENT
================================
Test rapide d'un seul module pour voir les erreurs
"""

import sys
import os

# Configuration pour affichage immédiat
os.environ['PYTHONUNBUFFERED'] = '1'

def log(msg):
    """Affichage immédiat"""
    print(msg)
    sys.stdout.flush()

log("="*70)
log("TEST SIMPLE - TAXES")
log("="*70)
log("")

# Import après configuration
log("Import modules...")
from connexion_double_v19 import ConnexionDoubleV19
from framework.migrateur_generique import MigrateurGenerique
from framework.gestionnaire_configuration import GestionnaireConfiguration

log("OK Imports")
log("")

# Connexion
log("="*70)
log("CONNEXION")
log("="*70)

conn = ConnexionDoubleV19()
log("Connexion SOURCE...")
if not conn.connecter_source():
    log("ERREUR connexion SOURCE")
    sys.exit(1)

log("✅ SOURCE OK")

log("Connexion DESTINATION...")
if not conn.connecter_destination():
    log("ERREUR connexion DESTINATION")
    sys.exit(1)

log("✅ DESTINATION OK")
log("")

# Configuration
log("="*70)
log("CONFIGURATION TAXES")
log("="*70)

configs = GestionnaireConfiguration.obtenir_toutes_configs()
if 'account.tax' not in configs:
    log("❌ Configuration account.tax manquante !")
    sys.exit(1)

config = configs['account.tax'].copy()
config['mode_test'] = True
config['limite_test'] = 5  # Seulement 5 taxes
config['mode_interactif'] = False

log(f"Config: {config.get('nom', 'account.tax')}")
log(f"Limite: {config.get('limite_test')} enregistrements")
log("")

# Compter taxes source
log("="*70)
log("COMPTAGE SOURCE")
log("="*70)

try:
    count_src = conn.executer_source('account.tax', 'search_count', [])
    log(f"✅ Taxes en SOURCE: {count_src}")
except Exception as e:
    log(f"❌ Erreur comptage SOURCE: {e}")
    sys.exit(1)

log("")

# Migration
log("="*70)
log("MIGRATION TAXES (5 premières)")
log("="*70)
log("")

try:
    log("Initialisation migrateur...")
    migrateur = MigrateurGenerique(conn, 'account.tax', config)
    log("✅ Migrateur initialisé")
    log("")
    
    log("Lancement migration...")
    log("(Cela peut prendre 30-60 secondes)")
    log("")
    
    stats = migrateur.migrer()
    
    log("")
    log("="*70)
    log("RÉSULTATS")
    log("="*70)
    log(f"Nouveaux : {stats['nouveaux']}")
    log(f"Existants: {stats['existants']}")
    log(f"Erreurs  : {stats['erreurs']}")
    log(f"Skippés  : {stats['skipped']}")
    log("")
    
    # Auto-corrections
    if hasattr(migrateur, 'auto_correcteur'):
        corrections = migrateur.auto_correcteur.corrections_appliquees
        if corrections:
            log(f"Auto-corrections: {len(corrections)}")
            for corr in corrections[:5]:
                log(f"  - {corr.get('type', 'N/A')}: {corr.get('correction', 'N/A')[:50]}")
    
    if stats['erreurs'] == 0:
        log("")
        log("✅ MIGRATION TAXES RÉUSSIE !")
    else:
        log("")
        log(f"⚠️ {stats['erreurs']} erreurs détectées")

except Exception as e:
    log("")
    log("="*70)
    log("ERREUR MIGRATION")
    log("="*70)
    log(f"Type: {type(e).__name__}")
    log(f"Message: {str(e)}")
    log("")
    
    # Traceback complet
    import traceback
    log("Traceback complet:")
    log(traceback.format_exc())

log("")
log("="*70)
log("TEST TERMINÉ")
log("="*70)

