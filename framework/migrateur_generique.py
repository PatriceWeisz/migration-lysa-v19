#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATEUR GÉNÉRIQUE
===================
Classe réutilisable pour migrer n'importe quel module Odoo
Gère automatiquement les différences de champs v16 → v19
"""

import json
from pathlib import Path
from .analyseur_differences_champs import AnalyseurDifferencesChamps
from .auto_correction import AutoCorrecteur
from .gestionnaire_statuts import GestionnaireStatuts

class MigrateurGenerique:
    """
    Classe générique pour migrer n'importe quel module Odoo
    Gère automatiquement tous les champs, relations et external_id
    """
    
    def __init__(self, connexion, model, config):
        """
        Initialise le migrateur
        
        Args:
            connexion: Instance ConnexionDoubleV19
            model: Nom du modèle Odoo (ex: 'project.project')
            config: dict avec:
                - nom: Nom du module (ex: 'Projets')
                - fichier: Nom fichier mapping (ex: 'project')
                - unique_field: Champ unique (ex: 'name')
                - mode_test: bool (default False)
                - test_limit: int (default 10)
                - skip_conditions: list de conditions
                - relations: dict des relations à mapper
                - valeurs_defaut: dict des valeurs par défaut
                - mode_update: bool (default False) - Met à jour les existants
        """
        self.conn = connexion
        self.model = model
        self.config = config
        self.logs_dir = Path('logs')
        self.logs_dir.mkdir(exist_ok=True)
        
        # Analyseur de différences de champs
        self.analyseur = AnalyseurDifferencesChamps(connexion)
        
        # Auto-correcteur
        mode_interactif = config.get('mode_interactif', True)
        self.auto_correcteur = AutoCorrecteur(connexion, mode_interactif)
        
        # Charger le mapping existant
        mapping_file = self.logs_dir / f"{config['fichier']}_mapping.json"
        if mapping_file.exists():
            with open(mapping_file, 'r') as f:
                self.mapping = json.load(f)
                self.mapping = {int(k): v for k, v in self.mapping.items()}
        else:
            self.mapping = {}
        
        # Charger les mappings de relations
        self.relation_mappings = {}
        for relation, fichier in config.get('relations', {}).items():
            rel_file = self.logs_dir / fichier
            if rel_file.exists():
                with open(rel_file, 'r') as f:
                    self.relation_mappings[relation] = json.load(f)
            else:
                self.relation_mappings[relation] = {}
    
    def afficher(self, msg=""):
        """Affiche un message"""
        import sys
        sys.stdout.write(str(msg) + '\n')
        sys.stdout.flush()
    
    def obtenir_champs_migrables(self):
        """
        Obtient automatiquement TOUS les champs migrables du modèle
        En comparant source et destination
        Inclut les champs binary (images)
        """
        self.afficher("Analyse des champs migrables...")
        
        # Champs SOURCE
        fields_src = self.conn.executer_source('ir.model.fields', 'search_read',
                                              [('model', '=', self.model), ('store', '=', True)],
                                              fields=['name', 'ttype', 'compute', 'readonly'])
        
        src_dict = {f['name']: f for f in fields_src}
        
        # Champs DESTINATION
        fields_dst = self.conn.executer_destination('ir.model.fields', 'search_read',
                                                   [('model', '=', self.model), ('store', '=', True)],
                                                   fields=['name', 'ttype'])
        
        dst_names = {f['name'] for f in fields_dst}
        
        # Champs à exclure
        EXCLUS = {
            'id', '__last_update', 'display_name',
            'create_date', 'create_uid', 'write_date', 'write_uid',
            'message_ids', 'message_follower_ids', 'activity_ids',
            'rating_ids', 'website_message_ids', 'message_main_attachment_id'
        }
        
        # Champs migrables
        migrables = []
        champs_binary = []  # Pour tracking
        
        for fname in src_dict.keys():
            field_info = src_dict[fname]
            
            # Exclure
            if fname in EXCLUS:
                continue
            if field_info.get('compute') and not field_info.get('store'):
                continue
            if fname not in dst_names:
                continue
            
            migrables.append(fname)
            
            # Tracker les champs binary (images)
            if field_info.get('ttype') == 'binary':
                champs_binary.append(fname)
        
        self.afficher(f"OK {len(migrables)} champs migrables détectés")
        if champs_binary:
            self.afficher(f"   dont {len(champs_binary)} champs binary (images/fichiers)")
        
        return migrables
    
    def mapper_relation(self, field_name, value):
        """
        Mappe automatiquement une relation many2one
        
        Args:
            field_name: Nom du champ
            value: Valeur source (id ou [id, 'name'])
        
        Returns:
            ID mappé ou None
        """
        if not value:
            return None
        
        # Extraire l'ID
        if isinstance(value, (list, tuple)):
            source_id = value[0]
        else:
            source_id = value
        
        # Chercher dans le mapping de la relation
        if field_name in self.relation_mappings:
            mapping = self.relation_mappings[field_name]
            if str(source_id) in mapping:
                return mapping[str(source_id)]
        
        # Pas trouvé
        return None
    
    def preparer_data(self, rec, champs):
        """
        Prépare les données pour la création/mise à jour
        Gère automatiquement les relations ET les transformations v16→v19
        
        Args:
            rec: Enregistrement source
            champs: Liste des champs à migrer
        
        Returns:
            dict des données prêtes pour create/write
        """
        # ÉTAPE 1: Appliquer les transformations v16 → v19
        rec_transforme = self.analyseur.appliquer_transformations(self.model, rec)
        
        data = {}
        relations_config = self.config.get('relations', {})
        
        for field in champs:
            if field == 'id':
                continue
            
            # Utiliser l'enregistrement transformé
            value = rec_transforme.get(field)
            
            # Ignorer valeurs vides
            if value is None or value is False or value == '':
                continue
            
            # PRIORITÉ 1: Gérer les champs One2many spéciaux (AVANT les autres)
            if field in ['invoice_repartition_line_ids', 'refund_repartition_line_ids']:
                if isinstance(value, list) and value and isinstance(value[0], int):
                    # Lire les lignes de répartition en SOURCE
                    try:
                        lines = self.conn.executer_source(
                            'account.tax.repartition.line',
                            'read',
                            value,
                            ['repartition_type', 'factor_percent', 'account_id', 'use_in_tax_closing']
                        )
                        
                        # Transformer en commandes Odoo (0, 0, {...})
                        commands = []
                        for line in lines:
                            line_data = {
                                'repartition_type': line.get('repartition_type', 'tax'),
                                'factor_percent': line.get('factor_percent', 100.0),
                                'use_in_tax_closing': line.get('use_in_tax_closing', False),
                            }
                            
                            # Account_id (optionnel, on le skip pour l'instant)
                            # TODO: mapper l'account_id
                            
                            commands.append((0, 0, line_data))
                        
                        if commands:
                            data[field] = commands
                    except Exception as e:
                        # Si erreur, on skip ce champ complètement
                        pass
                continue  # Passer au champ suivant
            
            # PRIORITÉ 2: Gérer les relations many2one
            if field in relations_config and isinstance(value, (list, tuple)):
                mapped_id = self.mapper_relation(field, value)
                if mapped_id:
                    data[field] = mapped_id
                elif field in self.config.get('valeurs_defaut', {}):
                    data[field] = self.config['valeurs_defaut'][field]
                # Sinon on skip ce champ
            
            # Relations many2one sans mapping spécifique
            elif isinstance(value, (list, tuple)) and len(value) == 2:
                data[field] = value[0]
            
            # Relations many2many ou one2many (liste d'IDs) - autres champs
            elif isinstance(value, list) and value and isinstance(value[0], int):
                # Autres champs One2many/Many2many: skip pour l'instant
                pass
            
            # Valeurs simples
            else:
                data[field] = value
        
        # Ajouter valeurs par défaut manquantes
        for field, value in self.config.get('valeurs_defaut', {}).items():
            if field not in data:
                data[field] = value
        
        return data
    
    def charger_external_ids(self):
        """Charge les external_id pour le mapping source -> destination"""
        self.afficher("Chargement external_id...")
        
        # External_id SOURCE
        ext_src = self.conn.executer_source('ir.model.data', 'search_read',
                                           [('model', '=', self.model)],
                                           fields=['res_id', 'module', 'name'])
        
        src_to_ext = {ext['res_id']: f"{ext['module']}.{ext['name']}" for ext in ext_src}
        
        # External_id DESTINATION
        ext_dst = self.conn.executer_destination('ir.model.data', 'search_read',
                                                [('model', '=', self.model)],
                                                fields=['res_id', 'module', 'name'])
        
        ext_to_dst = {f"{ext['module']}.{ext['name']}": ext['res_id'] for ext in ext_dst}
        
        self.afficher(f"OK {len(src_to_ext)} external_id SOURCE, {len(ext_to_dst)} DEST")
        
        return src_to_ext, ext_to_dst
    
    def migrer(self):
        """
        Lance la migration complète du module
        
        Returns:
            dict avec statistiques
        """
        self.afficher(f"\n{'='*70}")
        self.afficher(f"MIGRATION: {self.config['nom']}")
        self.afficher(f"Modèle: {self.model}")
        self.afficher(f"{'='*70}")
        
        # Charger external_id
        src_to_ext, ext_to_dst = self.charger_external_ids()
        
        # Obtenir champs
        champs = self.obtenir_champs_migrables()
        
        self.afficher(f"Mapping existant: {len(self.mapping)}")
        
        # Récupérer SOURCE
        self.afficher("Récupération SOURCE...")
        if self.config.get('mode_test'):
            src = self.conn.executer_source(self.model, 'search_read', [],
                                           fields=champs,
                                           limit=self.config.get('test_limit', 10))
        else:
            src = self.conn.executer_source(self.model, 'search_read', [],
                                           fields=champs)
        
        self.afficher(f"OK {len(src)} enregistrements")
        
        # Récupérer DESTINATION
        self.afficher("Récupération DESTINATION...")
        unique_field = self.config['unique_field']
        dst = self.conn.executer_destination(self.model, 'search_read', [],
                                            fields=[unique_field])
        dst_index = {d[unique_field]: d['id'] for d in dst if d.get(unique_field)}
        self.afficher(f"OK {len(dst)} enregistrements\n")
        
        # Compteurs
        stats = {
            'nouveaux': 0,
            'existants': 0,
            'erreurs': 0,
            'skipped': 0
        }
        
        # Migrer chaque enregistrement
        for idx, rec in enumerate(src, 1):
            if idx % 10 == 0 or idx == len(src):
                self.afficher(f"Traitement {idx}/{len(src)}...")
            
            source_id = rec['id']
            unique_val = rec.get(unique_field)
            
            # Skip conditions
            skip = False
            for condition in self.config.get('skip_conditions', []):
                if condition(rec):
                    stats['skipped'] += 1
                    skip = True
                    break
            
            if skip:
                continue
            
            # Vérifier via external_id d'abord
            dest_id = None
            if source_id in src_to_ext:
                ext_key = src_to_ext[source_id]
                if ext_key in ext_to_dst:
                    dest_id = ext_to_dst[ext_key]
                    self.mapping[source_id] = dest_id
            
            # Si pas trouvé via external_id, chercher par champ unique
            if not dest_id and unique_val and unique_val in dst_index:
                dest_id = dst_index[unique_val]
                self.mapping[source_id] = dest_id
            
            # Si trouvé (via external_id ou champ unique)
            if dest_id:
                # MODE UPDATE : Mettre à jour les champs manquants
                if self.config.get('mode_update', False):
                    try:
                        data = self.preparer_data(rec, champs)
                        if data:
                            self.conn.executer_destination(self.model, 'write',
                                                         [dest_id], data)
                            if idx % 10 != 0 and idx != len(src):
                                self.afficher(f"  -> MAJ: {unique_val}")
                    except Exception as e:
                        if idx % 10 != 0 and idx != len(src):
                            self.afficher(f"  -> Erreur MAJ: {str(e)[:40]}")
                
                stats['existants'] += 1
                continue
            
            # Créer (avec auto-correction)
            data = self.preparer_data(rec, champs)
            
            if not data:
                stats['erreurs'] += 1
                continue
            
            max_tentatives = 3
            tentative = 0
            cree = False
            
            while tentative < max_tentatives and not cree:
                try:
                    dest_id = self.conn.executer_destination(self.model, 'create', data)
                    self.mapping[source_id] = dest_id
                    
                    if unique_val:
                        dst_index[unique_val] = dest_id
                    
                    stats['nouveaux'] += 1
                    cree = True
                    
                except Exception as e:
                    tentative += 1
                    
                    # Tenter auto-correction
                    contexte = {
                        'model': self.model,
                        'record': rec,
                        'data': data,
                        'unique_val': unique_val
                    }
                    
                    corrige, data_corrigee, action = self.auto_correcteur.corriger_automatiquement(e, contexte)
                    
                    if corrige:
                        if action == 'RETRY':
                            # Réessayer avec données corrigées
                            data = data_corrigee
                            self.afficher(f"  -> Correction appliquée, nouvelle tentative...")
                            continue
                        
                        elif action == 'SKIP':
                            # Skip cet enregistrement
                            stats['skipped'] += 1
                            break
                        
                        elif action == 'RECHERCHER':
                            # Chercher si l'enregistrement existe déjà
                            try:
                                if unique_val:
                                    dest_ids = self.conn.executer_destination(
                                        self.model, 'search',
                                        [(self.config['champ_unique'], '=', unique_val)]
                                    )
                                    if dest_ids:
                                        dest_id = dest_ids[0]
                                        self.mapping[source_id] = dest_id
                                        stats['existants'] += 1
                                        cree = True
                                        break
                            except:
                                pass
                            
                            stats['skipped'] += 1
                            break
                        
                        elif action == 'STOP':
                            # L'utilisateur a demandé d'arrêter
                            self.afficher("\n⚠️ Migration arrêtée par l'utilisateur")
                            return stats
                    else:
                        # Pas de correction possible
                        if tentative >= max_tentatives:
                            self.afficher(f"ERREUR {unique_val}: {str(e)[:60]}")
                            stats['erreurs'] += 1
                            break
        
        # Sauvegarder mapping
        mapping_file = self.logs_dir / f"{self.config['fichier']}_mapping.json"
        with open(mapping_file, 'w') as f:
            json.dump({str(k): v for k, v in self.mapping.items()}, f, indent=2)
        
        # Résumé
        self.afficher(f"\n{'='*70}")
        self.afficher("RÉSULTAT")
        self.afficher(f"{'='*70}")
        self.afficher(f"Nouveaux : {stats['nouveaux']}")
        self.afficher(f"Existants: {stats['existants']}")
        self.afficher(f"Erreurs  : {stats['erreurs']}")
        self.afficher(f"Skippés  : {stats['skipped']}")
        self.afficher(f"Total    : {len(self.mapping)}/{len(src)}")
        self.afficher(f"{'='*70}")
        
        # Rapport auto-correction
        if self.auto_correcteur.corrections_appliquees:
            self.afficher("\n" + self.auto_correcteur.generer_rapport())
        
        return stats

