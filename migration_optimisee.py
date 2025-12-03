#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION OPTIMISÉE ULTRA-RAPIDE
=================================
Optimisations:
- Traitement par lots
- Cache des external_id
- Requêtes groupées
- Vérifications minimales
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Forcer affichage
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19
from utils.external_id_manager import ExternalIdManager

# Configuration
MODE_TEST = True
TEST_LIMIT = 10
BATCH_SIZE = 100  # Traiter par lots de 100

LOGS_DIR = Path('logs')
LOGS_DIR.mkdir(exist_ok=True)

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

class MigrationOptimisee:
    """Migration ultra-optimisée"""
    
    def __init__(self):
        self.conn = ConnexionDoubleV19()
        self.ext_mgr = None
        
        # Cache global des external_id pour éviter requêtes répétées
        self.cache_ext_id_source = {}
        self.cache_ext_id_dest = {}
        
        # Mappings en mémoire
        self.mappings = {}
    
    def precharger_external_ids(self, model):
        """Précharge TOUS les external_id d'un modèle en une seule requête"""
        afficher(f"  Prechargement external_id {model}...")
        
        try:
            # Source
            ext_src = self.conn.executer_source('ir.model.data', 'search_read',
                                               [('model', '=', model)],
                                               fields=['res_id', 'module', 'name'])
            
            for ext in ext_src:
                key = f"{model}_{ext['res_id']}"
                self.cache_ext_id_source[key] = {
                    'module': ext['module'],
                    'name': ext['name']
                }
            
            # Destination
            ext_dst = self.conn.executer_destination('ir.model.data', 'search_read',
                                                    [('model', '=', model)],
                                                    fields=['res_id', 'module', 'name'])
            
            for ext in ext_dst:
                key = f"{ext['module']}.{ext['name']}"
                self.cache_ext_id_dest[key] = ext['res_id']
            
            afficher(f"    OK {len(ext_src)} source, {len(ext_dst)} dest")
            return True
            
        except Exception as e:
            afficher(f"    ATTENTION: {e}")
            return False
    
    def verifier_existe_rapide(self, model, source_id):
        """Vérifie existence via cache (ultra-rapide)"""
        cache_key = f"{model}_{source_id}"
        
        # Vérifier si external_id existe
        if cache_key in self.cache_ext_id_source:
            ext_id = self.cache_ext_id_source[cache_key]
            ext_key = f"{ext_id['module']}.{ext_id['name']}"
            
            if ext_key in self.cache_ext_id_dest:
                return True, self.cache_ext_id_dest[ext_key], ext_id
        
        return False, None, None
    
    def copier_external_id_rapide(self, model, dest_id, source_id):
        """Copie external_id si disponible (via cache)"""
        cache_key = f"{model}_{source_id}"
        
        if cache_key in self.cache_ext_id_source:
            ext_id = self.cache_ext_id_source[cache_key]
            
            try:
                self.conn.executer_destination('ir.model.data', 'create', {
                    'name': ext_id['name'],
                    'module': ext_id['module'],
                    'model': model,
                    'res_id': dest_id,
                })
                
                # Mettre à jour le cache dest
                ext_key = f"{ext_id['module']}.{ext_id['name']}"
                self.cache_ext_id_dest[ext_key] = dest_id
                
                return True
            except:
                return False
        
        return False
    
    def migrer_module_optimise(self, model, fields, nom, data_preparer):
        """Migre un module de manière optimisée"""
        afficher(f"\n{'='*70}")
        afficher(f"MIGRATION: {nom}")
        if MODE_TEST:
            afficher(f"  MODE TEST: {TEST_LIMIT} enregistrements")
        afficher(f"{'='*70}")
        
        debut = datetime.now()
        
        # Précharger external_id
        self.precharger_external_ids(model)
        
        # Récupérer source
        afficher(f"  Recuperation SOURCE...")
        kwargs = {'fields': fields}
        if MODE_TEST:
            kwargs['limit'] = TEST_LIMIT
        
        records = self.conn.executer_source(model, 'search_read', [], **kwargs)
        total = len(records)
        afficher(f"  OK {total} enregistrements")
        
        # Récupérer les existants avec champs clés
        afficher(f"  Recuperation DESTINATION...")
        
        # Champs à récupérer selon le modèle pour vérifier doublons
        champs_dest = ['id']
        if model == 'account.account':
            champs_dest.append('code')
        elif model == 'res.partner':
            champs_dest.extend(['ref', 'email'])
        elif model == 'account.journal':
            champs_dest.append('code')
        elif model == 'res.users':
            champs_dest.append('login')
        elif model == 'product.template':
            champs_dest.append('default_code')
        
        dest_records = self.conn.executer_destination(model, 'search_read', [],
                                                      fields=champs_dest)
        
        # Créer index par champ unique
        dest_by_code = {}
        dest_by_ref = {}
        dest_by_email = {}
        dest_by_login = {}
        
        for rec in dest_records:
            if 'code' in rec and rec['code']:
                dest_by_code[rec['code']] = rec['id']
            if 'ref' in rec and rec['ref']:
                dest_by_ref[rec['ref']] = rec['id']
            if 'email' in rec and rec['email']:
                dest_by_email[rec['email']] = rec['id']
            if 'login' in rec and rec['login']:
                dest_by_login[rec['login']] = rec['id']
            if 'default_code' in rec and rec['default_code']:
                dest_by_code[rec['default_code']] = rec['id']
        
        dest_ids = {r['id'] for r in dest_records}
        afficher(f"  OK {len(dest_ids)} enregistrements existants")
        
        mapping = {}
        nouveau = 0
        existant = 0
        erreurs = 0
        
        # Traiter par lots
        for batch_start in range(0, total, BATCH_SIZE):
            batch = records[batch_start:batch_start + BATCH_SIZE]
            
            if not MODE_TEST:
                afficher(f"  Lot {batch_start//BATCH_SIZE + 1}/{(total + BATCH_SIZE - 1)//BATCH_SIZE}")
            
            for rec in batch:
                source_id = rec['id']
                
                # 1. Vérifier via cache external_id
                existe, dest_id, ext_id = self.verifier_existe_rapide(model, source_id)
                
                if existe:
                    mapping[source_id] = dest_id
                    existant += 1
                    if MODE_TEST:
                        afficher(f"  [{existant + nouveau}/{total}] Existe via ext_id (ID: {dest_id})")
                    continue
                
                # 2. Vérifier par champ unique (code, ref, login, email...)
                check_dest_id = None
                
                if model == 'account.account' and rec.get('code') in dest_by_code:
                    check_dest_id = dest_by_code[rec['code']]
                elif model == 'account.journal' and rec.get('code') in dest_by_code:
                    check_dest_id = dest_by_code[rec['code']]
                elif model == 'res.partner':
                    if rec.get('ref') and rec['ref'] in dest_by_ref:
                        check_dest_id = dest_by_ref[rec['ref']]
                    elif rec.get('email') and rec['email'] in dest_by_email:
                        check_dest_id = dest_by_email[rec['email']]
                elif model == 'res.users' and rec.get('login') in dest_by_login:
                    check_dest_id = dest_by_login[rec['login']]
                elif model == 'product.template' and rec.get('default_code') in dest_by_code:
                    check_dest_id = dest_by_code[rec['default_code']]
                
                if check_dest_id:
                    # Existe déjà, copier juste l'external_id
                    self.copier_external_id_rapide(model, check_dest_id, source_id)
                    mapping[source_id] = check_dest_id
                    existant += 1
                    if MODE_TEST:
                        afficher(f"  [{existant + nouveau}/{total}] Existe par code/ref (ID: {check_dest_id})")
                    continue
                
                # 3. Créer seulement si n'existe pas
                # Préparer données
                data = data_preparer(rec, self.mappings)
                
                if data is None:
                    # Skip si dépendances manquantes
                    erreurs += 1
                    continue
                    
                    try:
                        dest_id = self.conn.executer_destination(model, 'create', data)
                        
                        # Copier external_id
                        self.copier_external_id_rapide(model, dest_id, source_id)
                        
                        # Mettre à jour les index pour éviter doublons dans le même lot
                        if model == 'account.account' and rec.get('code'):
                            dest_by_code[rec['code']] = dest_id
                        elif model == 'account.journal' and rec.get('code'):
                            dest_by_code[rec['code']] = dest_id
                        elif model == 'res.partner':
                            if rec.get('ref'):
                                dest_by_ref[rec['ref']] = dest_id
                            if rec.get('email'):
                                dest_by_email[rec['email']] = dest_id
                        elif model == 'res.users' and rec.get('login'):
                            dest_by_login[rec['login']] = dest_id
                        elif model == 'product.template' and rec.get('default_code'):
                            dest_by_code[rec['default_code']] = dest_id
                        
                        mapping[source_id] = dest_id
                        dest_ids.add(dest_id)
                        nouveau += 1
                        
                        if MODE_TEST:
                            afficher(f"  [{existant + nouveau}/{total}] Cree (ID: {dest_id})")
                        
                    except Exception as e:
                        if MODE_TEST:
                            afficher(f"  ERREUR: {str(e)[:60]}")
                        erreurs += 1
        
        duree = (datetime.now() - debut).total_seconds()
        vitesse = total / duree if duree > 0 else 0
        
        afficher(f"\n  RESULTAT: {nouveau} nouveaux, {existant} existants, {erreurs} erreurs")
        afficher(f"  DUREE: {duree:.1f}s ({vitesse:.0f} enreg/s)")
        
        # Sauvegarder
        nom_fichier = model.replace('.', '_')
        with open(LOGS_DIR / f'{nom_fichier}_mapping.json', 'w') as f:
            json.dump(mapping, f, indent=2)
        
        self.mappings[model] = mapping
        return mapping
    
    def verifier_existence_par_champ(self, model, field, value):
        """Vérifie si un enregistrement existe par un champ unique"""
        try:
            results = self.conn.executer_destination(model, 'search',
                                                    [(field, '=', value)])
            return results[0] if results else None
        except:
            return None
    
    def preparer_compte(self, rec, mappings):
        """Prépare données compte - AVEC vérification du code"""
        # IMPORTANT: Vérifier d'abord si le code existe déjà
        code = rec['code']
        
        # Cette vérification sera faite AVANT la création dans migrer_module_optimise
        return {
            'code': code,
            'name': rec['name'],
            'account_type': rec.get('account_type', 'asset_current'),
            'reconcile': rec.get('reconcile', False),
        }
    
    def preparer_partner(self, rec, mappings):
        """Prépare données partenaire"""
        data = {
            'name': rec.get('name') or f"Contact {rec['id']}",
            'active': rec.get('active', True),
        }
        for f in ['email', 'phone', 'ref', 'vat', 'street', 'city', 'zip']:
            if rec.get(f):
                data[f] = rec[f]
        return data
    
    def preparer_journal(self, rec, mappings):
        """Prépare données journal"""
        account_mapping = mappings.get('account.account', {})
        
        data = {
            'name': rec['name'],
            'code': rec['code'],
            'type': rec['type'],
        }
        
        if rec.get('default_account_id') and rec['default_account_id'][0] in account_mapping:
            data['default_account_id'] = account_mapping[rec['default_account_id'][0]]
        
        return data
    
    def preparer_user(self, rec, mappings):
        """Prépare données utilisateur"""
        partner_mapping = mappings.get('res.partner', {})
        
        data = {
            'name': rec['name'],
            'login': rec['login'],
            'password': 'ChangeMeNow123!',
        }
        
        if rec.get('email'):
            data['email'] = rec['email']
        
        if rec.get('partner_id') and rec['partner_id'][0] in partner_mapping:
            data['partner_id'] = partner_mapping[rec['partner_id'][0]]
        
        return data
    
    def preparer_produit(self, rec, mappings):
        """Prépare données produit"""
        product_type = rec.get('type', 'consu')
        is_storable = (product_type == 'product')
        
        if is_storable:
            product_type = 'consu'
        
        data = {
            'name': rec['name'],
            'type': product_type,
            'list_price': rec.get('list_price', 0.0),
        }
        
        if is_storable:
            data['is_storable'] = True
        
        if rec.get('default_code'):
            data['default_code'] = rec['default_code']
        
        return data
    
    def preparer_taxe(self, rec, mappings):
        """Prépare données taxe"""
        account_mapping = mappings.get('account.account', {})
        
        data = {
            'name': rec['name'],
            'amount': rec.get('amount', 0.0),
            'amount_type': rec.get('amount_type', 'percent'),
            'type_tax_use': rec.get('type_tax_use', 'sale'),
        }
        
        # Mapper les comptes si disponibles
        if rec.get('invoice_repartition_line_ids'):
            # Les lignes de répartition seront gérées séparément
            pass
        
        return data
    
    def preparer_position_fiscale(self, rec, mappings):
        """Prépare position fiscale"""
        return {
            'name': rec['name'],
            'active': rec.get('active', True),
        }
    
    def preparer_condition_paiement(self, rec, mappings):
        """Prépare condition de paiement"""
        return {
            'name': rec['name'],
            'active': rec.get('active', True),
        }
    
    def executer(self):
        """Exécute la migration optimisée"""
        debut = datetime.now()
        
        afficher("="*70)
        afficher("MIGRATION OPTIMISEE v16 -> v19")
        if MODE_TEST:
            afficher(f"MODE TEST: {TEST_LIMIT} enregistrements par module")
        afficher("="*70)
        afficher(f"Debut: {debut.strftime('%Y-%m-%d %H:%M:%S')}")
        afficher("")
        
        # Connexion
        if not self.conn.connecter_tout():
            afficher("ERREUR: Connexion")
            return False
        
        self.ext_mgr = ExternalIdManager(self.conn)
        afficher("OK Connexion etablie\n")
        
        # PHASE 1 : Données de référence comptables
        self.migrer_module_optimise('account.account',
                                    ['code', 'name', 'account_type', 'reconcile'],
                                    '1. Plan Comptable',
                                    self.preparer_compte)
        
        self.migrer_module_optimise('account.tax',
                                    ['name', 'amount', 'amount_type', 'type_tax_use'],
                                    '2. Taxes',
                                    self.preparer_taxe)
        
        self.migrer_module_optimise('account.fiscal.position',
                                    ['name', 'active'],
                                    '3. Positions Fiscales',
                                    self.preparer_position_fiscale)
        
        self.migrer_module_optimise('account.payment.term',
                                    ['name', 'active'],
                                    '4. Conditions de Paiement',
                                    self.preparer_condition_paiement)
        
        # PHASE 2 : Partenaires et références
        self.migrer_module_optimise('res.partner',
                                    ['name', 'email', 'phone', 'ref', 'vat', 'street', 'city', 'zip', 'active'],
                                    '5. Partenaires',
                                    self.preparer_partner)
        
        self.migrer_module_optimise('account.journal',
                                    ['code', 'name', 'type', 'default_account_id'],
                                    '6. Journaux',
                                    self.preparer_journal)
        
        # PHASE 3 : Utilisateurs
        self.migrer_module_optimise('res.users',
                                    ['name', 'login', 'email', 'partner_id'],
                                    '7. Utilisateurs',
                                    self.preparer_user)
        
        # PHASE 4 : Produits
        self.migrer_module_optimise('product.template',
                                    ['name', 'default_code', 'type', 'list_price'],
                                    '8. Produits',
                                    self.preparer_produit)
        
        # Résumé
        duree = (datetime.now() - debut).total_seconds()
        
        afficher("\n" + "="*70)
        afficher("MIGRATION TERMINEE")
        afficher("="*70)
        
        total_migre = 0
        for model, mapping in self.mappings.items():
            # Nom plus lisible
            noms = {
                'account': 'Comptes',
                'tax': 'Taxes',
                'fiscal': 'Positions fiscales',
                'term': 'Cond. paiement',
                'partner': 'Partenaires',
                'journal': 'Journaux',
                'users': 'Utilisateurs',
                'template': 'Produits'
            }
            nom_affiche = noms.get(model.split('.')[-1], model.split('.')[-1])
            afficher(f"  {nom_affiche:25s}: {len(mapping):>6,d} mappes")
            total_migre += len(mapping)
        
        afficher(f"\n  TOTAL: {total_migre:,d} enregistrements")
        afficher(f"  DUREE: {duree:.1f}s")
        afficher(f"  VITESSE: {total_migre/duree:.0f} enreg/s")
        afficher("="*70)
        afficher(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if MODE_TEST:
            afficher("\nMODE TEST: Mettre MODE_TEST = False pour migration complete")
        
        return True


def main():
    migration = MigrationOptimisee()
    success = migration.executer()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

