#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DEBUG PROJETS - Analyse approfondie"""
import sys, os, json
from pathlib import Path
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from connexion_double_v19 import ConnexionDoubleV19

print("="*70)
print("DEBUG: ANALYSE PROJETS")
print("="*70)

conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    sys.exit(1)

print("OK Connexion\n")

# ÉTAPE 1 : Analyser la SOURCE
print("="*70)
print("ÉTAPE 1: ANALYSE SOURCE")
print("="*70)

src_projects = conn.executer_source('project.project', 'search_read', [],
                                    fields=['name', 'user_id', 'partner_id', 'company_id', 'active'])

print(f"Nombre de projets SOURCE: {len(src_projects)}\n")

for idx, proj in enumerate(src_projects, 1):
    name = proj.get('name', 'Sans nom')
    user_id = proj.get('user_id')
    partner_id = proj.get('partner_id')
    company_id = proj.get('company_id')
    active = proj.get('active')
    
    try:
        print(f"\nProjet {idx}: {name}")
    except:
        print(f"\nProjet {idx}: [nom avec accents]")
    
    print(f"  ID source     : {proj['id']}")
    print(f"  user_id       : {user_id}")
    print(f"  partner_id    : {partner_id}")
    print(f"  company_id    : {company_id}")
    print(f"  active        : {active}")

# ÉTAPE 2 : Analyser la DESTINATION
print("\n" + "="*70)
print("ÉTAPE 2: ANALYSE DESTINATION")
print("="*70)

dst_projects = conn.executer_destination('project.project', 'search_read', [],
                                         fields=['name', 'user_id', 'partner_id', 'company_id', 'active'])

print(f"Nombre de projets DESTINATION: {len(dst_projects)}\n")

for idx, proj in enumerate(dst_projects, 1):
    name = proj.get('name', 'Sans nom')
    try:
        print(f"\nProjet {idx}: {name}")
    except:
        print(f"\nProjet {idx}: [nom avec accents]")
    
    print(f"  ID dest       : {proj['id']}")
    print(f"  user_id       : {proj.get('user_id')}")
    print(f"  partner_id    : {proj.get('partner_id')}")

# ÉTAPE 3 : Vérifier les utilisateurs disponibles
print("\n" + "="*70)
print("ÉTAPE 3: UTILISATEURS DISPONIBLES EN DESTINATION")
print("="*70)

users_dst = conn.executer_destination('res.users', 'search_read', [],
                                      fields=['name', 'login', 'active'])

print(f"Nombre d'utilisateurs: {len(users_dst)}\n")
for user in users_dst[:10]:  # Afficher les 10 premiers
    print(f"  ID {user['id']}: {user.get('name')} ({user.get('login')})")

# ÉTAPE 4 : Charger mapping utilisateurs
print("\n" + "="*70)
print("ÉTAPE 4: MAPPING UTILISATEURS")
print("="*70)

mapping_file = Path('logs') / 'user_mapping.json'
if mapping_file.exists():
    with open(mapping_file, 'r') as f:
        user_mapping = json.load(f)
    print(f"Mapping utilisateurs disponible: {len(user_mapping)} mappés")
    for src_id, dst_id in list(user_mapping.items())[:5]:
        print(f"  Source {src_id} -> Dest {dst_id}")
else:
    print("ATTENTION: Aucun mapping utilisateurs trouvé!")
    user_mapping = {}

# ÉTAPE 5 : Tester la création d'UN projet
print("\n" + "="*70)
print("ÉTAPE 5: TEST CRÉATION D'UN PROJET")
print("="*70)

if src_projects:
    test_proj = src_projects[0]
    name = test_proj.get('name', 'Test')
    
    try:
        print(f"Test avec: {name}")
    except:
        print(f"Test avec: [nom avec accents]")
    
    # Préparer les données
    data = {
        'name': name + ' (TEST)',  # Ajouter TEST pour ne pas confondre
        'active': True
    }
    
    # Ajouter user_id
    src_user_id = test_proj.get('user_id')
    if src_user_id:
        if isinstance(src_user_id, (list, tuple)):
            src_user_id = src_user_id[0]
        
        # Chercher dans le mapping
        if str(src_user_id) in user_mapping:
            data['user_id'] = user_mapping[str(src_user_id)]
            print(f"  user_id mappé: {src_user_id} -> {data['user_id']}")
        else:
            data['user_id'] = 2  # Admin par défaut
            print(f"  user_id par défaut: 2 (Admin)")
    else:
        data['user_id'] = 2
        print(f"  user_id par défaut: 2 (Admin)")
    
    # Ajouter company_id si présent
    if test_proj.get('company_id'):
        company_id = test_proj['company_id']
        if isinstance(company_id, (list, tuple)):
            data['company_id'] = company_id[0]
        else:
            data['company_id'] = company_id
        print(f"  company_id: {data['company_id']}")
    
    print(f"\nDonnées à créer:")
    print(f"  {data}")
    
    try:
        print("\nTentative de création...")
        test_id = conn.executer_destination('project.project', 'create', data)
        print(f"✓ SUCCÈS! Projet créé avec ID: {test_id}")
        
        # Supprimer le projet de test
        print(f"Suppression du projet de test...")
        conn.executer_destination('project.project', 'unlink', [test_id])
        print("✓ Projet de test supprimé")
        
    except Exception as e:
        print(f"✗ ERREUR: {str(e)}")
        print(f"\nDétails de l'erreur:")
        import traceback
        print(traceback.format_exc())

print("\n" + "="*70)
print("FIN DU DEBUG")
print("="*70)

