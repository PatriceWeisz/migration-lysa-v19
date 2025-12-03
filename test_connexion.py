#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST CONNEXION UNIQUEMENT
"""

import sys
import os

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

afficher("="*70)
afficher("TEST CONNEXION")
afficher("="*70)

conn = ConnexionDoubleV19()

if conn.connecter_tout():
    afficher("\nSUCCES - Connexions OK")
else:
    afficher("\nECHEC - Erreur de connexion")

