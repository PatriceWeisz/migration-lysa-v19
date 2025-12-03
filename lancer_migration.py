#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT DE LANCEMENT MIGRATION SIMPLIFIE
=======================================
Affichage garanti en console + logs
"""

import sys
import os

# Forcer l'affichage immédiat
os.environ['PYTHONUNBUFFERED'] = '1'

def afficher(msg):
    """Affichage forcé en console et stderr"""
    sys.stdout.write(msg + '\n')
    sys.stdout.flush()
    sys.stderr.write(msg + '\n')
    sys.stderr.flush()

afficher("="*70)
afficher("LANCEMENT MIGRATION")
afficher("="*70)

# Lancer le test rapide d'abord
afficher("\nLancement du test rapide...")
result = os.system('python test_migration_rapide.py')

if result == 0:
    afficher("\nOK Test reussi !")
    afficher("\nVoulez-vous lancer la migration complete ?")
    afficher("  1. Oui, lancer maintenant")
    afficher("  2. Non, juste le test")
    afficher("\nEntrez votre choix (1 ou 2): ")
else:
    afficher("\nERREUR Test echoue")
    sys.exit(1)

