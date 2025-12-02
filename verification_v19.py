#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VÉRIFICATION POST-MIGRATION V19
===============================
Script de vérification et contrôle qualité après migration vers v19
"""

import sys
from datetime import datetime
from connexion_double_v19 import ConnexionDoubleV19
from utils.logger import setup_logger
from utils.helpers import format_number
from config_v19 import VALIDATION_CONFIG

# Configuration du logger
logger = setup_logger('verification_v19')


class VerificationV19:
    """Classe pour gérer les vérifications post-migration"""
    
    def __init__(self, connexion):
        self.connexion = connexion
        self.erreurs = []
        self.avertissements = []
        
    def verifier_version(self):
        """Vérifie que la destination est bien en v19"""
        logger.section("VÉRIFICATION VERSION ODOO")
        
        try:
            version = self.connexion.dest_common.version()
            version_str = version.get('server_version', '')
            
            logger.info(f"Version détectée: {version_str}")
            
            if '19.0' in version_str:
                logger.info("✓ Version v19 confirmée")
                return True
            else:
                self.erreurs.append(f"Version incorrecte: {version_str}")
                logger.error(f"✗ Version incorrecte: {version_str}")
                return False
                
        except Exception as e:
            self.erreurs.append(f"Erreur vérification version: {e}")
            logger.error(f"✗ Erreur: {e}")
            return False
    
    def comparer_comptages(self):
        """Compare les comptages entre source et destination"""
        logger.section("COMPARAISON DES COMPTAGES")
        
        modeles = [
            ('res.partner', 'Partenaires'),
            ('product.product', 'Produits'),
            ('account.account', 'Comptes comptables'),
            ('account.journal', 'Journaux'),
            ('account.move', 'Écritures comptables'),
        ]
        
        comparaisons = []
        
        for model, label in modeles:
            logger.info(f"\n{label}:")
            
            # Compter source
            count_source = self.connexion.compter_records(model, base='source')
            logger.info(f"  Source      : {format_number(count_source)}")
            
            # Compter destination
            count_dest = self.connexion.compter_records(model, base='destination')
            logger.info(f"  Destination : {format_number(count_dest)}")
            
            # Calcul différence
            diff = count_dest - count_source
            pct = (diff / count_source * 100) if count_source > 0 else 0
            
            logger.info(f"  Différence  : {diff:+,} ({pct:+.1f}%)")
            
            comparaisons.append({
                'model': model,
                'label': label,
                'source': count_source,
                'destination': count_dest,
                'diff': diff,
                'pct': pct,
            })
            
            # Vérifications
            if count_dest < count_source:
                msg = f"{label}: destination inférieure à source ({diff})"
                self.avertissements.append(msg)
                logger.warning(f"⚠️  {msg}")
        
        return comparaisons
    
    def verifier_partenaires(self):
        """Vérifications spécifiques aux partenaires"""
        if not VALIDATION_CONFIG.get('VERIFIER_PARTENAIRES', True):
            return True
            
        logger.section("VÉRIFICATION DES PARTENAIRES")
        
        try:
            # Partenaires sans nom
            sans_nom = self.connexion.executer_destination(
                'res.partner',
                'search_count',
                [('name', '=', False)]
            )
            
            if sans_nom > 0:
                msg = f"{sans_nom} partenaires sans nom détectés"
                self.avertissements.append(msg)
                logger.warning(f"⚠️  {msg}")
            else:
                logger.info("✓ Tous les partenaires ont un nom")
            
            # Doublons de VAT
            partenaires_vat = self.connexion.executer_destination(
                'res.partner',
                'search_read',
                [('vat', '!=', False)],
                fields=['vat']
            )
            
            vats = [p['vat'] for p in partenaires_vat if p.get('vat')]
            doublons_vat = len(vats) - len(set(vats))
            
            if doublons_vat > 0:
                msg = f"{doublons_vat} doublons de VAT détectés"
                self.avertissements.append(msg)
                logger.warning(f"⚠️  {msg}")
            else:
                logger.info("✓ Pas de doublons de VAT")
            
            return True
            
        except Exception as e:
            self.erreurs.append(f"Erreur vérification partenaires: {e}")
            logger.error(f"✗ Erreur: {e}")
            return False
    
    def verifier_soldes(self):
        """Vérifie les soldes comptables"""
        if not VALIDATION_CONFIG.get('VERIFIER_SOLDES', True):
            return True
            
        logger.section("VÉRIFICATION DES SOLDES")
        
        try:
            # Compter écritures déséquilibrées
            # Une écriture est équilibrée si sum(debit) = sum(credit)
            
            logger.info("Recherche d'écritures déséquilibrées...")
            
            # Récupérer toutes les écritures validées
            moves = self.connexion.executer_destination(
                'account.move',
                'search',
                [('state', '=', 'posted')]
            )
            
            logger.info(f"Vérification de {len(moves)} écritures...")
            
            desequilibrees = 0
            tolerance = VALIDATION_CONFIG.get('TOLERANCE_ECART', 0.01)
            
            # Vérifier par échantillon (pour ne pas être trop long)
            sample_size = min(1000, len(moves))
            import random
            sample = random.sample(moves, sample_size) if len(moves) > sample_size else moves
            
            for move_id in sample:
                # Récupérer les lignes
                lines = self.connexion.executer_destination(
                    'account.move.line',
                    'search_read',
                    [('move_id', '=', move_id)],
                    fields=['debit', 'credit']
                )
                
                total_debit = sum(line.get('debit', 0) for line in lines)
                total_credit = sum(line.get('credit', 0) for line in lines)
                diff = abs(total_debit - total_credit)
                
                if diff > tolerance:
                    desequilibrees += 1
            
            if desequilibrees > 0:
                pct = (desequilibrees / sample_size) * 100
                msg = f"{desequilibrees}/{sample_size} écritures déséquilibrées ({pct:.1f}%)"
                self.erreurs.append(msg)
                logger.error(f"✗ {msg}")
            else:
                logger.info(f"✓ Échantillon de {sample_size} écritures: toutes équilibrées")
            
            return desequilibrees == 0
            
        except Exception as e:
            self.erreurs.append(f"Erreur vérification soldes: {e}")
            logger.error(f"✗ Erreur: {e}")
            return False
    
    def verifier_sequences(self):
        """Vérifie les séquences"""
        if not VALIDATION_CONFIG.get('VERIFIER_SEQUENCES', True):
            return True
            
        logger.section("VÉRIFICATION DES SÉQUENCES")
        
        try:
            # Compter les séquences
            sequences = self.connexion.executer_destination(
                'ir.sequence',
                'search_count',
                []
            )
            
            logger.info(f"Nombre de séquences: {sequences}")
            
            if sequences > 0:
                logger.info("✓ Séquences présentes")
                return True
            else:
                msg = "Aucune séquence trouvée"
                self.avertissements.append(msg)
                logger.warning(f"⚠️  {msg}")
                return False
                
        except Exception as e:
            self.erreurs.append(f"Erreur vérification séquences: {e}")
            logger.error(f"✗ Erreur: {e}")
            return False
    
    def verifier_journaux(self):
        """Vérifie les journaux comptables"""
        logger.section("VÉRIFICATION DES JOURNAUX")
        
        try:
            # Compter les journaux
            journaux = self.connexion.executer_destination(
                'account.journal',
                'search_read',
                [],
                fields=['name', 'code', 'type']
            )
            
            logger.info(f"Nombre de journaux: {len(journaux)}")
            
            # Afficher les types
            types = {}
            for journal in journaux:
                jtype = journal.get('type', 'unknown')
                types[jtype] = types.get(jtype, 0) + 1
            
            logger.info("Répartition par type:")
            for jtype, count in types.items():
                logger.info(f"  - {jtype:15s}: {count}")
            
            # Vérifier les journaux essentiels
            essential_types = ['sale', 'purchase', 'bank', 'general']
            for etype in essential_types:
                if etype not in types:
                    msg = f"Aucun journal de type '{etype}' trouvé"
                    self.avertissements.append(msg)
                    logger.warning(f"⚠️  {msg}")
            
            return True
            
        except Exception as e:
            self.erreurs.append(f"Erreur vérification journaux: {e}")
            logger.error(f"✗ Erreur: {e}")
            return False
    
    def generer_rapport(self):
        """Génère un rapport final"""
        logger.section("RAPPORT DE VÉRIFICATION")
        
        total_erreurs = len(self.erreurs)
        total_avertissements = len(self.avertissements)
        
        if total_erreurs == 0 and total_avertissements == 0:
            logger.info("✓ Aucun problème détecté")
            logger.info("✓ La migration semble réussie")
            return True
        
        if total_erreurs > 0:
            logger.error(f"\n{total_erreurs} ERREUR(S) DÉTECTÉE(S):")
            for i, erreur in enumerate(self.erreurs, 1):
                logger.error(f"  {i}. {erreur}")
        
        if total_avertissements > 0:
            logger.warning(f"\n{total_avertissements} AVERTISSEMENT(S):")
            for i, avert in enumerate(self.avertissements, 1):
                logger.warning(f"  {i}. {avert}")
        
        return total_erreurs == 0
    
    def executer_toutes_verifications(self):
        """Exécute toutes les vérifications"""
        logger.section("DÉMARRAGE DES VÉRIFICATIONS")
        
        verifications = [
            ("Version Odoo", self.verifier_version),
            ("Comptages", self.comparer_comptages),
            ("Partenaires", self.verifier_partenaires),
            ("Journaux", self.verifier_journaux),
            ("Séquences", self.verifier_sequences),
            ("Soldes", self.verifier_soldes),
        ]
        
        for nom, fonction in verifications:
            logger.info(f"\n▶ Vérification: {nom}")
            try:
                fonction()
            except Exception as e:
                self.erreurs.append(f"Erreur {nom}: {e}")
                logger.error(f"✗ Erreur: {e}")
        
        return self.generer_rapport()


def main():
    """Fonction principale"""
    logger.section("VÉRIFICATION POST-MIGRATION VERS ODOO V19")
    
    # Connexion
    logger.info("Connexion aux bases...")
    connexion = ConnexionDoubleV19()
    
    if not connexion.connecter_tout():
        logger.error("✗ Échec de connexion aux bases")
        return False
    
    # Vérification
    verification = VerificationV19(connexion)
    success = verification.executer_toutes_verifications()
    
    # Statistiques de connexion
    connexion.afficher_stats()
    
    if success:
        logger.info("\n" + "=" * 70)
        logger.info("✓ VÉRIFICATION TERMINÉE: Aucune erreur critique")
        logger.info("=" * 70)
    else:
        logger.error("\n" + "=" * 70)
        logger.error("✗ VÉRIFICATION TERMINÉE: Des erreurs ont été détectées")
        logger.error("=" * 70)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

