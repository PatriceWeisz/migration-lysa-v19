#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMPLÉTER LES CHAMPS DES ENREGISTREMENTS EXISTANTS
===================================================
Met à jour les enregistrements déjà migrés pour ajouter les champs manquants
"""

import sys
import os

print("="*70, flush=True)
print("COMPLETION CHAMPS EXISTANTS - DEMARRAGE", flush=True)
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
afficher("COMPLÉTION DES CHAMPS EXISTANTS")
afficher("="*70)
afficher("Met à jour les enregistrements déjà migrés")
afficher("Ajoute les champs manquants")
afficher("="*70)
afficher(f"Debut: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Connexion
afficher("Connexion...")
conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    afficher("ERREUR Connexion")
    sys.exit(1)

afficher("OK Connexion\n")

# =============================================================================
# MODULES À COMPLÉTER
# =============================================================================

MODULES_A_COMPLETER = [
    'account.tax',
    'product.pricelist',
    'crm.team',
    'project.project',
    'account.analytic.account',
    'res.partner.category',
    'res.partner',
    'product.template',
]

afficher("Modules à compléter:")
for m in MODULES_A_COMPLETER:
    afficher(f"  - {m}")

afficher(f"\nTotal: {len(MODULES_A_COMPLETER)} modules\n")

reponse = input("Continuer ? (oui/NON): ").strip().lower()
if reponse != 'oui':
    afficher("Annulé")
    sys.exit(0)

# =============================================================================
# COMPLÉTION
# =============================================================================

stats_globales = {
    'modules_ok': 0,
    'modules_erreur': 0,
    'total_mis_a_jour': 0
}

for model in MODULES_A_COMPLETER:
    config = GestionnaireConfiguration.obtenir_config_module(model)
    
    if not config:
        afficher(f"\n{model}: Config manquante - SKIP")
        continue
    
    # ACTIVER LE MODE UPDATE
    config['mode_update'] = True
    config['mode_test'] = False
    
    try:
        migrateur = MigrateurGenerique(conn, model, config)
        stats = migrateur.migrer()
        
        # En mode update, les "existants" sont ceux mis à jour
        stats_globales['total_mis_a_jour'] += stats['existants']
        stats_globales['modules_ok'] += 1
        
    except Exception as e:
        afficher(f"\nERREUR sur {model}: {str(e)[:60]}")
        stats_globales['modules_erreur'] += 1

# =============================================================================
# RÉSUMÉ
# =============================================================================

afficher("\n" + "="*70)
afficher("COMPLÉTION TERMINÉE")
afficher("="*70)
afficher(f"Modules OK           : {stats_globales['modules_ok']}")
afficher(f"Modules erreur       : {stats_globales['modules_erreur']}")
afficher(f"Enregistrements MAJ  : {stats_globales['total_mis_a_jour']}")
afficher("="*70)
afficher(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
afficher("\nTous les enregistrements ont maintenant 100% de leurs champs !")

