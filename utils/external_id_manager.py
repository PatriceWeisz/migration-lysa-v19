#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GESTIONNAIRE D'EXTERNAL ID
===========================
Gère la création et la recherche d'external_id pour tous les enregistrements migrés
"""

import logging

class ExternalIdManager:
    """Gestionnaire des external_id pour la migration"""
    
    def __init__(self, connexion):
        """
        Initialise le gestionnaire
        
        Args:
            connexion: Instance de ConnexionDoubleV19
        """
        self.conn = connexion
        self.cache_external_ids_source = {}  # Cache des external_id source
    
    def get_external_id_from_source(self, model, source_id):
        """
        Récupère l'external_id d'un enregistrement depuis la source
        
        Args:
            model: Nom du modèle Odoo
            source_id: ID de l'enregistrement dans la source
        
        Returns:
            dict|None: {'module': 'xxx', 'name': 'yyy'} ou None si pas d'external_id
        """
        cache_key = f"{model}_{source_id}"
        
        # Vérifier le cache
        if cache_key in self.cache_external_ids_source:
            return self.cache_external_ids_source[cache_key]
        
        try:
            # Rechercher dans ir.model.data de la source
            results = self.conn.executer_source(
                'ir.model.data',
                'search_read',
                [
                    ('model', '=', model),
                    ('res_id', '=', source_id)
                ],
                fields=['module', 'name']
            )
            
            if results:
                ext_id = {
                    'module': results[0]['module'],
                    'name': results[0]['name']
                }
                self.cache_external_ids_source[cache_key] = ext_id
                return ext_id
            
            self.cache_external_ids_source[cache_key] = None
            return None
            
        except Exception as e:
            logging.warning(f"Erreur recuperation external_id source {model}/{source_id}: {e}")
            return None
    
    def copier_external_id(self, model, dest_id, source_id):
        """
        Copie l'external_id de la source vers la destination
        
        Args:
            model: Nom du modèle Odoo
            dest_id: ID de l'enregistrement dans la destination
            source_id: ID de l'enregistrement dans la source
        
        Returns:
            bool: True si succès, False sinon
        """
        # Récupérer l'external_id de la source
        ext_id = self.get_external_id_from_source(model, source_id)
        
        if not ext_id:
            # Pas d'external_id dans la source, on n'en crée pas
            logging.debug(f"Pas d'external_id pour {model}/{source_id}")
            return False
        
        try:
            # Créer l'enregistrement ir.model.data dans la destination
            # avec le MÊME module et name que la source
            self.conn.executer_destination(
                'ir.model.data',
                'create',
                {
                    'name': ext_id['name'],
                    'module': ext_id['module'],
                    'model': model,
                    'res_id': dest_id,
                }
            )
            logging.info(f"External_id copie: {ext_id['module']}.{ext_id['name']} -> ID {dest_id}")
            return True
            
        except Exception as e:
            logging.warning(f"Erreur copie external_id {ext_id['module']}.{ext_id['name']}: {e}")
            return False
    
    def rechercher_par_external_id(self, model, source_id):
        """
        Recherche un enregistrement dans la destination par son external_id source
        
        Args:
            model: Nom du modèle Odoo
            source_id: ID de l'enregistrement dans la source
        
        Returns:
            int|None: ID de l'enregistrement dans la destination, ou None si non trouvé
        """
        # Récupérer l'external_id de la source
        ext_id = self.get_external_id_from_source(model, source_id)
        
        if not ext_id:
            return None
        
        try:
            # Rechercher dans ir.model.data de la destination avec le même module/name
            results = self.conn.executer_destination(
                'ir.model.data',
                'search_read',
                [
                    ('name', '=', ext_id['name']),
                    ('module', '=', ext_id['module']),
                    ('model', '=', model)
                ],
                fields=['res_id']
            )
            
            if results:
                return results[0]['res_id']
            return None
            
        except Exception as e:
            logging.warning(f"Erreur recherche external_id {ext_id['module']}.{ext_id['name']}: {e}")
            return None
    
    def verifier_existe(self, model, source_id):
        """
        Vérifie si un enregistrement existe déjà via son external_id
        
        Args:
            model: Nom du modèle Odoo
            source_id: ID de l'enregistrement dans la source
        
        Returns:
            tuple: (existe: bool, dest_id: int|None, external_id: dict|None)
        """
        dest_id = self.rechercher_par_external_id(model, source_id)
        ext_id = self.get_external_id_from_source(model, source_id)
        return (dest_id is not None, dest_id, ext_id)
    
    def get_all_external_ids_from_source(self, model):
        """
        Récupère tous les external_id d'un modèle depuis la source
        
        Args:
            model: Nom du modèle Odoo
        
        Returns:
            dict: {source_id: {'module': 'xxx', 'name': 'yyy'}}
        """
        try:
            # Rechercher tous les external_id dans la source pour ce modèle
            results = self.conn.executer_source(
                'ir.model.data',
                'search_read',
                [('model', '=', model)],
                fields=['module', 'name', 'res_id']
            )
            
            mapping = {}
            for result in results:
                source_id = result['res_id']
                mapping[source_id] = {
                    'module': result['module'],
                    'name': result['name']
                }
            
            logging.info(f"OK {len(mapping)} external_ids trouves pour {model} dans source")
            return mapping
            
        except Exception as e:
            logging.error(f"Erreur recuperation external_ids source {model}: {e}")
            return {}
    
    def charger_mapping_depuis_external_ids(self, model):
        """
        Charge un mapping source_id -> dest_id depuis les external_id déjà copiés
        
        Args:
            model: Nom du modèle Odoo
        
        Returns:
            dict: {source_id: dest_id}
        """
        # Récupérer tous les external_id de la source
        source_ext_ids = self.get_all_external_ids_from_source(model)
        
        if not source_ext_ids:
            return {}
        
        mapping = {}
        
        try:
            # Pour chaque external_id source, chercher dans la destination
            for source_id, ext_id in source_ext_ids.items():
                results = self.conn.executer_destination(
                    'ir.model.data',
                    'search_read',
                    [
                        ('module', '=', ext_id['module']),
                        ('name', '=', ext_id['name']),
                        ('model', '=', model)
                    ],
                    fields=['res_id']
                )
                
                if results:
                    mapping[source_id] = results[0]['res_id']
            
            logging.info(f"OK {len(mapping)} enregistrements mappes pour {model}")
            return mapping
            
        except Exception as e:
            logging.error(f"Erreur chargement mapping {model}: {e}")
            return {}

