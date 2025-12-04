#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
REPRENDRE MIGRATION INTERROMPUE
================================
Reprend une migration là où elle s'est arrêtée
Vérifie l'intégrité avant de continuer
"""

import sys
import os

print("="*70, flush=True)
print("REPRISE MIGRATION - DEMARRAGE", flush=True)
print("="*70, flush=True)
print("Import...", flush=True)

from datetime import datetime

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19
from framework.migrateur_generique import MigrateurGenerique
from framework.gestionnaire_configuration import GestionnaireConfiguration
from framework.gestionnaire_reprise import GestionnaireReprise, VerificateurIntegrite

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

afficher("\nOK - Modules charges")
afficher("="*70)
afficher("REPRISE DE MIGRATION")
afficher("="*70)
afficher(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Connexion
afficher("Connexion...")
conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    afficher("ERREUR Connexion")
    sys.exit(1)

afficher("OK Connexion\n")

# =============================================================================
# VÉRIFIER L'ÉTAT
# =============================================================================

gestionnaire = GestionnaireReprise()
gestionnaire.afficher_etat()

if not gestionnaire.checkpoint['date_debut']:
    afficher("\n⚠️ Aucune migration en cours")
    afficher("Utilisez: python migration_framework.py")
    sys.exit(0)

# =============================================================================
# VÉRIFICATION D'INTÉGRITÉ
# =============================================================================

afficher("\n" + "="*70)
afficher("VÉRIFICATION D'INTÉGRITÉ DES MODULES TERMINÉS")
afficher("="*70)

verificateur = VerificateurIntegrite(conn)
modules_termines = gestionnaire.checkpoint['modules_termines']

if modules_termines:
    afficher(f"\nVérification de {len(modules_termines)} modules...\n")
    
    problemes_detectes = []
    
    for idx, module in enumerate(modules_termines, 1):
        config = GestionnaireConfiguration.obtenir_config_module(module)
        if not config:
            continue
        
        afficher(f"{idx}/{len(modules_termines)} - {module}...", end='')
        
        resultat = verificateur.verifier_module(module, config['fichier'])
        
        if resultat['ok']:
            afficher(" ✅")
        else:
            afficher(f" ❌ {len(resultat['problemes'])} problèmes")
            problemes_detectes.append(resultat)
            for prob in resultat['problemes']:
                afficher(f"    └─ {prob}")
    
    afficher("\n" + "="*70)
    if problemes_detectes:
        afficher(f"⚠️ {len(problemes_detectes)} modules avec problèmes d'intégrité")
        afficher("\nOptions:")
        afficher("  1. Continuer quand même (risqué)")
        afficher("  2. Corriger les problèmes d'abord")
        afficher("  3. Remigrer les modules problématiques")
        afficher("")
        
        reponse = input("Continuer ? (1/2/3): ").strip()
        if reponse != '1':
            afficher("Migration interrompue - Corrigez les problèmes")
            sys.exit(0)
    else:
        afficher("✅ TOUS les modules terminés sont intègres")
else:
    afficher("Aucun module terminé - Début de migration")

# =============================================================================
# OBTENIR LES MODULES RESTANTS
# =============================================================================

afficher("\n" + "="*70)
afficher("MODULES RESTANT À MIGRER")
afficher("="*70)

phases = GestionnaireConfiguration.obtenir_modules_par_phase()
tous_modules = []
for phase_modules in phases.values():
    tous_modules.extend(phase_modules)

modules_restants = gestionnaire.obtenir_modules_a_migrer(tous_modules)

afficher(f"\nModules restants: {len(modules_restants)}")
for m in modules_restants[:10]:
    config = GestionnaireConfiguration.obtenir_config_module(m)
    if config:
        afficher(f"  - {m:40s} ({config['nom']})")

if len(modules_restants) > 10:
    afficher(f"  ... et {len(modules_restants) - 10} autres")

if not modules_restants:
    afficher("\n✅ MIGRATION COMPLÈTE - Tous les modules sont migrés")
    sys.exit(0)

afficher(f"\n{len(modules_restants)} modules à migrer")
reponse = input("Continuer la migration ? (oui/NON): ").strip().lower()

if reponse != 'oui':
    afficher("Reprise annulée")
    sys.exit(0)

# =============================================================================
# REPRISE DE LA MIGRATION
# =============================================================================

afficher("\n" + "="*70)
afficher("REPRISE DE LA MIGRATION")
afficher("="*70)

for phase_nom, phase_modules in phases.items():
    # Skip les phases déjà complètes
    phase_restante = [m for m in phase_modules if m in modules_restants]
    
    if not phase_restante:
        continue
    
    afficher(f"\n{'='*70}")
    afficher(f"{phase_nom}")
    afficher(f"{'='*70}")
    
    for model in phase_restante:
        config = GestionnaireConfiguration.obtenir_config_module(model)
        
        if not config:
            afficher(f"\n{model}: CONFIG MANQUANTE - SKIP")
            continue
        
        # Marquer début
        gestionnaire.marquer_module_debut(model)
        
        try:
            migrateur = MigrateurGenerique(conn, model, config)
            stats = migrateur.migrer()
            
            # Marquer terminé
            gestionnaire.marquer_module_termine(model, stats)
            
        except KeyboardInterrupt:
            afficher("\n\n⚠️ MIGRATION INTERROMPUE PAR L'UTILISATEUR")
            afficher("État sauvegardé dans checkpoint")
            afficher("Relancez 'python reprendre_migration.py' pour continuer")
            sys.exit(0)
            
        except Exception as e:
            afficher(f"\nERREUR FATALE sur {model}: {str(e)[:80]}")
            gestionnaire.marquer_module_termine(model, {'nouveaux': 0, 'existants': 0, 'erreurs': 1})

# =============================================================================
# FIN
# =============================================================================

afficher("\n" + "="*70)
afficher("MIGRATION TERMINÉE")
afficher("="*70)
gestionnaire.afficher_etat()
afficher("\nProchaine étape: Vérification complète")
afficher("  python verifier_integrite_complete.py")

