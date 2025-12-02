#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VÉRIFICATION ET COMPARAISON DES JOURNAUX
========================================
Compare les journaux entre source et destination pour vérifier les paramétrages
"""

import sys
from connexion_double_v19 import ConnexionDoubleV19
from utils.logger import setup_logger

logger = setup_logger('verifier_journaux')


class VerificationJournaux:
    """Classe pour vérifier et comparer les journaux"""
    
    def __init__(self, connexion):
        self.connexion = connexion
        self.differences = []
        self.journaux_manquants = []
        self.journaux_surplus = []
        
    def recuperer_tous_journaux(self, base='source'):
        """Récupère tous les journaux avec leurs détails"""
        logger.info(f"Récupération des journaux de la {base.upper()}...")
        
        # Champs communs entre v16 et v19
        fields_base = [
            'id', 'name', 'code', 'type',
            'active', 'sequence',
            'currency_id',
            'company_id',
            'default_account_id',
            'suspense_account_id',
            'profit_account_id',
            'loss_account_id',
            'refund_sequence',
        ]
        
        # Champs spécifiques v19 (pas en v16)
        fields_v19 = [
            'payment_debit_account_id',
            'payment_credit_account_id',
        ]
        
        # Utiliser les champs adaptés selon la base
        if base == 'source':
            fields = fields_base  # v16 n'a pas les champs payment_xxx
        else:
            fields = fields_base + fields_v19  # v19 a tous les champs
        
        try:
            if base == 'source':
                journaux = self.connexion.executer_source(
                    'account.journal',
                    'search_read',
                    [],
                    fields=fields
                )
            else:
                journaux = self.connexion.executer_destination(
                    'account.journal',
                    'search_read',
                    [],
                    fields=fields
                )
            
            logger.info(f"✓ {len(journaux)} journaux récupérés")
            return journaux
            
        except Exception as e:
            logger.error(f"✗ Erreur récupération: {e}")
            return []
    
    def afficher_journal_detaille(self, journal, base=''):
        """Affiche les détails d'un journal"""
        print(f"\n  {'─' * 66}")
        print(f"  Journal: {journal.get('code')} - {journal.get('name')}")
        print(f"  Type: {journal.get('type')}")
        print(f"  Actif: {journal.get('active')}")
        print(f"  Séquence: {journal.get('sequence')}")
        
        # Currency
        currency = journal.get('currency_id')
        if currency and currency != False:
            print(f"  Devise: {currency[1] if isinstance(currency, (list, tuple)) else currency}")
        
        # Company
        company = journal.get('company_id')
        if company and company != False:
            print(f"  Société: {company[1] if isinstance(company, (list, tuple)) else company}")
        
        # Comptes comptables
        print(f"\n  Comptes configurés:")
        
        # Comptes communs v16/v19
        comptes_fields = [
            ('default_account_id', 'Compte par défaut'),
            ('suspense_account_id', 'Compte suspens'),
            ('profit_account_id', 'Compte profit'),
            ('loss_account_id', 'Compte perte'),
        ]
        
        # Comptes spécifiques v19
        if 'payment_debit_account_id' in journal:
            comptes_fields.extend([
                ('payment_debit_account_id', 'Compte paiement débit'),
                ('payment_credit_account_id', 'Compte paiement crédit'),
            ])
        
        for field, label in comptes_fields:
            compte = journal.get(field)
            if compte and compte != False:
                if isinstance(compte, (list, tuple)) and len(compte) >= 2:
                    print(f"    - {label:30s}: {compte[1]} (ID: {compte[0]})")
                else:
                    print(f"    - {label:30s}: {compte}")
            else:
                print(f"    - {label:30s}: Non configuré")
    
    def comparer_journaux(self):
        """Compare les journaux entre source et destination"""
        logger.section("COMPARAISON SOURCE vs DESTINATION")
        
        # Récupérer les journaux des deux bases
        journaux_source = self.recuperer_tous_journaux('source')
        journaux_dest = self.recuperer_tous_journaux('destination')
        
        # Créer des dictionnaires par code
        source_dict = {j['code']: j for j in journaux_source}
        dest_dict = {j['code']: j for j in journaux_dest}
        
        logger.info(f"\nJournaux dans SOURCE: {len(source_dict)}")
        logger.info(f"Journaux dans DESTINATION: {len(dest_dict)}")
        
        # Chercher les journaux manquants dans la destination
        codes_source = set(source_dict.keys())
        codes_dest = set(dest_dict.keys())
        
        manquants = codes_source - codes_dest
        surplus = codes_dest - codes_source
        communs = codes_source & codes_dest
        
        # Afficher les manquants
        if manquants:
            logger.warning(f"\n⚠️  {len(manquants)} journal(aux) manquant(s) dans DESTINATION:")
            for code in sorted(manquants):
                journal = source_dict[code]
                logger.warning(f"  - {code:15s} {journal['type']:10s} {journal['name']}")
                self.journaux_manquants.append(journal)
        else:
            logger.info("\n✓ Tous les journaux de la source sont dans la destination")
        
        # Afficher les surplus
        if surplus:
            logger.info(f"\nℹ️  {len(surplus)} journal(aux) en surplus dans DESTINATION (créés manuellement):")
            for code in sorted(surplus):
                journal = dest_dict[code]
                logger.info(f"  - {code:15s} {journal['type']:10s} {journal['name']}")
        
        # Comparer les journaux communs
        logger.section(f"COMPARAISON DÉTAILLÉE ({len(communs)} journaux communs)")
        
        for code in sorted(communs):
            source_j = source_dict[code]
            dest_j = dest_dict[code]
            
            diff = self.comparer_un_journal(source_j, dest_j)
            if diff:
                self.differences.append({
                    'code': code,
                    'differences': diff
                })
        
        return len(manquants) == 0 and len(self.differences) == 0
    
    def comparer_un_journal(self, source, dest):
        """Compare un journal source vs destination"""
        diff = {}
        
        # Champs à comparer
        champs_simples = ['name', 'type', 'active', 'sequence']
        
        for champ in champs_simples:
            val_source = source.get(champ)
            val_dest = dest.get(champ)
            
            if val_source != val_dest:
                diff[champ] = {'source': val_source, 'dest': val_dest}
        
        # Comparer les comptes (seulement si configurés)
        champs_comptes = [
            'default_account_id',
            'suspense_account_id',
            'profit_account_id',
            'loss_account_id',
            'payment_debit_account_id',
            'payment_credit_account_id',
        ]
        
        for champ in champs_comptes:
            compte_source = source.get(champ)
            compte_dest = dest.get(champ)
            
            # Extraire le code du compte (pas l'ID car différent entre bases)
            code_source = None
            code_dest = None
            
            if compte_source and compte_source != False:
                if isinstance(compte_source, (list, tuple)) and len(compte_source) >= 2:
                    code_source = compte_source[1]  # Format: [id, 'code name']
            
            if compte_dest and compte_dest != False:
                if isinstance(compte_dest, (list, tuple)) and len(compte_dest) >= 2:
                    code_dest = compte_dest[1]
            
            # Comparer les codes (pas les IDs)
            if code_source != code_dest:
                diff[champ] = {
                    'source': code_source or 'Non configuré',
                    'dest': code_dest or 'Non configuré'
                }
        
        # Afficher si différences
        if diff:
            logger.warning(f"\n⚠️  Différences pour journal '{source['code']}':")
            for champ, valeurs in diff.items():
                logger.warning(f"  - {champ:30s}:")
                logger.warning(f"      Source      : {valeurs['source']}")
                logger.warning(f"      Destination : {valeurs['dest']}")
        
        return diff
    
    def lister_journaux_source(self):
        """Liste tous les journaux de la source avec leurs détails"""
        logger.section("LISTE DÉTAILLÉE DES JOURNAUX SOURCE")
        
        journaux = self.recuperer_tous_journaux('source')
        
        # Grouper par type
        par_type = {}
        for journal in journaux:
            jtype = journal.get('type', 'unknown')
            if jtype not in par_type:
                par_type[jtype] = []
            par_type[jtype].append(journal)
        
        # Afficher par type
        for jtype in sorted(par_type.keys()):
            logger.info(f"\n{'═' * 70}")
            logger.info(f"TYPE: {jtype.upper()} ({len(par_type[jtype])} journaux)")
            logger.info(f"{'═' * 70}")
            
            for journal in sorted(par_type[jtype], key=lambda x: x.get('code', '')):
                self.afficher_journal_detaille(journal, 'source')
    
    def lister_journaux_destination(self):
        """Liste tous les journaux de la destination avec leurs détails"""
        logger.section("LISTE DÉTAILLÉE DES JOURNAUX DESTINATION")
        
        journaux = self.recuperer_tous_journaux('destination')
        
        # Grouper par type
        par_type = {}
        for journal in journaux:
            jtype = journal.get('type', 'unknown')
            if jtype not in par_type:
                par_type[jtype] = []
            par_type[jtype].append(journal)
        
        # Afficher par type
        for jtype in sorted(par_type.keys()):
            logger.info(f"\n{'═' * 70}")
            logger.info(f"TYPE: {jtype.upper()} ({len(par_type[jtype])} journaux)")
            logger.info(f"{'═' * 70}")
            
            for journal in sorted(par_type[jtype], key=lambda x: x.get('code', '')):
                self.afficher_journal_detaille(journal, 'destination')
    
    def generer_rapport(self):
        """Génère un rapport de vérification"""
        logger.section("RAPPORT DE VÉRIFICATION")
        
        if not self.journaux_manquants and not self.differences:
            logger.info("✅ Tous les journaux sont correctement migrés")
            logger.info("✅ Aucune différence de configuration détectée")
            return True
        
        if self.journaux_manquants:
            logger.warning(f"\n⚠️  {len(self.journaux_manquants)} JOURNAL(AUX) MANQUANT(S):")
            for journal in self.journaux_manquants:
                logger.warning(f"  - {journal['code']:15s} {journal['type']:10s} {journal['name']}")
            logger.warning("\n  → Action recommandée: Lancer migration_journaux.py")
        
        if self.differences:
            logger.warning(f"\n⚠️  {len(self.differences)} JOURNAL(AUX) AVEC DIFFÉRENCES:")
            for item in self.differences:
                logger.warning(f"  - {item['code']}: {len(item['differences'])} différence(s)")
            logger.warning("\n  → Vérifiez manuellement les configurations")
        
        return False
    
    def executer_verification_complete(self):
        """Exécute la vérification complète"""
        logger.section("VÉRIFICATION COMPLÈTE DES JOURNAUX")
        
        # 1. Lister les journaux source
        print("\n" + "█" * 70)
        self.lister_journaux_source()
        
        # 2. Lister les journaux destination
        print("\n" + "█" * 70)
        self.lister_journaux_destination()
        
        # 3. Comparer
        print("\n" + "█" * 70)
        resultat = self.comparer_journaux()
        
        # 4. Rapport final
        print("\n" + "█" * 70)
        self.generer_rapport()
        
        return resultat


def main():
    """Fonction principale"""
    logger.section("VÉRIFICATION DES JOURNAUX - SOURCE vs DESTINATION")
    
    # Connexion
    logger.info("Connexion aux bases...")
    connexion = ConnexionDoubleV19()
    
    if not connexion.connecter_tout():
        logger.error("✗ Échec de connexion aux bases")
        return False
    
    # Vérification
    verification = VerificationJournaux(connexion)
    success = verification.executer_verification_complete()
    
    # Statistiques de connexion
    connexion.afficher_stats()
    
    if success:
        logger.info("\n✅ Vérification terminée: Journaux OK")
    else:
        logger.warning("\n⚠️  Vérification terminée: Des différences ont été détectées")
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

