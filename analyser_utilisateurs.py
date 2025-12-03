#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ANALYSE UTILISATEURS - Actifs et Inactifs"""
import sys, os
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19

print("="*70)
print("ANALYSE: UTILISATEURS SOURCE")
print("="*70)

conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    sys.exit(1)

print("OK Connexion\n")

# TOUS les utilisateurs (actifs ET inactifs)
print("Recuperation TOUS les utilisateurs (actifs + inactifs)...")
all_users = conn.executer_source('res.users', 'search_read',
                                 [('active', 'in', [True, False])],
                                 fields=['id', 'name', 'login', 'active'])

print(f"TOTAL: {len(all_users)} utilisateurs\n")

actifs = [u for u in all_users if u.get('active')]
inactifs = [u for u in all_users if not u.get('active')]

print(f"Actifs   : {len(actifs)}")
print(f"Inactifs : {len(inactifs)}\n")

print("="*70)
print("UTILISATEURS ACTIFS:")
print("="*70)
for u in actifs:
    print(f"  ID {u['id']:>3} : {u.get('login', 'N/A'):30s} - {u.get('name', 'N/A')}")

print("\n" + "="*70)
print("UTILISATEURS INACTIFS:")
print("="*70)
for u in inactifs[:20]:  # Afficher les 20 premiers
    print(f"  ID {u['id']:>3} : {u.get('login', 'N/A'):30s} - {u.get('name', 'N/A')}")

if len(inactifs) > 20:
    print(f"  ... et {len(inactifs) - 20} autres")

# Vérifier les utilisateurs référencés dans les projets
print("\n" + "="*70)
print("VÉRIFICATION: Utilisateurs dans les projets")
print("="*70)

projects = conn.executer_source('project.project', 'search_read', [],
                                fields=['name', 'user_id'])

user_ids_in_projects = set()
for p in projects:
    user_id = p.get('user_id')
    if user_id and isinstance(user_id, (list, tuple)):
        user_ids_in_projects.add(user_id[0])

print(f"Utilisateurs référencés dans les projets: {user_ids_in_projects}")

# Vérifier si ces IDs existent dans res.users
all_user_ids = {u['id'] for u in all_users}

for uid in user_ids_in_projects:
    if uid in all_user_ids:
        user = [u for u in all_users if u['id'] == uid][0]
        status = "ACTIF" if user.get('active') else "INACTIF"
        print(f"  ID {uid}: {user.get('name')} - {status}")
    else:
        print(f"  ID {uid}: INTROUVABLE dans res.users!")

