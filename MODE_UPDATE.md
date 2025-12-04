# 🔄 MODE UPDATE - Compléter les Champs Existants

## Problème

Les enregistrements déjà migrés n'ont que 20-30% de leurs champs.

**Exemple project.project :**
- Actuellement : 5 champs (name, user_id, partner_id, company_id, active)
- Manquants : 39 champs (alias_id, date, description, tags, etc.)

---

## ✅ Solution : Mode Update

Le framework a maintenant un **mode_update** qui :
1. ✅ Identifie les enregistrements via **external_id** (priorité)
2. ✅ Ou via champ unique si pas d'external_id
3. ✅ Met à jour avec TOUS les champs manquants
4. ✅ Préserve les données existantes

---

## 🎯 Utilisation

### Option 1 : Script Automatique

```bash
python completer_champs_existants.py
```

Met à jour automatiquement les 8 modules principaux.

### Option 2 : Module par Module

```python
from framework import MigrateurGenerique, GestionnaireConfiguration
from connexion_double_v19 import ConnexionDoubleV19

conn = ConnexionDoubleV19()
conn.connecter_tout()

# Configuration avec mode_update activé
config = GestionnaireConfiguration.obtenir_config_module('project.project')
config['mode_update'] = True  # ← ACTIVER LE MODE UPDATE

migrateur = MigrateurGenerique(conn, 'project.project', config)
stats = migrateur.migrer()

print(f"{stats['existants']} projets mis à jour avec tous leurs champs")
```

### Option 3 : Via migration_framework.py

Modifier `migration_framework.py` :

```python
# Ajouter mode test à la config
config['mode_test'] = MODE_TEST
config['test_limit'] = TEST_LIMIT
config['mode_update'] = True  # ← AJOUTER CETTE LIGNE
```

---

## 📊 Exemple Concret

### Avant Update

```python
# Projet migré avec 5 champs seulement
{
    'name': 'AMELIORATION CONTINUE',
    'user_id': 2,
    'partner_id': False,
    'company_id': 1,
    'active': True
}
```

### Après Update

```python
# Projet avec 44 champs
{
    'name': 'AMELIORATION CONTINUE',
    'user_id': 2,
    'partner_id': False,
    'company_id': 1,
    'active': True,
    'alias_name': 'amelioration-continue',
    'alias_id': 123,
    'date': '2024-01-15',
    'date_start': '2024-01-01',
    'description': 'Description du projet...',
    'privacy_visibility': 'employees',
    'rating_status': 'stage',
    'sequence': 10,
    'tag_ids': [1, 2, 3],
    'color': 3,
    'favorite_user_ids': [2],
    # ... 25 autres champs
}
```

---

## ⚠️ Important

### Identification via External_id

Le framework utilise **external_id en priorité** :

```python
# 1. Chercher via external_id (fiable à 100%)
if source_id in src_to_ext:
    ext_key = src_to_ext[source_id]
    if ext_key in ext_to_dst:
        dest_id = ext_to_dst[ext_key]  # ✅ Trouvé !

# 2. Sinon chercher par champ unique
if not dest_id and unique_val in dst_index:
    dest_id = dst_index[unique_val]
```

Cela garantit qu'on met à jour le **bon** enregistrement.

---

## 🔍 Vérification Avant/Après

### Avant Update

```bash
python verifier_mappings_existants.py
# Projets: 9 mappés (5 champs chacun)
```

### Lancer Update

```bash
python completer_champs_existants.py
```

### Après Update

```bash
python verifier_mappings_existants.py
# Projets: 9 mappés (44 champs chacun) ✅
```

---

## 🎯 Modules Prioritaires à Compléter

1. **project.project** - 5/44 champs → 44/44
2. **res.users** - 6/121 champs → 121/121
3. **account.tax** - 6/20 champs → 20/20
4. **product.template** - 10/50 champs → 50/50
5. **res.partner** - 15/80 champs → 80/80
6. **crm.team** - 4/13 champs → 13/13
7. **product.pricelist** - 4/7 champs → 7/7
8. **account.analytic.account** - 4/13 champs → 13/13

---

## 💡 Avantages

✅ **Pas de doublon** - Identifie via external_id  
✅ **Pas de perte** - Préserve données existantes  
✅ **Complet** - Ajoute TOUS les champs manquants  
✅ **Sûr** - Ne touche pas aux champs déjà remplis  
✅ **Rapide** - Utilise write() batch  

---

## 📝 Note Technique

La méthode `write()` d'Odoo ne modifie QUE les champs fournis.
Les autres champs restent intacts.

```python
# Avant
projet = {'name': 'Test', 'user_id': 2}

# Update
write([projet_id], {'description': 'Nouvelle desc', 'color': 3})

# Après
projet = {'name': 'Test', 'user_id': 2, 'description': 'Nouvelle desc', 'color': 3}
# name et user_id sont préservés ✅
```

---

**À lancer dans un terminal externe pour voir l'affichage en temps réel !**

