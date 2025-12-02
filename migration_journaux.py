#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION DES JOURNAUX VERS V19
===============================
Script de migration des journaux comptables vers Odoo v19
À exécuter APRÈS le plan comptable
"""

import sys
from datetime import datetime
from connexion_double_v19 import ConnexionDoubleV19
from utils.logger import setup_logger
from utils.helpers import ProgressTracker, chunk_list, format_number
from config_v19 import MIGRATION_PARAMS

# Configuration du logger
logger = setup_logger('migration_journaux')


class MigrationJournaux:
    """Classe pour gérer la migration des journaux"""
    
    def __init__(self, connexion):
        self.connexion = connexion
        self.stats = {
            'total_source': 0,
            'total_dest_avant': 0,
            'migres': 0,
            'erreurs': 0,
            'ignores': 0,
        }
        # Mapping des IDs source -> destination
        self.journal_mapping = {}
        
    def compter_journaux(self):
        """Compte les journaux dans les deux bases"""
        logger.section("COMPTAGE DES JOURNAUX")
        
        # Source
        self.stats['total_source'] = self.connexion.compter_records(
            'account.journal', 
            domain=[],
            base='source'
        )
        logger.info(f"Journaux dans SOURCE: {format_number(self.stats['total_source'])}")
        
        # Destination
        self.stats['total_dest_avant'] = self.connexion.compter_records(
            'account.journal',
            domain=[],
            base='destination'
        )
        logger.info(f"Journaux dans DESTINATION: {format_number(self.stats['total_dest_avant'])}")
        
    def recuperer_journaux_source(self, limit=None):
        """Récupère les journaux de la source"""
        logger.info("Récupération des journaux source...")
        
        # Champs à récupérer
        fields = [
            'id', 'name', 'code', 'type',
            'active',
            'sequence',
            'currency_id',
            'company_id',
            # Comptes par défaut (à mapper)
            # 'default_account_id',
            # 'suspense_account_id',
            # 'profit_account_id',
            # 'loss_account_id',
        ]
        
        # Domaine (tous les journaux)
        domain = []
        
        # Limite si spécifiée
        kwargs = {'fields': fields}
        if limit:
            kwargs['limit'] = limit
        
        # Récupération
        try:
            journaux = self.connexion.executer_source(
                'account.journal',
                'search_read',
                domain,
                **kwargs
            )
            
            logger.info(f"✓ {len(journaux)} journaux récupérés")
            return journaux
        except Exception as e:
            logger.error(f"✗ Erreur récupération journaux: {e}")
            return []
    
    def verifier_existence(self, journal):
        """Vérifie si un journal existe déjà dans la destination"""
        # Vérifier par code (le code du journal est unique)
        if journal.get('code'):
            existing = self.connexion.executer_destination(
                'account.journal',
                'search',
                [('code', '=', journal['code'])]
            )
            if existing:
                return existing[0]
        
        # Vérifier par nom et type
        if journal.get('name') and journal.get('type'):
            existing = self.connexion.executer_destination(
                'account.journal',
                'search',
                [('name', '=', journal['name']), ('type', '=', journal['type'])]
            )
            if existing:
                return existing[0]
        
        return None
    
    def preparer_donnees(self, journal):
        """Prépare les données pour l'insertion"""
        # Champs obligatoires
        data = {
            'name': journal['name'],
            'code': journal['code'],
            'type': journal['type'],
        }
        
        # Champs optionnels
        if journal.get('active') is not None:
            data['active'] = journal['active']
        
        if journal.get('sequence'):
            data['sequence'] = journal['sequence']
        
        # Currency et Company : Odoo les gérera automatiquement en SaaS
        # On ne les migre pas pour éviter les conflits
        
        # Note: Les comptes par défaut nécessiteraient le mapping account_mapping.json
        # Pour l'instant, on les ignore. Odoo v19 les créera automatiquement.
        
        return data
    
    def migrer_journal(self, journal):
        """Migre un seul journal"""
        try:
            # Vérifier si existe déjà
            if MIGRATION_PARAMS.get('VERIFIER_DOUBLONS', True):
                existing_id = self.verifier_existence(journal)
                if existing_id:
                    logger.debug(f"Journal '{journal['code']}' existe déjà (ID: {existing_id})")
                    # Stocker le mapping
                    self.journal_mapping[journal['id']] = existing_id
                    self.stats['ignores'] += 1
                    return existing_id
            
            # Mode simulation
            if MIGRATION_PARAMS.get('MODE_SIMULATION', False):
                logger.debug(f"[SIMULATION] Migration de '{journal['code']} - {journal['name']}'")
                self.stats['migres'] += 1
                return None
            
            # Préparer les données
            data = self.preparer_donnees(journal)
            
            # Créer le journal
            new_id = self.connexion.executer_destination(
                'account.journal',
                'create',
                data
            )
            
            # Stocker le mapping
            self.journal_mapping[journal['id']] = new_id
            
            logger.debug(f"✓ Journal '{journal['code']}' migré (ID: {new_id})")
            self.stats['migres'] += 1
            return new_id
            
        except Exception as e:
            logger.error(f"✗ Erreur migration '{journal.get('code', '?')}': {e}")
            self.stats['erreurs'] += 1
            return None
    
    def migrer_tous(self, journaux):
        """Migre tous les journaux (pas de lots car peu nombreux)"""
        logger.section(f"MIGRATION DES JOURNAUX ({len(journaux)} journaux)")
        
        tracker = ProgressTracker(len(journaux), "Migration journaux")
        
        for journal in journaux:
            self.migrer_journal(journal)
            tracker.update()
            tracker.display()
        
        tracker.finish()
    
    def sauvegarder_mapping(self):
        """Sauvegarde le mapping des journaux pour utilisation ultérieure"""
        import json
        import os
        
        mapping_file = os.path.join('logs', 'journal_mapping.json')
        
        try:
            os.makedirs('logs', exist_ok=True)
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.journal_mapping, f, indent=2)
            
            logger.info(f"✓ Mapping sauvegardé dans {mapping_file}")
            logger.info(f"  {len(self.journal_mapping)} correspondances enregistrées")
            
        except Exception as e:
            logger.warning(f"⚠️  Impossible de sauvegarder le mapping: {e}")
    
    def afficher_statistiques(self):
        """Affiche les statistiques finales"""
        logger.section("STATISTIQUES DE MIGRATION")
        
        logger.info(f"Journaux source       : {format_number(self.stats['total_source'])}")
        logger.info(f"Dest avant migration  : {format_number(self.stats['total_dest_avant'])}")
        logger.info(f"Migrés avec succès    : {format_number(self.stats['migres'])}")
        logger.info(f"Ignorés (doublons)    : {format_number(self.stats['ignores'])}")
        logger.info(f"Erreurs               : {format_number(self.stats['erreurs'])}")
        
        # Compter après migration
        total_dest_apres = self.connexion.compter_records(
            'account.journal',
            domain=[],
            base='destination'
        )
        logger.info(f"Dest après migration  : {format_number(total_dest_apres)}")
        
        nouveaux = total_dest_apres - self.stats['total_dest_avant']
        logger.info(f"Nouveaux journaux     : {format_number(nouveaux)}")
        
        # Afficher la répartition par type
        self.afficher_types()
    
    def afficher_types(self):
        """Affiche la répartition des journaux par type"""
        logger.info("\nRépartition par type dans DESTINATION:")
        
        types = ['sale', 'purchase', 'cash', 'bank', 'general']
        
        for jtype in types:
            count = self.connexion.compter_records(
                'account.journal',
                domain=[('type', '=', jtype)],
                base='destination'
            )
            logger.info(f"  - {jtype:15s}: {count:>3}")
    
    def executer(self, limit=None):
        """Exécute la migration complète"""
        logger.section("DÉMARRAGE MIGRATION JOURNAUX")
        
        if MIGRATION_PARAMS.get('MODE_SIMULATION', False):
            logger.warning("⚠️  MODE SIMULATION ACTIVÉ - Aucune donnée ne sera écrite")
        
        # Comptage initial
        self.compter_journaux()
        
        # Récupération
        journaux = self.recuperer_journaux_source(limit)
        
        if not journaux:
            logger.warning("Aucun journal à migrer")
            return False
        
        # Trier par type puis par code
        journaux.sort(key=lambda x: (x.get('type', ''), x.get('code', '')))
        
        # Migration (pas de lots car peu de journaux)
        self.migrer_tous(journaux)
        
        # Sauvegarder le mapping
        self.sauvegarder_mapping()
        
        # Statistiques
        self.afficher_statistiques()
        
        return True


def main():
    """Fonction principale"""
    logger.section("MIGRATION DES JOURNAUX VERS ODOO V19")
    
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
    migration = MigrationJournaux(connexion)
    
    # Limite pour tests (None = tous)
    limit = MIGRATION_PARAMS.get('MAX_RECORDS', None)
    if limit:
        logger.warning(f"⚠️  LIMITE DE TEST: {limit} enregistrements maximum")
    
    success = migration.executer(limit)
    
    # Statistiques de connexion
    connexion.afficher_stats()
    
    if success:
        logger.info("\n✓ Migration des journaux terminée avec succès")
        logger.info("✓ Le fichier de mapping est disponible dans logs/journal_mapping.json")
    else:
        logger.error("\n✗ La migration a échoué")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

