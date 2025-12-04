#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONFIGURATION UNIVERSELLE - TOUS LES MODULES ODOO
==================================================
Framework UNIVERSEL pour n'importe quelle base Odoo v16-17-18
TOUS les modules standards inclus
"""

def obtenir_modules_v19_nouveaux():
    """Modules nouveaux ou modifiés en v19"""
    return {
        # ======================================================================
        # NOUVEAUTÉS V19
        # ======================================================================
        'account.report': {'nom': 'Rapports comptables v19', 'fichier': 'account_report', 'unique': 'name', 'ordre': 160},
        'account.report.line': {'nom': 'Lignes rapports compta', 'fichier': 'account_report_line', 'unique': None, 'ordre': 162},
        'account.disallowed.expenses': {'nom': 'Dépenses non déductibles', 'fichier': 'disallowed_expenses', 'unique': None, 'ordre': 2480},
        'account.move.send': {'nom': 'Envoi factures v19', 'fichier': 'move_send', 'unique': None, 'ordre': 2485},
        'account.payment.method.line': {'nom': 'Méthodes paiement journal', 'fichier': 'payment_method_line', 'unique': None, 'ordre': 165},
        
        # WhatsApp (nouveau en v19)
        'whatsapp.template': {'nom': 'Templates WhatsApp', 'fichier': 'whatsapp_template', 'unique': 'name', 'ordre': 1150},
        'whatsapp.message': {'nom': 'Messages WhatsApp', 'fichier': 'whatsapp_message', 'unique': None, 'ordre': 2490},
        
        # Améliorations Documents v19
        'documents.share': {'nom': 'Partages documents', 'fichier': 'document_share', 'unique': None, 'ordre': 2495},
        'documents.workflow.rule': {'nom': 'Règles workflow docs', 'fichier': 'document_workflow', 'unique': 'name', 'ordre': 1155},
        
        # Améliorations Projets v19
        'project.milestone': {'nom': 'Jalons projets', 'fichier': 'milestone', 'unique': None, 'ordre': 2500},
        'project.collaborator': {'nom': 'Collaborateurs projets', 'fichier': 'project_collaborator', 'unique': None, 'ordre': 2505},
        
        # Feuilles de temps v19
        'hr.timesheet.switch': {'nom': 'Basculement temps', 'fichier': 'timesheet_switch', 'unique': None, 'ordre': 2510},
        
        # Skills/Compétences (nouveau v19)
        'hr.skill': {'nom': 'Compétences', 'fichier': 'skill', 'unique': 'name', 'ordre': 1160},
        'hr.skill.level': {'nom': 'Niveaux compétences', 'fichier': 'skill_level', 'unique': None, 'ordre': 1162},
        'hr.skill.type': {'nom': 'Types compétences', 'fichier': 'skill_type', 'unique': 'name', 'ordre': 1158},
        'hr.employee.skill': {'nom': 'Compétences employés', 'fichier': 'employee_skill', 'unique': None, 'ordre': 2515},
        
        # Planning amélioré v19
        'planning.recurrency': {'nom': 'Récurrence planning', 'fichier': 'planning_recurrency', 'unique': None, 'ordre': 1165},
        
        # Nouveaux rapports v19
        'spreadsheet.dashboard': {'nom': 'Dashboards Spreadsheet', 'fichier': 'spreadsheet_dashboard', 'unique': 'name', 'ordre': 1170},
        'spreadsheet.dashboard.group': {'nom': 'Groupes dashboards', 'fichier': 'dashboard_group', 'unique': 'name', 'ordre': 1168},
    }

def obtenir_configuration_complete():
    """
    Configuration EXHAUSTIVE de TOUS les modules Odoo v16-17-18-19
    
    Returns:
        dict {module: config}
    """
    return {
        # ======================================================================
        # COMPTABILITÉ (30+ modules)
        # ======================================================================
        'account.account': {'nom': 'Comptes', 'fichier': 'account', 'unique': 'code', 'ordre': 100},
        'account.group': {'nom': 'Groupes comptes', 'fichier': 'account_group', 'unique': 'code_prefix', 'ordre': 98},
        'account.tax': {'nom': 'Taxes', 'fichier': 'tax', 'unique': 'name', 'ordre': 105},
        'account.tax.group': {'nom': 'Groupes taxes', 'fichier': 'tax_group', 'unique': 'name', 'ordre': 103},
        'account.tax.repartition.line': {'nom': 'Répartition taxes', 'fichier': 'tax_repartition', 'unique': None, 'ordre': 107},
        'account.journal': {'nom': 'Journaux', 'fichier': 'journal', 'unique': 'code', 'ordre': 110},
        'account.journal.group': {'nom': 'Groupes journaux', 'fichier': 'journal_group', 'unique': 'name', 'ordre': 108},
        'account.fiscal.position': {'nom': 'Positions fiscales', 'fichier': 'fiscal_position', 'unique': 'name', 'ordre': 115},
        'account.fiscal.position.account': {'nom': 'Comptes positions fiscales', 'fichier': 'fiscal_position_account', 'unique': None, 'ordre': 117},
        'account.fiscal.position.tax': {'nom': 'Taxes positions fiscales', 'fichier': 'fiscal_position_tax', 'unique': None, 'ordre': 118},
        'account.payment.term': {'nom': 'Conditions paiement', 'fichier': 'payment_term', 'unique': 'name', 'ordre': 120},
        'account.payment.term.line': {'nom': 'Lignes conditions paiement', 'fichier': 'payment_term_line', 'unique': None, 'ordre': 122},
        'account.analytic.plan': {'nom': 'Plans analytiques', 'fichier': 'analytic_plan', 'unique': 'name', 'ordre': 125},
        'account.analytic.account': {'nom': 'Comptes analytiques', 'fichier': 'analytic_account', 'unique': 'code', 'ordre': 130},
        'account.analytic.line': {'nom': 'Lignes analytiques', 'fichier': 'analytic_line', 'unique': None, 'ordre': 2200},
        'account.analytic.distribution': {'nom': 'Distribution analytique', 'fichier': 'analytic_distribution', 'unique': None, 'ordre': 132},
        'account.budget.post': {'nom': 'Postes budgétaires', 'fichier': 'budget_post', 'unique': 'name', 'ordre': 135},
        'crossovered.budget': {'nom': 'Budgets', 'fichier': 'budget', 'unique': 'name', 'ordre': 140},
        'crossovered.budget.lines': {'nom': 'Lignes budgétaires', 'fichier': 'budget_line', 'unique': None, 'ordre': 142},
        'account.move': {'nom': 'Factures/Écritures', 'fichier': 'account_move', 'unique': 'name', 'ordre': 2100},
        'account.move.line': {'nom': 'Lignes comptables', 'fichier': 'account_move_line', 'unique': None, 'ordre': 2105},
        'account.payment': {'nom': 'Paiements', 'fichier': 'payment', 'unique': 'name', 'ordre': 2110},
        'account.payment.register': {'nom': 'Registre paiements', 'fichier': 'payment_register', 'unique': None, 'ordre': 2112},
        'account.bank.statement': {'nom': 'Relevés bancaires', 'fichier': 'bank_statement', 'unique': 'name', 'ordre': 2115},
        'account.bank.statement.line': {'nom': 'Lignes relevés', 'fichier': 'bank_statement_line', 'unique': None, 'ordre': 2120},
        'account.partial.reconcile': {'nom': 'Rapprochements partiels', 'fichier': 'partial_reconcile', 'unique': None, 'ordre': 2125},
        'account.full.reconcile': {'nom': 'Rapprochements complets', 'fichier': 'full_reconcile', 'unique': 'name', 'ordre': 2130},
        'account.reconcile.model': {'nom': 'Modèles rapprochement', 'fichier': 'reconcile_model', 'unique': 'name', 'ordre': 145},
        'account.cash.rounding': {'nom': 'Arrondis caisse', 'fichier': 'cash_rounding', 'unique': 'name', 'ordre': 150},
        'account.incoterms': {'nom': 'Incoterms', 'fichier': 'incoterms', 'unique': 'code', 'ordre': 152},
        'account.asset': {'nom': 'Actifs/Immobilisations', 'fichier': 'asset', 'unique': 'name', 'ordre': 2135},
        'account.asset.category': {'nom': 'Catégories actifs', 'fichier': 'asset_category', 'unique': 'name', 'ordre': 153},
        
        # ======================================================================
        # VENTES ET CRM (20+ modules)
        # ======================================================================
        'sale.order': {'nom': 'Commandes clients', 'fichier': 'sale_order', 'unique': 'name', 'ordre': 2000},
        'sale.order.line': {'nom': 'Lignes commandes', 'fichier': 'sale_order_line', 'unique': None, 'ordre': 2005},
        'sale.order.option': {'nom': 'Options commandes', 'fichier': 'sale_order_option', 'unique': None, 'ordre': 2007},
        'sale.quote.template': {'nom': 'Modèles devis', 'fichier': 'quote_template', 'unique': 'name', 'ordre': 200},
        'sale.quote.line': {'nom': 'Lignes modèles devis', 'fichier': 'quote_line', 'unique': None, 'ordre': 205},
        'sale.subscription': {'nom': 'Abonnements', 'fichier': 'subscription', 'unique': 'code', 'ordre': 2010},
        'sale.subscription.template': {'nom': 'Modèles abonnements', 'fichier': 'subscription_template', 'unique': 'name', 'ordre': 210},
        'sale.subscription.line': {'nom': 'Lignes abonnements', 'fichier': 'subscription_line', 'unique': None, 'ordre': 2012},
        'sale.coupon.program': {'nom': 'Programmes coupons', 'fichier': 'coupon_program', 'unique': 'name', 'ordre': 215},
        'sale.coupon': {'nom': 'Coupons', 'fichier': 'coupon', 'unique': 'code', 'ordre': 220},
        'crm.team': {'nom': 'Équipes commerciales', 'fichier': 'crm_team', 'unique': 'name', 'ordre': 180},
        'crm.stage': {'nom': 'Étapes CRM', 'fichier': 'crm_stage', 'unique': 'name', 'ordre': 185},
        'crm.lead': {'nom': 'Leads/Opportunités', 'fichier': 'lead', 'unique': None, 'ordre': 2015},
        'crm.lead.tag': {'nom': 'Tags CRM', 'fichier': 'lead_tag', 'unique': 'name', 'ordre': 170},
        'crm.lost.reason': {'nom': 'Raisons perte', 'fichier': 'lost_reason', 'unique': 'name', 'ordre': 172},
        'utm.campaign': {'nom': 'Campagnes UTM', 'fichier': 'utm_campaign', 'unique': 'name', 'ordre': 165},
        'utm.medium': {'nom': 'Medium UTM', 'fichier': 'utm_medium', 'unique': 'name', 'ordre': 166},
        'utm.source': {'nom': 'Source UTM', 'fichier': 'utm_source', 'unique': 'name', 'ordre': 167},
        
        # ======================================================================
        # ACHATS (10+ modules)
        # ======================================================================
        'purchase.order': {'nom': 'Commandes fournisseurs', 'fichier': 'purchase_order', 'unique': 'name', 'ordre': 2020},
        'purchase.order.line': {'nom': 'Lignes commandes achat', 'fichier': 'purchase_order_line', 'unique': None, 'ordre': 2025},
        'purchase.requisition': {'nom': 'Appels d\'offres', 'fichier': 'requisition', 'unique': 'name', 'ordre': 2027},
        'purchase.requisition.line': {'nom': 'Lignes appels offres', 'fichier': 'requisition_line', 'unique': None, 'ordre': 2029},
        'product.supplierinfo': {'nom': 'Fournisseurs produits', 'fichier': 'supplierinfo', 'unique': None, 'ordre': 230},
        
        # ======================================================================
        # ABONNEMENTS / SERVICES SUR SITE (10+ modules)
        # ======================================================================
        'sale.subscription': {'nom': 'Abonnements récurrents', 'fichier': 'subscription', 'unique': 'code', 'ordre': 2030},
        'sale.subscription.line': {'nom': 'Lignes abonnements', 'fichier': 'subscription_line', 'unique': None, 'ordre': 2032},
        'sale.subscription.template': {'nom': 'Plans abonnements', 'fichier': 'subscription_template', 'unique': 'name', 'ordre': 235},
        'sale.subscription.stage': {'nom': 'Étapes abonnements', 'fichier': 'subscription_stage', 'unique': 'name', 'ordre': 233},
        'sale.subscription.alert': {'nom': 'Alertes abonnements', 'fichier': 'subscription_alert', 'unique': None, 'ordre': 2034},
        
        # Services sur site / Interventions
        'project.project': {'nom': 'Projets/Services', 'fichier': 'project', 'unique': 'name', 'ordre': 300},
        'project.task': {'nom': 'Tâches/Interventions', 'fichier': 'task', 'unique': None, 'ordre': 2150},
        'project.task.type': {'nom': 'Étapes tâches', 'fichier': 'task_type', 'unique': 'name', 'ordre': 305},
        'project.milestone': {'nom': 'Jalons', 'fichier': 'milestone', 'unique': None, 'ordre': 2152},
        'project.tags': {'nom': 'Tags projets', 'fichier': 'project_tag', 'unique': 'name', 'ordre': 295},
        
        # ======================================================================
        # MAINTENANCE ET RÉPARATION (10+ modules)
        # ======================================================================
        'maintenance.equipment': {'nom': 'Équipements', 'fichier': 'equipment', 'unique': 'name', 'ordre': 400},
        'maintenance.equipment.category': {'nom': 'Catégories équipements', 'fichier': 'equipment_category', 'unique': 'name', 'ordre': 395},
        'maintenance.request': {'nom': 'Demandes maintenance', 'fichier': 'maintenance_request', 'unique': 'name', 'ordre': 2160},
        'maintenance.stage': {'nom': 'Étapes maintenance', 'fichier': 'maintenance_stage', 'unique': 'name', 'ordre': 405},
        'maintenance.team': {'nom': 'Équipes maintenance', 'fichier': 'maintenance_team', 'unique': 'name', 'ordre': 407},
        
        # Réparation
        'repair.order': {'nom': 'Ordres réparation', 'fichier': 'repair_order', 'unique': 'name', 'ordre': 2165},
        'repair.line': {'nom': 'Lignes réparation', 'fichier': 'repair_line', 'unique': None, 'ordre': 2167},
        'repair.fee': {'nom': 'Frais réparation', 'fichier': 'repair_fee', 'unique': None, 'ordre': 2169},
        
        # ======================================================================
        # QUALITÉ (10+ modules)
        # ======================================================================
        'quality.point': {'nom': 'Points contrôle qualité', 'fichier': 'quality_point', 'unique': 'name', 'ordre': 450},
        'quality.check': {'nom': 'Contrôles qualité', 'fichier': 'quality_check', 'unique': None, 'ordre': 2170},
        'quality.alert': {'nom': 'Alertes qualité', 'fichier': 'quality_alert', 'unique': 'name', 'ordre': 2172},
        'quality.alert.stage': {'nom': 'Étapes alertes qualité', 'fichier': 'quality_alert_stage', 'unique': 'name', 'ordre': 455},
        'quality.alert.team': {'nom': 'Équipes qualité', 'fichier': 'quality_team', 'unique': 'name', 'ordre': 457},
        'quality.tag': {'nom': 'Tags qualité', 'fichier': 'quality_tag', 'unique': 'name', 'ordre': 452},
        
        # ======================================================================
        # FLOTTE / PARC AUTOMOBILE (15+ modules)
        # ======================================================================
        'fleet.vehicle': {'nom': 'Véhicules', 'fichier': 'vehicle', 'unique': 'license_plate', 'ordre': 2180},
        'fleet.vehicle.model': {'nom': 'Modèles véhicules', 'fichier': 'vehicle_model', 'unique': 'name', 'ordre': 470},
        'fleet.vehicle.model.brand': {'nom': 'Marques véhicules', 'fichier': 'vehicle_brand', 'unique': 'name', 'ordre': 465},
        'fleet.vehicle.model.category': {'nom': 'Catégories véhicules', 'fichier': 'vehicle_category', 'unique': 'name', 'ordre': 467},
        'fleet.vehicle.state': {'nom': 'États véhicules', 'fichier': 'vehicle_state', 'unique': 'name', 'ordre': 468},
        'fleet.vehicle.tag': {'nom': 'Tags véhicules', 'fichier': 'vehicle_tag', 'unique': 'name', 'ordre': 469},
        'fleet.vehicle.log.contract': {'nom': 'Contrats véhicules', 'fichier': 'vehicle_contract', 'unique': None, 'ordre': 2185},
        'fleet.vehicle.log.services': {'nom': 'Services véhicules', 'fichier': 'vehicle_service', 'unique': None, 'ordre': 2190},
        'fleet.vehicle.cost': {'nom': 'Coûts véhicules', 'fichier': 'vehicle_cost', 'unique': None, 'ordre': 2192},
        'fleet.vehicle.odometer': {'nom': 'Kilométrage', 'fichier': 'vehicle_odometer', 'unique': None, 'ordre': 2194},
        'fleet.service.type': {'nom': 'Types services', 'fichier': 'service_type', 'unique': 'name', 'ordre': 475},
        
        # ======================================================================
        # PLANNING ET RESSOURCES (10+ modules)
        # ======================================================================
        'planning.slot': {'nom': 'Créneaux planning', 'fichier': 'planning_slot', 'unique': None, 'ordre': 2300},
        'planning.role': {'nom': 'Rôles planning', 'fichier': 'planning_role', 'unique': 'name', 'ordre': 500},
        'planning.template': {'nom': 'Modèles planning', 'fichier': 'planning_template', 'unique': 'name', 'ordre': 505},
        'resource.calendar': {'nom': 'Horaires travail', 'fichier': 'calendar', 'unique': 'name', 'ordre': 510},
        'resource.calendar.attendance': {'nom': 'Présences horaires', 'fichier': 'calendar_attendance', 'unique': None, 'ordre': 512},
        'resource.calendar.leaves': {'nom': 'Congés horaires', 'fichier': 'calendar_leaves', 'unique': None, 'ordre': 514},
        'resource.resource': {'nom': 'Ressources', 'fichier': 'resource', 'unique': 'name', 'ordre': 515},
        
        # ======================================================================
        # CALENDRIER ET RENDEZ-VOUS (10+ modules)
        # ======================================================================
        'calendar.event': {'nom': 'Événements calendrier', 'fichier': 'calendar_event', 'unique': None, 'ordre': 2305},
        'calendar.event.type': {'nom': 'Types événements', 'fichier': 'calendar_event_type', 'unique': 'name', 'ordre': 520},
        'calendar.alarm': {'nom': 'Alarmes', 'fichier': 'calendar_alarm', 'unique': 'name', 'ordre': 522},
        'appointment.type': {'nom': 'Types rendez-vous', 'fichier': 'appointment_type', 'unique': 'name', 'ordre': 525},
        'appointment.invite': {'nom': 'Invitations rendez-vous', 'fichier': 'appointment_invite', 'unique': None, 'ordre': 2310},
        'calendar.booking': {'nom': 'Réservations', 'fichier': 'booking', 'unique': None, 'ordre': 2312},
        
        # ======================================================================
        # HELPDESK / SUPPORT (10+ modules)
        # ======================================================================
        'helpdesk.team': {'nom': 'Équipes support', 'fichier': 'helpdesk_team', 'unique': 'name', 'ordre': 550},
        'helpdesk.stage': {'nom': 'Étapes tickets', 'fichier': 'helpdesk_stage', 'unique': 'name', 'ordre': 555},
        'helpdesk.ticket': {'nom': 'Tickets support', 'fichier': 'ticket', 'unique': 'name', 'ordre': 2320},
        'helpdesk.ticket.type': {'nom': 'Types tickets', 'fichier': 'ticket_type', 'unique': 'name', 'ordre': 557},
        'helpdesk.sla': {'nom': 'SLA', 'fichier': 'sla', 'unique': 'name', 'ordre': 560},
        'helpdesk.tag': {'nom': 'Tags tickets', 'fichier': 'helpdesk_tag', 'unique': 'name', 'ordre': 552},
        
        # ======================================================================
        # MARKETING (15+ modules)
        # ======================================================================
        'marketing.campaign': {'nom': 'Campagnes marketing', 'fichier': 'marketing_campaign', 'unique': 'name', 'ordre': 600},
        'marketing.activity': {'nom': 'Activités marketing', 'fichier': 'marketing_activity', 'unique': 'name', 'ordre': 605},
        'marketing.participant': {'nom': 'Participants', 'fichier': 'marketing_participant', 'unique': None, 'ordre': 2350},
        'mailing.mailing': {'nom': 'Mailings', 'fichier': 'mailing', 'unique': 'name', 'ordre': 2355},
        'mailing.list': {'nom': 'Listes diffusion', 'fichier': 'mailing_list', 'unique': 'name', 'ordre': 610},
        'mailing.contact': {'nom': 'Contacts mailing', 'fichier': 'mailing_contact', 'unique': 'email', 'ordre': 615},
        'mailing.trace': {'nom': 'Traces mailing', 'fichier': 'mailing_trace', 'unique': None, 'ordre': 2360},
        'link.tracker': {'nom': 'Liens trackés', 'fichier': 'link_tracker', 'unique': 'url', 'ordre': 620},
        'link.tracker.click': {'nom': 'Clics liens', 'fichier': 'link_click', 'unique': None, 'ordre': 2365},
        'link.tracker.code': {'nom': 'Codes tracking', 'fichier': 'link_code', 'unique': 'code', 'ordre': 622},
        'social.media': {'nom': 'Médias sociaux', 'fichier': 'social_media', 'unique': 'name', 'ordre': 625},
        'social.account': {'nom': 'Comptes sociaux', 'fichier': 'social_account', 'unique': None, 'ordre': 627},
        'social.post': {'nom': 'Posts sociaux', 'fichier': 'social_post', 'unique': None, 'ordre': 2370},
        
        # ======================================================================
        # SONDAGES ET FORMULAIRES (10+ modules)
        # ======================================================================
        'survey.survey': {'nom': 'Sondages', 'fichier': 'survey', 'unique': 'title', 'ordre': 650},
        'survey.question': {'nom': 'Questions', 'fichier': 'survey_question', 'unique': None, 'ordre': 655},
        'survey.question.answer': {'nom': 'Réponses possibles', 'fichier': 'survey_answer', 'unique': None, 'ordre': 657},
        'survey.user_input': {'nom': 'Réponses utilisateurs', 'fichier': 'survey_user_input', 'unique': None, 'ordre': 2380},
        'survey.user_input.line': {'nom': 'Détail réponses', 'fichier': 'survey_input_line', 'unique': None, 'ordre': 2385},
        
        # ======================================================================
        # SIGNATURE ÉLECTRONIQUE (8+ modules)
        # ======================================================================
        'sign.template': {'nom': 'Modèles signature', 'fichier': 'sign_template', 'unique': 'name', 'ordre': 700},
        'sign.item': {'nom': 'Champs signature', 'fichier': 'sign_item', 'unique': None, 'ordre': 705},
        'sign.item.type': {'nom': 'Types champs signature', 'fichier': 'sign_item_type', 'unique': 'name', 'ordre': 702},
        'sign.request': {'nom': 'Demandes signature', 'fichier': 'sign_request', 'unique': None, 'ordre': 2390},
        'sign.request.item': {'nom': 'Items demandes', 'fichier': 'sign_request_item', 'unique': None, 'ordre': 2395},
        
        # ======================================================================
        # POINT DE VENTE (15+ modules)
        # ======================================================================
        'pos.config': {'nom': 'Configuration POS', 'fichier': 'pos_config', 'unique': 'name', 'ordre': 750},
        'pos.session': {'nom': 'Sessions POS', 'fichier': 'pos_session', 'unique': 'name', 'ordre': 2400},
        'pos.order': {'nom': 'Commandes POS', 'fichier': 'pos_order', 'unique': 'pos_reference', 'ordre': 2405},
        'pos.order.line': {'nom': 'Lignes POS', 'fichier': 'pos_order_line', 'unique': None, 'ordre': 2410},
        'pos.payment': {'nom': 'Paiements POS', 'fichier': 'pos_payment', 'unique': None, 'ordre': 2412},
        'pos.payment.method': {'nom': 'Méthodes paiement POS', 'fichier': 'pos_payment_method', 'unique': 'name', 'ordre': 755},
        'pos.category': {'nom': 'Catégories POS', 'fichier': 'pos_category', 'unique': 'name', 'ordre': 757},
        'loyalty.program': {'nom': 'Programmes fidélité', 'fichier': 'loyalty_program', 'unique': 'name', 'ordre': 760},
        'loyalty.card': {'nom': 'Cartes fidélité', 'fichier': 'loyalty_card', 'unique': 'code', 'ordre': 2415},
        'loyalty.reward': {'nom': 'Récompenses', 'fichier': 'loyalty_reward', 'unique': None, 'ordre': 765},
        
        # ======================================================================
        # LIVRAISON ET EXPÉDITION (10+ modules)
        # ======================================================================
        'delivery.carrier': {'nom': 'Transporteurs', 'fichier': 'delivery_carrier', 'unique': 'name', 'ordre': 800},
        'delivery.price.rule': {'nom': 'Règles tarifs livraison', 'fichier': 'delivery_price_rule', 'unique': None, 'ordre': 805},
        'stock.package.type': {'nom': 'Types colis', 'fichier': 'package_type', 'unique': 'name', 'ordre': 810},
        'stock.quant.package': {'nom': 'Colis', 'fichier': 'package', 'unique': 'name', 'ordre': 2420},
        'delivery.tracking.ref': {'nom': 'Tracking livraisons', 'fichier': 'delivery_tracking', 'unique': None, 'ordre': 2425},
        
        # ======================================================================
        # IoT ET MATÉRIEL (5+ modules)
        # ======================================================================
        'iot.box': {'nom': 'Box IoT', 'fichier': 'iot_box', 'unique': 'name', 'ordre': 850},
        'iot.device': {'nom': 'Devices IoT', 'fichier': 'iot_device', 'unique': 'identifier', 'ordre': 2430},
        
        # ======================================================================
        # KNOWLEDGE / WIKI (5+ modules)
        # ======================================================================
        'knowledge.article': {'nom': 'Articles knowledge', 'fichier': 'knowledge_article', 'unique': None, 'ordre': 900},
        'knowledge.article.favorite': {'nom': 'Favoris knowledge', 'fichier': 'knowledge_favorite', 'unique': None, 'ordre': 2435},
        'knowledge.cover': {'nom': 'Couvertures articles', 'fichier': 'knowledge_cover', 'unique': None, 'ordre': 905},
        
        # ======================================================================
        # APPROVALS / APPROBATIONS (5+ modules)
        # ======================================================================
        'approval.category': {'nom': 'Catégories approbations', 'fichier': 'approval_category', 'unique': 'name', 'ordre': 950},
        'approval.request': {'nom': 'Demandes approbation', 'fichier': 'approval_request', 'unique': None, 'ordre': 2440},
        'approval.approver': {'nom': 'Approbateurs', 'fichier': 'approver', 'unique': None, 'ordre': 2445},
        
        # ======================================================================
        # CONTRATS (5+ modules)
        # ======================================================================
        'hr.contract': {'nom': 'Contrats employés', 'fichier': 'hr_contract', 'unique': None, 'ordre': 2450},
        'hr.contract.type': {'nom': 'Types contrats', 'fichier': 'contract_type', 'unique': 'name', 'ordre': 1000},
        
        # ======================================================================
        # ÉVALUATIONS / APPRAISALS (5+ modules)
        # ======================================================================
        'hr.appraisal': {'nom': 'Évaluations', 'fichier': 'appraisal', 'unique': None, 'ordre': 2455},
        'hr.appraisal.goal': {'nom': 'Objectifs évaluations', 'fichier': 'appraisal_goal', 'unique': None, 'ordre': 2457},
        
        # ======================================================================
        # RECRUTEMENT (10+ modules)
        # ======================================================================
        'hr.recruitment.source': {'nom': 'Sources recrutement', 'fichier': 'recruitment_source', 'unique': 'name', 'ordre': 1050},
        'hr.recruitment.degree': {'nom': 'Diplômes', 'fichier': 'degree', 'unique': 'name', 'ordre': 1052},
        'hr.recruitment.stage': {'nom': 'Étapes recrutement', 'fichier': 'recruitment_stage', 'unique': 'name', 'ordre': 1055},
        'hr.applicant': {'nom': 'Candidatures', 'fichier': 'applicant', 'unique': None, 'ordre': 2460},
        'hr.applicant.category': {'nom': 'Tags candidats', 'fichier': 'applicant_tag', 'unique': 'name', 'ordre': 1057},
        
        # ======================================================================
        # PAIE (10+ modules)
        # ======================================================================
        'hr.payslip': {'nom': 'Bulletins paie', 'fichier': 'payslip', 'unique': None, 'ordre': 2465},
        'hr.payslip.line': {'nom': 'Lignes bulletins', 'fichier': 'payslip_line', 'unique': None, 'ordre': 2470},
        'hr.payslip.run': {'nom': 'Lots paie', 'fichier': 'payslip_run', 'unique': 'name', 'ordre': 2475},
        'hr.salary.rule': {'nom': 'Règles salariales', 'fichier': 'salary_rule', 'unique': 'code', 'ordre': 1100},
        'hr.salary.rule.category': {'nom': 'Catégories règles', 'fichier': 'salary_category', 'unique': 'code', 'ordre': 1095},
        'hr.payroll.structure': {'nom': 'Structures paie', 'fichier': 'payroll_structure', 'unique': 'code', 'ordre': 1105},
        'hr.payroll.structure.type': {'nom': 'Types structures', 'fichier': 'payroll_type', 'unique': 'name', 'ordre': 1103},
    }

