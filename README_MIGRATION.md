# 🚀 GUIDE DE MIGRATION ODOO v16 → v19

## 📋 Vue d'ensemble

Ce projet contient tous les scripts nécessaires pour migrer une base Odoo v16 vers Odoo v19 SaaS.

### Architecture

```
migration_lysa_v19/
├── orchestrateur_migration.py    # 🎯 Script principal
├── PLAN_MIGRATION_COMPLET.md     # 📋 Plan détaillé
│
├── Scripts de migration (par module)
│   ├── migrer_taxes.py
│   ├── migrer_etiquettes_contact.py
│   ├── migrer_listes_prix.py
│   ├── migrer_comptes_analytiques.py
│   ├── migrer_equipes_commerciales.py
│   └── migrer_projets.py
│
├── Scripts de vérification
│   ├── verifier_mappings_existants.py
│   └── construire_mapping_*.py
│
└── logs/
    └── *_mapping.json             # Mappings source_id → dest_id
```

---

## ✅ Ce qui EST déjà migré (7,935+ enregistrements)

| Module | Migrés | Status |
|--------|--------|--------|
| Plan comptable | 2,654 | ✅ |
| Partenaires | 2,891 | ✅ |
| Produits | 2,110 | ✅ |
| Taxes | 31 | ✅ |
| Journaux | 40 | ✅ |
| Unités mesure | 25 | ✅ |
| Étiquettes contact | 16 | ✅ |
| Listes de prix | 57 | ✅ |
| Utilisateurs | 1 | ✅ |
| Employés | 34 | ✅ |
| Entrepôts | 20 | ✅ |

---

## 🎯 Utilisation

### Option 1 : Migration Complète Automatique

Utilise l'orchestrateur pour tout migrer :

```bash
python orchestrateur_migration.py
```

**Avantages :**
- Lance tous les modules dans l'ordre
- Vérifie après chaque module
- S'arrête en cas d'erreur
- Affiche un résumé complet

### Option 2 : Migration Module par Module

Pour plus de contrôle, lancez chaque script individuellement :

```bash
# 1. Taxes
python migrer_taxes.py

# 2. Comptes analytiques  
python migrer_comptes_analytiques.py

# 3. Équipes commerciales
python migrer_equipes_commerciales.py

# etc.
```

**Avantages :**
- Contrôle total
- Debugging facile
- Peut relancer un module spécifique

### Option 3 : Vérification seule

Pour vérifier l'état actuel sans migrer :

```bash
python verifier_mappings_existants.py
```

---

## 📝 Créer un nouveau script de migration

Modèle à suivre (voir `migrer_taxes.py`) :

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MIGRATION [NOM DU MODULE]"""
import sys, os, json
from pathlib import Path
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

print("="*70)
print("MIGRATION: [NOM]")
print("="*70)
print("Chargement des modules... (10-15 secondes)")
print("="*70)

from connexion_double_v19 import ConnexionDoubleV19

print("OK - Modules charges")

conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    sys.exit(1)

print("OK Connexion\n")

LOGS_DIR = Path('logs')
mapping_file = LOGS_DIR / '[nom]_mapping.json'
mapping = json.load(open(mapping_file)) if mapping_file.exists() else {}
mapping = {int(k): v for k, v in mapping.items()}
print(f"Mapping: {len(mapping)}")

# Récupérer SOURCE
src = conn.executer_source('[model]', 'search_read', [],
                           fields=['name', ...])
print(f"SOURCE: {len(src)}")

# Récupérer DESTINATION
dst = conn.executer_destination('[model]', 'search_read', [], fields=['name'])
dst_index = {d['name']: d['id'] for d in dst if d.get('name')}
print(f"DESTINATION: {len(dst)}\n")

# Migrer chaque enregistrement
nouveaux = existants = 0
for idx, rec in enumerate(src, 1):
    name = rec.get('name', '')
    print(f"{idx}/{len(src)} - {name}")
    
    # Déjà mappé ?
    if rec['id'] in mapping:
        print("  -> Deja mappe")
        existants += 1
        continue
    
    # Existe en destination ?
    if name in dst_index:
        mapping[rec['id']] = dst_index[name]
        print(f"  -> Trouve")
        existants += 1
        continue
    
    # Créer
    try:
        data = {k: v for k, v in rec.items() 
               if k != 'id' and v not in (None, False, '')}
        
        # Nettoyer relations many2one
        for k in list(data.keys()):
            if isinstance(data[k], (list, tuple)) and len(data[k]) == 2:
                data[k] = data[k][0]
        
        dest_id = conn.executer_destination('[model]', 'create', data)
        mapping[rec['id']] = dest_id
        dst_index[name] = dest_id
        print(f"  -> CREE (ID: {dest_id})")
        nouveaux += 1
    except Exception as e:
        print(f"  -> ERREUR: {str(e)[:50]}")

# Sauvegarder mapping
with open(mapping_file, 'w') as f:
    json.dump({str(k): v for k, v in mapping.items()}, f, indent=2)

print(f"\nRESULTAT: {nouveaux} nouveaux, {existants} existants")
print(f"Total: {len(mapping)}/{len(src)}")
```

---

## 🔍 Vérifications Importantes

### Avant de migrer un module

1. Vérifier les dépendances (voir `PLAN_MIGRATION_COMPLET.md`)
2. S'assurer que les modules parents sont migrés
3. Vérifier les champs obligatoires en v19

### Après chaque migration

1. Vérifier le fichier mapping dans `logs/`
2. Comparer le total source vs destination
3. Tester manuellement quelques enregistrements

### En cas d'erreur

1. Lire le message d'erreur complet
2. Vérifier les champs manquants/obligatoires
3. Ajouter les valeurs par défaut si nécessaire
4. Relancer (les mappings existants ne seront pas re-créés)

---

## 📊 Prochaines Étapes

Une fois TOUS les modules de base migrés avec succès :

### Phase 2 : Transactions

1. **Nomenclatures (BOM)**
   - Bills of Materials
   - Composants

2. **Ordres de fabrication**
   - Manufacturing Orders
   - Work Orders

3. **Commandes**
   - Devis/Commandes clients
   - Commandes fournisseurs

4. **Stock**
   - Transferts
   - Mouvements
   - Inventaires

5. **Factures**
   - Factures clients/fournisseurs
   - Avoirs

6. **Paiements**
   - Paiements
   - Rapprochements

---

## 🆘 Troubleshooting

### Le script ne démarre pas

- **Attendre 10-15 secondes** : l'import de `connexion_double_v19` prend du temps
- Message "Chargement des modules..." doit s'afficher immédiatement
- Puis "OK - Modules charges" après ~15 secondes
- Puis la connexion s'affiche

### Erreur "Missing required field"

Un champ obligatoire en v19 n'existait pas en v16.

**Solution :** Ajouter une valeur par défaut dans le script :

```python
data = {...}
# Ajouter valeurs par défaut pour v19
if 'required_field' not in data:
    data['required_field'] = valeur_par_defaut
```

### Erreur "duplicate key"

Un enregistrement existe déjà en destination.

**Solution :** Le script vérifie normalement les doublons. Si l'erreur persiste :
1. Vérifier le champ `unique_field` utilisé
2. Peut-être utiliser un autre champ (code, ref, etc.)

---

## 📞 Support

En cas de problème :
1. Consulter `PLAN_MIGRATION_COMPLET.md`
2. Vérifier les logs dans `logs/`
3. Relire les messages d'erreur complets
4. Les scripts sont **idempotents** : relancer ne crée pas de doublons

---

**Bonne migration ! 🚀**

