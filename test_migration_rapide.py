#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST MIGRATION RAPIDE
====================
Script ultra-simple pour tester la migration avec affichage immédiat
"""

import sys
from datetime import datetime
from connexion_double_v19 import ConnexionDoubleV19
from utils.external_id_manager import ExternalIdManager

print("="*70, flush=True)
print("TEST MIGRATION RAPIDE", flush=True)
print("="*70, flush=True)
print(f"Debut: {datetime.now()}", flush=True)

# Connexion
print("\n1. Connexion...", flush=True)
conn = ConnexionDoubleV19()

if not conn.connecter_tout():
    print("ERREUR: Connexion echouee", flush=True)
    sys.exit(1)

print("OK Connecte !", flush=True)

# Gestionnaire external_id
print("\n2. Init external_id manager...", flush=True)
ext_mgr = ExternalIdManager(conn)
print("OK Gestionnaire pret", flush=True)

# Test 1 : Récupérer 5 comptes SOURCE
print("\n3. Test recuperation 5 comptes SOURCE...", flush=True)
comptes = conn.executer_source('account.account', 'search_read', [], 
                               fields=['code', 'name'], limit=5)
print(f"OK {len(comptes)} comptes recuperes", flush=True)

for compte in comptes:
    print(f"  - {compte['code']} : {compte['name']}", flush=True)

# Test 2 : Vérifier external_id d'UN compte
print("\n4. Test external_id du premier compte...", flush=True)
premier_compte_id = comptes[0]['id']
print(f"  Compte ID: {premier_compte_id}", flush=True)

print("  Recherche external_id...", flush=True)
ext_id = ext_mgr.get_external_id_from_source('account.account', premier_compte_id)

if ext_id:
    print(f"  OK External_id trouve: {ext_id['module']}.{ext_id['name']}", flush=True)
else:
    print(f"  Pas d'external_id pour ce compte", flush=True)

# Test 3 : Vérifier si existe dans destination
print("\n5. Test verification existence dans DESTINATION...", flush=True)
existe, dest_id, ext_id_check = ext_mgr.verifier_existe('account.account', premier_compte_id)

if existe:
    print(f"  OK Compte existe dans destination (ID: {dest_id})", flush=True)
    if ext_id_check:
        print(f"     External_id: {ext_id_check['module']}.{ext_id_check['name']}", flush=True)
else:
    print(f"  Compte n'existe pas encore dans destination", flush=True)

print("\n" + "="*70, flush=True)
print("TEST TERMINE AVEC SUCCES", flush=True)
print("="*70, flush=True)

