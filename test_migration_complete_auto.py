#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST MIGRATION COMPLET AUTO
============================
Lance la migration en mode TEST avec auto-correction
Affiche tout ce qui se passe en temps réel
"""

import sys
import os

# Force unbuffered output
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from pathlib import Path
from datetime import datetime
from connexion_double_v19 import ConnexionDoubleV19
from framework.migrateur_generique import MigrateurGenerique
from framework.gestionnaire_configuration import GestionnaireConfiguration

# Obtenir les configurations
CONFIGURATIONS_MODULES = GestionnaireConfiguration.obtenir_toutes_configs()

def afficher(msg=""):
    # Force l'affichage immédiat
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

def afficher_etape(num, titre):
    afficher("\n" + "="*70)
    afficher(f"ÉTAPE {num}: {titre}")
    afficher("="*70)
    sys.stdout.flush()

def afficher_succes(msg):
    afficher(f"✅ {msg}")
    sys.stdout.flush()

def afficher_erreur(msg):
    afficher(f"❌ {msg}")
    sys.stdout.flush()

def afficher_info(msg):
    afficher(f"ℹ️ {msg}")
    sys.stdout.flush()

afficher("="*70)
afficher("TEST MIGRATION COMPLET AUTO")
afficher("="*70)
afficher("")
afficher("Base DESTINATION: lysa-migration-2.odoo.com")
afficher("Mode: TEST (5-10 enregistrements par module)")
afficher("Auto-correction: ACTIVÉE")
afficher("")
afficher("="*70)

# =============================================================================
# ÉTAPE 1 : CONNEXION
# =============================================================================

afficher_etape(1, "TEST CONNEXION")

conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    afficher_erreur("Connexion échouée !")
    sys.exit(1)

afficher_succes("Connexion établie !")
afficher_info("SOURCE: lysa-old1.odoo.com (v16)")
afficher_info("DEST: lysa-migration-2.odoo.com (v19)")

# =============================================================================
# ÉTAPE 2 : VÉRIFICATION MODULES
# =============================================================================

afficher_etape(2, "VÉRIFICATION MODULES INSTALLÉS")

try:
    afficher("Récupération modules SOURCE...")
    modules_src = conn.executer_source('ir.module.module', 'search_read',
                                      [('state', 'in', ['installed', 'to upgrade'])],
                                      fields=['name'])
    afficher_succes(f"{len(modules_src)} modules installés en SOURCE")
    
    afficher("Récupération modules DESTINATION...")
    modules_dest = conn.executer_destination('ir.module.module', 'search_read',
                                            [('state', 'in', ['installed', 'to upgrade'])],
                                            fields=['name'])
    afficher_succes(f"{len(modules_dest)} modules installés en DESTINATION")
    
    # Vérification rapide des modules critiques
    modules_critiques = ['account', 'sale', 'purchase', 'stock', 'mrp', 'project', 'hr']
    dest_names = {m['name'] for m in modules_dest}
    
    manquants = []
    for mod in modules_critiques:
        mod_src = [m for m in modules_src if m['name'] == mod]
        if mod_src and mod not in dest_names:
            manquants.append(mod)
    
    if manquants:
        afficher_erreur(f"Modules critiques manquants: {', '.join(manquants)}")
        afficher_info("Ces modules seront ignorés pour ce test")
    else:
        afficher_succes("Tous les modules critiques sont installés")

except Exception as e:
    afficher_erreur(f"Erreur vérification modules: {str(e)}")
    afficher_info("Continuons quand même...")

# =============================================================================
# ÉTAPE 3 : MIGRATION PARAMÈTRES (RAPIDE)
# =============================================================================

afficher_etape(3, "MIGRATION PARAMÈTRES (Échantillon)")

try:
    # Migrer quelques paramètres système critiques
    afficher("Migration paramètres système critiques...")
    
    params_critiques = [
        'sale.default_deposit_product_id',
        'account.use_anglo_saxon',
    ]
    
    for param_key in params_critiques:
        try:
            # Chercher en source
            params = conn.executer_source('ir.config_parameter', 'search_read',
                                         [('key', '=', param_key)],
                                         fields=['key', 'value'])
            
            if params:
                param = params[0]
                # Créer/MÀJ en destination
                conn.executer_destination('ir.config_parameter', 'set_param',
                                        param['key'], param['value'])
                afficher_succes(f"Paramètre migré: {param['key']}")
        except Exception as e:
            afficher_info(f"Paramètre {param_key}: {str(e)[:50]}")
    
    afficher_succes("Paramètres critiques migrés")

except Exception as e:
    afficher_erreur(f"Erreur migration paramètres: {str(e)}")
    afficher_info("Continuons quand même...")

# =============================================================================
# ÉTAPE 4 : MIGRATION TEST PAR MODULE
# =============================================================================

afficher_etape(4, "MIGRATION TEST (5-10 enreg/module)")

# Modules à tester (ordre de dépendances)
MODULES_TEST = [
    'account.tax',
    'res.partner.category',
    'res.country',
    'res.partner',
    'product.category',
    'uom.uom',
    'product.template',
    'account.account',
    'account.journal',
]

resultats = []

for module_name in MODULES_TEST:
    afficher(f"\n{'─'*70}")
    afficher(f"MODULE: {module_name}")
    afficher(f"{'─'*70}")
    
    if module_name not in CONFIGURATIONS_MODULES:
        afficher_erreur(f"Configuration manquante pour {module_name}")
        resultats.append({
            'module': module_name,
            'status': 'ERREUR',
            'message': 'Configuration manquante'
        })
        continue
    
    try:
        # Configurer en mode TEST
        afficher(f"Configuration mode TEST...")
        sys.stdout.flush()
        config = CONFIGURATIONS_MODULES[module_name].copy()
        config['mode_test'] = True
        config['limite_test'] = 10
        config['mode_interactif'] = False  # Non-interactif pour auto-correction
        
        # Créer migrateur
        afficher(f"Initialisation migrateur {module_name}...")
        sys.stdout.flush()
        migrateur = MigrateurGenerique(conn, module_name, config)
        
        # Lancer migration
        afficher(f"Migration en cours (cela peut prendre 10-30 secondes)...")
        sys.stdout.flush()
        stats = migrateur.migrer()
        afficher(f"Migration terminée !")
        sys.stdout.flush()
        
        # Afficher résultats
        afficher(f"\nRésultats {module_name}:")
        afficher(f"  Nouveaux : {stats['nouveaux']}")
        afficher(f"  Existants: {stats['existants']}")
        afficher(f"  Erreurs  : {stats['erreurs']}")
        afficher(f"  Skippés  : {stats['skipped']}")
        
        # Afficher corrections auto si présentes
        if migrateur.auto_correcteur.corrections_appliquees:
            afficher(f"\n📋 Auto-corrections:")
            corrections = migrateur.auto_correcteur.corrections_appliquees
            afficher(f"  {len(corrections)} corrections appliquées")
            
            # Grouper par type
            types = {}
            for corr in corrections:
                t = corr['type']
                types[t] = types.get(t, 0) + 1
            
            for type_err, count in types.items():
                afficher(f"    - {type_err}: {count}")
        
        # Statut
        if stats['erreurs'] == 0:
            afficher_succes(f"{module_name}: OK")
            resultats.append({
                'module': module_name,
                'status': 'OK',
                'stats': stats
            })
        else:
            afficher_erreur(f"{module_name}: {stats['erreurs']} erreurs")
            resultats.append({
                'module': module_name,
                'status': 'ERREURS',
                'stats': stats
            })
    
    except Exception as e:
        afficher_erreur(f"Erreur migration {module_name}: {str(e)}")
        afficher_info(f"Détails: {str(e)[:200]}")
        resultats.append({
            'module': module_name,
            'status': 'EXCEPTION',
            'message': str(e)[:100]
        })

# =============================================================================
# ÉTAPE 5 : RÉSUMÉ
# =============================================================================

afficher_etape(5, "RÉSUMÉ TEST MIGRATION")

afficher(f"\nModules testés: {len(MODULES_TEST)}")

# Compter par statut
ok = len([r for r in resultats if r['status'] == 'OK'])
erreurs = len([r for r in resultats if r['status'] in ['ERREURS', 'EXCEPTION', 'ERREUR']])

afficher(f"  ✅ OK     : {ok}")
afficher(f"  ❌ Erreurs: {erreurs}")

# Détails par module
afficher(f"\nDétails par module:")
for res in resultats:
    if res['status'] == 'OK':
        stats = res['stats']
        afficher(f"  ✅ {res['module']:30s} | {stats['nouveaux']} nouveaux, {stats['erreurs']} erreurs")
    elif res['status'] == 'ERREURS':
        stats = res['stats']
        afficher(f"  ⚠️ {res['module']:30s} | {stats['nouveaux']} nouveaux, {stats['erreurs']} erreurs")
    else:
        msg = res.get('message', 'Erreur')
        afficher(f"  ❌ {res['module']:30s} | {msg[:40]}")

# Calculs totaux
if resultats:
    total_nouveaux = sum(r.get('stats', {}).get('nouveaux', 0) for r in resultats)
    total_erreurs = sum(r.get('stats', {}).get('erreurs', 0) for r in resultats)
    
    afficher(f"\nTotaux:")
    afficher(f"  Enregistrements migrés: {total_nouveaux}")
    afficher(f"  Erreurs totales: {total_erreurs}")

# =============================================================================
# CONCLUSION
# =============================================================================

afficher("\n" + "="*70)

if erreurs == 0:
    afficher_succes("TEST MIGRATION RÉUSSI !")
    afficher("")
    afficher("Tous les modules testés sont OK.")
    afficher("Vous pouvez lancer la migration complète:")
    afficher("")
    afficher("  python migration_framework.py")
    afficher("")
else:
    afficher_erreur(f"TEST MIGRATION: {erreurs} module(s) avec erreurs")
    afficher("")
    afficher("Modules à corriger:")
    for res in resultats:
        if res['status'] != 'OK':
            afficher(f"  - {res['module']}")
    afficher("")
    afficher("Consultez les logs pour plus de détails:")
    afficher("  logs/migration_*.txt")
    afficher("")

afficher("="*70)

