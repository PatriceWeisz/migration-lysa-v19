#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GESTIONNAIRE DE STATUTS
========================
Gère la préservation des statuts (state) pour tous les documents
"""

class GestionnaireStatuts:
    """
    Gère les statuts des documents et leur préservation
    Certains documents ne peuvent pas être créés dans certains états
    """
    
    @staticmethod
    def obtenir_strategie_statut(model):
        """
        Retourne la stratégie de gestion du statut pour un modèle
        
        Returns:
            dict {
                'migrer_state': bool,  # Migrer le champ state ?
                'creer_en_draft': bool,  # Créer en draft puis valider ?
                'methode_validation': str,  # Méthode pour valider
                'etats_possibles': list,  # États possibles
            }
        """
        strategies = {
            # ==================================================================
            # FACTURES - CRITIQUE
            # ==================================================================
            'account.move': {
                'migrer_state': True,  # ✅ Important
                'creer_en_draft': True,  # ❌ Créer en draft d'abord
                'etats': {
                    'draft': {'action': None},  # Créer tel quel
                    'posted': {'action': 'action_post'},  # Créer draft puis poster
                    'cancel': {'action': 'button_cancel'},  # Créer draft puis annuler
                },
                'champs_supplementaires': {
                    'posted': ['invoice_date'],  # Date obligatoire pour poster
                }
            },
            
            # ==================================================================
            # COMMANDES VENTES
            # ==================================================================
            'sale.order': {
                'migrer_state': True,
                'creer_en_draft': True,
                'etats': {
                    'draft': {'action': None},
                    'sent': {'action': 'action_quotation_send'},
                    'sale': {'action': 'action_confirm'},  # Confirmer
                    'done': {'action': 'action_done'},
                    'cancel': {'action': 'action_cancel'},
                },
            },
            
            # ==================================================================
            # COMMANDES ACHATS
            # ==================================================================
            'purchase.order': {
                'migrer_state': True,
                'creer_en_draft': True,
                'etats': {
                    'draft': {'action': None},
                    'sent': {'action': 'button_confirm'},
                    'purchase': {'action': 'button_confirm'},
                    'done': {'action': 'button_done'},
                    'cancel': {'action': 'button_cancel'},
                },
            },
            
            # ==================================================================
            # STOCK - BONS LIVRAISON/RÉCEPTION
            # ==================================================================
            'stock.picking': {
                'migrer_state': True,
                'creer_en_draft': True,
                'etats': {
                    'draft': {'action': None},
                    'confirmed': {'action': 'action_confirm'},
                    'assigned': {'action': 'action_assign'},  # Réserver
                    'done': {'action': 'button_validate'},  # Valider
                    'cancel': {'action': 'action_cancel'},
                },
                'champs_supplementaires': {
                    'done': ['date_done'],  # Date validation
                }
            },
            
            # ==================================================================
            # FABRICATION
            # ==================================================================
            'mrp.production': {
                'migrer_state': True,
                'creer_en_draft': True,
                'etats': {
                    'draft': {'action': None},
                    'confirmed': {'action': 'action_confirm'},
                    'progress': {'action': 'button_mark_done'},  # Commencer
                    'done': {'action': 'button_mark_done'},  # Terminer
                    'cancel': {'action': 'action_cancel'},
                },
            },
            
            # ==================================================================
            # PAIEMENTS
            # ==================================================================
            'account.payment': {
                'migrer_state': True,
                'creer_en_draft': True,
                'etats': {
                    'draft': {'action': None},
                    'posted': {'action': 'action_post'},  # Valider
                    'sent': {'action': None},
                    'reconciled': {'action': None},  # Auto après rapprochement
                    'cancel': {'action': 'action_cancel'},
                },
            },
            
            # ==================================================================
            # NOTES DE FRAIS
            # ==================================================================
            'hr.expense': {
                'migrer_state': True,
                'creer_en_draft': True,
                'etats': {
                    'draft': {'action': None},
                    'reported': {'action': 'action_submit_expenses'},  # Soumettre
                    'approved': {'action': 'approve_expense_sheets'},  # Approuver
                    'done': {'action': 'action_sheet_move_create'},  # Comptabiliser
                    'refused': {'action': 'refuse_expense'},  # Refuser
                },
            },
            
            # ==================================================================
            # CONGÉS
            # ==================================================================
            'hr.leave': {
                'migrer_state': True,
                'creer_en_draft': False,  # Peut créer dans l'état final
                'etats': {
                    'draft': {'action': None},
                    'confirm': {'action': 'action_confirm'},
                    'validate': {'action': 'action_validate'},  # Approuver
                    'refuse': {'action': 'action_refuse'},  # Refuser
                },
            },
            
            # ==================================================================
            # CRM
            # ==================================================================
            'crm.lead': {
                'migrer_state': False,  # Pas de state, utilise stage_id
                'champ_statut': 'stage_id',  # Utiliser stage au lieu de state
            },
            
            # ==================================================================
            # PROJETS/TÂCHES
            # ==================================================================
            'project.task': {
                'migrer_state': False,  # Pas de state, utilise stage_id
                'champ_statut': 'stage_id',
            },
        }
        
        return strategies.get(model, {
            'migrer_state': True,  # Par défaut, migrer le state
            'creer_en_draft': False,  # Créer dans l'état final
        })
    
    @staticmethod
    def appliquer_statut(connexion, model, dest_id, state_source, strategy):
        """
        Applique le bon statut à un enregistrement créé
        
        Args:
            connexion: ConnexionDoubleV19
            model: Nom du modèle
            dest_id: ID dans la destination
            state_source: État dans la source
            strategy: Stratégie du modèle
        
        Returns:
            bool: Succès ou échec
        """
        if not strategy.get('migrer_state'):
            return True
        
        # Si pas besoin de créer en draft
        if not strategy.get('creer_en_draft'):
            return True
        
        # Obtenir l'action pour cet état
        etats = strategy.get('etats', {})
        etat_config = etats.get(state_source, {})
        action = etat_config.get('action')
        
        if not action:
            return True  # Pas d'action nécessaire
        
        try:
            # Exécuter l'action pour changer l'état
            connexion.executer_destination(model, action, [dest_id])
            return True
        except Exception as e:
            # Log l'erreur mais ne pas bloquer
            print(f"ATTENTION: Impossible d'appliquer état {state_source}: {str(e)[:60]}")
            return False
    
    @staticmethod
    def obtenir_champs_supplementaires(model, state):
        """
        Retourne les champs supplémentaires nécessaires pour un état
        
        Exemple: Pour poster une facture, invoice_date est obligatoire
        """
        strategy = GestionnaireStatuts.obtenir_strategie_statut(model)
        champs_supp = strategy.get('champs_supplementaires', {})
        return champs_supp.get(state, [])

