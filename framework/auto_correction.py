#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTO-CORRECTION INTELLIGENTE
=============================
Analyse les erreurs et les corrige automatiquement quand possible
Demande validation utilisateur pour décisions importantes
"""

import re
from pathlib import Path

class AutoCorrecteur:
    """Analyse et corrige automatiquement les erreurs de migration"""
    
    def __init__(self, connexion, mode_interactif=True):
        self.conn = connexion
        self.mode_interactif = mode_interactif
        self.corrections_appliquees = []
        self.corrections_refusees = []
    
    def analyser_erreur(self, erreur, contexte):
        """
        Analyse une erreur et propose une correction
        
        Args:
            erreur: Message d'erreur
            contexte: dict avec {model, record, data}
        
        Returns:
            dict {
                'type': type d'erreur,
                'correction_auto': bool,
                'correction': action à faire,
                'demander_avis': bool
            }
        """
        erreur_str = str(erreur).lower()
        
        # =====================================================================
        # ERREURS AUTO-CORRIGIBLES (sans demander avis)
        # =====================================================================
        
        # 1. Champ invalide (n'existe pas en v19)
        if 'invalid field' in erreur_str:
            match = re.search(r"Invalid field '(\w+)'", str(erreur))
            if match:
                champ = match.group(1)
                return {
                    'type': 'CHAMP_INVALIDE',
                    'champ': champ,
                    'correction_auto': True,
                    'correction': f'Retirer le champ {champ} de la migration',
                    'demander_avis': False,
                    'action': lambda data: data.pop(champ, None)
                }
        
        # 2. Champ vide pour un champ obligatoire
        if 'missing required value' in erreur_str or 'required field' in erreur_str:
            match = re.search(r"field '(\w+)'", str(erreur), re.IGNORECASE)
            if match:
                champ = match.group(1)
                
                # Valeurs par défaut automatiques
                defaults_auto = {
                    'active': True,
                    'user_id': 2,
                    'company_id': 1,
                    'state': 'draft',
                    'type': 'other',
                    'currency_id': 1,
                }
                
                if champ in defaults_auto:
                    return {
                        'type': 'CHAMP_OBLIGATOIRE',
                        'champ': champ,
                        'correction_auto': True,
                        'correction': f'Ajouter {champ}={defaults_auto[champ]}',
                        'demander_avis': False,
                        'action': lambda data: data.update({champ: defaults_auto[champ]})
                    }
                else:
                    return {
                        'type': 'CHAMP_OBLIGATOIRE_INCONNU',
                        'champ': champ,
                        'correction_auto': False,
                        'correction': f'Champ obligatoire {champ} sans valeur par défaut connue',
                        'demander_avis': True,
                        'question': f"Valeur par défaut pour {champ} ? "
                    }
        
        # 3. Identifiant doit être email
        if 'identifiant doit' in erreur_str and 'email' in erreur_str:
            return {
                'type': 'LOGIN_INVALIDE',
                'correction_auto': True,
                'correction': 'Skip cet utilisateur (login invalide)',
                'demander_avis': False,
                'action': lambda data: 'SKIP'
            }
        
        # 4. Doublon (already exists, duplicate)
        if 'already exists' in erreur_str or 'duplicate' in erreur_str:
            return {
                'type': 'DOUBLON',
                'correction_auto': True,
                'correction': 'Récupérer l\'enregistrement existant',
                'demander_avis': False,
                'action': 'RECHERCHER_EXISTANT'
            }
        
        # 5. Limite emails (trial SaaS)
        if 'daily limit' in erreur_str:
            return {
                'type': 'LIMITE_EMAILS',
                'correction_auto': True,
                'correction': 'Rechercher l\'utilisateur créé (erreur email seulement)',
                'demander_avis': False,
                'action': 'RECHERCHER_EXISTANT'
            }
        
        # =====================================================================
        # ERREURS NÉCESSITANT AVIS UTILISATEUR
        # =====================================================================
        
        # 6. Relation manquante (user, partner, etc.)
        if 'another model is using' in erreur_str or 'constraint' in erreur_str:
            match = re.search(r"constraint: '([^']+)'", str(erreur))
            if match:
                contrainte = match.group(1)
                return {
                    'type': 'RELATION_MANQUANTE',
                    'contrainte': contrainte,
                    'correction_auto': False,
                    'correction': f'Relation {contrainte} manquante',
                    'demander_avis': True,
                    'question': f"Options pour {contrainte}:\n  1. Utiliser valeur par défaut (ex: admin)\n  2. Skip cet enregistrement\n  3. Arrêter\nChoix ? "
                }
        
        # 7. Erreur inconnue
        return {
            'type': 'ERREUR_INCONNUE',
            'correction_auto': False,
            'correction': 'Erreur non reconnue',
            'demander_avis': True,
            'question': f"Erreur: {str(erreur)[:100]}\n  1. Skip\n  2. Arrêter\nChoix ? "
        }
    
    def corriger_automatiquement(self, erreur, contexte):
        """
        Tente de corriger automatiquement une erreur
        
        Returns:
            tuple (corrige: bool, data_corrigee: dict, action: str)
        """
        analyse = self.analyser_erreur(erreur, contexte)
        
        # Si correction automatique possible
        if analyse['correction_auto']:
            if callable(analyse.get('action')):
                # Appliquer la correction
                data_corrigee = contexte['data'].copy()
                analyse['action'](data_corrigee)
                
                self.corrections_appliquees.append({
                    'type': analyse['type'],
                    'module': contexte['model'],
                    'correction': analyse['correction']
                })
                
                return True, data_corrigee, 'RETRY'
            
            elif analyse.get('action') == 'SKIP':
                self.corrections_appliquees.append({
                    'type': analyse['type'],
                    'module': contexte['model'],
                    'correction': analyse['correction']
                })
                return True, None, 'SKIP'
            
            elif analyse.get('action') == 'RECHERCHER_EXISTANT':
                return True, None, 'RECHERCHER'
        
        # Si avis utilisateur nécessaire
        if analyse['demander_avis'] and self.mode_interactif:
            print(f"\n⚠️ DÉCISION REQUISE")
            print(f"Module: {contexte['model']}")
            print(f"Enregistrement: {contexte.get('unique_val', 'N/A')}")
            print(f"Problème: {analyse['correction']}")
            print("")
            
            if 'question' in analyse:
                reponse = input(analyse['question']).strip()
                
                if analyse['type'] == 'CHAMP_OBLIGATOIRE_INCONNU':
                    # L'utilisateur fournit une valeur
                    if reponse:
                        data_corrigee = contexte['data'].copy()
                        data_corrigee[analyse['champ']] = reponse
                        return True, data_corrigee, 'RETRY'
                    else:
                        return True, None, 'SKIP'
                
                elif analyse['type'] == 'RELATION_MANQUANTE':
                    if reponse == '1':
                        # Utiliser valeur par défaut
                        data_corrigee = contexte['data'].copy()
                        # Déterminer la valeur par défaut selon le champ
                        if 'user_id' in str(erreur):
                            data_corrigee['user_id'] = 2
                        return True, data_corrigee, 'RETRY'
                    elif reponse == '2':
                        return True, None, 'SKIP'
                    else:
                        return False, None, 'STOP'
                
                elif analyse['type'] == 'ERREUR_INCONNUE':
                    if reponse == '1':
                        return True, None, 'SKIP'
                    else:
                        return False, None, 'STOP'
        
        # Pas de correction possible
        return False, None, 'ERROR'
    
    def generer_rapport(self):
        """Génère un rapport des corrections appliquées"""
        rapport = []
        rapport.append("="*70)
        rapport.append("RAPPORT AUTO-CORRECTION")
        rapport.append("="*70)
        rapport.append(f"\nCorrections appliquées: {len(self.corrections_appliquees)}")
        
        # Grouper par type
        par_type = {}
        for corr in self.corrections_appliquees:
            t = corr['type']
            if t not in par_type:
                par_type[t] = []
            par_type[t].append(corr)
        
        for type_err, corrections in par_type.items():
            rapport.append(f"\n{type_err}: {len(corrections)} corrections")
            for corr in corrections[:5]:
                rapport.append(f"  - {corr['module']}: {corr['correction']}")
            if len(corrections) > 5:
                rapport.append(f"  ... et {len(corrections) - 5} autres")
        
        return "\n".join(rapport)

