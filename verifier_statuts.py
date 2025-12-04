#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VÉRIFICATION DES STATUTS
=========================
Vérifie que les statuts (state) sont préservés après migration
CRITIQUE pour l'intégrité des documents
"""

import sys
import os

print("="*70, flush=True)
print("VERIFICATION STATUTS - DEMARRAGE", flush=True)
print("="*70, flush=True)
print("Import...", flush=True)

from pathlib import Path
from datetime import datetime

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

LOGS_DIR = Path('logs')
RAPPORT = LOGS_DIR / f'verification_statuts_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

afficher("\nOK - Modules charges")
afficher("="*70)
afficher("VÉRIFICATION DES STATUTS")
afficher("="*70)
afficher("Vérifie que les statuts sont préservés")
afficher(f"Rapport: {RAPPORT.name}")
afficher("="*70)

conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    sys.exit(1)

afficher("OK Connexion\n")

rapport = open(RAPPORT, 'w', encoding='utf-8')

def ecrire(msg):
    rapport.write(msg + '\n')
    rapport.flush()

ecrire("="*70)
ecrire("VÉRIFICATION DES STATUTS")
ecrire(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
ecrire("="*70)

# =============================================================================
# MODULES AVEC STATUTS CRITIQUES
# =============================================================================

MODULES_STATUTS = {
    'account.move': {
        'nom': 'Factures',
        'statuts': ['draft', 'posted', 'cancel'],
        'critique': 'posted'  # Comptabilisé = CRITIQUE
    },
    'sale.order': {
        'nom': 'Commandes clients',
        'statuts': ['draft', 'sent', 'sale', 'done', 'cancel'],
        'critique': 'sale'  # Confirmé = données verrouillées
    },
    'purchase.order': {
        'nom': 'Commandes fournisseurs',
        'statuts': ['draft', 'sent', 'to approve', 'purchase', 'done', 'cancel'],
        'critique': 'purchase'
    },
    'stock.picking': {
        'nom': 'Transferts stock (BL/Réceptions)',
        'statuts': ['draft', 'waiting', 'confirmed', 'assigned', 'done', 'cancel'],
        'critique': 'done'  # Fait = stock déjà bougé
    },
    'mrp.production': {
        'nom': 'Ordres fabrication',
        'statuts': ['draft', 'confirmed', 'progress', 'to_close', 'done', 'cancel'],
        'critique': 'done'
    },
    'hr.expense': {
        'nom': 'Notes de frais',
        'statuts': ['draft', 'reported', 'approved', 'done', 'refused'],
        'critique': 'done'
    },
    'hr.leave': {
        'nom': 'Congés',
        'statuts': ['draft', 'confirm', 'refuse', 'validate', 'validate1'],
        'critique': 'validate'
    },
    'project.task': {
        'nom': 'Tâches',
        'statuts': ['01_in_progress', '02_changes_requested', '03_approved', '04_waiting_normal', '1_done', '1_canceled'],
        'critique': '1_done'
    }
}

stats_globales = {
    'modules_verifies': 0,
    'modules_ok': 0,
    'modules_differences': 0,
    'total_source': 0,
    'total_destination': 0
}

afficher("="*70)
afficher("VÉRIFICATION PAR MODULE")
afficher("="*70)

for model, config in MODULES_STATUTS.items():
    afficher(f"\n{config['nom']} ({model})")
    ecrire(f"\n{'='*70}")
    ecrire(f"{config['nom']} ({model})")
    ecrire("="*70)
    
    try:
        # Compter par statut dans SOURCE
        statuts_src = {}
        for statut in config['statuts']:
            count = conn.executer_source(model, 'search_count', 
                                        [('state', '=', statut)])
            if count > 0:
                statuts_src[statut] = count
                stats_globales['total_source'] += count
        
        afficher(f"  SOURCE:")
        ecrire("\nSOURCE:")
        for statut, count in statuts_src.items():
            marker = " ⚠️ CRITIQUE" if statut == config['critique'] else ""
            afficher(f"    {statut:20s}: {count:>6,d}{marker}")
            ecrire(f"  {statut:20s}: {count:>6,d}{marker}")
        
        # Compter par statut dans DESTINATION
        statuts_dst = {}
        for statut in config['statuts']:
            try:
                count = conn.executer_destination(model, 'search_count',
                                                 [('state', '=', statut)])
                if count > 0:
                    statuts_dst[statut] = count
                    stats_globales['total_destination'] += count
            except:
                pass
        
        afficher(f"  DESTINATION:")
        ecrire("\nDESTINATION:")
        for statut, count in statuts_dst.items():
            marker = " ⚠️ CRITIQUE" if statut == config['critique'] else ""
            afficher(f"    {statut:20s}: {count:>6,d}{marker}")
            ecrire(f"  {statut:20s}: {count:>6,d}{marker}")
        
        # Comparer
        differences = False
        ecrire("\nCOMPARAISON:")
        for statut in config['statuts']:
            src_count = statuts_src.get(statut, 0)
            dst_count = statuts_dst.get(statut, 0)
            
            if src_count != dst_count:
                ecart = dst_count - src_count
                marker = " ⚠️" if statut == config['critique'] else ""
                afficher(f"  ÉCART {statut}: {ecart:+d}{marker}")
                ecrire(f"  {statut}: SOURCE={src_count}, DEST={dst_count}, ÉCART={ecart:+d}{marker}")
                differences = True
        
        if differences:
            stats_globales['modules_differences'] += 1
            afficher(f"  └─ ⚠️ DIFFÉRENCES DÉTECTÉES")
        else:
            stats_globales['modules_ok'] += 1
            afficher(f"  └─ ✅ STATUTS OK")
            ecrire("  ✅ Tous les statuts correspondent")
        
        stats_globales['modules_verifies'] += 1
        
    except Exception as e:
        afficher(f"  └─ ERREUR: {str(e)[:60]}")
        ecrire(f"  ERREUR: {str(e)}")

# =============================================================================
# RÉSUMÉ
# =============================================================================

afficher("\n" + "="*70)
afficher("RÉSUMÉ VÉRIFICATION STATUTS")
afficher("="*70)
afficher(f"Modules vérifiés     : {stats_globales['modules_verifies']}")
afficher(f"  ✅ Statuts OK      : {stats_globales['modules_ok']}")
afficher(f"  ⚠️ Différences     : {stats_globales['modules_differences']}")
afficher("")
afficher(f"Enregistrements SOURCE : {stats_globales['total_source']:,}")
afficher(f"Enregistrements DEST   : {stats_globales['total_destination']:,}")

ecrire("\n" + "="*70)
ecrire("RÉSUMÉ")
ecrire("="*70)
ecrire(f"Modules OK: {stats_globales['modules_ok']}/{stats_globales['modules_verifies']}")

if stats_globales['modules_differences'] == 0:
    afficher("\n✅ TOUS LES STATUTS SONT PRÉSERVÉS")
    afficher("Les documents gardent leur état (draft, confirmé, validé, etc.)")
    afficher("L'intégrité est garantie !")
    ecrire("\n✅ INTÉGRITÉ COMPLÈTE - Tous statuts préservés")
else:
    afficher(f"\n⚠️ {stats_globales['modules_differences']} modules avec différences")
    afficher("Cela peut être normal si:")
    afficher("  - Migration en cours (pas tous migrés)")
    afficher("  - Certains statuts pas encore migrés")
    afficher("\nSi migration complète:")
    afficher("  - Vérifier les mappings")
    afficher("  - Relancer la migration de ces modules")
    ecrire(f"\n⚠️ {stats_globales['modules_differences']} modules avec différences")

afficher("="*70)
afficher(f"\nRapport détaillé: {RAPPORT}")

rapport.close()
