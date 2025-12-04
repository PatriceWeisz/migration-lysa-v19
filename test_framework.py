#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST DU FRAMEWORK
=================
Test rapide du framework sur 1 module avec 5 enregistrements
"""

import sys
import os

print("="*70, flush=True)
print("TEST FRAMEWORK - DEMARRAGE", flush=True)
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

afficher("\nOK - Modules charges")
afficher("="*70)
afficher("TEST FRAMEWORK SUR MODULE: account.tax")
afficher("="*70)
afficher(f"Debut: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Connexion
afficher("Connexion...")
conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    afficher("ERREUR Connexion")
    sys.exit(1)

afficher("OK Connexion\n")

# Configuration en mode TEST
config = GestionnaireConfiguration.obtenir_config_module('account.tax')
if not config:
    afficher("ERREUR: Config account.tax introuvable")
    sys.exit(1)

config['mode_test'] = True
config['test_limit'] = 5

afficher(f"Configuration: {config['nom']}")
afficher(f"Mode: TEST (limite {config['test_limit']} enregistrements)\n")

# Créer migrateur
try:
    migrateur = MigrateurGenerique(conn, 'account.tax', config)
    afficher("Migrateur créé avec succès\n")
except Exception as e:
    afficher(f"ERREUR création migrateur: {str(e)}")
    sys.exit(1)

# Lancer migration
try:
    stats = migrateur.migrer()
    
    afficher("\n" + "="*70)
    afficher("TEST RÉUSSI !")
    afficher("="*70)
    afficher(f"Le framework fonctionne correctement")
    afficher(f"Vous pouvez maintenant lancer: python migration_framework.py")
    afficher("="*70)
    
except Exception as e:
    afficher(f"\nERREUR durant migration: {str(e)}")
    import traceback
    afficher(traceback.format_exc())
    sys.exit(1)

afficher(f"\nFin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

