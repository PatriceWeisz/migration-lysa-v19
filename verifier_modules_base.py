#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VÉRIFICATION DES MODULES DE BASE
=================================
Vérifie quels modules de base sont déjà migrés
"""

import sys
import os
from pathlib import Path

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

def verifier_module(conn, model, nom):
    """Vérifie un module"""
    try:
        count_src = conn.executer_source(model, 'search_count', [])
        count_dst = conn.executer_destination(model, 'search_count', [])
        
        if count_dst >= count_src:
            status = "OK COMPLET"
            pct = 100.0
        else:
            status = f"MANQUE {count_src - count_dst}"
            pct = (count_dst / count_src * 100) if count_src > 0 else 0
        
        afficher(f"  {nom:35s} : {count_dst:>5,d}/{count_src:>5,d} ({pct:>5.1f}%) - {status}")
        
        return count_src, count_dst, status
        
    except Exception as e:
        afficher(f"  {nom:35s} : ERREUR - {str(e)[:40]}")
        return 0, 0, "ERREUR"

afficher("="*70)
afficher("VERIFICATION MODULES DE BASE")
afficher("="*70)

conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    afficher("ERREUR Connexion")
    sys.exit(1)

afficher("OK Connexion\n")

modules_incomplets = []

# Phase 1 : Comptabilité
afficher("="*70)
afficher("PHASE 1 : COMPTABILITE DE BASE")
afficher("="*70)

src, dst, status = verifier_module(conn, 'account.account', 'Plan comptable')
if "MANQUE" in status:
    modules_incomplets.append(('account.account', 'Plan comptable', src - dst))

verifier_module(conn, 'account.tax', 'Taxes')
verifier_module(conn, 'account.fiscal.position', 'Positions fiscales')
verifier_module(conn, 'account.payment.term', 'Conditions paiement')
verifier_module(conn, 'account.journal', 'Journaux')

# Analytique
afficher("\n" + "="*70)
afficher("COMPTABILITE ANALYTIQUE")
afficher("="*70)
verifier_module(conn, 'account.analytic.plan', 'Plans analytiques')
verifier_module(conn, 'account.analytic.account', 'Comptes analytiques')
verifier_module(conn, 'account.budget.post', 'Postes budgetaires')

# Partenaires
afficher("\n" + "="*70)
afficher("PHASE 2 : PARTENAIRES")
afficher("="*70)
verifier_module(conn, 'res.partner', 'Partenaires')
verifier_module(conn, 'res.partner.category', 'Etiquettes contact')
verifier_module(conn, 'res.partner.industry', 'Secteurs activite')
verifier_module(conn, 'res.partner.title', 'Titres')
verifier_module(conn, 'res.bank', 'Banques')
verifier_module(conn, 'res.partner.bank', 'Comptes bancaires')

# Produits
afficher("\n" + "="*70)
afficher("PHASE 3 : PRODUITS")
afficher("="*70)
verifier_module(conn, 'product.category', 'Categories produits')
verifier_module(conn, 'uom.category', 'Categories unites')
verifier_module(conn, 'uom.uom', 'Unites de mesure')
verifier_module(conn, 'product.template', 'Modeles produits')

# RH
afficher("\n" + "="*70)
afficher("PHASE 4 : RESSOURCES HUMAINES")
afficher("="*70)
verifier_module(conn, 'res.users', 'Utilisateurs')
verifier_module(conn, 'hr.department', 'Departements')
verifier_module(conn, 'hr.job', 'Postes/Fonctions')
verifier_module(conn, 'hr.employee', 'Employes')
verifier_module(conn, 'hr.leave.type', 'Types conges')

# Stock
afficher("\n" + "="*70)
afficher("PHASE 5 : STOCK")
afficher("="*70)
verifier_module(conn, 'stock.location', 'Emplacements')
verifier_module(conn, 'stock.warehouse', 'Entrepots')
verifier_module(conn, 'stock.picking.type', 'Types operations')

# Ventes
afficher("\n" + "="*70)
afficher("PHASE 6 : VENTES (Config)")
afficher("="*70)
verifier_module(conn, 'product.pricelist', 'Listes de prix')
verifier_module(conn, 'crm.team', 'Equipes commerciales')
verifier_module(conn, 'crm.stage', 'Etapes CRM')

# Projets
afficher("\n" + "="*70)
afficher("PHASE 7 : PROJETS")
afficher("="*70)
verifier_module(conn, 'project.project', 'Projets')
verifier_module(conn, 'project.task.type', 'Etapes taches')

afficher("\n" + "="*70)
afficher("MODULES A COMPLETER")
afficher("="*70)

if modules_incomplets:
    for model, nom, manque in modules_incomplets:
        afficher(f"  {nom:35s} : {manque:>5,d} manquants")
else:
    afficher("  TOUS les modules de base sont complets !")

afficher("="*70)

