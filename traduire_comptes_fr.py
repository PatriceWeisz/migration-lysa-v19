#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TRADUCTION DES LIBELLÉS DE COMPTES EN FRANÇAIS
==============================================
Met à jour les libellés des comptes en anglais vers français
en se basant sur la source
"""

import sys
import json
import os
from connexion_double_v19 import ConnexionDoubleV19
from utils.logger import setup_logger
from config_v19 import MIGRATION_PARAMS

logger = setup_logger('traduire_comptes')


class TraductionComptes:
    """Classe pour traduire les libellés des comptes"""
    
    def __init__(self, connexion):
        self.connexion = connexion
        self.account_mapping = {}
        self.stats = {
            'comptes_traduits': 0,
            'comptes_identiques': 0,
            'erreurs': 0,
        }
        
    def charger_mapping_comptes(self):
        """Charge le mapping des comptes"""
        mapping_file = os.path.join('logs', 'account_mapping.json')
        
        if not os.path.exists(mapping_file):
            logger.error("✗ Fichier account_mapping.json non trouvé")
            return False
        
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                self.account_mapping = json.load(f)
            
            logger.info(f"✓ Mapping de {len(self.account_mapping)} comptes chargé")
            return True
        except Exception as e:
            logger.error(f"✗ Erreur chargement mapping: {e}")
            return False
    
    def recuperer_comptes_avec_libelles(self, base='source'):
        """Récupère les comptes avec leurs libellés"""
        logger.info(f"Récupération des comptes {base.upper()}...")
        
        fields = ['id', 'code', 'name']
        
        try:
            if base == 'source':
                comptes = self.connexion.executer_source(
                    'account.account',
                    'search_read',
                    [],
                    fields=fields
                )
            else:
                comptes = self.connexion.executer_destination(
                    'account.account',
                    'search_read',
                    [],
                    fields=fields
                )
            
            logger.info(f"✓ {len(comptes)} comptes récupérés")
            return comptes
            
        except Exception as e:
            logger.error(f"✗ Erreur: {e}")
            return []
    
    def comparer_et_traduire(self):
        """Compare et traduit les libellés"""
        logger.section("TRADUCTION DES LIBELLÉS EN FRANÇAIS")
        
        # Récupérer les comptes
        comptes_source = self.recuperer_comptes_avec_libelles('source')
        comptes_dest = self.recuperer_comptes_avec_libelles('destination')
        
        if not comptes_source or not comptes_dest:
            logger.error("✗ Impossible de récupérer les comptes")
            return False
        
        # Créer dictionnaire source par code
        source_by_code = {c['code']: c for c in comptes_source if c.get('code')}
        
        # Créer dictionnaire destination par code
        dest_by_code = {c['code']: c for c in comptes_dest if c.get('code')}
        
        logger.info(f"\nComptes source par code: {len(source_by_code)}")
        logger.info(f"Comptes destination par code: {len(dest_by_code)}")
        
        # Trouver les comptes à traduire
        comptes_a_traduire = []
        
        for code, compte_source in source_by_code.items():
            if code in dest_by_code:
                compte_dest = dest_by_code[code]
                
                # Comparer les noms
                name_source = compte_source.get('name', '').strip()
                name_dest = compte_dest.get('name', '').strip()
                
                if name_source and name_dest and name_source != name_dest:
                    comptes_a_traduire.append({
                        'id_dest': compte_dest['id'],
                        'code': code,
                        'name_actuel': name_dest,
                        'name_francais': name_source,
                    })
        
        logger.info(f"\n✓ {len(comptes_a_traduire)} compte(s) à traduire en français")
        
        if not comptes_a_traduire:
            logger.info("✓ Tous les libellés sont déjà corrects")
            return True
        
        # Afficher un aperçu
        logger.info("\nAperçu des traductions (10 premiers):")
        for compte in comptes_a_traduire[:10]:
            logger.info(f"  {compte['code']:10s}:")
            logger.info(f"    EN: {compte['name_actuel'][:50]}")
            logger.info(f"    FR: {compte['name_francais'][:50]}")
        
        if len(comptes_a_traduire) > 10:
            logger.info(f"  ... et {len(comptes_a_traduire) - 10} autre(s)")
        
        # Confirmer avant traduction
        if not MIGRATION_PARAMS.get('MODE_SIMULATION', False):
            logger.warning(f"\n⚠️  Vous allez traduire {len(comptes_a_traduire)} libellés de comptes")
            logger.info("   Les libellés anglais seront remplacés par les libellés français")
        
        # Appliquer les traductions
        return self.appliquer_traductions(comptes_a_traduire)
    
    def appliquer_traductions(self, comptes):
        """Applique les traductions des libellés"""
        logger.section(f"APPLICATION DES TRADUCTIONS ({len(comptes)} comptes)")
        
        from utils.helpers import ProgressTracker
        
        tracker = ProgressTracker(len(comptes), "Traduction comptes")
        
        for compte in comptes:
            try:
                if MIGRATION_PARAMS.get('MODE_SIMULATION', False):
                    logger.debug(f"[SIMULATION] {compte['code']}: {compte['name_francais']}")
                else:
                    # Mettre à jour le nom du compte
                    self.connexion.executer_destination(
                        'account.account',
                        'write',
                        [compte['id_dest']],
                        {'name': compte['name_francais']}
                    )
                    logger.debug(f"✓ {compte['code']}: Traduit")
                
                self.stats['comptes_traduits'] += 1
                
            except Exception as e:
                logger.error(f"✗ Erreur traduction {compte['code']}: {e}")
                self.stats['erreurs'] += 1
            
            tracker.update()
            
            # Afficher progression tous les 50
            if tracker.current % 50 == 0:
                tracker.display()
        
        tracker.finish()
        return True
    
    def afficher_statistiques(self):
        """Affiche les statistiques"""
        logger.section("STATISTIQUES DE TRADUCTION")
        
        logger.info(f"Comptes traduits      : {self.stats['comptes_traduits']}")
        logger.info(f"Erreurs               : {self.stats['erreurs']}")
        
        if self.stats['erreurs'] == 0:
            logger.info("\n✅ Traduction terminée sans erreur")
        else:
            logger.warning(f"\n⚠️  {self.stats['erreurs']} erreur(s)")
    
    def executer(self):
        """Exécute la traduction complète"""
        logger.section("TRADUCTION DES COMPTES EN FRANÇAIS")
        
        if MIGRATION_PARAMS.get('MODE_SIMULATION', False):
            logger.warning("⚠️  MODE SIMULATION ACTIVÉ")
        
        # Charger le mapping (optionnel pour cette opération)
        # self.charger_mapping_comptes()
        
        # Comparer et traduire
        success = self.comparer_et_traduire()
        
        # Statistiques
        self.afficher_statistiques()
        
        return success


def main():
    """Fonction principale"""
    logger.section("TRADUCTION DES LIBELLÉS DE COMPTES EN FRANÇAIS")
    
    # Connexion
    logger.info("Connexion aux bases...")
    connexion = ConnexionDoubleV19()
    
    if not connexion.connecter_tout():
        logger.error("✗ Échec de connexion aux bases")
        return False
    
    # Traduction
    traduction = TraductionComptes(connexion)
    success = traduction.executer()
    
    # Statistiques de connexion
    connexion.afficher_stats()
    
    if success:
        logger.info("\n✅ Traduction des comptes terminée")
        logger.info("\n💡 Les libellés des comptes sont maintenant en français")
        logger.info("💡 Relancez verifier_journaux.py pour vérifier")
    else:
        logger.error("\n✗ La traduction a échoué")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

