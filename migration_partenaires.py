#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION DES PARTENAIRES VERS V19
==================================
Script de migration des clients et fournisseurs vers Odoo v19
"""

import sys
from datetime import datetime
from connexion_double_v19 import ConnexionDoubleV19
from utils.logger import setup_logger
from utils.helpers import ProgressTracker, chunk_list, format_number
from config_v19 import MIGRATION_PARAMS

# Configuration du logger
logger = setup_logger('migration_partenaires')


class MigrationPartenaires:
    """Classe pour gérer la migration des partenaires"""
    
    def __init__(self, connexion):
        self.connexion = connexion
        self.stats = {
            'total_source': 0,
            'total_dest_avant': 0,
            'migres': 0,
            'erreurs': 0,
            'ignores': 0,
        }
        
    def compter_partenaires(self):
        """Compte les partenaires dans les deux bases"""
        logger.section("COMPTAGE DES PARTENAIRES")
        
        # Source
        self.stats['total_source'] = self.connexion.compter_records(
            'res.partner', 
            domain=[],
            base='source'
        )
        logger.info(f"Partenaires dans SOURCE: {format_number(self.stats['total_source'])}")
        
        # Destination
        self.stats['total_dest_avant'] = self.connexion.compter_records(
            'res.partner',
            domain=[],
            base='destination'
        )
        logger.info(f"Partenaires dans DESTINATION: {format_number(self.stats['total_dest_avant'])}")
        
    def recuperer_partenaires_source(self, limit=None):
        """Récupère les partenaires de la source"""
        logger.info("Récupération des partenaires source...")
        
        # Champs à récupérer
        fields = [
            'id', 'name', 'email', 'phone', 'mobile',
            'street', 'street2', 'city', 'zip',
            'country_id', 'state_id',
            'vat', 'ref',
            'customer_rank', 'supplier_rank',
            'is_company', 'parent_id',
            'comment',
        ]
        
        # Domaine (tous les partenaires, y compris ceux sans nom pour les traiter)
        domain = []
        
        # Limite si spécifiée
        kwargs = {'fields': fields}
        if limit:
            kwargs['limit'] = limit
        
        # Récupération
        partenaires = self.connexion.executer_source(
            'res.partner',
            'search_read',
            domain,
            **kwargs
        )
        
        logger.info(f"✓ {len(partenaires)} partenaires récupérés")
        return partenaires
    
    def verifier_existence(self, partenaire):
        """Vérifie si un partenaire existe déjà dans la destination"""
        # Vérifier par VAT si présent
        if partenaire.get('vat'):
            existing = self.connexion.executer_destination(
                'res.partner',
                'search',
                [('vat', '=', partenaire['vat'])]
            )
            if existing:
                return existing[0]
        
        # Vérifier par ref si présent
        if partenaire.get('ref'):
            existing = self.connexion.executer_destination(
                'res.partner',
                'search',
                [('ref', '=', partenaire['ref'])]
            )
            if existing:
                return existing[0]
        
        # Vérifier par nom exact
        existing = self.connexion.executer_destination(
            'res.partner',
            'search',
            [('name', '=', partenaire['name'])]
        )
        if existing:
            return existing[0]
        
        return None
    
    def preparer_donnees(self, partenaire):
        """Prépare les données pour l'insertion"""
        # Le nom est OBLIGATOIRE en v19
        # Si le nom est vide ou False, utiliser un nom par défaut
        name = partenaire.get('name', '')
        
        # Gérer le cas où name est False (booléen) au lieu d'une chaîne
        if not isinstance(name, str):
            name = ''
        
        name = name.strip()
        
        if not name:
            # Générer un nom par défaut basé sur l'ID ou l'email
            if partenaire.get('email'):
                name = f"Contact {partenaire['email']}"
            elif partenaire.get('ref'):
                name = f"Contact {partenaire['ref']}"
            else:
                name = f"Contact {partenaire['id']}"
            logger.warning(f"⚠️  Partenaire sans nom (ID: {partenaire['id']}), nom généré: {name}")
        
        data = {
            'name': name,
        }
        
        # Champs optionnels
        optional_fields = [
            'email', 'phone', 'mobile',
            'street', 'street2', 'city', 'zip',
            'vat', 'ref', 'comment',
            'customer_rank', 'supplier_rank',
            'is_company',
        ]
        
        for field in optional_fields:
            if partenaire.get(field):
                data[field] = partenaire[field]
        
        # Gestion des relations (country_id, state_id, parent_id)
        # Pour la migration, on va les ignorer dans un premier temps
        # car il faudrait mapper les IDs entre les bases
        
        return data
    
    def migrer_partenaire(self, partenaire):
        """Migre un seul partenaire"""
        try:
            # Vérifier si existe déjà
            if MIGRATION_PARAMS.get('VERIFIER_DOUBLONS', True):
                existing_id = self.verifier_existence(partenaire)
                if existing_id:
                    logger.debug(f"Partenaire '{partenaire['name']}' existe déjà (ID: {existing_id})")
                    self.stats['ignores'] += 1
                    return existing_id
            
            # Mode simulation
            if MIGRATION_PARAMS.get('MODE_SIMULATION', False):
                logger.debug(f"[SIMULATION] Migration de '{partenaire['name']}'")
                self.stats['migres'] += 1
                return None
            
            # Préparer les données
            data = self.preparer_donnees(partenaire)
            
            # Créer le partenaire
            new_id = self.connexion.executer_destination(
                'res.partner',
                'create',
                data
            )
            
            logger.debug(f"✓ Partenaire '{partenaire['name']}' migré (ID: {new_id})")
            self.stats['migres'] += 1
            return new_id
            
        except Exception as e:
            logger.error(f"✗ Erreur migration '{partenaire.get('name', '?')}': {e}")
            self.stats['erreurs'] += 1
            return None
    
    def migrer_par_lots(self, partenaires):
        """Migre les partenaires par lots"""
        batch_size = MIGRATION_PARAMS.get('BATCH_SIZE', 200)
        chunks = chunk_list(partenaires, batch_size)
        
        logger.section(f"MIGRATION PAR LOTS ({len(chunks)} lots de {batch_size})")
        
        tracker = ProgressTracker(len(partenaires), "Migration partenaires")
        
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"\nLot {i}/{len(chunks)} ({len(chunk)} partenaires)")
            
            for partenaire in chunk:
                self.migrer_partenaire(partenaire)
                tracker.update()
                
                # Afficher progression tous les 10
                if tracker.current % 10 == 0:
                    tracker.display()
        
        tracker.finish()
    
    def afficher_statistiques(self):
        """Affiche les statistiques finales"""
        logger.section("STATISTIQUES DE MIGRATION")
        
        logger.info(f"Partenaires source    : {format_number(self.stats['total_source'])}")
        logger.info(f"Dest avant migration  : {format_number(self.stats['total_dest_avant'])}")
        logger.info(f"Migrés avec succès    : {format_number(self.stats['migres'])}")
        logger.info(f"Ignorés (doublons)    : {format_number(self.stats['ignores'])}")
        logger.info(f"Erreurs               : {format_number(self.stats['erreurs'])}")
        
        # Compter après migration
        total_dest_apres = self.connexion.compter_records(
            'res.partner',
            domain=[],
            base='destination'
        )
        logger.info(f"Dest après migration  : {format_number(total_dest_apres)}")
        
        nouveaux = total_dest_apres - self.stats['total_dest_avant']
        logger.info(f"Nouveaux partenaires  : {format_number(nouveaux)}")
    
    def executer(self, limit=None):
        """Exécute la migration complète"""
        logger.section("DÉMARRAGE MIGRATION PARTENAIRES")
        
        if MIGRATION_PARAMS.get('MODE_SIMULATION', False):
            logger.warning("⚠️  MODE SIMULATION ACTIVÉ - Aucune donnée ne sera écrite")
        
        # Comptage initial
        self.compter_partenaires()
        
        # Récupération
        partenaires = self.recuperer_partenaires_source(limit)
        
        if not partenaires:
            logger.warning("Aucun partenaire à migrer")
            return False
        
        # Migration
        self.migrer_par_lots(partenaires)
        
        # Statistiques
        self.afficher_statistiques()
        
        return True


def main():
    """Fonction principale"""
    logger.section("MIGRATION DES PARTENAIRES VERS ODOO V19")
    
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
    migration = MigrationPartenaires(connexion)
    
    # Limite pour tests (None = tous)
    limit = MIGRATION_PARAMS.get('MAX_RECORDS', None)
    if limit:
        logger.warning(f"⚠️  LIMITE DE TEST: {limit} enregistrements maximum")
    
    success = migration.executer(limit)
    
    # Statistiques de connexion
    connexion.afficher_stats()
    
    if success:
        logger.info("\n✓ Migration des partenaires terminée avec succès")
    else:
        logger.error("\n✗ La migration a échoué")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

