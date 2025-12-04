#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GESTIONNAIRE DE REPRISE
========================
Gère la reprise d'une migration interrompue
Assure l'intégrité des données via external_id
"""

import json
from pathlib import Path
from datetime import datetime

class GestionnaireReprise:
    """Gère les checkpoints et la reprise de migration"""
    
    def __init__(self, logs_dir='logs'):
        self.logs_dir = Path(logs_dir)
        self.logs_dir.mkdir(exist_ok=True)
        self.checkpoint_file = self.logs_dir / 'checkpoint_migration.json'
        self.checkpoint = self.charger_checkpoint()
    
    def charger_checkpoint(self):
        """Charge le dernier checkpoint"""
        if self.checkpoint_file.exists():
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {
            'date_debut': None,
            'date_dernier_checkpoint': None,
            'modules_termines': [],
            'module_en_cours': None,
            'dernier_id_source': None,
            'stats_globales': {
                'modules_ok': 0,
                'modules_erreur': 0,
                'total_crees': 0,
                'total_mis_a_jour': 0
            }
        }
    
    def sauver_checkpoint(self):
        """Sauvegarde le checkpoint actuel"""
        self.checkpoint['date_dernier_checkpoint'] = datetime.now().isoformat()
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.checkpoint, f, indent=2)
    
    def marquer_module_debut(self, module):
        """Marque le début de migration d'un module"""
        if not self.checkpoint['date_debut']:
            self.checkpoint['date_debut'] = datetime.now().isoformat()
        
        self.checkpoint['module_en_cours'] = module
        self.checkpoint['dernier_id_source'] = None
        self.sauver_checkpoint()
    
    def marquer_module_termine(self, module, stats):
        """Marque la fin de migration d'un module"""
        if module not in self.checkpoint['modules_termines']:
            self.checkpoint['modules_termines'].append(module)
        
        self.checkpoint['module_en_cours'] = None
        self.checkpoint['dernier_id_source'] = None
        
        # Mettre à jour stats globales
        if stats['erreurs'] == 0:
            self.checkpoint['stats_globales']['modules_ok'] += 1
        else:
            self.checkpoint['stats_globales']['modules_erreur'] += 1
        
        self.checkpoint['stats_globales']['total_crees'] += stats['nouveaux']
        self.checkpoint['stats_globales']['total_mis_a_jour'] += stats['existants']
        
        self.sauver_checkpoint()
    
    def enregistrer_progression(self, source_id):
        """Enregistre l'ID source en cours de traitement"""
        self.checkpoint['dernier_id_source'] = source_id
        # On ne sauvegarde pas à chaque enregistrement (trop lent)
        # Seulement tous les 100 enregistrements
    
    def est_module_termine(self, module):
        """Vérifie si un module a déjà été migré"""
        return module in self.checkpoint['modules_termines']
    
    def obtenir_modules_a_migrer(self, tous_modules):
        """
        Retourne les modules restant à migrer
        
        Args:
            tous_modules: Liste de tous les modules
        
        Returns:
            Liste des modules pas encore migrés
        """
        return [m for m in tous_modules if not self.est_module_termine(m)]
    
    def reinitialiser(self):
        """Réinitialise le checkpoint (nouvelle migration)"""
        self.checkpoint = {
            'date_debut': None,
            'date_dernier_checkpoint': None,
            'modules_termines': [],
            'module_en_cours': None,
            'dernier_id_source': None,
            'stats_globales': {
                'modules_ok': 0,
                'modules_erreur': 0,
                'total_crees': 0,
                'total_mis_a_jour': 0
            }
        }
        self.sauver_checkpoint()
        
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
    
    def afficher_etat(self):
        """Affiche l'état actuel de la migration"""
        print("\n" + "="*70)
        print("ÉTAT DE LA MIGRATION")
        print("="*70)
        
        if self.checkpoint['date_debut']:
            print(f"Début: {self.checkpoint['date_debut']}")
            print(f"Dernier checkpoint: {self.checkpoint['date_dernier_checkpoint']}")
            print(f"Modules terminés: {len(self.checkpoint['modules_termines'])}")
            print(f"Module en cours: {self.checkpoint['module_en_cours']}")
            print(f"\nStatistiques:")
            print(f"  Modules OK: {self.checkpoint['stats_globales']['modules_ok']}")
            print(f"  Créés: {self.checkpoint['stats_globales']['total_crees']}")
            print(f"  Mis à jour: {self.checkpoint['stats_globales']['total_mis_a_jour']}")
        else:
            print("Aucune migration en cours")
        
        print("="*70)


