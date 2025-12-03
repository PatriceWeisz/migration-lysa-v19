#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FINALISER UTILISATEURS
======================
Désactive les utilisateurs qui étaient inactifs dans la source
À LANCER À LA FIN de toute la migration
"""
import sys, os, json
from pathlib import Path
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

print("="*70)
print("FINALISATION: DESACTIVATION DES UTILISATEURS")
print("="*70)
print("Ce script désactive les utilisateurs qui étaient inactifs")
print("dans la source mais ont été créés actifs pour la migration")
print("="*70)

from connexion_double_v19 import ConnexionDoubleV19

conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    sys.exit(1)

print("OK Connexion\n")

# Charger le mapping utilisateurs
LOGS_DIR = Path('logs')
mapping_file = LOGS_DIR / 'user_mapping.json'
if not mapping_file.exists():
    print("ERREUR: Aucun mapping utilisateurs trouvé!")
    sys.exit(1)

with open(mapping_file, 'r') as f:
    user_mapping = json.load(f)

print(f"Mapping utilisateurs: {len(user_mapping)} mappés\n")

# Récupérer TOUS les utilisateurs de la source avec leur statut
print("Récupération des utilisateurs SOURCE...")
src_users = conn.executer_source('res.users', 'search_read',
                                 [('active', 'in', [True, False])],
                                 fields=['id', 'name', 'login', 'active'])

print(f"OK {len(src_users)} utilisateurs SOURCE\n")

# Identifier ceux qui doivent être désactivés
a_desactiver = []

for user in src_users:
    src_id = user['id']
    src_active = user.get('active', True)
    
    # Si l'utilisateur était INACTIF dans la source
    # et qu'il a été migré
    if not src_active and str(src_id) in user_mapping:
        dest_id = user_mapping[str(src_id)]
        a_desactiver.append({
            'src_id': src_id,
            'dest_id': dest_id,
            'login': user.get('login'),
            'name': user.get('name')
        })

print(f"Utilisateurs à désactiver: {len(a_desactiver)}\n")

if not a_desactiver:
    print("Aucun utilisateur à désactiver!")
    sys.exit(0)

# Demander confirmation
print("="*70)
print("ATTENTION: Cette opération va désactiver les utilisateurs suivants:")
print("="*70)
for idx, user in enumerate(a_desactiver[:10], 1):
    try:
        print(f"  {idx}. {user['login']} - {user['name']}")
    except:
        print(f"  {idx}. {user['login']}")

if len(a_desactiver) > 10:
    print(f"  ... et {len(a_desactiver) - 10} autres")

print("="*70)
reponse = input("\nContinuer ? (oui/NON): ").strip().lower()

if reponse != 'oui':
    print("Annulé par l'utilisateur")
    sys.exit(0)

# Désactiver les utilisateurs
print("\nDésactivation en cours...\n")
desactives = 0
erreurs = 0

for idx, user in enumerate(a_desactiver, 1):
    try:
        print(f"{idx}/{len(a_desactiver)} - {user['login']}")
    except:
        print(f"{idx}/{len(a_desactiver)}")
    
    try:
        conn.executer_destination('res.users', 'write',
                                 [user['dest_id']],
                                 {'active': False})
        print("  -> Désactivé")
        desactives += 1
    except Exception as e:
        try:
            print(f"  -> ERREUR: {str(e)[:60]}")
        except:
            print(f"  -> ERREUR")
        erreurs += 1

print("\n" + "="*70)
print("FINALISATION TERMINÉE")
print("="*70)
print(f"Utilisateurs désactivés : {desactives}")
print(f"Erreurs                 : {erreurs}")
print("="*70)

