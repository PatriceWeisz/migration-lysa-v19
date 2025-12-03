#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION DU PLAN COMPTABLE VERS V19
====================================
Script de migration du plan comptable (comptes comptables) vers Odoo v19
À exécuter AVANT la migration des partenaires
"""

import sys
from datetime import datetime
from connexion_double_v19 import ConnexionDoubleV19
from utils.logger import setup_logger
from utils.helpers import ProgressTracker, chunk_list, format_number
from utils.external_id_manager import ExternalIdManager
from config_v19 import MIGRATION_PARAMS

# Configuration du logger
logger = setup_logger('migration_plan_comptable')


class MigrationPlanComptable:
    """Classe pour gérer la migration du plan comptable"""
    
    def __init__(self, connexion):
        self.connexion = connexion
        self.ext_id_mgr = ExternalIdManager(connexion)
        self.stats = {
            'total_source': 0,
            'total_dest_avant': 0,
            'migres': 0,
            'existants': 0,
            'erreurs': 0,
            'ignores': 0,
        }
        # Mapping des IDs source -> destination
        self.account_mapping = {}
        
    def compter_comptes(self):
        """Compte les comptes dans les deux bases"""
        logger.section("COMPTAGE DES COMPTES COMPTABLES")
        
        # Source
        self.stats['total_source'] = self.connexion.compter_records(
            'account.account', 
            domain=[],
            base='source'
        )
        logger.info(f"Comptes dans SOURCE: {format_number(self.stats['total_source'])}")
        
        # Destination
        self.stats['total_dest_avant'] = self.connexion.compter_records(
            'account.account',
            domain=[],
            base='destination'
        )
        logger.info(f"Comptes dans DESTINATION: {format_number(self.stats['total_dest_avant'])}")
        
    def recuperer_comptes_source(self, limit=None):
        """Récupère les comptes de la source"""
        logger.info("Récupération des comptes source...")
        
        # Champs à récupérer
        # Note: La base source utilise déjà 'account_type' (v16 récent)
        fields = [
            'code', 'name',
            'account_type',  # Champ déjà présent en v16 récent
            'reconcile',
            'deprecated',
            'currency_id',
            'group_id',
            'company_id',
            'note',
        ]
        
        # Domaine (tous les comptes actifs)
        domain = [('deprecated', '=', False)]
        
        # Limite si spécifiée
        kwargs = {'fields': fields}
        if limit:
            kwargs['limit'] = limit
        
        # Récupération
        try:
            comptes = self.connexion.executer_source(
                'account.account',
                'search_read',
                domain,
                **kwargs
            )
            
            logger.info(f"✓ {len(comptes)} comptes récupérés")
            return comptes
        except Exception as e:
            logger.error(f"✗ Erreur récupération comptes: {e}")
            return []
    
    def verifier_existence(self, compte):
        """Vérifie si un compte existe déjà dans la destination"""
        # Vérifier par code (le code du compte est unique)
        if compte.get('code'):
            existing = self.connexion.executer_destination(
                'account.account',
                'search',
                [('code', '=', compte['code'])]
            )
            if existing:
                return existing[0]
        
        return None
    
    def mapper_account_type_from_user_type(self, user_type_id):
        """
        Mappe user_type_id (v16) vers account_type (v19)
        En v16, user_type_id est une relation vers account.account.type
        En v19, account_type est une sélection directe
        """
        # Mapping basé sur les noms internes des types v16
        type_mapping = {
            # Types v16 (nom interne) → type v19
            'receivable': 'asset_receivable',
            'payable': 'liability_payable',
            'liquidity': 'asset_cash',
            'other': 'asset_current',
            'equity': 'equity',
            'income': 'income',
            'income_other': 'income_other',
            'expense': 'expense',
            'expense_depreciation': 'expense_depreciation',
            'expense_direct_cost': 'expense_direct_cost',
            'asset_fixed': 'asset_non_current',
            'asset_current': 'asset_current',
            'asset_non_current': 'asset_non_current',
            'liability_current': 'liability_current',
            'liability_non_current': 'liability_non_current',
        }
        
        # Si c'est False ou None
        if not user_type_id:
            return 'asset_current'  # Type par défaut
        
        # Si c'est un tuple/liste (id, name)
        if isinstance(user_type_id, (list, tuple)) and len(user_type_id) >= 2:
            type_name = user_type_id[1]
            # Chercher dans le mapping par le nom
            for key, value in type_mapping.items():
                if key.lower() in type_name.lower():
                    return value
        
        # Retourner type par défaut
        return 'asset_current'
    
    def mapper_account_type(self, source_type):
        """
        Mappe les types de compte de v16 vers v19
        En v19, les types sont simplifiés
        """
        # Mapping des types principaux
        type_mapping = {
            # Actif
            'asset_receivable': 'asset_receivable',
            'asset_cash': 'asset_cash',
            'asset_current': 'asset_current',
            'asset_non_current': 'asset_non_current',
            'asset_prepayments': 'asset_prepayments',
            'asset_fixed': 'asset_non_current',
            
            # Passif
            'liability_payable': 'liability_payable',
            'liability_credit_card': 'liability_credit_card',
            'liability_current': 'liability_current',
            'liability_non_current': 'liability_non_current',
            
            # Equity
            'equity': 'equity',
            'equity_unaffected': 'equity_unaffected',
            
            # Revenus
            'income': 'income',
            'income_other': 'income_other',
            
            # Charges
            'expense': 'expense',
            'expense_depreciation': 'expense_depreciation',
            'expense_direct_cost': 'expense_direct_cost',
            
            # Hors bilan
            'off_balance': 'off_balance',
        }
        
        # Si c'est un tuple (id, name) depuis v16
        if isinstance(source_type, (list, tuple)) and len(source_type) >= 2:
            # Extraire le nom technique du type
            type_name = source_type[1] if isinstance(source_type[1], str) else str(source_type[0])
        else:
            type_name = str(source_type)
        
        # Retourner le type mappé ou le type par défaut
        return type_mapping.get(type_name, 'asset_current')
    
    def preparer_donnees(self, compte):
        """Prépare les données pour l'insertion"""
        # Champs obligatoires
        data = {
            'code': compte['code'],
            'name': compte['name'],
        }
        
        # Type de compte (obligatoire en v19)
        # La base source utilise déjà 'account_type' (string)
        if 'account_type' in compte and compte['account_type']:
            # Le type est déjà au bon format
            data['account_type'] = compte['account_type']
        else:
            # Type par défaut basé sur le code
            code = compte['code']
            if code.startswith('1'):
                data['account_type'] = 'asset_current'
            elif code.startswith('2'):
                data['account_type'] = 'liability_current'
            elif code.startswith('3'):
                data['account_type'] = 'equity'
            elif code.startswith('4'):
                if code.startswith('41'):
                    data['account_type'] = 'asset_receivable'
                elif code.startswith('40'):
                    data['account_type'] = 'liability_payable'
                else:
                    data['account_type'] = 'liability_current'
            elif code.startswith('5'):
                data['account_type'] = 'asset_cash'
            elif code.startswith('6'):
                data['account_type'] = 'expense'
            elif code.startswith('7'):
                data['account_type'] = 'income'
            else:
                data['account_type'] = 'asset_current'
        
        # Champs optionnels
        if compte.get('reconcile') is not None:
            data['reconcile'] = compte['reconcile']
        
        # Note: 'deprecated' n'existe plus en v19, remplacé par 'active' (inverse)
        # On ne migre PAS ce champ car Odoo v19 utilise 'active' par défaut à True
        
        if compte.get('note'):
            data['note'] = compte['note']
        
        # Company_id : peut être requis en SaaS
        # On ne le met pas car Odoo l'ajoutera automatiquement
        # Si nécessaire, décommenter :
        # if compte.get('company_id'):
        #     data['company_id'] = compte['company_id'][0] if isinstance(compte['company_id'], (list, tuple)) else compte['company_id']
        
        # Group (à mapper si existe dans destination)
        # Currency (à mapper si existe dans destination)
        # On ignore ces champs pour l'instant car ils nécessitent un mapping
        
        return data
    
    def migrer_compte(self, compte):
        """Migre un seul compte"""
        try:
            source_id = compte['id']
            
            # 1. Vérifier si existe déjà via external_id
            existe, dest_id, ext_id = self.ext_id_mgr.verifier_existe('account.account', source_id)
            if existe:
                if ext_id:
                    logger.debug(f"Compte '{compte['code']}' existe via external_id {ext_id['module']}.{ext_id['name']} (ID: {dest_id})")
                else:
                    logger.debug(f"Compte '{compte['code']}' existe (ID: {dest_id})")
                self.account_mapping[source_id] = dest_id
                self.stats['existants'] += 1
                return dest_id
            
            # 2. Sinon vérifier par code (doublon)
            if MIGRATION_PARAMS.get('VERIFIER_DOUBLONS', True):
                existing_id = self.verifier_existence(compte)
                if existing_id:
                    logger.debug(f"Compte '{compte['code']}' existe déjà (ID: {existing_id})")
                    # Copier l'external_id de la source si disponible
                    if ext_id:
                        self.ext_id_mgr.copier_external_id('account.account', existing_id, source_id)
                        logger.debug(f"  External_id copié: {ext_id['module']}.{ext_id['name']}")
                    # Stocker le mapping
                    self.account_mapping[source_id] = existing_id
                    self.stats['existants'] += 1
                    return existing_id
            
            # Mode simulation
            if MIGRATION_PARAMS.get('MODE_SIMULATION', False):
                logger.debug(f"[SIMULATION] Migration de '{compte['code']} - {compte['name']}'")
                self.stats['migres'] += 1
                return None
            
            # Préparer les données
            data = self.preparer_donnees(compte)
            
            # Créer le compte
            new_id = self.connexion.executer_destination(
                'account.account',
                'create',
                data
            )
            
            # Copier l'external_id de la source
            ext_id = self.ext_id_mgr.get_external_id_from_source('account.account', source_id)
            if ext_id:
                self.ext_id_mgr.copier_external_id('account.account', new_id, source_id)
                logger.debug(f"  External_id copié: {ext_id['module']}.{ext_id['name']}")
            
            # Stocker le mapping
            self.account_mapping[source_id] = new_id
            
            logger.debug(f"OK Compte '{compte['code']}' migre (ID: {new_id})")
            self.stats['migres'] += 1
            return new_id
            
        except Exception as e:
            logger.error(f"✗ Erreur migration '{compte.get('code', '?')}': {e}")
            self.stats['erreurs'] += 1
            return None
    
    def migrer_par_lots(self, comptes):
        """Migre les comptes par lots"""
        batch_size = MIGRATION_PARAMS.get('BATCH_SIZE', 100)
        chunks = chunk_list(comptes, batch_size)
        
        logger.section(f"MIGRATION PAR LOTS ({len(chunks)} lots de {batch_size})")
        
        tracker = ProgressTracker(len(comptes), "Migration plan comptable")
        
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"\nLot {i}/{len(chunks)} ({len(chunk)} comptes)")
            
            for compte in chunk:
                self.migrer_compte(compte)
                tracker.update()
                
                # Afficher progression tous les 10
                if tracker.current % 10 == 0:
                    tracker.display()
        
        tracker.finish()
    
    def sauvegarder_mapping(self):
        """Sauvegarde le mapping des comptes pour utilisation ultérieure"""
        import json
        import os
        
        mapping_file = os.path.join('logs', 'account_mapping.json')
        
        try:
            os.makedirs('logs', exist_ok=True)
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.account_mapping, f, indent=2)
            
            logger.info(f"✓ Mapping sauvegardé dans {mapping_file}")
            logger.info(f"  {len(self.account_mapping)} correspondances enregistrées")
            
        except Exception as e:
            logger.warning(f"⚠️  Impossible de sauvegarder le mapping: {e}")
    
    def afficher_statistiques(self):
        """Affiche les statistiques finales"""
        logger.section("STATISTIQUES DE MIGRATION")
        
        logger.info(f"Comptes source        : {format_number(self.stats['total_source'])}")
        logger.info(f"Dest avant migration  : {format_number(self.stats['total_dest_avant'])}")
        logger.info(f"Migrés avec succès    : {format_number(self.stats['migres'])}")
        logger.info(f"Ignorés (doublons)    : {format_number(self.stats['ignores'])}")
        logger.info(f"Erreurs               : {format_number(self.stats['erreurs'])}")
        
        # Compter après migration
        total_dest_apres = self.connexion.compter_records(
            'account.account',
            domain=[],
            base='destination'
        )
        logger.info(f"Dest après migration  : {format_number(total_dest_apres)}")
        
        nouveaux = total_dest_apres - self.stats['total_dest_avant']
        logger.info(f"Nouveaux comptes      : {format_number(nouveaux)}")
    
    def executer(self, limit=None):
        """Exécute la migration complète"""
        logger.section("DÉMARRAGE MIGRATION PLAN COMPTABLE")
        
        if MIGRATION_PARAMS.get('MODE_SIMULATION', False):
            logger.warning("⚠️  MODE SIMULATION ACTIVÉ - Aucune donnée ne sera écrite")
        
        # Comptage initial
        self.compter_comptes()
        
        # Récupération
        comptes = self.recuperer_comptes_source(limit)
        
        if not comptes:
            logger.warning("Aucun compte à migrer")
            return False
        
        # Trier par code pour avoir un ordre logique
        comptes.sort(key=lambda x: x.get('code', ''))
        
        # Migration
        self.migrer_par_lots(comptes)
        
        # Sauvegarder le mapping
        self.sauvegarder_mapping()
        
        # Statistiques
        self.afficher_statistiques()
        
        return True


def main():
    """Fonction principale"""
    logger.section("MIGRATION DU PLAN COMPTABLE VERS ODOO V19")
    
    # Connexion
    logger.info("Connexion aux bases...")
    connexion = ConnexionDoubleV19()
    
    if not connexion.connecter_tout():
        logger.error("✗ Échec de connexion aux bases")
        return False
    
    # Vérifier version v19
    if not connexion.verifier_version_destination():
        logger.warning("⚠️  La destination n'est peut-être pas en v19")
    
    # Migration
    migration = MigrationPlanComptable(connexion)
    
    # Limite pour tests (None = tous)
    limit = MIGRATION_PARAMS.get('MAX_RECORDS', None)
    if limit:
        logger.warning(f"⚠️  LIMITE DE TEST: {limit} enregistrements maximum")
    
    success = migration.executer(limit)
    
    # Statistiques de connexion
    connexion.afficher_stats()
    
    if success:
        logger.info("\n✓ Migration du plan comptable terminée avec succès")
        logger.info("✓ Le fichier de mapping est disponible dans logs/account_mapping.json")
    else:
        logger.error("\n✗ La migration a échoué")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

