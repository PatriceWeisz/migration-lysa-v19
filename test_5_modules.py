#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST 5 MODULES ESSENTIELS
"""

import sys
import os
os.environ['PYTHONUNBUFFERED'] = '1'

def log(msg):
    print(msg)
    sys.stdout.flush()

from connexion_double_v19 import ConnexionDoubleV19
from framework.migrateur_generique import MigrateurGenerique
from framework.gestionnaire_configuration import GestionnaireConfiguration

log("="*70)
log("TEST 5 MODULES ESSENTIELS")
log("="*70)

conn = ConnexionDoubleV19()
conn.connecter_tout()

MODULES = [
    'account.tax',
    'res.partner.category',
    'res.country',  
    'product.category',
    'uom.uom',
]

configs = GestionnaireConfiguration.obtenir_toutes_configs()
resultats = []

for module in MODULES:
    log(f"\n{'='*70}")
    log(f"MODULE: {module}")
    log(f"{'='*70}")
    
    try:
        config = configs[module].copy()
        config['mode_test'] = True
        config['limite_test'] = 10
        config['mode_interactif'] = False
        
        migrateur = MigrateurGenerique(conn, module, config)
        stats = migrateur.migrer()
        
        log(f"\n✅ {module}:")
        log(f"   Nouveaux: {stats['nouveaux']}, Erreurs: {stats['erreurs']}")
        
        resultats.append((module, stats))
        
    except Exception as e:
        log(f"\n❌ {module}: {str(e)[:100]}")
        resultats.append((module, {'erreurs': 1}))

log(f"\n{'='*70}")
log("RÉSUMÉ")
log(f"{'='*70}")

for module, stats in resultats:
    if isinstance(stats, dict) and stats.get('erreurs', 0) == 0:
        log(f"✅ {module:30s} OK")
    else:
        log(f"❌ {module:30s} ERREUR")

log(f"\n{'='*70}")
log("TEST TERMINÉ")
log(f"{'='*70}")

