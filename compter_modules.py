#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COMPTAGE DES MODULES À MIGRER
==============================
Compte les enregistrements dans chaque module pour estimer la durée
"""

import sys
import os
from datetime import datetime

# Forcer affichage
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

def compter_module(conn, model, nom, domain=None):
    """Compte les enregistrements d'un module"""
    try:
        count = conn.executer_source(model, 'search_count', domain or [])
        afficher(f"  {nom:35s} : {count:>8,d} enregistrements")
        return count
    except Exception as e:
        afficher(f"  {nom:35s} : ERREUR - {str(e)[:40]}")
        return 0

def main():
    afficher("="*70)
    afficher("COMPTAGE DES MODULES SOURCE")
    afficher("="*70)
    afficher(f"Debut: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Connexion
    afficher("Connexion...")
    conn = ConnexionDoubleV19()
    
    if not conn.connecter_tout():
        afficher("ERREUR: Connexion echouee")
        return False
    
    afficher("OK\n")
    
    total = 0
    
    # Phase 1 : Données de base
    afficher("="*70)
    afficher("PHASE 1 : DONNEES DE BASE COMPTABLES")
    afficher("="*70)
    total += compter_module(conn, 'account.account', 'Plan comptable')
    total += compter_module(conn, 'account.tax', 'Taxes')
    total += compter_module(conn, 'account.fiscal.position', 'Positions fiscales')
    total += compter_module(conn, 'account.payment.term', 'Conditions de paiement')
    total += compter_module(conn, 'account.journal', 'Journaux')
    
    # Comptabilité analytique
    afficher("\n" + "="*70)
    afficher("PHASE 1bis : COMPTABILITE ANALYTIQUE")
    afficher("="*70)
    total += compter_module(conn, 'account.analytic.plan', 'Plans analytiques')
    total += compter_module(conn, 'account.analytic.account', 'Comptes analytiques')
    total += compter_module(conn, 'account.analytic.line', 'Lignes analytiques')
    total += compter_module(conn, 'crossovered.budget', 'Budgets')
    total += compter_module(conn, 'crossovered.budget.lines', 'Lignes budgetaires')
    total += compter_module(conn, 'account.budget.post', 'Postes budgetaires')
    
    # Partenaires et données associées
    afficher("\n" + "="*70)
    afficher("PHASE 1ter : PARTENAIRES ET CONTACTS")
    afficher("="*70)
    total += compter_module(conn, 'res.partner', 'Partenaires')
    total += compter_module(conn, 'res.partner.category', 'Etiquettes de contact')
    total += compter_module(conn, 'res.partner.industry', 'Secteurs activite')
    total += compter_module(conn, 'res.partner.title', 'Titres (M., Mme...)')
    total += compter_module(conn, 'res.bank', 'Banques')
    total += compter_module(conn, 'res.partner.bank', 'Comptes bancaires')
    
    # Produits et unités
    afficher("\n" + "="*70)
    afficher("PHASE 1quater : PRODUITS ET UNITES")
    afficher("="*70)
    total += compter_module(conn, 'product.category', 'Categories produits')
    total += compter_module(conn, 'uom.category', 'Categories unites mesure')
    total += compter_module(conn, 'uom.uom', 'Unites de mesure')
    
    # Phase 2 : RH
    afficher("\n" + "="*70)
    afficher("PHASE 2 : RESSOURCES HUMAINES")
    afficher("="*70)
    total += compter_module(conn, 'res.users', 'Utilisateurs', [('id', '!=', 1)])
    total += compter_module(conn, 'hr.department', 'Departements')
    total += compter_module(conn, 'hr.job', 'Postes/Fonctions')
    total += compter_module(conn, 'hr.employee', 'Employes')
    total += compter_module(conn, 'hr.appraisal', 'Evaluations employes')
    total += compter_module(conn, 'hr.expense', 'Notes de frais')
    total += compter_module(conn, 'hr.leave.type', 'Types de conges')
    total += compter_module(conn, 'hr.leave.allocation', 'Allocations de conges')
    total += compter_module(conn, 'hr.leave', 'Demandes de conges')
    
    # Phase 2bis : Projets et Tâches
    afficher("\n" + "="*70)
    afficher("PHASE 2bis : PROJETS ET TACHES")
    afficher("="*70)
    total += compter_module(conn, 'project.project', 'Projets')
    total += compter_module(conn, 'project.task', 'Taches')
    total += compter_module(conn, 'project.task.type', 'Etapes de taches')
    total += compter_module(conn, 'project.tags', 'Tags de projets')
    
    # Phase 2ter : Activités et Agenda
    afficher("\n" + "="*70)
    afficher("PHASE 2ter : ACTIVITES ET AGENDA")
    afficher("="*70)
    total += compter_module(conn, 'mail.activity', 'Activites planifiees')
    total += compter_module(conn, 'mail.activity.type', 'Types activites')
    total += compter_module(conn, 'calendar.event', 'Evenements agenda')
    total += compter_module(conn, 'calendar.event.type', 'Types evenements')
    
    # Phase 3 : Stock
    afficher("\n" + "="*70)
    afficher("PHASE 3 : STOCK ET ENTREPOTS")
    afficher("="*70)
    total += compter_module(conn, 'stock.location', 'Emplacements stock')
    total += compter_module(conn, 'stock.warehouse', 'Entrepots')
    total += compter_module(conn, 'stock.route', 'Routes stock')
    total += compter_module(conn, 'stock.picking.type', 'Types operations stock')
    
    # Phase 4 : Produits
    afficher("\n" + "="*70)
    afficher("PHASE 4 : PRODUITS")
    afficher("="*70)
    total += compter_module(conn, 'product.template', 'Modeles produits')
    total += compter_module(conn, 'product.product', 'Variantes produits')
    
    # Phase 5 : Fabrication
    afficher("\n" + "="*70)
    afficher("PHASE 5 : FABRICATION")
    afficher("="*70)
    total += compter_module(conn, 'mrp.bom', 'Nomenclatures (BOM)')
    total += compter_module(conn, 'mrp.bom.line', 'Lignes nomenclature')
    total += compter_module(conn, 'mrp.workcenter', 'Centres de travail')
    total += compter_module(conn, 'mrp.routing', 'Gammes fabrication')
    total += compter_module(conn, 'mrp.production', 'Ordres de fabrication')
    total += compter_module(conn, 'mrp.workorder', 'Ordres de travail')
    
    # Phase 6 : CRM et Ventes
    afficher("\n" + "="*70)
    afficher("PHASE 6 : CRM ET VENTES")
    afficher("="*70)
    total += compter_module(conn, 'product.pricelist', 'Listes de prix')
    total += compter_module(conn, 'product.pricelist.item', 'Regles listes de prix')
    total += compter_module(conn, 'crm.team', 'Equipes commerciales')
    total += compter_module(conn, 'crm.stage', 'Etapes CRM')
    total += compter_module(conn, 'crm.lead', 'Pistes/Opportunites')
    total += compter_module(conn, 'sale.order.template', 'Modeles de devis')
    total += compter_module(conn, 'sale.order', 'Commandes de vente')
    total += compter_module(conn, 'sale.order.line', 'Lignes commandes vente')
    
    # Phase 7 : Achats
    afficher("\n" + "="*70)
    afficher("PHASE 7 : ACHATS")
    afficher("="*70)
    total += compter_module(conn, 'purchase.order', 'Commandes achat')
    total += compter_module(conn, 'purchase.order.line', 'Lignes commandes achat')
    
    # Phase 8 : Mouvements de stock
    afficher("\n" + "="*70)
    afficher("PHASE 8 : MOUVEMENTS DE STOCK")
    afficher("="*70)
    total += compter_module(conn, 'stock.picking', 'Transferts stock')
    total += compter_module(conn, 'stock.move', 'Mouvements stock')
    total += compter_module(conn, 'stock.move.line', 'Lignes mouvement stock')
    
    # Phase 9 : Factures
    afficher("\n" + "="*70)
    afficher("PHASE 9 : FACTURES ET COMPTABILITE")
    afficher("="*70)
    total += compter_module(conn, 'account.asset', 'Immobilisations')
    total += compter_module(conn, 'account.asset.category', 'Categories immobilisations')
    total += compter_module(conn, 'account.move', 'Factures/Ecritures', [('state', '=', 'posted')])
    total += compter_module(conn, 'account.move.line', 'Lignes ecriture')
    total += compter_module(conn, 'account.payment', 'Paiements')
    
    # Phase 10 : Rapprochements
    afficher("\n" + "="*70)
    afficher("PHASE 10 : RAPPROCHEMENTS")
    afficher("="*70)
    total += compter_module(conn, 'account.partial.reconcile', 'Rapprochements partiels')
    total += compter_module(conn, 'account.full.reconcile', 'Rapprochements complets')
    
    # Phase 11 : Paramétrages Système
    afficher("\n" + "="*70)
    afficher("PHASE 11 : PARAMETRAGES SYSTEME")
    afficher("="*70)
    total += compter_module(conn, 'ir.sequence', 'Sequences numerotation')
    total += compter_module(conn, 'ir.sequence.date_range', 'Sequences par date')
    total += compter_module(conn, 'mail.template', 'Modeles emails')
    total += compter_module(conn, 'base.automation', 'Regles automatiques')
    total += compter_module(conn, 'ir.cron', 'Taches planifiees')
    total += compter_module(conn, 'ir.rule', 'Regles enregistrement')
    total += compter_module(conn, 'ir.filters', 'Filtres sauvegardes')
    total += compter_module(conn, 'ir.actions.server', 'Actions serveur')
    total += compter_module(conn, 'ir.actions.report', 'Rapports personnalises')
    total += compter_module(conn, 'ir.model.fields', 'Champs personnalises', [('state', '=', 'manual')])
    total += compter_module(conn, 'ir.ui.view', 'Vues personnalisees', [('type', '=', 'form')])
    total += compter_module(conn, 'ir.ui.menu', 'Menus personnalises')
    
    # Résumé
    afficher("\n" + "="*70)
    afficher("RESUME TOTAL")
    afficher("="*70)
    afficher(f"Total enregistrements : {total:,d}")
    afficher(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    afficher("="*70)
    
    return True

if __name__ == "__main__":
    main()

