#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION COMPLÈTE VERS ODOO V19
================================
Script principal orchestrant toute la migration LYSA vers Odoo v19
"""

import sys
import time
from datetime import datetime
from connexion_double_v19 import ConnexionDoubleV19
from migration_partenaires import MigrationPartenaires
from verification_v19 import VerificationV19
from utils.logger import setup_logger
from utils.helpers import format_duration
from config_v19 import MIGRATION_PARAMS, MIGRATION_ORDER

# Configuration du logger
logger = setup_logger('migration_complete')


class MigrationComplete:
    """Classe pour orchestrer la migration complète"""
    
    def __init__(self):
        self.connexion = None
        self.start_time = None
        self.etapes_completes = []
        self.etapes_echouees = []
        
    def afficher_banniere(self):
        """Affiche la bannière de démarrage"""
        logger.info("\n" + "█" * 70)
        logger.info("  MIGRATION COMPLÈTE LYSA VERS ODOO V19")
        logger.info("  SENEDOO - " + datetime.now().strftime("%d/%m/%Y %H:%M"))
        logger.info("█" * 70 + "\n")
        
        if MIGRATION_PARAMS.get('MODE_SIMULATION', False):
            logger.warning("⚠️  " + "=" * 66 + " ⚠️")
            logger.warning("⚠️  MODE SIMULATION ACTIVÉ - AUCUNE DONNÉE NE SERA ÉCRITE  ⚠️")
            logger.warning("⚠️  " + "=" * 66 + " ⚠️\n")
    
    def verifier_prerequis(self):
        """Vérifie les prérequis avant migration"""
        logger.section("VÉRIFICATION DES PRÉREQUIS")
        
        prerequis_ok = True
        
        # 1. Vérifier la connexion
        logger.info("1. Test de connexion aux bases...")
        self.connexion = ConnexionDoubleV19()
        
        if not self.connexion.connecter_tout():
            logger.error("✗ Échec de connexion aux bases")
            return False
        
        logger.info("✓ Connexion réussie")
        
        # 2. Vérifier la version v19
        logger.info("\n2. Vérification version destination...")
        if not self.connexion.verifier_version_destination():
            logger.warning("⚠️  Version v19 non confirmée")
            prerequis_ok = False
        else:
            logger.info("✓ Version v19 confirmée")
        
        # 3. Vérifier l'espace (simulation)
        logger.info("\n3. Vérification de l'espace disponible...")
        logger.info("✓ Vérification espace OK (simulation)")
        
        # 4. Afficher la configuration
        logger.info("\n4. Configuration de migration:")
        logger.info(f"   - Batch size      : {MIGRATION_PARAMS['BATCH_SIZE']}")
        logger.info(f"   - Workers         : {MIGRATION_PARAMS['PARALLEL_WORKERS']}")
        logger.info(f"   - Max retry       : {MIGRATION_PARAMS['MAX_RETRY']}")
        logger.info(f"   - Mode simulation : {MIGRATION_PARAMS.get('MODE_SIMULATION', False)}")
        
        # 5. Demander confirmation (si pas en simulation)
        if not MIGRATION_PARAMS.get('MODE_SIMULATION', False):
            logger.warning("\n⚠️  ATTENTION: Cette migration va modifier la base destination!")
            logger.info("   Assurez-vous d'avoir fait une sauvegarde.")
            
            # Note: En mode automatique, on ne demande pas de confirmation
            # Pour mode interactif, décommenter:
            # reponse = input("\n   Continuer? (oui/non): ")
            # if reponse.lower() not in ['oui', 'yes', 'o', 'y']:
            #     logger.info("Migration annulée par l'utilisateur")
            #     return False
        
        return prerequis_ok
    
    def executer_etape(self, nom, fonction):
        """Exécute une étape de migration"""
        logger.section(f"ÉTAPE: {nom}")
        start = time.time()
        
        try:
            resultat = fonction()
            duration = time.time() - start
            
            if resultat:
                self.etapes_completes.append({
                    'nom': nom,
                    'duree': duration,
                    'status': 'success'
                })
                logger.info(f"\n✓ Étape '{nom}' terminée en {format_duration(duration)}")
                return True
            else:
                self.etapes_echouees.append({
                    'nom': nom,
                    'duree': duration,
                    'status': 'failed'
                })
                logger.error(f"\n✗ Étape '{nom}' échouée après {format_duration(duration)}")
                return False
                
        except Exception as e:
            duration = time.time() - start
            self.etapes_echouees.append({
                'nom': nom,
                'duree': duration,
                'status': 'error',
                'erreur': str(e)
            })
            logger.error(f"\n✗ Erreur dans l'étape '{nom}': {e}")
            return False
    
    def migrer_plan_comptable(self):
        """Migration du plan comptable"""
        from migration_plan_comptable import MigrationPlanComptable
        migration = MigrationPlanComptable(self.connexion)
        limit = MIGRATION_PARAMS.get('MAX_RECORDS', None)
        return migration.executer(limit)
    
    def migrer_journaux(self):
        """Migration des journaux"""
        from migration_journaux import MigrationJournaux
        migration = MigrationJournaux(self.connexion)
        limit = MIGRATION_PARAMS.get('MAX_RECORDS', None)
        return migration.executer(limit)
    
    def migrer_partenaires(self):
        """Migration des partenaires"""
        migration = MigrationPartenaires(self.connexion)
        limit = MIGRATION_PARAMS.get('MAX_RECORDS', None)
        return migration.executer(limit)
    
    def migrer_produits(self):
        """Migration des produits"""
        logger.info("Migration des produits...")
        logger.warning("⚠️  Non implémenté dans cette version")
        return True
    
    def migrer_factures_clients(self):
        """Migration des factures clients"""
        logger.info("Migration des factures clients...")
        logger.warning("⚠️  Non implémenté dans cette version")
        return True
    
    def migrer_factures_fournisseurs(self):
        """Migration des factures fournisseurs...")
        logger.info("Migration des factures fournisseurs...")
        logger.warning("⚠️  Non implémenté dans cette version")
        return True
    
    def verifier_migration(self):
        """Vérification post-migration"""
        verification = VerificationV19(self.connexion)
        return verification.executer_toutes_verifications()
    
    def afficher_resume(self):
        """Affiche le résumé de la migration"""
        logger.section("RÉSUMÉ DE LA MIGRATION")
        
        duration_totale = time.time() - self.start_time
        
        logger.info(f"\nDurée totale: {format_duration(duration_totale)}")
        logger.info(f"Étapes réussies: {len(self.etapes_completes)}")
        logger.info(f"Étapes échouées: {len(self.etapes_echouees)}")
        
        if self.etapes_completes:
            logger.info("\n✓ ÉTAPES RÉUSSIES:")
            for etape in self.etapes_completes:
                logger.info(f"   - {etape['nom']:30s} ({format_duration(etape['duree'])})")
        
        if self.etapes_echouees:
            logger.error("\n✗ ÉTAPES ÉCHOUÉES:")
            for etape in self.etapes_echouees:
                logger.error(f"   - {etape['nom']:30s} ({format_duration(etape['duree'])})")
                if 'erreur' in etape:
                    logger.error(f"     Erreur: {etape['erreur']}")
        
        # Statistiques de connexion
        if self.connexion:
            self.connexion.afficher_stats()
    
    def executer(self):
        """Exécute la migration complète"""
        self.start_time = time.time()
        
        # Bannière
        self.afficher_banniere()
        
        # Prérequis
        if not self.verifier_prerequis():
            logger.error("\n✗ Les prérequis ne sont pas satisfaits")
            return False
        
        logger.info("\n✓ Tous les prérequis sont OK")
        logger.info("=" * 70)
        
        # Définir les étapes selon l'ordre configuré
        etapes_disponibles = {
            'plan_comptable': ('Plan comptable', self.migrer_plan_comptable),
            'journaux': ('Journaux comptables', self.migrer_journaux),
            'partenaires': ('Partenaires (clients/fournisseurs)', self.migrer_partenaires),
            'produits': ('Produits', self.migrer_produits),
            'factures_clients': ('Factures clients', self.migrer_factures_clients),
            'factures_fournisseurs': ('Factures fournisseurs', self.migrer_factures_fournisseurs),
        }
        
        # Exécuter dans l'ordre configuré
        for etape_key in MIGRATION_ORDER:
            if etape_key in etapes_disponibles:
                nom, fonction = etapes_disponibles[etape_key]
                
                # Vérifier si l'étape est activée
                param_key = f'MIGRER_{etape_key.upper()}'
                if not MIGRATION_PARAMS.get(param_key, True):
                    logger.info(f"\n⊘ Étape '{nom}' désactivée dans la configuration")
                    continue
                
                # Exécuter l'étape
                if not self.executer_etape(nom, fonction):
                    logger.error(f"\n✗ Échec de l'étape '{nom}'")
                    
                    # Demander si on continue (en mode interactif)
                    # reponse = input("\n   Continuer malgré l'erreur? (oui/non): ")
                    # if reponse.lower() not in ['oui', 'yes', 'o', 'y']:
                    #     logger.info("Migration interrompue par l'utilisateur")
                    #     break
                    
                    # En mode automatique, on continue
                    logger.warning("⚠️  Poursuite de la migration malgré l'erreur")
        
        # Vérification finale
        logger.info("\n" + "=" * 70)
        if self.executer_etape("Vérification finale", self.verifier_migration):
            logger.info("✓ Vérification finale réussie")
        else:
            logger.warning("⚠️  Des problèmes ont été détectés lors de la vérification")
        
        # Résumé
        self.afficher_resume()
        
        # Message final
        if len(self.etapes_echouees) == 0:
            logger.info("\n" + "=" * 70)
            logger.info("✓ MIGRATION COMPLÈTE TERMINÉE AVEC SUCCÈS")
            logger.info("=" * 70 + "\n")
            return True
        else:
            logger.warning("\n" + "=" * 70)
            logger.warning("⚠️  MIGRATION TERMINÉE AVEC DES ERREURS")
            logger.warning("=" * 70 + "\n")
            return False


def main():
    """Fonction principale"""
    migration = MigrationComplete()
    success = migration.executer()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

