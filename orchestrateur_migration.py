#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ORCHESTRATEUR DE MIGRATION COMPLÈTE
====================================
Gère la migration complète v16 → v19 avec vérifications
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
import subprocess

# Forcer sortie immédiate
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

LOGS_DIR = Path('logs')
LOGS_DIR.mkdir(exist_ok=True)

# =============================================================================
# CONFIGURATION DES MODULES
# =============================================================================

MODULES_BASE = [
    {
        'phase': '1. Comptabilité',
        'modules': [
            {'script': 'migrer_taxes.py', 'nom': 'Taxes', 'total_attendu': 31},
            {'script': 'migrer_plans_analytiques.py', 'nom': 'Plans analytiques', 'total_attendu': 2},
            {'script': 'migrer_comptes_analytiques.py', 'nom': 'Comptes analytiques', 'total_attendu': 15},
        ]
    },
    {
        'phase': '2. Partenaires',
        'modules': [
            {'script': 'migrer_etiquettes_contact.py', 'nom': 'Étiquettes contact', 'total_attendu': 16},
            {'script': 'migrer_comptes_bancaires.py', 'nom': 'Comptes bancaires', 'total_attendu': 1},
        ]
    },
    {
        'phase': '3. Produits',
        'modules': [
            {'script': 'migrer_listes_prix.py', 'nom': 'Listes de prix', 'total_attendu': 57},
        ]
    },
    {
        'phase': '4. Stock',
        'modules': [
            {'script': 'migrer_emplacements.py', 'nom': 'Emplacements', 'total_attendu': 83},
            {'script': 'migrer_types_operations.py', 'nom': 'Types opérations', 'total_attendu': 133},
        ]
    },
    {
        'phase': '5. Ventes',
        'modules': [
            {'script': 'migrer_equipes_commerciales.py', 'nom': 'Équipes commerciales', 'total_attendu': 40},
        ]
    },
    {
        'phase': '6. Projets',
        'modules': [
            {'script': 'migrer_projets.py', 'nom': 'Projets', 'total_attendu': 9},
        ]
    }
]

# =============================================================================
# FONCTIONS
# =============================================================================

def afficher(msg, niveau='INFO'):
    """Affiche un message avec horodatage"""
    timestamp = datetime.now().strftime('%H:%M:%S')
    prefix = {
        'INFO': '   ',
        'OK': ' ✓ ',
        'WARN': ' ⚠ ',
        'ERROR': ' ✗ '
    }.get(niveau, '   ')
    print(f"[{timestamp}] {prefix} {msg}")
    sys.stdout.flush()

def executer_script(script_path):
    """
    Exécute un script Python et retourne le code de sortie
    """
    if not Path(script_path).exists():
        afficher(f"Script introuvable: {script_path}", 'ERROR')
        return False
    
    try:
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes max
        )
        
        # Afficher la sortie
        if result.stdout:
            print(result.stdout)
        
        if result.returncode != 0:
            if result.stderr:
                print(result.stderr)
            return False
        
        return True
        
    except subprocess.TimeoutExpired:
        afficher(f"Timeout: {script_path}", 'ERROR')
        return False
    except Exception as e:
        afficher(f"Erreur execution: {str(e)}", 'ERROR')
        return False

def verifier_mapping(nom_fichier, total_attendu):
    """
    Vérifie qu'un mapping est complet
    """
    mapping_file = LOGS_DIR / f'{nom_fichier}_mapping.json'
    
    if not mapping_file.exists():
        afficher(f"Mapping introuvable: {nom_fichier}", 'WARN')
        return False, 0
    
    try:
        with open(mapping_file, 'r') as f:
            mapping = json.load(f)
        
        total = len(mapping)
        pourcentage = (total / total_attendu * 100) if total_attendu > 0 else 0
        
        if total >= total_attendu:
            afficher(f"Mapping OK: {total}/{total_attendu} ({pourcentage:.0f}%)", 'OK')
            return True, total
        else:
            afficher(f"Mapping incomplet: {total}/{total_attendu} ({pourcentage:.0f}%)", 'WARN')
            return False, total
            
    except Exception as e:
        afficher(f"Erreur lecture mapping: {str(e)}", 'ERROR')
        return False, 0