class VerificateurIntegrite:
    """Vérifie l'intégrité du transfert de données"""
    
    def __init__(self, connexion):
        self.conn = connexion
        self.logs_dir = Path('logs')
    
    def verifier_module(self, model, nom_fichier):
        """
        Vérifie l'intégrité de la migration d'un module
        
        Returns:
            dict avec résultats de vérification
        """
        resultat = {
            'module': model,
            'ok': True,
            'problemes': []
        }
        
        # Charger mapping
        mapping_file = self.logs_dir / f'{nom_fichier}_mapping.json'
        if not mapping_file.exists():
            resultat['ok'] = False
            resultat['problemes'].append("Fichier mapping manquant")
            return resultat
        
        with open(mapping_file, 'r') as f:
            mapping = json.load(f)
        
        # Vérifier via external_id
        try:
            # External_id SOURCE
            ext_src = self.conn.executer_source('ir.model.data', 'search_read',
                                               [('model', '=', model)],
                                               fields=['res_id', 'module', 'name'])
            
            src_to_ext = {ext['res_id']: f"{ext['module']}.{ext['name']}" for ext in ext_src}
            
            # External_id DESTINATION
            ext_dst = self.conn.executer_destination('ir.model.data', 'search_read',
                                                    [('model', '=', model)],
                                                    fields=['res_id', 'module', 'name'])
            
            ext_to_dst = {f"{ext['module']}.{ext['name']}": ext['res_id'] for ext in ext_dst}
            
            # Vérifier cohérence mapping vs external_id
            incoherences = 0
            for src_id, dest_id in mapping.items():
                src_id = int(src_id)
                
                # Si external_id existe
                if src_id in src_to_ext:
                    ext_key = src_to_ext[src_id]
                    if ext_key in ext_to_dst:
                        dest_id_via_ext = ext_to_dst[ext_key]
                        if dest_id != dest_id_via_ext:
                            incoherences += 1
                            resultat['problemes'].append(
                                f"Incohérence ID {src_id}: mapping dit {dest_id}, external_id dit {dest_id_via_ext}"
                            )
            
            if incoherences > 0:
                resultat['ok'] = False
                resultat['problemes'].append(f"{incoherences} incohérences mapping/external_id")
            
            # Vérifier complétude
            count_src = self.conn.executer_source(model, 'search_count', [])
            count_mapped = len(mapping)
            
            if count_mapped < count_src:
                pourcentage = (count_mapped / count_src * 100) if count_src > 0 else 0
                if pourcentage < 95:
                    resultat['ok'] = False
                    resultat['problemes'].append(
                        f"Migration incomplète: {count_mapped}/{count_src} ({pourcentage:.1f}%)"
                    )
                elif pourcentage < 100:
                    resultat['problemes'].append(
                        f"Migration quasi-complète: {count_mapped}/{count_src} ({pourcentage:.1f}%)"
                    )
            
        except Exception as e:
            resultat['ok'] = False
            resultat['problemes'].append(f"Erreur vérification: {str(e)[:60]}")
        
        return resultat
    
    def verifier_tout(self, modules):
        """
        Vérifie l'intégrité de tous les modules
        
        Args:
            modules: Liste des modules à vérifier
        
        Returns:
            dict avec résultats globaux
        """
        resultats = []
        modules_ok = 0
        modules_problemes = 0
        
        for model in modules:
            config = GestionnaireConfiguration.obtenir_config_module(model)
            if not config:
                continue
            
            resultat = self.verifier_module(model, config['fichier'])
            resultats.append(resultat)
            
            if resultat['ok']:
                modules_ok += 1
            else:
                modules_problemes += 1
        
        return {
            'modules_ok': modules_ok,
            'modules_problemes': modules_problemes,
            'details': resultats
        }

