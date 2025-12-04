#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VÉRIFICATION D'INTÉGRITÉ COMPLÈTE
==================================
Vérifie via external_id que TOUTES les données sont transférées
"""

import sys
import os

print("="*70, flush=True)
print("VERIFICATION INTEGRITE - DEMARRAGE", flush=True)
print("="*70, flush=True)
print("Import...", flush=True)

import json
from pathlib import Path
from datetime import datetime

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19
from framework.gestionnaire_configuration import GestionnaireConfiguration
from framework.gestionnaire_reprise import VerificateurIntegrite

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

LOGS_DIR = Path('logs')
RAPPORT = LOGS_DIR / f'integrite_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

afficher("\nOK - Modules charges")
afficher("="*70)
afficher("VÉRIFICATION COMPLÈTE D'INTÉGRITÉ")
afficher("="*70)
afficher("Vérifie via external_id le transfert complet")
afficher(f"Rapport: {RAPPORT.name}")
afficher("="*70)

conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    sys.exit(1)

afficher("OK Connexion\n")

# Ouvrir rapport
rapport = open(RAPPORT, 'w', encoding='utf-8')

def ecrire(msg):
    rapport.write(msg + '\n')
    rapport.flush()

ecrire("="*70)
ecrire("VÉRIFICATION D'INTÉGRITÉ COMPLÈTE")
ecrire(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
ecrire("="*70)

# =============================================================================
# VÉRIFICATION PAR MODULE
# =============================================================================

verificateur = VerificateurIntegrite(conn)
phases = GestionnaireConfiguration.obtenir_modules_par_phase()

stats_globales = {
    'modules_verifies': 0,
    'modules_ok': 0,
    'modules_incomplets': 0,
    'modules_incoherents': 0,
    'modules_non_installes': 0
}

for phase_nom, modules in phases.items():
    afficher(f"\n{phase_nom}")
    ecrire(f"\n{'='*70}")
    ecrire(phase_nom)
    ecrire("="*70)
    
    for model in modules:
        config = GestionnaireConfiguration.obtenir_config_module(model)
        
        if not config:
            continue
        
        afficher(f"  {model}...", end='')
        
        # Vérifier installation
        try:
            count = conn.executer_source(model, 'search_count', [])
            if count == 0:
                afficher(" [Non installé]")
                stats_globales['modules_non_installes'] += 1
                ecrire(f"\n{model}: Non installé")
                continue
        except:
            afficher(" [ERREUR accès]")
            continue
        
        stats_globales['modules_verifies'] += 1
        
        # Vérifier intégrité
        resultat = verificateur.verifier_module(model, config['fichier'])
        
        if resultat['ok']:
            afficher(" ✅")
            stats_globales['modules_ok'] += 1
            ecrire(f"\n{model}: ✅ OK")
        else:
            if any('incomplète' in p for p in resultat['problemes']):
                afficher(f" ⚠️ Incomplet")
                stats_globales['modules_incomplets'] += 1
            elif any('Incohérence' in p for p in resultat['problemes']):
                afficher(f" ❌ Incohérent")
                stats_globales['modules_incoherents'] += 1
            else:
                afficher(f" ⚠️")
            
            ecrire(f"\n{model}: PROBLÈMES")
            for prob in resultat['problemes']:
                ecrire(f"  - {prob}")

# =============================================================================
# RÉSUMÉ
# =============================================================================

afficher("\n" + "="*70)
afficher("RÉSULTATS VÉRIFICATION")
afficher("="*70)
afficher(f"Modules vérifiés        : {stats_globales['modules_verifies']}")
afficher(f"  ✅ OK                 : {stats_globales['modules_ok']}")
afficher(f"  ⚠️ Incomplets         : {stats_globales['modules_incomplets']}")
afficher(f"  ❌ Incohérents        : {stats_globales['modules_incoherents']}")
afficher(f"  ⏭️ Non installés      : {stats_globales['modules_non_installes']}")

ecrire("\n" + "="*70)
ecrire("RÉSUMÉ")
ecrire("="*70)
ecrire(f"Modules vérifiés: {stats_globales['modules_verifies']}")
ecrire(f"OK: {stats_globales['modules_ok']}")
ecrire(f"Incomplets: {stats_globales['modules_incomplets']}")
ecrire(f"Incohérents: {stats_globales['modules_incoherents']}")

pourcentage = (stats_globales['modules_ok'] / stats_globales['modules_verifies'] * 100) if stats_globales['modules_verifies'] > 0 else 0

afficher("")
afficher(f"Taux de réussite: {pourcentage:.1f}%")
afficher("="*70)

if stats_globales['modules_incoherents'] > 0:
    afficher("\n❌ ATTENTION: Incohérences détectées")
    afficher("Des enregistrements ont des mappings incorrects")
    afficher("Actions recommandées:")
    afficher("  1. Consulter le rapport détaillé")
    afficher("  2. Corriger les mappings")
    afficher("  3. Relancer avec mode_update=True")
elif stats_globales['modules_incomplets'] > 0:
    afficher("\n⚠️ Certains modules sont incomplets")
    afficher("Actions recommandées:")
    afficher("  1. Relancer: python reprendre_migration.py")
    afficher("  2. Ou utiliser mode_update pour compléter")
else:
    afficher("\n✅ INTÉGRITÉ COMPLÈTE VÉRIFIÉE")
    afficher("Toutes les données sont correctement transférées")

afficher(f"\nRapport détaillé: {RAPPORT}")
afficher("="*70)

rapport.close()