# =============================================================================
# PROGRAMME PRINCIPAL
# =============================================================================

def main():
    afficher("="*70)
    afficher("ORCHESTRATEUR DE MIGRATION ODOO v16 → v19")
    afficher("="*70)
    afficher(f"Debut: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    afficher("")
    
    # Statistiques globales
    stats = {
        'phases_ok': 0,
        'phases_erreur': 0,
        'modules_ok': 0,
        'modules_erreur': 0,
        'modules_skip': 0
    }
    
    # Parcourir toutes les phases
    for phase_config in MODULES_BASE:
        phase_nom = phase_config['phase']
        
        afficher("")
        afficher("="*70)
        afficher(f"PHASE: {phase_nom}")
        afficher("="*70)
        
        phase_ok = True
        
        # Parcourir les modules de cette phase
        for module in phase_config['modules']:
            script = module['script']
            nom = module['nom']
            total_attendu = module.get('total_attendu', 0)
            
            afficher("")
            afficher(f"Module: {nom}")
            afficher(f"Script: {script}")
            
            # Vérifier si le script existe
            if not Path(script).exists():
                afficher("Script introuvable - SKIP", 'WARN')
                stats['modules_skip'] += 1
                continue
            
            # Exécuter le script
            afficher("Execution en cours...")
            succes = executer_script(script)
            
            if not succes:
                afficher(f"Echec: {nom}", 'ERROR')
                stats['modules_erreur'] += 1
                phase_ok = False
                
                # Demander si on continue
                reponse = input("\nContinuer malgre l'erreur ? (o/N): ").strip().lower()
                if reponse != 'o':
                    afficher("Migration interrompue par l'utilisateur", 'WARN')
                    return 1
                continue
            
            # Vérifier le mapping
            # Extraire le nom du fichier mapping depuis le script
            nom_fichier = script.replace('migrer_', '').replace('.py', '')
            mapping_ok, total = verifier_mapping(nom_fichier, total_attendu)
            
            if mapping_ok:
                afficher(f"Module OK: {nom}", 'OK')
                stats['modules_ok'] += 1
            else:
                afficher(f"Module incomplet: {nom}", 'WARN')
                stats['modules_erreur'] += 1
                phase_ok = False
        
        # Résumé de la phase
        if phase_ok:
            afficher(f"\nPhase OK: {phase_nom}", 'OK')
            stats['phases_ok'] += 1
        else:
            afficher(f"\nPhase avec erreurs: {phase_nom}", 'WARN')
            stats['phases_erreur'] += 1
    
    # ==========================================================================
    # RÉSUMÉ FINAL
    # ==========================================================================
    
    afficher("")
    afficher("="*70)
    afficher("MIGRATION TERMINÉE")
    afficher("="*70)
    afficher(f"Phases OK        : {stats['phases_ok']}")
    afficher(f"Phases erreurs   : {stats['phases_erreur']}")
    afficher(f"Modules OK       : {stats['modules_ok']}")
    afficher(f"Modules erreurs  : {stats['modules_erreur']}")
    afficher(f"Modules skippés  : {stats['modules_skip']}")
    afficher("="*70)
    afficher(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if stats['modules_erreur'] > 0 or stats['phases_erreur'] > 0:
        afficher("\nATTENTION: Des erreurs ont été détectées", 'WARN')
        return 1
    else:
        afficher("\nSUCCÈS: Tous les modules de base sont migrés !", 'OK')
        afficher("\nÉTAPE SUIVANTE: Migration des transactions", 'INFO')
        return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        afficher("\n\nMigration interrompue par l'utilisateur", 'WARN')
        sys.exit(1)
    except Exception as e:
        afficher(f"\n\nErreur fatale: {str(e)}", 'ERROR')
        sys.exit(1)

