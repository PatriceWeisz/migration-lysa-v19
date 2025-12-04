#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ANALYSEUR DES DIFFÉRENCES DE CHAMPS v16 → v19
==============================================
Identifie les changements de noms, champs disparus, nouveaux champs obligatoires
"""

class AnalyseurDifferencesChamps:
    """Analyse les différences de champs entre v16 et v19"""
    
    def __init__(self, connexion):
        self.conn = connexion
        self.differences = {}
    
    def analyser_module(self, model):
        """
        Analyse les différences de champs pour un module
        
        Returns:
            dict {
                'champs_renommes': {'ancien_nom': 'nouveau_nom'},
                'champs_disparus': ['champ1', 'champ2'],
                'nouveaux_obligatoires': ['champ3', 'champ4'],
                'transformations': {'champ': fonction_transformation}
            }
        """
        # Récupérer champs SOURCE
        fields_src = self.conn.executer_source('ir.model.fields', 'search_read',
                                              [('model', '=', model), ('store', '=', True)],
                                              fields=['name', 'ttype', 'required'])
        
        src_dict = {f['name']: f for f in fields_src}
        
        # Récupérer champs DESTINATION
        fields_dst = self.conn.executer_destination('ir.model.fields', 'search_read',
                                                   [('model', '=', model), ('store', '=', True)],
                                                   fields=['name', 'ttype', 'required'])
        
        dst_dict = {f['name']: f for f in fields_dst}
        
        # Analyse
        result = {
            'champs_renommes': {},
            'champs_disparus': [],
            'nouveaux_obligatoires': [],
            'transformations': {},
            'mappings_connus': {}  # Mappings connus pour ce module
        }
        
        # Champs disparus
        for fname in src_dict:
            if fname not in dst_dict:
                result['champs_disparus'].append(fname)
        
        # Nouveaux champs obligatoires
        for fname in dst_dict:
            if fname not in src_dict and dst_dict[fname].get('required'):
                result['nouveaux_obligatoires'].append(fname)
        
        # Mappings connus par module (historique des changements v16→v19)
        result['mappings_connus'] = self._obtenir_mappings_connus(model)
        
        return result
    
    def _obtenir_mappings_connus(self, model):
        """
        Retourne les mappings de champs connus pour un module spécifique
        Basé sur l'expérience de migration v16 → v19
        """
        mappings_connus = {
            'account.account': {
                'champs_renommes': {
                    'user_type_id': 'account_type',  # many2one → selection
                },
                'champs_disparus': ['deprecated'],
                'transformations': {
                    # user_type_id était many2one, account_type est selection
                    'user_type_id': lambda val: self._convertir_user_type_id(val)
                },
                'nouveaux_obligatoires_defaults': {
                    'account_type': 'asset_receivable'  # Valeur par défaut si manquant
                }
            },
            
            'product.template': {
                'champs_disparus': ['mobile', 'detailed_type'],
                'transformations': {
                    # En v16: type='product' → En v19: type='consu' + is_storable=True
                    'type': lambda val: 'consu' if val == 'product' else val
                },
                'champs_ajoutes_si': {
                    # Si type était 'product', ajouter is_storable=True
                    'is_storable': lambda rec: True if rec.get('type') == 'product' else False
                },
                'nouveaux_obligatoires_defaults': {
                    'is_storable': False
                }
            },
            
            'res.partner': {
                'champs_disparus': ['mobile'],
                'transformations': {
                    # Si mobile existe mais pas phone, copier mobile vers phone
                    '_copy_mobile_to_phone': lambda rec: rec.get('mobile') if not rec.get('phone') else None
                },
                'nouveaux_obligatoires_defaults': {
                    'autopost_bills': 'ask',
                    'group_on': 'default',
                    'group_rfq': 'default'
                }
            },
            
            'account.journal': {
                'champs_disparus': ['payment_debit_account_id', 'payment_credit_account_id'],
            },
            
            'res.users': {
                'champs_ajoutes_si': {
                    'password': lambda rec: 'ChangeMe123!'  # Obligatoire à la création
                }
            },
            
            'project.project': {
                'nouveaux_obligatoires_defaults': {
                    'privacy_visibility': 'employees',
                    'alias_contact': 'everyone',
                }
            },
            
            'account.analytic.account': {
                'nouveaux_obligatoires_defaults': {
                    'plan_id': 2  # Plan par défaut
                }
            }
        }
        
        return mappings_connus.get(model, {})
    
    def _convertir_user_type_id(self, val):
        """Convertit user_type_id (many2one) en account_type (selection)"""
        # Mapping des IDs de user_type vers les valeurs de selection
        mapping = {
            1: 'asset_receivable',
            2: 'asset_cash',
            3: 'asset_current',
            4: 'asset_non_current',
            5: 'asset_prepayments',
            6: 'asset_fixed',
            7: 'liability_payable',
            8: 'liability_credit_card',
            9: 'liability_current',
            10: 'liability_non_current',
            11: 'equity',
            12: 'equity_unaffected',
            13: 'income',
            14: 'income_other',
            15: 'expense',
            16: 'expense_depreciation',
            17: 'expense_direct_cost',
            18: 'off_balance'
        }
        
        if isinstance(val, (list, tuple)):
            type_id = val[0]
            return mapping.get(type_id, 'asset_receivable')
        
        return 'asset_receivable'
    
    def appliquer_transformations(self, model, rec_source):
        """
        Applique les transformations connues pour un enregistrement
        
        Args:
            model: Nom du modèle
            rec_source: Enregistrement source
        
        Returns:
            dict: Enregistrement transformé pour v19
        """
        mappings = self._obtenir_mappings_connus(model)
        rec_dest = rec_source.copy()
        
        # Appliquer renommages
        for ancien, nouveau in mappings.get('champs_renommes', {}).items():
            if ancien in rec_dest:
                rec_dest[nouveau] = rec_dest.pop(ancien)
        
        # Supprimer champs disparus
        for champ in mappings.get('champs_disparus', []):
            rec_dest.pop(champ, None)
        
        # Appliquer transformations
        for champ, func in mappings.get('transformations', {}).items():
            if champ in rec_dest:
                rec_dest[champ] = func(rec_dest[champ])
        
        # Ajouter nouveaux champs obligatoires avec defaults
        for champ, default in mappings.get('nouveaux_obligatoires_defaults', {}).items():
            if champ not in rec_dest:
                if callable(default):
                    rec_dest[champ] = default(rec_source)
                else:
                    rec_dest[champ] = default
        
        # Ajouter champs conditionnels
        for champ, func in mappings.get('champs_ajoutes_si', {}).items():
            if champ not in rec_dest:
                valeur = func(rec_source)
                if valeur is not None:
                    rec_dest[champ] = valeur
        
        return rec_dest

