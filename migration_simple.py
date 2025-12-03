#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIGRATION SIMPLE ET VISIBLE
===========================
Script simplifié avec affichage garanti ligne par ligne
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# FORCER unbuffered dès le début
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)
sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', buffering=1)

# Imports après configuration buffering
from connexion_double_v19 import ConnexionDoubleV19
from utils.external_id_manager import ExternalIdManager

# Configuration
MODE_TEST = False  # False = MIGRATION COMPLETE
TEST_LIMIT_PAR_MODULE = 10  # Utilisé seulement si MODE_TEST = True
LOGS_DIR = Path('logs')
LOGS_DIR.mkdir(exist_ok=True)

def afficher(msg=""):
    """Affichage garanti"""
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

def migrer_plan_comptable(conn, ext_mgr):
    """Migre le plan comptable"""
    afficher("\n" + "="*70)
    afficher("1. PLAN COMPTABLE")
    if MODE_TEST:
        afficher(f"   MODE TEST: {TEST_LIMIT_PAR_MODULE} comptes")
    afficher("="*70)
    
    afficher("Recuperation comptes SOURCE...")
    kwargs = {'fields': ['code', 'name', 'account_type', 'reconcile']}
    if MODE_TEST:
        kwargs['limit'] = TEST_LIMIT_PAR_MODULE
    
    comptes = conn.executer_source('account.account', 'search_read', [], **kwargs)
    
    afficher(f"OK {len(comptes)} comptes recuperes")
    
    mapping = {}
    nouveau = 0
    existant = 0
    erreurs = 0
    
    for idx, compte in enumerate(comptes, 1):
        source_id = compte['id']
        code = compte['code']
        
        afficher(f"[{idx}/10] {code} - {compte['name'][:40]}")
        
        # Vérifier si existe
        existe, dest_id, ext_id = ext_mgr.verifier_existe('account.account', source_id)
        
        if existe:
            afficher(f"  -> Existe deja (ID: {dest_id})")
            mapping[source_id] = dest_id
            existant += 1
        else:
            # Créer
            data = {
                'code': code,
                'name': compte['name'],
                'account_type': compte.get('account_type', 'asset_current'),
            }
            if compte.get('reconcile') is not None:
                data['reconcile'] = compte['reconcile']
            
            try:
                dest_id = conn.executer_destination('account.account', 'create', data)
                afficher(f"  -> Cree (ID: {dest_id})")
                
                # Copier external_id si existe
                if ext_id:
                    ext_mgr.copier_external_id('account.account', dest_id, source_id)
                    afficher(f"     External_id: {ext_id['module']}.{ext_id['name']}")
                
                mapping[source_id] = dest_id
                nouveau += 1
                
            except Exception as e:
                afficher(f"  -> ERREUR: {str(e)[:80]}")
                erreurs += 1
    
    afficher(f"\nRESULTAT: {nouveau} nouveaux, {existant} existants, {erreurs} erreurs")
    
    # Sauvegarder mapping
    with open(LOGS_DIR / 'account_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=2)
    
    return mapping

def migrer_partenaires(conn, ext_mgr):
    """Migre les partenaires"""
    afficher("\n" + "="*70)
    afficher("2. PARTENAIRES")
    if MODE_TEST:
        afficher(f"   MODE TEST: {TEST_LIMIT_PAR_MODULE} partenaires")
    afficher("="*70)
    
    afficher("Recuperation partenaires SOURCE...")
    kwargs = {'fields': ['name', 'email', 'phone', 'ref']}
    if MODE_TEST:
        kwargs['limit'] = TEST_LIMIT_PAR_MODULE
    
    partners = conn.executer_source('res.partner', 'search_read', [], **kwargs)
    
    afficher(f"OK {len(partners)} partenaires recuperes")
    
    mapping = {}
    nouveau = 0
    existant = 0
    
    for idx, partner in enumerate(partners, 1):
        source_id = partner['id']
        name = partner.get('name') or f"Contact {source_id}"
        
        afficher(f"[{idx}/10] {name[:50]}")
        
        existe, dest_id, ext_id = ext_mgr.verifier_existe('res.partner', source_id)
        
        if existe:
            afficher(f"  -> Existe (ID: {dest_id})")
            mapping[source_id] = dest_id
            existant += 1
        else:
            data = {'name': name}
            if partner.get('email'):
                data['email'] = partner['email']
            if partner.get('phone'):
                data['phone'] = partner['phone']
            
            try:
                dest_id = conn.executer_destination('res.partner', 'create', data)
                afficher(f"  -> Cree (ID: {dest_id})")
                
                if ext_id:
                    ext_mgr.copier_external_id('res.partner', dest_id, source_id)
                
                mapping[source_id] = dest_id
                nouveau += 1
            except Exception as e:
                afficher(f"  -> ERREUR: {str(e)[:80]}")
    
    afficher(f"\nRESULTAT: {nouveau} nouveaux, {existant} existants")
    
    with open(LOGS_DIR / 'partner_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=2)
    
    return mapping

def migrer_journaux(conn, ext_mgr, account_mapping):
    """Migre les journaux"""
    afficher("\n" + "="*70)
    afficher("3. JOURNAUX")
    if MODE_TEST:
        afficher(f"   MODE TEST: {TEST_LIMIT_PAR_MODULE} journaux")
    afficher("="*70)
    
    afficher("Recuperation journaux SOURCE...")
    kwargs = {'fields': ['code', 'name', 'type', 'default_account_id']}
    if MODE_TEST:
        kwargs['limit'] = TEST_LIMIT_PAR_MODULE
    
    journaux = conn.executer_source('account.journal', 'search_read', [], **kwargs)
    
    afficher(f"OK {len(journaux)} journaux recuperes")
    
    # Récupérer journaux destination
    journaux_dest = conn.executer_destination('account.journal', 'search_read', [],
                                             fields=['code'])
    journaux_dest_by_code = {j['code']: j['id'] for j in journaux_dest}
    
    mapping = {}
    nouveau = 0
    existant = 0
    
    for idx, journal in enumerate(journaux, 1):
        source_id = journal['id']
        code = journal['code']
        
        afficher(f"[{idx}/10] {code} - {journal['name']}")
        
        # Vérifier via external_id
        existe, dest_id, ext_id = ext_mgr.verifier_existe('account.journal', source_id)
        
        if existe:
            afficher(f"  -> Existe via external_id (ID: {dest_id})")
            mapping[source_id] = dest_id
            existant += 1
        elif code in journaux_dest_by_code:
            # Existe par code
            dest_id = journaux_dest_by_code[code]
            afficher(f"  -> Existe par code (ID: {dest_id})")
            
            # Copier external_id si disponible
            if ext_id:
                ext_mgr.copier_external_id('account.journal', dest_id, source_id)
                afficher(f"     External_id copie: {ext_id['module']}.{ext_id['name']}")
            
            mapping[source_id] = dest_id
            existant += 1
        else:
            data = {
                'name': journal['name'],
                'code': code,
                'type': journal['type'],
            }
            
            if journal.get('default_account_id') and journal['default_account_id'][0] in account_mapping:
                data['default_account_id'] = account_mapping[journal['default_account_id'][0]]
            
            try:
                dest_id = conn.executer_destination('account.journal', 'create', data)
                afficher(f"  -> Cree (ID: {dest_id})")
                
                if ext_id:
                    ext_mgr.copier_external_id('account.journal', dest_id, source_id)
                
                mapping[source_id] = dest_id
                nouveau += 1
            except Exception as e:
                afficher(f"  -> ERREUR: {str(e)[:80]}")
    
    afficher(f"\nRESULTAT: {nouveau} nouveaux, {existant} existants")
    
    with open(LOGS_DIR / 'journal_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=2)
    
    return mapping

def migrer_employes(conn, ext_mgr):
    """Migre les employés"""
    afficher("\n" + "="*70)
    afficher("4. EMPLOYES")
    if MODE_TEST:
        afficher(f"   MODE TEST: {TEST_LIMIT_PAR_MODULE} employes")
    afficher("="*70)
    
    afficher("Recuperation employes SOURCE...")
    kwargs = {'fields': ['name', 'work_email', 'work_phone']}
    if MODE_TEST:
        kwargs['limit'] = TEST_LIMIT_PAR_MODULE
    
    employes = conn.executer_source('hr.employee', 'search_read', [], **kwargs)
    
    afficher(f"OK {len(employes)} employes recuperes")
    
    mapping = {}
    nouveau = 0
    existant = 0
    
    for idx, emp in enumerate(employes, 1):
        source_id = emp['id']
        name = emp['name']
        
        afficher(f"[{idx}/10] {name}")
        
        existe, dest_id, ext_id = ext_mgr.verifier_existe('hr.employee', source_id)
        
        if existe:
            afficher(f"  -> Existe (ID: {dest_id})")
            mapping[source_id] = dest_id
            existant += 1
        else:
            data = {'name': name}
            if emp.get('work_email'):
                data['work_email'] = emp['work_email']
            if emp.get('work_phone'):
                data['work_phone'] = emp['work_phone']
            
            try:
                dest_id = conn.executer_destination('hr.employee', 'create', data)
                afficher(f"  -> Cree (ID: {dest_id})")
                
                if ext_id:
                    ext_mgr.copier_external_id('hr.employee', dest_id, source_id)
                
                mapping[source_id] = dest_id
                nouveau += 1
            except Exception as e:
                afficher(f"  -> ERREUR: {str(e)[:80]}")
    
    afficher(f"\nRESULTAT: {nouveau} nouveaux, {existant} existants")
    
    with open(LOGS_DIR / 'employe_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=2)
    
    return mapping

def migrer_produits(conn, ext_mgr):
    """Migre les produits"""
    afficher("\n" + "="*70)
    afficher("5. PRODUITS")
    if MODE_TEST:
        afficher(f"   MODE TEST: {TEST_LIMIT_PAR_MODULE} produits")
    afficher("="*70)
    
    afficher("Recuperation produits SOURCE...")
    kwargs = {'fields': ['name', 'default_code', 'type', 'list_price']}
    if MODE_TEST:
        kwargs['limit'] = TEST_LIMIT_PAR_MODULE
    
    produits = conn.executer_source('product.template', 'search_read', [], **kwargs)
    
    afficher(f"OK {len(produits)} produits recuperes")
    
    mapping = {}
    nouveau = 0
    existant = 0
    
    for idx, prod in enumerate(produits, 1):
        source_id = prod['id']
        name = prod['name']
        
        afficher(f"[{idx}/10] {name[:50]}")
        
        existe, dest_id, ext_id = ext_mgr.verifier_existe('product.template', source_id)
        
        if existe:
            afficher(f"  -> Existe (ID: {dest_id})")
            mapping[source_id] = dest_id
            existant += 1
        else:
            product_type = prod.get('type', 'consu')
            is_storable = (product_type == 'product')
            if is_storable:
                product_type = 'consu'
            
            data = {
                'name': name,
                'type': product_type,
                'list_price': prod.get('list_price', 0.0),
            }
            
            if is_storable:
                data['is_storable'] = True
            if prod.get('default_code'):
                data['default_code'] = prod['default_code']
            
            try:
                dest_id = conn.executer_destination('product.template', 'create', data)
                afficher(f"  -> Cree (ID: {dest_id})")
                
                if ext_id:
                    ext_mgr.copier_external_id('product.template', dest_id, source_id)
                
                mapping[source_id] = dest_id
                nouveau += 1
            except Exception as e:
                afficher(f"  -> ERREUR: {str(e)[:80]}")
    
    afficher(f"\nRESULTAT: {nouveau} nouveaux, {existant} existants")
    
    with open(LOGS_DIR / 'product_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=2)
    
    return mapping

def main():
    afficher("="*70)
    if MODE_TEST:
        afficher(f"MIGRATION TEST - {TEST_LIMIT_PAR_MODULE} ENREGISTREMENTS PAR MODULE")
    else:
        afficher("MIGRATION COMPLETE - TOUS LES ENREGISTREMENTS")
    afficher("="*70)
    afficher(f"Debut: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    afficher("")
    
    # Connexion
    afficher("Connexion aux bases...")
    conn = ConnexionDoubleV19()
    
    if not conn.connecter_tout():
        afficher("ERREUR: Connexion echouee")
        return False
    
    afficher("OK Connexion reussie")
    
    # External ID manager
    afficher("\nInitialisation external_id manager...")
    ext_mgr = ExternalIdManager(conn)
    afficher("OK Pret")
    
    # Migration
    try:
        compte_mapping = migrer_plan_comptable(conn, ext_mgr)
        partner_mapping = migrer_partenaires(conn, ext_mgr)
        journal_mapping = migrer_journaux(conn, ext_mgr, compte_mapping)
        employe_mapping = migrer_employes(conn, ext_mgr)
        produit_mapping = migrer_produits(conn, ext_mgr)
        
        afficher("\n" + "="*70)
        afficher("MIGRATION TEST TERMINEE")
        afficher("="*70)
        afficher(f"Comptes mappes    : {len(compte_mapping)}")
        afficher(f"Partenaires mappes: {len(partner_mapping)}")
        afficher(f"Journaux mappes   : {len(journal_mapping)}")
        afficher(f"Employes mappes   : {len(employe_mapping)}")
        afficher(f"Produits mappes   : {len(produit_mapping)}")
        afficher("="*70)
        afficher(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        afficher(f"\nERREUR GLOBALE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

