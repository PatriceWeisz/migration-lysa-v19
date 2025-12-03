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
MODE_TEST = True  # False = MIGRATION COMPLETE, True = TEST 10 par module
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

def migrer_users(conn, ext_mgr, partner_mapping):
    """Migre les utilisateurs avec groupes"""
    afficher("\n" + "="*70)
    afficher("3. UTILISATEURS (avec groupes)")
    if MODE_TEST:
        afficher(f"   MODE TEST: {TEST_LIMIT_PAR_MODULE} users")
    afficher("="*70)
    
    afficher("Recuperation users SOURCE...")
    kwargs = {'fields': ['name', 'login', 'email', 'active', 'groups_id', 'partner_id']}
    if MODE_TEST:
        kwargs['limit'] = TEST_LIMIT_PAR_MODULE
    
    users = conn.executer_source('res.users', 'search_read', 
                                [('id', '!=', 1)],  # Exclure admin
                                **kwargs)
    
    afficher(f"OK {len(users)} users recuperes")
    
    # Mapper les groupes via external_id
    afficher("Mapping des groupes d'acces...")
    group_mapping = {}
    
    try:
        # Récupérer external_id des groupes source
        ext_groups_src = conn.executer_source('ir.model.data', 'search_read',
                                             [('model', '=', 'res.groups')],
                                             fields=['res_id', 'module', 'name'])
        
        # Récupérer external_id des groupes dest
        ext_groups_dst = conn.executer_destination('ir.model.data', 'search_read',
                                                  [('model', '=', 'res.groups')],
                                                  fields=['res_id', 'module', 'name'])
        
        # Créer index
        src_ext_to_id = {f"{g['module']}.{g['name']}": g['res_id'] for g in ext_groups_src}
        dst_ext_to_id = {f"{g['module']}.{g['name']}": g['res_id'] for g in ext_groups_dst}
        
        # Mapper
        for ext_key, src_id in src_ext_to_id.items():
            if ext_key in dst_ext_to_id:
                group_mapping[src_id] = dst_ext_to_id[ext_key]
        
        afficher(f"OK {len(group_mapping)} groupes mappes")
    except Exception as e:
        afficher(f"ATTENTION: Mapping groupes impossible: {e}")
    
    # Index des users dest
    users_dest = conn.executer_destination('res.users', 'search_read', [],
                                          fields=['login'])
    users_dest_by_login = {u['login']: u['id'] for u in users_dest}
    
    mapping = {}
    nouveau = 0
    existant = 0
    
    for idx, user in enumerate(users, 1):
        source_id = user['id']
        login = user['login']
        name = user['name']
        
        afficher(f"[{idx}/{len(users)}] {name} ({login})")
        
        # Vérifier via external_id
        existe, dest_id, ext_id = ext_mgr.verifier_existe('res.users', source_id)
        
        if existe:
            afficher(f"  -> Existe (ID: {dest_id})")
            mapping[source_id] = dest_id
            existant += 1
        elif login in users_dest_by_login:
            dest_id = users_dest_by_login[login]
            afficher(f"  -> Existe par login (ID: {dest_id})")
            
            if ext_id:
                ext_mgr.copier_external_id('res.users', dest_id, source_id)
            
            mapping[source_id] = dest_id
            existant += 1
        else:
            data = {
                'name': name,
                'login': login,
                'password': 'ChangeMeNow123!',
            }
            
            if user.get('email'):
                data['email'] = user['email']
            
            # Partenaire lié
            if user.get('partner_id') and user['partner_id'][0] in partner_mapping:
                data['partner_id'] = partner_mapping[user['partner_id'][0]]
            
            # Groupes
            if user.get('groups_id'):
                groups_dest_ids = []
                for g_id in user['groups_id']:
                    if g_id in group_mapping:
                        groups_dest_ids.append(group_mapping[g_id])
                
                if groups_dest_ids:
                    data['groups_id'] = [(6, 0, groups_dest_ids)]
            
            try:
                dest_id = conn.executer_destination('res.users', 'create', data)
                afficher(f"  -> Cree (ID: {dest_id}) - Mot de passe: ChangeMeNow123!")
                
                if ext_id:
                    ext_mgr.copier_external_id('res.users', dest_id, source_id)
                
                mapping[source_id] = dest_id
                users_dest_by_login[login] = dest_id
                nouveau += 1
            except Exception as e:
                afficher(f"  -> ERREUR: {str(e)[:80]}")
    
    afficher(f"\nRESULTAT: {nouveau} nouveaux, {existant} existants")
    if nouveau > 0:
        afficher(f"IMPORTANT: Mot de passe temporaire pour tous: ChangeMeNow123!")
    
    with open(LOGS_DIR / 'user_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=2)
    
    return mapping

def migrer_departements(conn, ext_mgr):
    """Migre les départements RH"""
    afficher("\n" + "="*70)
    afficher("4. DEPARTEMENTS RH")
    if MODE_TEST:
        afficher(f"   MODE TEST: {TEST_LIMIT_PAR_MODULE} departements")
    afficher("="*70)
    
    kwargs = {'fields': ['name', 'parent_id', 'active']}
    if MODE_TEST:
        kwargs['limit'] = TEST_LIMIT_PAR_MODULE
    
    depts = conn.executer_source('hr.department', 'search_read', [], **kwargs)
    afficher(f"OK {len(depts)} departements recuperes")
    
    mapping = {}
    nouveau = 0
    existant = 0
    
    # Trier pour parents d'abord
    depts_triees = sorted(depts, key=lambda x: (x['parent_id'][0] if x.get('parent_id') else 0))
    
    for idx, dept in enumerate(depts_triees, 1):
        source_id = dept['id']
        name = dept['name']
        
        if MODE_TEST or idx % 10 == 0:
            afficher(f"[{idx}/{len(depts)}] {name}")
        
        existe, dest_id, ext_id = ext_mgr.verifier_existe('hr.department', source_id)
        
        if not existe:
            data = {'name': name, 'active': dept.get('active', True)}
            
            # Parent si déjà mappé
            if dept.get('parent_id') and dept['parent_id'][0] in mapping:
                data['parent_id'] = mapping[dept['parent_id'][0]]
            
            try:
                dest_id = conn.executer_destination('hr.department', 'create', data)
                if ext_id:
                    ext_mgr.copier_external_id('hr.department', dest_id, source_id)
                nouveau += 1
                if MODE_TEST:
                    afficher(f"  -> Cree (ID: {dest_id})")
            except:
                continue
        else:
            existant += 1
            if MODE_TEST:
                afficher(f"  -> Existe (ID: {dest_id})")
        
        mapping[source_id] = dest_id
    
    afficher(f"\nRESULTAT: {nouveau} nouveaux, {existant} existants")
    
    with open(LOGS_DIR / 'department_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=2)
    
    return mapping

def migrer_postes(conn, ext_mgr, dept_mapping):
    """Migre les postes/fonctions"""
    afficher("\n" + "="*70)
    afficher("5. POSTES/FONCTIONS")
    if MODE_TEST:
        afficher(f"   MODE TEST: {TEST_LIMIT_PAR_MODULE} postes")
    afficher("="*70)
    
    kwargs = {'fields': ['name', 'department_id', 'active']}
    if MODE_TEST:
        kwargs['limit'] = TEST_LIMIT_PAR_MODULE
    
    jobs = conn.executer_source('hr.job', 'search_read', [], **kwargs)
    afficher(f"OK {len(jobs)} postes recuperes")
    
    mapping = {}
    nouveau = 0
    existant = 0
    
    for idx, job in enumerate(jobs, 1):
        source_id = job['id']
        name = job['name']
        
        if MODE_TEST or idx % 10 == 0:
            afficher(f"[{idx}/{len(jobs)}] {name}")
        
        existe, dest_id, ext_id = ext_mgr.verifier_existe('hr.job', source_id)
        
        if not existe:
            data = {'name': name, 'active': job.get('active', True)}
            
            if job.get('department_id') and job['department_id'][0] in dept_mapping:
                data['department_id'] = dept_mapping[job['department_id'][0]]
            
            try:
                dest_id = conn.executer_destination('hr.job', 'create', data)
                if ext_id:
                    ext_mgr.copier_external_id('hr.job', dest_id, source_id)
                nouveau += 1
                if MODE_TEST:
                    afficher(f"  -> Cree (ID: {dest_id})")
            except:
                continue
        else:
            existant += 1
            if MODE_TEST:
                afficher(f"  -> Existe (ID: {dest_id})")
        
        mapping[source_id] = dest_id
    
    afficher(f"\nRESULTAT: {nouveau} nouveaux, {existant} existants")
    
    with open(LOGS_DIR / 'job_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=2)
    
    return mapping

def migrer_employes(conn, ext_mgr, user_mapping, dept_mapping, job_mapping):
    """Migre les employés"""
    afficher("\n" + "="*70)
    afficher("6. EMPLOYES")
    if MODE_TEST:
        afficher(f"   MODE TEST: {TEST_LIMIT_PAR_MODULE} employes")
    afficher("="*70)
    
    afficher("Recuperation employes SOURCE...")
    kwargs = {'fields': ['name', 'work_email', 'work_phone', 'user_id', 'department_id', 'job_id']}
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
            
            # User lié
            if emp.get('user_id') and emp['user_id'][0] in user_mapping:
                data['user_id'] = user_mapping[emp['user_id'][0]]
            
            # Département
            if emp.get('department_id') and emp['department_id'][0] in dept_mapping:
                data['department_id'] = dept_mapping[emp['department_id'][0]]
            
            # Poste
            if emp.get('job_id') and emp['job_id'][0] in job_mapping:
                data['job_id'] = job_mapping[emp['job_id'][0]]
            
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

def migrer_entrepots(conn, ext_mgr, partner_mapping):
    """Migre les entrepôts"""
    afficher("\n" + "="*70)
    afficher("7. ENTREPOTS")
    if MODE_TEST:
        afficher(f"   MODE TEST: {TEST_LIMIT_PAR_MODULE} entrepots")
    afficher("="*70)
    
    kwargs = {'fields': ['name', 'code', 'partner_id', 'active']}
    if MODE_TEST:
        kwargs['limit'] = TEST_LIMIT_PAR_MODULE
    
    warehouses = conn.executer_source('stock.warehouse', 'search_read', [], **kwargs)
    afficher(f"OK {len(warehouses)} entrepots recuperes")
    
    # Index dest par code
    wh_dest = conn.executer_destination('stock.warehouse', 'search_read', [],
                                       fields=['code'])
    wh_dest_by_code = {w['code']: w['id'] for w in wh_dest}
    
    mapping = {}
    nouveau = 0
    existant = 0
    
    for idx, wh in enumerate(warehouses, 1):
        source_id = wh['id']
        name = wh['name']
        code = wh.get('code', '')
        
        afficher(f"[{idx}/{len(warehouses)}] {name} ({code})")
        
        existe, dest_id, ext_id = ext_mgr.verifier_existe('stock.warehouse', source_id)
        
        if existe:
            afficher(f"  -> Existe (ID: {dest_id})")
            mapping[source_id] = dest_id
            existant += 1
        elif code and code in wh_dest_by_code:
            dest_id = wh_dest_by_code[code]
            afficher(f"  -> Existe par code (ID: {dest_id})")
            
            if ext_id:
                ext_mgr.copier_external_id('stock.warehouse', dest_id, source_id)
            
            mapping[source_id] = dest_id
            existant += 1
        else:
            data = {
                'name': name,
                'code': code or name[:5].upper(),
                'active': wh.get('active', True),
            }
            
            if wh.get('partner_id') and wh['partner_id'][0] in partner_mapping:
                data['partner_id'] = partner_mapping[wh['partner_id'][0]]
            
            try:
                dest_id = conn.executer_destination('stock.warehouse', 'create', data)
                afficher(f"  -> Cree (ID: {dest_id})")
                
                if ext_id:
                    ext_mgr.copier_external_id('stock.warehouse', dest_id, source_id)
                
                mapping[source_id] = dest_id
                wh_dest_by_code[code or name[:5].upper()] = dest_id
                nouveau += 1
            except Exception as e:
                afficher(f"  -> ERREUR: {str(e)[:80]}")
    
    afficher(f"\nRESULTAT: {nouveau} nouveaux, {existant} existants")
    
    with open(LOGS_DIR / 'warehouse_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=2)
    
    return mapping

def migrer_produits(conn, ext_mgr):
    """Migre les produits"""
    afficher("\n" + "="*70)
    afficher("8. PRODUITS")
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

def migrer_nomenclatures(conn, ext_mgr, product_mapping):
    """Migre les nomenclatures (BOM)"""
    afficher("\n" + "="*70)
    afficher("9. NOMENCLATURES (BOM)")
    if MODE_TEST:
        afficher(f"   MODE TEST: {TEST_LIMIT_PAR_MODULE} nomenclatures")
    afficher("="*70)
    
    kwargs = {'fields': ['product_tmpl_id', 'product_id', 'product_qty', 'type']}
    if MODE_TEST:
        kwargs['limit'] = TEST_LIMIT_PAR_MODULE
    
    try:
        boms = conn.executer_source('mrp.bom', 'search_read', [], **kwargs)
        afficher(f"OK {len(boms)} nomenclatures recuperees")
        
        mapping = {}
        nouveau = 0
        existant = 0
        
        for idx, bom in enumerate(boms, 1):
            source_id = bom['id']
            
            if MODE_TEST:
                afficher(f"[{idx}/{len(boms)}] BOM ID {source_id}")
            
            existe, dest_id, ext_id = ext_mgr.verifier_existe('mrp.bom', source_id)
            
            if not existe:
                # Créer uniquement si produit existe
                if bom.get('product_tmpl_id') and bom['product_tmpl_id'][0] in product_mapping:
                    data = {
                        'product_tmpl_id': product_mapping[bom['product_tmpl_id'][0]],
                        'product_qty': bom.get('product_qty', 1.0),
                        'type': bom.get('type', 'normal'),
                    }
                    
                    try:
                        dest_id = conn.executer_destination('mrp.bom', 'create', data)
                        if ext_id:
                            ext_mgr.copier_external_id('mrp.bom', dest_id, source_id)
                        nouveau += 1
                        if MODE_TEST:
                            afficher(f"  -> Cree (ID: {dest_id})")
                    except Exception as e:
                        if MODE_TEST:
                            afficher(f"  -> ERREUR: {str(e)[:80]}")
                        continue
            else:
                existant += 1
                if MODE_TEST:
                    afficher(f"  -> Existe (ID: {dest_id})")
            
            if dest_id:
                mapping[source_id] = dest_id
        
        afficher(f"\nRESULTAT: {nouveau} nouveaux, {existant} existants")
        
        with open(LOGS_DIR / 'bom_mapping.json', 'w') as f:
            json.dump(mapping, f, indent=2)
        
        return mapping
        
    except Exception as e:
        afficher(f"Module mrp.bom non disponible ou erreur: {e}")
        return {}

def migrer_factures_clients(conn, ext_mgr, partner_mapping, journal_mapping):
    """Migre les factures clients"""
    afficher("\n" + "="*70)
    afficher("10. FACTURES CLIENTS")
    if MODE_TEST:
        afficher(f"   MODE TEST: {TEST_LIMIT_PAR_MODULE} factures")
    afficher("="*70)
    
    kwargs = {'fields': ['name', 'partner_id', 'invoice_date', 'journal_id', 'state', 'amount_total']}
    if MODE_TEST:
        kwargs['limit'] = TEST_LIMIT_PAR_MODULE
    
    factures = conn.executer_source('account.move', 'search_read',
                                    [('move_type', '=', 'out_invoice'), ('state', '=', 'posted')],
                                    **kwargs)
    
    afficher(f"OK {len(factures)} factures clients recuperees")
    
    mapping = {}
    nouveau = 0
    existant = 0
    erreurs = 0
    
    for idx, facture in enumerate(factures, 1):
        source_id = facture['id']
        name = facture.get('name', 'N/A')
        
        if MODE_TEST:
            afficher(f"[{idx}/{len(factures)}] {name}")
        elif idx % 50 == 0:
            afficher(f"[{idx}/{len(factures)}] Traitement...")
        
        existe, dest_id, ext_id = ext_mgr.verifier_existe('account.move', source_id)
        
        if not existe:
            # Vérifier dépendances
            if not facture.get('partner_id') or facture['partner_id'][0] not in partner_mapping:
                if MODE_TEST:
                    afficher(f"  -> SKIP: Partenaire non mappe")
                erreurs += 1
                continue
            
            data = {
                'partner_id': partner_mapping[facture['partner_id'][0]],
                'move_type': 'out_invoice',
                'invoice_date': facture.get('invoice_date'),
            }
            
            if facture.get('journal_id') and facture['journal_id'][0] in journal_mapping:
                data['journal_id'] = journal_mapping[facture['journal_id'][0]]
            
            try:
                dest_id = conn.executer_destination('account.move', 'create', data)
                if ext_id:
                    ext_mgr.copier_external_id('account.move', dest_id, source_id)
                nouveau += 1
                if MODE_TEST:
                    afficher(f"  -> Cree (ID: {dest_id})")
            except Exception as e:
                if MODE_TEST:
                    afficher(f"  -> ERREUR: {str(e)[:80]}")
                erreurs += 1
                continue
        else:
            existant += 1
            if MODE_TEST:
                afficher(f"  -> Existe (ID: {dest_id})")
        
        if dest_id:
            mapping[source_id] = dest_id
    
    afficher(f"\nRESULTAT: {nouveau} nouveaux, {existant} existants, {erreurs} erreurs")
    
    with open(LOGS_DIR / 'invoice_out_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=2)
    
    return mapping

def migrer_factures_fournisseurs(conn, ext_mgr, partner_mapping, journal_mapping):
    """Migre les factures fournisseurs"""
    afficher("\n" + "="*70)
    afficher("11. FACTURES FOURNISSEURS")
    if MODE_TEST:
        afficher(f"   MODE TEST: {TEST_LIMIT_PAR_MODULE} factures")
    afficher("="*70)
    
    kwargs = {'fields': ['name', 'partner_id', 'invoice_date', 'journal_id', 'state']}
    if MODE_TEST:
        kwargs['limit'] = TEST_LIMIT_PAR_MODULE
    
    factures = conn.executer_source('account.move', 'search_read',
                                    [('move_type', '=', 'in_invoice'), ('state', '=', 'posted')],
                                    **kwargs)
    
    afficher(f"OK {len(factures)} factures fournisseurs recuperees")
    
    mapping = {}
    nouveau = 0
    existant = 0
    
    for idx, facture in enumerate(factures, 1):
        source_id = facture['id']
        
        if MODE_TEST or idx % 50 == 0:
            afficher(f"[{idx}/{len(factures)}] {facture.get('name', 'N/A')}")
        
        existe, dest_id, ext_id = ext_mgr.verifier_existe('account.move', source_id)
        
        if not existe:
            if not facture.get('partner_id') or facture['partner_id'][0] not in partner_mapping:
                continue
            
            data = {
                'partner_id': partner_mapping[facture['partner_id'][0]],
                'move_type': 'in_invoice',
                'invoice_date': facture.get('invoice_date'),
            }
            
            if facture.get('journal_id') and facture['journal_id'][0] in journal_mapping:
                data['journal_id'] = journal_mapping[facture['journal_id'][0]]
            
            try:
                dest_id = conn.executer_destination('account.move', 'create', data)
                if ext_id:
                    ext_mgr.copier_external_id('account.move', dest_id, source_id)
                nouveau += 1
                if MODE_TEST:
                    afficher(f"  -> Cree (ID: {dest_id})")
            except:
                continue
        else:
            existant += 1
            if MODE_TEST:
                afficher(f"  -> Existe (ID: {dest_id})")
        
        if dest_id:
            mapping[source_id] = dest_id
    
    afficher(f"\nRESULTAT: {nouveau} nouveaux, {existant} existants")
    
    with open(LOGS_DIR / 'invoice_in_mapping.json', 'w') as f:
        json.dump(mapping, f, indent=2)
    
    return mapping

def migrer_paiements(conn, ext_mgr, partner_mapping, journal_mapping):
    """Migre les paiements"""
    afficher("\n" + "="*70)
    afficher("12. PAIEMENTS")
    if MODE_TEST:
        afficher(f"   MODE TEST: {TEST_LIMIT_PAR_MODULE} paiements")
    afficher("="*70)
    
    kwargs = {'fields': ['name', 'partner_id', 'date', 'journal_id', 'payment_type', 'amount']}
    if MODE_TEST:
        kwargs['limit'] = TEST_LIMIT_PAR_MODULE
    
    try:
        paiements = conn.executer_source('account.payment', 'search_read', [], **kwargs)
        afficher(f"OK {len(paiements)} paiements recuperes")
        
        mapping = {}
        nouveau = 0
        existant = 0
        
        for idx, pmt in enumerate(paiements, 1):
            source_id = pmt['id']
            
            if MODE_TEST or idx % 50 == 0:
                afficher(f"[{idx}/{len(paiements)}] Paiement ID {source_id}")
            
            existe, dest_id, ext_id = ext_mgr.verifier_existe('account.payment', source_id)
            
            if not existe:
                if not pmt.get('partner_id') or pmt['partner_id'][0] not in partner_mapping:
                    continue
                
                data = {
                    'partner_id': partner_mapping[pmt['partner_id'][0]],
                    'payment_type': pmt.get('payment_type', 'inbound'),
                    'amount': pmt.get('amount', 0.0),
                    'date': pmt.get('date'),
                }
                
                if pmt.get('journal_id') and pmt['journal_id'][0] in journal_mapping:
                    data['journal_id'] = journal_mapping[pmt['journal_id'][0]]
                
                try:
                    dest_id = conn.executer_destination('account.payment', 'create', data)
                    if ext_id:
                        ext_mgr.copier_external_id('account.payment', dest_id, source_id)
                    nouveau += 1
                    if MODE_TEST:
                        afficher(f"  -> Cree (ID: {dest_id})")
                except:
                    continue
            else:
                existant += 1
            
            if dest_id:
                mapping[source_id] = dest_id
        
        afficher(f"\nRESULTAT: {nouveau} nouveaux, {existant} existants")
        
        with open(LOGS_DIR / 'payment_mapping.json', 'w') as f:
            json.dump(mapping, f, indent=2)
        
        return mapping
        
    except Exception as e:
        afficher(f"Module account.payment erreur: {e}")
        return {}

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
    
    # Migration dans l'ordre des dépendances
    try:
        # Phase 1 : Données de base
        compte_mapping = migrer_plan_comptable(conn, ext_mgr)
        partner_mapping = migrer_partenaires(conn, ext_mgr)
        journal_mapping = migrer_journaux(conn, ext_mgr, compte_mapping)
        
        # Phase 2 : Utilisateurs et RH
        user_mapping = migrer_users(conn, ext_mgr, partner_mapping)
        dept_mapping = migrer_departements(conn, ext_mgr)
        job_mapping = migrer_postes(conn, ext_mgr, dept_mapping)
        employe_mapping = migrer_employes(conn, ext_mgr, user_mapping, dept_mapping, job_mapping)
        
        # Phase 3 : Stock et produits
        warehouse_mapping = migrer_entrepots(conn, ext_mgr, partner_mapping)
        produit_mapping = migrer_produits(conn, ext_mgr)
        bom_mapping = migrer_nomenclatures(conn, ext_mgr, produit_mapping)
        
        # Phase 4 : Transactions
        invoice_out_mapping = migrer_factures_clients(conn, ext_mgr, partner_mapping, journal_mapping)
        invoice_in_mapping = migrer_factures_fournisseurs(conn, ext_mgr, partner_mapping, journal_mapping)
        payment_mapping = migrer_paiements(conn, ext_mgr, partner_mapping, journal_mapping)
        
        # Résumé final
        afficher("\n" + "="*70)
        afficher("MIGRATION TERMINEE")
        afficher("="*70)
        afficher(f"Comptes mappes           : {len(compte_mapping)}")
        afficher(f"Partenaires mappes       : {len(partner_mapping)}")
        afficher(f"Journaux mappes          : {len(journal_mapping)}")
        afficher(f"Users mappes             : {len(user_mapping)}")
        afficher(f"Departements mappes      : {len(dept_mapping)}")
        afficher(f"Postes mappes            : {len(job_mapping)}")
        afficher(f"Employes mappes          : {len(employe_mapping)}")
        afficher(f"Entrepots mappes         : {len(warehouse_mapping)}")
        afficher(f"Produits mappes          : {len(produit_mapping)}")
        afficher(f"Nomenclatures mappees    : {len(bom_mapping)}")
        afficher(f"Factures clients mappees : {len(invoice_out_mapping)}")
        afficher(f"Factures fourn. mappees  : {len(invoice_in_mapping)}")
        afficher(f"Paiements mappes         : {len(payment_mapping)}")
        afficher("="*70)
        afficher(f"Fin: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if MODE_TEST:
            afficher("\nATTENTION: Mode TEST active - Seulement 10 enregistrements par module")
            afficher("Pour migration complete: Modifier MODE_TEST = False dans le script")
        
        return True
        
    except Exception as e:
        afficher(f"\nERREUR GLOBALE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

