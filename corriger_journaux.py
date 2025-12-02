#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CORRECTION AUTOMATIQUE DES JOURNAUX
===================================
Corrige les configurations des journaux dans la destination
en se basant sur la source
"""

import sys
import json
import os
from connexion_double_v19 import ConnexionDoubleV19
from utils.logger import setup_logger
from config_v19 import MIGRATION_PARAMS

logger = setup_logger('corriger_journaux')


class CorrectionJournaux:
    """Classe pour corriger les journaux"""
    
    def __init__(self, connexion):
        self.connexion = connexion
        self.account_mapping = {}
        self.stats = {
            'journaux_crees': 0,
            'journaux_corriges': 0,
            'comptes_mis_a_jour': 0,
            'erreurs': 0,
        }
        
    def charger_mapping_comptes(self):
        """Charge le mapping des comptes depuis le fichier JSON"""
        mapping_file = os.path.join('logs', 'account_mapping.json')
        
        if not os.path.exists(mapping_file):
            logger.warning("⚠️  Fichier account_mapping.json non trouvé")
            logger.info("   Les comptes ne pourront pas être mappés automatiquement")
            return False
        
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                self.account_mapping = json.load(f)
            
            logger.info(f"✓ Mapping de {len(self.account_mapping)} comptes chargé")
            return True
        except Exception as e:
            logger.error(f"✗ Erreur chargement mapping: {e}")
            return False
    
    def trouver_compte_destination(self, compte_source_id):
        """Trouve l'ID de destination d'un compte via le mapping"""
        if not self.account_mapping:
            return None
        
        # Le mapping est : {id_source_str: id_destination_int}
        compte_source_str = str(compte_source_id)
        
        if compte_source_str in self.account_mapping:
            return self.account_mapping[compte_source_str]
        
        return None
    
    def recuperer_journaux_source(self):
        """Récupère tous les journaux source"""
        logger.info("Récupération des journaux source...")
        
        fields = [
            'id', 'name', 'code', 'type',
            'active', 'sequence',
            'default_account_id',
            'suspense_account_id',
            'profit_account_id',
            'loss_account_id',
        ]
        
        try:
            journaux = self.connexion.executer_source(
                'account.journal',
                'search_read',
                [],
                fields=fields
            )
            logger.info(f"✓ {len(journaux)} journaux source récupérés")
            return {j['code']: j for j in journaux}
        except Exception as e:
            logger.error(f"✗ Erreur: {e}")
            return {}
    
    def recuperer_journaux_destination(self):
        """Récupère tous les journaux destination"""
        logger.info("Récupération des journaux destination...")
        
        fields = [
            'id', 'name', 'code', 'type',
            'active', 'sequence',
            'default_account_id',
            'suspense_account_id',
            'profit_account_id',
            'loss_account_id',
        ]
        
        try:
            journaux = self.connexion.executer_destination(
                'account.journal',
                'search_read',
                [],
                fields=fields
            )
            logger.info(f"✓ {len(journaux)} journaux destination récupérés")
            return {j['code']: j for j in journaux}
        except Exception as e:
            logger.error(f"✗ Erreur: {e}")
            return {}
    
    def creer_journal_manquant(self, journal_source):
        """Crée un journal manquant dans la destination"""
        logger.info(f"\n📝 Création du journal '{journal_source['code']}'...")
        
        try:
            if MIGRATION_PARAMS.get('MODE_SIMULATION', False):
                logger.info("[SIMULATION] Journal non créé")
                return True
            
            # Données minimales pour créer le journal
            data = {
                'name': journal_source['name'],
                'code': journal_source['code'],
                'type': journal_source['type'],
            }
            
            if journal_source.get('sequence'):
                data['sequence'] = journal_source['sequence']
            
            # Créer le journal
            new_id = self.connexion.executer_destination(
                'account.journal',
                'create',
                data
            )
            
            logger.info(f"✓ Journal '{journal_source['code']}' créé (ID: {new_id})")
            self.stats['journaux_crees'] += 1
            
            # Maintenant corriger ses comptes
            return self.corriger_comptes_journal(new_id, journal_source)
            
        except Exception as e:
            logger.error(f"✗ Erreur création journal: {e}")
            self.stats['erreurs'] += 1
            return False
    
    def corriger_comptes_journal(self, journal_dest_id, journal_source):
        """Corrige les comptes d'un journal"""
        updates = {}
        comptes_corriges = 0
        
        # Champs de comptes à vérifier
        champs_comptes = [
            'default_account_id',
            'suspense_account_id',
            'profit_account_id',
            'loss_account_id',
        ]
        
        for champ in champs_comptes:
            compte_source = journal_source.get(champ)
            
            # Si le compte est configuré dans la source
            if compte_source and compte_source != False:
                if isinstance(compte_source, (list, tuple)) and len(compte_source) >= 2:
                    compte_source_id = compte_source[0]
                    compte_source_name = compte_source[1]
                    
                    # Trouver le compte correspondant dans la destination
                    compte_dest_id = self.trouver_compte_destination(compte_source_id)
                    
                    if compte_dest_id:
                        updates[champ] = compte_dest_id
                        comptes_corriges += 1
                        logger.debug(f"  ✓ {champ}: {compte_source_name} → ID {compte_dest_id}")
                    else:
                        logger.warning(f"  ⚠️  {champ}: Compte source {compte_source_name} non trouvé dans destination")
        
        # Appliquer les mises à jour si nécessaire
        if updates:
            try:
                if not MIGRATION_PARAMS.get('MODE_SIMULATION', False):
                    self.connexion.executer_destination(
                        'account.journal',
                        'write',
                        [journal_dest_id],
                        updates
                    )
                
                logger.info(f"✓ {comptes_corriges} compte(s) mis à jour")
                self.stats['comptes_mis_a_jour'] += comptes_corriges
                return True
            except Exception as e:
                logger.error(f"✗ Erreur mise à jour comptes: {e}")
                return False
        
        return True
    
    def corriger_journal_existant(self, code, journal_source, journal_dest):
        """Corrige un journal existant - FORCE la synchronisation complète"""
        logger.info(f"\n🔧 Correction du journal '{code}'...")
        
        updates = {}
        details = []
        
        # Vérifier TOUS les comptes (synchronisation forcée)
        champs_comptes = [
            'default_account_id',
            'suspense_account_id',
            'profit_account_id',
            'loss_account_id',
        ]
        
        for champ in champs_comptes:
            compte_source = journal_source.get(champ)
            compte_dest = journal_dest.get(champ)
            
            # Extraire les infos du compte source
            code_source = None
            compte_source_id = None
            
            if compte_source and compte_source != False:
                if isinstance(compte_source, (list, tuple)):
                    code_source = compte_source[1] if len(compte_source) >= 2 else None
                    compte_source_id = compte_source[0]
            
            # Extraire les infos du compte destination
            code_dest = None
            if compte_dest and compte_dest != False:
                if isinstance(compte_dest, (list, tuple)):
                    code_dest = compte_dest[1] if len(compte_dest) >= 2 else None
            
            # FORCER la synchronisation si :
            # 1. Le compte source est configuré ET
            # 2. Le compte destination est différent OU non configuré
            if compte_source_id:
                compte_dest_id = self.trouver_compte_destination(compte_source_id)
                
                if compte_dest_id:
                    # Vérifier si différent
                    if code_source != code_dest:
                        updates[champ] = compte_dest_id
                        if code_dest:
                            details.append(f"  🔄 {champ}: '{code_dest}' → '{code_source}'")
                        else:
                            details.append(f"  ✅ {champ}: Configuration de '{code_source}'")
                else:
                    logger.warning(f"  ⚠️  {champ}: Compte source '{code_source}' non trouvé dans mapping")
            elif compte_dest and compte_dest != False:
                # Le compte n'est PAS dans la source mais EST dans la destination
                # On peut choisir de le retirer (mettre à False) ou le laisser
                # Pour l'instant, on le laisse (cas des comptes profit/loss v19)
                pass
        
        # Afficher les changements
        if details:
            for detail in details:
                logger.info(detail)
        
        # Appliquer les corrections
        if updates:
            try:
                if not MIGRATION_PARAMS.get('MODE_SIMULATION', False):
                    self.connexion.executer_destination(
                        'account.journal',
                        'write',
                        [journal_dest['id']],
                        updates
                    )
                    logger.info(f"✓ Journal '{code}' corrigé ({len(updates)} compte(s) mis à jour)")
                else:
                    logger.info(f"[SIMULATION] Journal '{code}' : {len(updates)} compte(s) seraient mis à jour")
                
                self.stats['journaux_corriges'] += 1
                self.stats['comptes_mis_a_jour'] += len(updates)
                return True
            except Exception as e:
                logger.error(f"✗ Erreur correction: {e}")
                import traceback
                traceback.print_exc()
                self.stats['erreurs'] += 1
                return False
        else:
            logger.info(f"ℹ️  Journal '{code}' : Aucun compte à synchroniser")
            return True
    
    def executer_correction(self):
        """Exécute la correction complète"""
        logger.section("CORRECTION AUTOMATIQUE DES JOURNAUX")
        
        if MIGRATION_PARAMS.get('MODE_SIMULATION', False):
            logger.warning("⚠️  MODE SIMULATION ACTIVÉ")
        
        # Charger le mapping des comptes
        if not self.charger_mapping_comptes():
            logger.error("✗ Impossible de continuer sans le mapping des comptes")
            return False
        
        # Récupérer les journaux
        journaux_source = self.recuperer_journaux_source()
        journaux_dest = self.recuperer_journaux_destination()
        
        if not journaux_source or not journaux_dest:
            logger.error("✗ Impossible de récupérer les journaux")
            return False
        
        # Identifier les journaux manquants
        codes_source = set(journaux_source.keys())
        codes_dest = set(journaux_dest.keys())
        manquants = codes_source - codes_dest
        
        # 1. Créer les journaux manquants
        if manquants:
            logger.section(f"CRÉATION DES JOURNAUX MANQUANTS ({len(manquants)})")
            for code in sorted(manquants):
                self.creer_journal_manquant(journaux_source[code])
        else:
            logger.info("\n✓ Aucun journal manquant")
        
        # 2. Corriger les journaux existants
        communs = codes_source & codes_dest
        if communs:
            logger.section(f"CORRECTION DES JOURNAUX EXISTANTS ({len(communs)})")
            
            for code in sorted(communs):
                self.corriger_journal_existant(
                    code,
                    journaux_source[code],
                    journaux_dest[code]
                )
        
        # Statistiques
        self.afficher_statistiques()
        
        return True
    
    def afficher_statistiques(self):
        """Affiche les statistiques de correction"""
        logger.section("STATISTIQUES DE CORRECTION")
        
        logger.info(f"Journaux créés        : {self.stats['journaux_crees']}")
        logger.info(f"Journaux corrigés     : {self.stats['journaux_corriges']}")
        logger.info(f"Comptes mis à jour    : {self.stats['comptes_mis_a_jour']}")
        logger.info(f"Erreurs               : {self.stats['erreurs']}")
        
        if self.stats['erreurs'] == 0:
            logger.info("\n✅ Correction terminée sans erreur")
        else:
            logger.warning(f"\n⚠️  {self.stats['erreurs']} erreur(s) pendant la correction")


def main():
    """Fonction principale"""
    logger.section("CORRECTION AUTOMATIQUE DES JOURNAUX")
    
    # Connexion
    logger.info("Connexion aux bases...")
    connexion = ConnexionDoubleV19()
    
    if not connexion.connecter_tout():
        logger.error("✗ Échec de connexion aux bases")
        return False
    
    # Correction
    correction = CorrectionJournaux(connexion)
    success = correction.executer_correction()
    
    # Statistiques de connexion
    connexion.afficher_stats()
    
    if success:
        logger.info("\n✅ Correction des journaux terminée")
        logger.info("\n💡 Relancez verifier_journaux.py pour vérifier les corrections")
    else:
        logger.error("\n✗ La correction a échoué")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

