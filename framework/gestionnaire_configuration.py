#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GESTIONNAIRE DE CONFIGURATION
==============================
Définit les configurations de tous les modules à migrer
"""

class GestionnaireConfiguration:
    """Gère les configurations de migration pour tous les modules"""
    
    @staticmethod
    def obtenir_config_module(model):
        """
        Retourne la configuration pour un module donné
        
        Args:
            model: Nom du modèle Odoo
        
        Returns:
            dict de configuration ou None
        """
        configs = GestionnaireConfiguration.obtenir_toutes_configs()
        return configs.get(model)
    
    @staticmethod
    def obtenir_toutes_configs():
        """
        Retourne toutes les configurations de migration
        
        Returns:
            dict {model: config}
        """
        return {
            # ==================================================================
            # COMPTABILITÉ
            # ==================================================================
            
            'account.account': {
                'nom': 'Plan comptable',
                'fichier': 'account',
                'unique_field': 'code',
                'relations': {
                    'user_type_id': 'account_type_mapping.json',
                    'group_id': 'account_group_mapping.json',
                },
                'ordre': 10
            },
            
            'account.tax': {
                'nom': 'Taxes',
                'fichier': 'tax',
                'unique_field': 'name',
                'relations': {
                    'company_id': 'company_mapping.json',
                    'country_id': 'country_mapping.json',
                    'tax_group_id': 'tax_group_mapping.json',
                    'cash_basis_transition_account_id': 'account_mapping.json',
                },
                'ordre': 15
            },
            
            'account.journal': {
                'nom': 'Journaux',
                'fichier': 'account_journal',
                'unique_field': 'code',
                'relations': {
                    'company_id': 'company_mapping.json',
                    'default_account_id': 'account_mapping.json',
                    'suspense_account_id': 'account_mapping.json',
                    'profit_account_id': 'account_mapping.json',
                    'loss_account_id': 'account_mapping.json',
                },
                'ordre': 20
            },
            
            'account.fiscal.position': {
                'nom': 'Positions fiscales',
                'fichier': 'fiscal_position',
                'unique_field': 'name',
                'relations': {
                    'company_id': 'company_mapping.json',
                },
                'ordre': 25
            },
            
            'account.payment.term': {
                'nom': 'Conditions de paiement',
                'fichier': 'payment_term',
                'unique_field': 'name',
                'relations': {
                    'company_id': 'company_mapping.json',
                },
                'ordre': 30
            },
            
            'account.analytic.plan': {
                'nom': 'Plans analytiques',
                'fichier': 'analytic_plan',
                'unique_field': 'name',
                'relations': {
                    'company_id': 'company_mapping.json',
                },
                'ordre': 35
            },
            
            'account.analytic.account': {
                'nom': 'Comptes analytiques',
                'fichier': 'analytic_account',
                'unique_field': 'code',
                'relations': {
                    'plan_id': 'analytic_plan_mapping.json',
                    'partner_id': 'partner_mapping.json',
                    'company_id': 'company_mapping.json',
                },
                'valeurs_defaut': {
                    'plan_id': 2  # Plan par défaut si manquant
                },
                'ordre': 40
            },
            
            # ==================================================================
            # PARTENAIRES
            # ==================================================================
            
            'res.partner': {
                'nom': 'Partenaires',
                'fichier': 'partner',
                'unique_field': 'email',  # ou 'ref'
                'relations': {
                    'parent_id': 'partner_mapping.json',
                    'company_id': 'company_mapping.json',
                    'user_id': 'user_mapping.json',
                    'country_id': 'country_mapping.json',
                    'state_id': 'state_mapping.json',
                    'industry_id': 'industry_mapping.json',
                    'title': 'title_mapping.json',
                },
                'ordre': 50
            },
            
            'res.partner.category': {
                'nom': 'Étiquettes contact',
                'fichier': 'partner_category',
                'unique_field': 'name',
                'relations': {
                    'parent_id': 'partner_category_mapping.json',
                },
                'ordre': 45
            },
            
            'res.partner.industry': {
                'nom': 'Secteurs d\'activité',
                'fichier': 'industry',
                'unique_field': 'name',
                'ordre': 42
            },
            
            # ==================================================================
            # UTILISATEURS ET RH
            # ==================================================================
            
            'res.users': {
                'nom': 'Utilisateurs',
                'fichier': 'user',
                'unique_field': 'login',
                'relations': {
                    'partner_id': 'partner_mapping.json',
                    'company_id': 'company_mapping.json',
                },
                'valeurs_defaut': {
                    'active': True,  # Tous actifs pendant migration
                    'password': 'ChangeMe123!'
                },
                'skip_conditions': [
                    lambda rec: rec.get('login') in ['admin', '__export__', 'portal', 'default'],
                    lambda rec: '@' not in rec.get('login', '')
                ],
                'ordre': 5  # EN PREMIER!
            },
            
            'hr.department': {
                'nom': 'Départements RH',
                'fichier': 'hr_department',
                'unique_field': 'name',
                'relations': {
                    'company_id': 'company_mapping.json',
                    'manager_id': 'employee_mapping.json',
                    'parent_id': 'hr_department_mapping.json',
                },
                'ordre': 60
            },
            
            'hr.job': {
                'nom': 'Postes/Fonctions',
                'fichier': 'hr_job',
                'unique_field': 'name',
                'relations': {
                    'company_id': 'company_mapping.json',
                    'department_id': 'hr_department_mapping.json',
                },
                'ordre': 65
            },
            
            'hr.employee': {
                'nom': 'Employés',
                'fichier': 'employe',
                'unique_field': 'work_email',
                'relations': {
                    'user_id': 'user_mapping.json',
                    'department_id': 'hr_department_mapping.json',
                    'job_id': 'hr_job_mapping.json',
                    'parent_id': 'employee_mapping.json',
                    'coach_id': 'employee_mapping.json',
                    'address_home_id': 'partner_mapping.json',
                    'company_id': 'company_mapping.json',
                },
                'ordre': 70
            },
            
            # ==================================================================
            # PRODUITS
            # ==================================================================
            
            'product.category': {
                'nom': 'Catégories produits',
                'fichier': 'product_category',
                'unique_field': 'name',
                'relations': {
                    'parent_id': 'product_category_mapping.json',
                },
                'ordre': 80
            },
            
            'uom.category': {
                'nom': 'Catégories unités',
                'fichier': 'uom_category',
                'unique_field': 'name',
                'ordre': 82
            },
            
            'uom.uom': {
                'nom': 'Unités de mesure',
                'fichier': 'uom',
                'unique_field': 'name',
                'relations': {
                    'category_id': 'uom_category_mapping.json',
                },
                'ordre': 85
            },
            
            'product.template': {
                'nom': 'Produits',
                'fichier': 'product_template',
                'unique_field': 'default_code',  # ou 'name' si pas de code
                'relations': {
                    'categ_id': 'product_category_mapping.json',
                    'uom_id': 'uom_mapping.json',
                    'uom_po_id': 'uom_mapping.json',
                    'responsible_id': 'user_mapping.json',
                    'company_id': 'company_mapping.json',
                },
                'ordre': 90
            },
            
            'product.pricelist': {
                'nom': 'Listes de prix',
                'fichier': 'pricelist',
                'unique_field': 'name',
                'relations': {
                    'currency_id': 'currency_mapping.json',
                    'company_id': 'company_mapping.json',
                },
                'ordre': 95
            },
            
            # ==================================================================
            # STOCK
            # ==================================================================
            
            'stock.warehouse': {
                'nom': 'Entrepôts',
                'fichier': 'stock_warehouse',
                'unique_field': 'code',
                'relations': {
                    'company_id': 'company_mapping.json',
                    'partner_id': 'partner_mapping.json',
                },
                'ordre': 100
            },
            
            'stock.location': {
                'nom': 'Emplacements',
                'fichier': 'location',
                'unique_field': 'complete_name',
                'relations': {
                    'location_id': 'location_mapping.json',
                    'company_id': 'company_mapping.json',
                    'warehouse_id': 'stock_warehouse_mapping.json',
                },
                'ordre': 105
            },
            
            'stock.picking.type': {
                'nom': 'Types d\'opérations',
                'fichier': 'picking_type',
                'unique_field': 'name',
                'relations': {
                    'warehouse_id': 'stock_warehouse_mapping.json',
                    'default_location_src_id': 'location_mapping.json',
                    'default_location_dest_id': 'location_mapping.json',
                    'company_id': 'company_mapping.json',
                },
                'ordre': 110
            },
            
            # ==================================================================
            # VENTES ET CRM
            # ==================================================================
            
            'crm.team': {
                'nom': 'Équipes commerciales',
                'fichier': 'crm_team',
                'unique_field': 'name',
                'relations': {
                    'user_id': 'user_mapping.json',
                    'company_id': 'company_mapping.json',
                },
                'valeurs_defaut': {
                    'user_id': 2  # Admin par défaut
                },
                'ordre': 115
            },
            
            'crm.stage': {
                'nom': 'Étapes CRM',
                'fichier': 'crm_stage',
                'unique_field': 'name',
                'relations': {
                    'team_id': 'crm_team_mapping.json',
                },
                'ordre': 120
            },
            
            # ==================================================================
            # PROJETS
            # ==================================================================
            
            'project.project': {
                'nom': 'Projets',
                'fichier': 'project',
                'unique_field': 'name',
                'relations': {
                    'user_id': 'user_mapping.json',
                    'partner_id': 'partner_mapping.json',
                    'company_id': 'company_mapping.json',
                },
                'valeurs_defaut': {
                    'user_id': 2  # Admin par défaut
                },
                'ordre': 125
            },
            
            'project.task.type': {
                'nom': 'Étapes de tâches',
                'fichier': 'task_type',
                'unique_field': 'name',
                'relations': {
                    'project_ids': 'project_mapping.json',
                },
                'ordre': 130
            },
            
            # ==================================================================
            # DOCUMENTS ET PIÈCES JOINTES
            # ==================================================================
            
            'ir.attachment': {
                'nom': 'Pièces jointes',
                'fichier': 'attachment',
                'unique_field': 'name',  # ou checksum
                'relations': {
                    'res_id': 'dynamic',  # Dépend de res_model
                    'company_id': 'company_mapping.json',
                },
                'ordre': 900  # Après tous les autres modules
            },
            
            'documents.document': {
                'nom': 'Documents',
                'fichier': 'document',
                'unique_field': 'name',
                'relations': {
                    'owner_id': 'user_mapping.json',
                    'partner_id': 'partner_mapping.json',
                    'folder_id': 'document_folder_mapping.json',
                    'attachment_id': 'attachment_mapping.json',
                    'company_id': 'company_mapping.json',
                },
                'ordre': 905  # Après ir.attachment
            },
            
            # ==================================================================
            # RAPPORTS ET IMPRESSIONS PDF
            # ==================================================================
            
            'report.paperformat': {
                'nom': 'Formats de papier',
                'fichier': 'paper_format',
                'unique_field': 'name',
                'ordre': 910
            },
            
            'ir.actions.report': {
                'nom': 'Modèles d\'impression PDF',
                'fichier': 'report',
                'unique_field': 'name',
                'relations': {
                    'paperformat_id': 'paper_format_mapping.json',
                    'groups_id': 'dynamic',  # Mapping groupes
                },
                'ordre': 915
            },
            
            # ==================================================================
            # MODÈLES ET TEMPLATES
            # ==================================================================
            
            'mail.template': {
                'nom': 'Modèles d\'emails',
                'fichier': 'mail_template',
                'unique_field': 'name',
                'relations': {
                    'user_id': 'user_mapping.json',
                },
                'ordre': 920
            },
            
            'sms.template': {
                'nom': 'Modèles SMS',
                'fichier': 'sms_template',
                'unique_field': 'name',
                'ordre': 925
            },
            
            # ==================================================================
            # SYSTÈME - SÉQUENCES ET PARAMÈTRES
            # ==================================================================
            
            'ir.sequence': {
                'nom': 'Séquences de numérotation',
                'fichier': 'sequence',
                'unique_field': 'code',  # ou 'name'
                'relations': {
                    'company_id': 'company_mapping.json',
                },
                'ordre': 850
            },
            
            'ir.sequence.date_range': {
                'nom': 'Plages de dates séquences',
                'fichier': 'sequence_date_range',
                'unique_field': 'date_from',
                'relations': {
                    'sequence_id': 'sequence_mapping.json',
                },
                'ordre': 855
            },
            
            'ir.config_parameter': {
                'nom': 'Paramètres système',
                'fichier': 'config_parameter',
                'unique_field': 'key',
                'ordre': 860
            },
            
            'decimal.precision': {
                'nom': 'Précisions décimales',
                'fichier': 'decimal_precision',
                'unique_field': 'name',
                'ordre': 865
            },
            
            # ==================================================================
            # CHATTER - MESSAGES ET ACTIVITÉS
            # ==================================================================
            
            'mail.message': {
                'nom': 'Messages (historique chatter)',
                'fichier': 'mail_message',
                'unique_field': 'message_id',  # ID unique email
                'relations': {
                    'author_id': 'partner_mapping.json',
                    'model': 'text',  # Nom du modèle
                    'res_id': 'dynamic',  # ID dans le modèle
                },
                'ordre': 980  # Après tous les autres modules
            },
            
            'mail.followers': {
                'nom': 'Abonnés (followers)',
                'fichier': 'mail_followers',
                'unique_field': None,  # Pas de champ unique
                'relations': {
                    'partner_id': 'partner_mapping.json',
                    'res_model': 'text',
                    'res_id': 'dynamic',
                },
                'ordre': 985
            },
            
            'mail.activity': {
                'nom': 'Activités planifiées',
                'fichier': 'mail_activity',
                'unique_field': None,
                'relations': {
                    'user_id': 'user_mapping.json',
                    'create_uid': 'user_mapping.json',
                    'res_model': 'text',
                    'res_id': 'dynamic',
                    'activity_type_id': 'activity_type_mapping.json',
                },
                'ordre': 990
            },
            
            'mail.activity.type': {
                'nom': 'Types d\'activités',
                'fichier': 'activity_type',
                'unique_field': 'name',
                'ordre': 870
            },
            
            # ==================================================================
            # AUTOMATISATIONS ET ACTIONS
            # ==================================================================
            
            'base.automation': {
                'nom': 'Automatisations',
                'fichier': 'automation',
                'unique_field': 'name',
                'relations': {
                    'model_id': 'ir_model_mapping.json',
                    'trigger_field_ids': 'dynamic',
                    'filter_domain': 'text',  # À copier tel quel
                },
                'ordre': 930
            },
            
            'ir.actions.server': {
                'nom': 'Actions serveur',
                'fichier': 'action_server',
                'unique_field': 'name',
                'relations': {
                    'model_id': 'ir_model_mapping.json',
                    'crud_model_id': 'ir_model_mapping.json',
                },
                'ordre': 935
            },
            
            'ir.cron': {
                'nom': 'Tâches planifiées',
                'fichier': 'cron',
                'unique_field': 'name',
                'relations': {
                    'user_id': 'user_mapping.json',
                    'ir_actions_server_id': 'action_server_mapping.json',
                },
                'ordre': 940
            },
            
            # ==================================================================
            # STUDIO - MODÈLES PERSONNALISÉS
            # ==================================================================
            
            'ir.model': {
                'nom': 'Modèles (y compris Studio)',
                'fichier': 'ir_model',
                'unique_field': 'model',
                'ordre': 950
            },
            
            'ir.model.fields': {
                'nom': 'Champs personnalisés (x_studio_*)',
                'fichier': 'ir_model_fields',
                'unique_field': 'name',
                'relations': {
                    'model_id': 'ir_model_mapping.json',
                    'relation': 'text',  # Nom du modèle cible
                },
                'ordre': 955
            },
            
            'ir.ui.view': {
                'nom': 'Vues (y compris Studio)',
                'fichier': 'view',
                'unique_field': 'name',
                'relations': {
                    'model': 'text',
                    'inherit_id': 'view_mapping.json',
                },
                'ordre': 960
            },
            
            'ir.ui.menu': {
                'nom': 'Menus personnalisés',
                'fichier': 'menu',
                'unique_field': 'name',
                'relations': {
                    'parent_id': 'menu_mapping.json',
                    'action': 'text',
                },
                'ordre': 965
            },
            
            'ir.filters': {
                'nom': 'Filtres sauvegardés',
                'fichier': 'filter',
                'unique_field': 'name',
                'relations': {
                    'user_id': 'user_mapping.json',
                    'model_id': 'text',
                },
                'ordre': 970
            },
            
            'ir.rule': {
                'nom': 'Règles de sécurité',
                'fichier': 'rule',
                'unique_field': 'name',
                'relations': {
                    'model_id': 'ir_model_mapping.json',
                    'groups': 'dynamic',
                },
                'ordre': 975
            },
            
            # ==================================================================
            # TRANSACTIONS - NOMENCLATURES
            # ==================================================================
            
            'mrp.bom': {
                'nom': 'Nomenclatures (BOM)',
                'fichier': 'bom',
                'unique_field': 'code',
                'relations': {
                    'product_id': 'product_mapping.json',
                    'product_tmpl_id': 'product_template_mapping.json',
                    'company_id': 'company_mapping.json',
                },
                'ordre': 1000
            },
            
            'mrp.bom.line': {
                'nom': 'Lignes nomenclatures',
                'fichier': 'bom_line',
                'unique_field': None,
                'relations': {
                    'bom_id': 'bom_mapping.json',
                    'product_id': 'product_mapping.json',
                },
                'ordre': 1005
            },
            
            # ==================================================================
            # TRANSACTIONS - VENTES
            # ==================================================================
            
            'sale.order': {
                'nom': 'Commandes clients',
                'fichier': 'sale_order',
                'unique_field': 'name',
                'relations': {
                    'partner_id': 'partner_mapping.json',
                    'user_id': 'user_mapping.json',
                    'team_id': 'crm_team_mapping.json',
                    'pricelist_id': 'pricelist_mapping.json',
                    'company_id': 'company_mapping.json',
                    'warehouse_id': 'stock_warehouse_mapping.json',
                },
                'ordre': 1010
            },
            
            'sale.order.line': {
                'nom': 'Lignes commandes clients',
                'fichier': 'sale_order_line',
                'unique_field': None,
                'relations': {
                    'order_id': 'sale_order_mapping.json',
                    'product_id': 'product_mapping.json',
                    'product_uom': 'uom_mapping.json',
                },
                'ordre': 1015
            },
            
            # ==================================================================
            # TRANSACTIONS - ACHATS
            # ==================================================================
            
            'purchase.order': {
                'nom': 'Commandes fournisseurs',
                'fichier': 'purchase_order',
                'unique_field': 'name',
                'relations': {
                    'partner_id': 'partner_mapping.json',
                    'user_id': 'user_mapping.json',
                    'company_id': 'company_mapping.json',
                },
                'ordre': 1020
            },
            
            'purchase.order.line': {
                'nom': 'Lignes commandes fournisseurs',
                'fichier': 'purchase_order_line',
                'unique_field': None,
                'relations': {
                    'order_id': 'purchase_order_mapping.json',
                    'product_id': 'product_mapping.json',
                    'product_uom': 'uom_mapping.json',
                    'account_analytic_id': 'analytic_account_mapping.json',
                },
                'ordre': 1025
            },
            
            # ==================================================================
            # TRANSACTIONS - FABRICATION
            # ==================================================================
            
            'mrp.production': {
                'nom': 'Ordres de fabrication',
                'fichier': 'production',
                'unique_field': 'name',
                'relations': {
                    'product_id': 'product_mapping.json',
                    'bom_id': 'bom_mapping.json',
                    'user_id': 'user_mapping.json',
                    'company_id': 'company_mapping.json',
                    'location_src_id': 'location_mapping.json',
                    'location_dest_id': 'location_mapping.json',
                },
                'ordre': 1030
            },
            
            'mrp.workorder': {
                'nom': 'Ordres de travail',
                'fichier': 'workorder',
                'unique_field': 'name',
                'relations': {
                    'production_id': 'production_mapping.json',
                    'workcenter_id': 'workcenter_mapping.json',
                },
                'ordre': 1035
            },
            
            # ==================================================================
            # TRANSACTIONS - STOCK
            # ==================================================================
            
            'stock.picking': {
                'nom': 'Transferts de stock',
                'fichier': 'picking',
                'unique_field': 'name',
                'relations': {
                    'partner_id': 'partner_mapping.json',
                    'picking_type_id': 'picking_type_mapping.json',
                    'location_id': 'location_mapping.json',
                    'location_dest_id': 'location_mapping.json',
                },
                'ordre': 1040
            },
            
            'stock.move': {
                'nom': 'Mouvements de stock',
                'fichier': 'stock_move',
                'unique_field': None,
                'relations': {
                    'picking_id': 'picking_mapping.json',
                    'product_id': 'product_mapping.json',
                    'location_id': 'location_mapping.json',
                    'location_dest_id': 'location_mapping.json',
                    'partner_id': 'partner_mapping.json',
                },
                'ordre': 1045
            },
            
            'stock.move.line': {
                'nom': 'Lignes mouvements stock',
                'fichier': 'stock_move_line',
                'unique_field': None,
                'relations': {
                    'move_id': 'stock_move_mapping.json',
                    'product_id': 'product_mapping.json',
                    'location_id': 'location_mapping.json',
                    'location_dest_id': 'location_mapping.json',
                },
                'ordre': 1050
            },
            
            'stock.quant': {
                'nom': 'Quantités en stock',
                'fichier': 'stock_quant',
                'unique_field': None,
                'relations': {
                    'product_id': 'product_mapping.json',
                    'location_id': 'location_mapping.json',
                },
                'ordre': 1055
            },
            
            # ==================================================================
            # TRANSACTIONS - FACTURES
            # ==================================================================
            
            'account.move': {
                'nom': 'Factures/Avoirs/Écritures',
                'fichier': 'account_move',
                'unique_field': 'name',
                'relations': {
                    'partner_id': 'partner_mapping.json',
                    'journal_id': 'account_journal_mapping.json',
                    'company_id': 'company_mapping.json',
                    'invoice_user_id': 'user_mapping.json',
                    'team_id': 'crm_team_mapping.json',
                },
                'ordre': 1060
            },
            
            'account.move.line': {
                'nom': 'Lignes comptables',
                'fichier': 'account_move_line',
                'unique_field': None,
                'relations': {
                    'move_id': 'account_move_mapping.json',
                    'account_id': 'account_mapping.json',
                    'partner_id': 'partner_mapping.json',
                    'product_id': 'product_mapping.json',
                    'tax_ids': 'tax_mapping.json',
                    'analytic_account_id': 'analytic_account_mapping.json',
                },
                'ordre': 1065
            },
            
            # ==================================================================
            # TRANSACTIONS - PAIEMENTS
            # ==================================================================
            
            'account.payment': {
                'nom': 'Paiements',
                'fichier': 'payment',
                'unique_field': 'name',
                'relations': {
                    'partner_id': 'partner_mapping.json',
                    'journal_id': 'account_journal_mapping.json',
                    'destination_journal_id': 'account_journal_mapping.json',
                },
                'ordre': 1070
            },
            
            'account.bank.statement': {
                'nom': 'Relevés bancaires',
                'fichier': 'bank_statement',
                'unique_field': 'name',
                'relations': {
                    'journal_id': 'account_journal_mapping.json',
                },
                'ordre': 1075
            },
            
            'account.bank.statement.line': {
                'nom': 'Lignes relevés bancaires',
                'fichier': 'bank_statement_line',
                'unique_field': None,
                'relations': {
                    'statement_id': 'bank_statement_mapping.json',
                    'partner_id': 'partner_mapping.json',
                },
                'ordre': 1080
            },
            
            'account.partial.reconcile': {
                'nom': 'Rapprochements partiels',
                'fichier': 'partial_reconcile',
                'unique_field': None,
                'relations': {
                    'debit_move_id': 'account_move_line_mapping.json',
                    'credit_move_id': 'account_move_line_mapping.json',
                },
                'ordre': 1085
            },
            
            'account.full.reconcile': {
                'nom': 'Rapprochements complets',
                'fichier': 'full_reconcile',
                'unique_field': 'name',
                'ordre': 1090
            },
            
            # ==================================================================
            # TRANSACTIONS - RH
            # ==================================================================
            
            'hr.expense': {
                'nom': 'Notes de frais (avec justificatifs)',
                'fichier': 'expense',
                'unique_field': 'name',
                'relations': {
                    'employee_id': 'employee_mapping.json',
                    'product_id': 'product_mapping.json',
                    'account_id': 'account_mapping.json',
                },
                'ordre': 1095
            },
            
            'hr.expense.sheet': {
                'nom': 'Feuilles de notes de frais',
                'fichier': 'expense_sheet',
                'unique_field': 'name',
                'relations': {
                    'employee_id': 'employee_mapping.json',
                    'user_id': 'user_mapping.json',
                },
                'ordre': 1100
            },
            
            'hr.leave.allocation': {
                'nom': 'Allocations de congés',
                'fichier': 'leave_allocation',
                'unique_field': None,
                'relations': {
                    'employee_id': 'employee_mapping.json',
                    'holiday_status_id': 'leave_type_mapping.json',
                },
                'ordre': 1105
            },
            
            'hr.leave': {
                'nom': 'Demandes de congés',
                'fichier': 'leave',
                'unique_field': None,
                'relations': {
                    'employee_id': 'employee_mapping.json',
                    'holiday_status_id': 'leave_type_mapping.json',
                },
                'ordre': 1110
            },
            
            # ==================================================================
            # TRANSACTIONS - ANALYTIQUE
            # ==================================================================
            
            'account.analytic.line': {
                'nom': 'Lignes analytiques',
                'fichier': 'analytic_line',
                'unique_field': None,
                'relations': {
                    'account_id': 'analytic_account_mapping.json',
                    'partner_id': 'partner_mapping.json',
                    'user_id': 'user_mapping.json',
                    'product_id': 'product_mapping.json',
                    'move_id': 'account_move_line_mapping.json',
                },
                'ordre': 1115
            },
            
            'crossovered.budget': {
                'nom': 'Budgets',
                'fichier': 'budget',
                'unique_field': 'name',
                'relations': {
                    'creating_user_id': 'user_mapping.json',
                },
                'ordre': 1120
            },
            
            'crossovered.budget.lines': {
                'nom': 'Lignes budgétaires',
                'fichier': 'budget_line',
                'unique_field': None,
                'relations': {
                    'crossovered_budget_id': 'budget_mapping.json',
                    'analytic_account_id': 'analytic_account_mapping.json',
                },
                'ordre': 1125
            },
            
            # ==================================================================
            # TRANSACTIONS - PROJETS ET TÂCHES
            # ==================================================================
            
            'project.task': {
                'nom': 'Tâches projets',
                'fichier': 'task',
                'unique_field': None,
                'relations': {
                    'project_id': 'project_mapping.json',
                    'user_ids': 'user_mapping.json',
                    'partner_id': 'partner_mapping.json',
                    'stage_id': 'task_type_mapping.json',
                    'parent_id': 'task_mapping.json',
                },
                'ordre': 1130
            },
            
            'account.analytic.line': {
                'nom': 'Feuilles de temps',
                'fichier': 'timesheet',
                'unique_field': None,
                'relations': {
                    'task_id': 'task_mapping.json',
                    'project_id': 'project_mapping.json',
                    'employee_id': 'employee_mapping.json',
                    'user_id': 'user_mapping.json',
                },
                'ordre': 1135
            },
            
            # ==================================================================
            # TRANSACTIONS - CRM
            # ==================================================================
            
            'crm.lead': {
                'nom': 'Leads/Opportunités',
                'fichier': 'lead',
                'unique_field': None,
                'relations': {
                    'partner_id': 'partner_mapping.json',
                    'user_id': 'user_mapping.json',
                    'team_id': 'crm_team_mapping.json',
                    'stage_id': 'crm_stage_mapping.json',
                },
                'ordre': 1140
            },
            
            # ==================================================================
            # FEUILLES DE CALCUL ET TABLEAUX DE BORD
            # ==================================================================
            
            'spreadsheet.template': {
                'nom': 'Modèles feuilles de calcul',
                'fichier': 'spreadsheet_template',
                'unique_field': 'name',
                'ordre': 1145
            },
            
            'documents.document': {
                'nom': 'Feuilles de calcul (documents)',
                'fichier': 'document_spreadsheet',
                'unique_field': None,
                'relations': {
                    'owner_id': 'user_mapping.json',
                    'folder_id': 'document_folder_mapping.json',
                },
                'ordre': 1150
            },
            
            'board.board': {
                'nom': 'Tableaux de bord',
                'fichier': 'board',
                'unique_field': 'name',
                'ordre': 1155
            },
            
            # ==================================================================
            # SITE WEB - STRUCTURE
            # ==================================================================
            
            'website': {
                'nom': 'Sites web',
                'fichier': 'website',
                'unique_field': 'name',
                'relations': {
                    'company_id': 'company_mapping.json',
                    'user_id': 'user_mapping.json',
                },
                'ordre': 1200
            },
            
            'website.page': {
                'nom': 'Pages du site web',
                'fichier': 'website_page',
                'unique_field': 'url',
                'relations': {
                    'website_id': 'website_mapping.json',
                    'view_id': 'view_mapping.json',
                },
                'ordre': 1205
            },
            
            'website.menu': {
                'nom': 'Menus du site web',
                'fichier': 'website_menu',
                'unique_field': 'name',
                'relations': {
                    'website_id': 'website_mapping.json',
                    'parent_id': 'website_menu_mapping.json',
                    'page_id': 'website_page_mapping.json',
                },
                'ordre': 1210
            },
            
            # ==================================================================
            # SITE WEB - E-COMMERCE
            # ==================================================================
            
            'product.public.category': {
                'nom': 'Catégories e-commerce',
                'fichier': 'product_public_category',
                'unique_field': 'name',
                'relations': {
                    'parent_id': 'product_public_category_mapping.json',
                    'website_id': 'website_mapping.json',
                },
                'ordre': 1215
            },
            
            'product.ribbon': {
                'nom': 'Rubans promotionnels',
                'fichier': 'product_ribbon',
                'unique_field': 'name',
                'ordre': 1220
            },
            
            'website.snippet.filter': {
                'nom': 'Filtres snippets',
                'fichier': 'snippet_filter',
                'unique_field': 'name',
                'relations': {
                    'website_id': 'website_mapping.json',
                },
                'ordre': 1225
            },
            
            # ==================================================================
            # SITE WEB - BLOG
            # ==================================================================
            
            'blog.blog': {
                'nom': 'Blogs',
                'fichier': 'blog',
                'unique_field': 'name',
                'relations': {
                    'website_id': 'website_mapping.json',
                },
                'ordre': 1230
            },
            
            'blog.post': {
                'nom': 'Articles de blog',
                'fichier': 'blog_post',
                'unique_field': 'name',
                'relations': {
                    'blog_id': 'blog_mapping.json',
                    'author_id': 'partner_mapping.json',
                    'website_id': 'website_mapping.json',
                },
                'ordre': 1235
            },
            
            'blog.tag': {
                'nom': 'Tags blog',
                'fichier': 'blog_tag',
                'unique_field': 'name',
                'ordre': 1237
            },
            
            # ==================================================================
            # SITE WEB - FORUM
            # ==================================================================
            
            'forum.forum': {
                'nom': 'Forums',
                'fichier': 'forum',
                'unique_field': 'name',
                'relations': {
                    'website_id': 'website_mapping.json',
                },
                'ordre': 1240
            },
            
            'forum.post': {
                'nom': 'Posts forum',
                'fichier': 'forum_post',
                'unique_field': None,
                'relations': {
                    'forum_id': 'forum_mapping.json',
                    'create_uid': 'user_mapping.json',
                },
                'ordre': 1245
            },
            
            # ==================================================================
            # SITE WEB - ÉVÉNEMENTS
            # ==================================================================
            
            'event.event': {
                'nom': 'Événements',
                'fichier': 'event',
                'unique_field': 'name',
                'relations': {
                    'user_id': 'user_mapping.json',
                    'website_id': 'website_mapping.json',
                },
                'ordre': 1250
            },
            
            'event.registration': {
                'nom': 'Inscriptions événements',
                'fichier': 'event_registration',
                'unique_field': None,
                'relations': {
                    'event_id': 'event_mapping.json',
                    'partner_id': 'partner_mapping.json',
                },
                'ordre': 1255
            },
            
            # ==================================================================
            # SITE WEB - SLIDES/E-LEARNING
            # ==================================================================
            
            'slide.channel': {
                'nom': 'Canaux de formation',
                'fichier': 'slide_channel',
                'unique_field': 'name',
                'relations': {
                    'website_id': 'website_mapping.json',
                    'user_id': 'user_mapping.json',
                },
                'ordre': 1260
            },
            
            'slide.slide': {
                'nom': 'Slides/Cours',
                'fichier': 'slide',
                'unique_field': None,
                'relations': {
                    'channel_id': 'slide_channel_mapping.json',
                    'user_id': 'user_mapping.json',
                },
                'ordre': 1265
            },
            
            # ==================================================================
            # SITE WEB - CONTENU
            # ==================================================================
            
            'website.redirect': {
                'nom': 'Redirections URL',
                'fichier': 'website_redirect',
                'unique_field': 'url_from',
                'relations': {
                    'website_id': 'website_mapping.json',
                },
                'ordre': 1270
            },
            
            'website.seo.metadata': {
                'nom': 'Métadonnées SEO',
                'fichier': 'seo_metadata',
                'unique_field': None,
                'ordre': 1275
            },
        }
    
    @staticmethod
    def obtenir_ordre_migration():
        """
        Retourne l'ordre de migration des modules
        Basé sur les dépendances
        
        Returns:
            list de modèles dans l'ordre
        """
        configs = GestionnaireConfiguration.obtenir_toutes_configs()
        
        # Trier par ordre
        modules_ordonnes = sorted(configs.items(), key=lambda x: x[1].get('ordre', 999))
        
        return [model for model, config in modules_ordonnes]
    
    @staticmethod
    def obtenir_modules_par_phase():
        """
        Retourne les modules groupés par phase
        
        Returns:
            dict {phase_nom: [modules]}
        """
        return {
            'Phase 1 - Utilisateurs': [
                'res.users',
            ],
            'Phase 2 - Comptabilité': [
                'account.account',
                'account.tax',
                'account.journal',
                'account.fiscal.position',
                'account.payment.term',
                'account.analytic.plan',
                'account.analytic.account',
            ],
            'Phase 3 - Partenaires': [
                'res.partner.industry',
                'res.partner.category',
                'res.partner',
                'res.partner.bank',
            ],
            'Phase 4 - RH': [
                'hr.department',
                'hr.job',
                'hr.employee',
                'hr.leave.type',
            ],
            'Phase 5 - Produits': [
                'product.category',
                'uom.category',
                'uom.uom',
                'product.template',
                'product.pricelist',
            ],
            'Phase 6 - Stock': [
                'stock.warehouse',
                'stock.location',
                'stock.picking.type',
            ],
            'Phase 7 - Ventes': [
                'crm.team',
                'crm.stage',
            ],
            'Phase 8 - Projets': [
                'project.project',
                'project.task.type',
            ],
            'Phase 9 - Documents et Fichiers': [
                'ir.attachment',
                'documents.document',
            ],
            'Phase 10 - Rapports et Templates': [
                'report.paperformat',
                'ir.actions.report',
                'mail.template',
                'sms.template',
            ],
            'Phase 11 - Automatisations et Actions': [
                'base.automation',
                'ir.actions.server',
                'ir.cron',
            ],
            'Phase 12 - Système': [
                'ir.sequence',
                'ir.sequence.date_range',
                'ir.config_parameter',
                'decimal.precision',
                'mail.activity.type',
            ],
            'Phase 13 - Automatisations': [
                'base.automation',
                'ir.actions.server',
                'ir.cron',
            ],
            'Phase 14 - Studio - Structure': [
                'ir.model',
                'ir.model.fields',
                'ir.ui.view',
                'ir.ui.menu',
                'ir.filters',
                'ir.rule',
            ],
            'Phase 15 - Chatter (après tout)': [
                'mail.message',
                'mail.followers',
                'mail.activity',
            ],
            
            # ==================================================================
            # PHASE 2 : TRANSACTIONS
            # ==================================================================
            
            'Phase 16 - Nomenclatures': [
                'mrp.bom',
                'mrp.bom.line',
            ],
            
            'Phase 17 - Ventes': [
                'sale.order',
                'sale.order.line',
            ],
            
            'Phase 18 - Achats': [
                'purchase.order',
                'purchase.order.line',
            ],
            
            'Phase 19 - Fabrication': [
                'mrp.production',
                'mrp.workorder',
            ],
            
            'Phase 20 - Stock': [
                'stock.picking',
                'stock.move',
                'stock.move.line',
                'stock.quant',
            ],
            
            'Phase 21 - Factures': [
                'account.move',  # Factures + Avoirs
                'account.move.line',
            ],
            
            'Phase 22 - Paiements': [
                'account.payment',
                'account.bank.statement',
                'account.bank.statement.line',
            ],
            
            'Phase 23 - Rapprochements': [
                'account.partial.reconcile',
                'account.full.reconcile',
            ],
            
            'Phase 24 - Notes de Frais': [
                'hr.expense',
                'hr.expense.sheet',
            ],
            
            'Phase 25 - Analytique Transactions': [
                'account.analytic.line',
            ],
        }

