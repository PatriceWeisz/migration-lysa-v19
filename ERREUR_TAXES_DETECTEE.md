# 🔍 ERREUR TAXES DÉTECTÉE

**Date détection : 4 décembre 2025, 01:15**  
**Statut : ✅ CORRIGÉE le 4 décembre 2025, 02:45**

## 📋 Résumé de la Session de Test

**Date :** 4 décembre 2025, 01:13  
**Base test :** lysa-migration-2.odoo.com  
**Module testé :** account.tax (Taxes)

---

## ❌ Erreur Détectée

### Message d'Erreur

```python
TypeError: 'int' object is not iterable
File: /home/odoo/src/odoo/19.0/addons/account/models/account_tax.py
Line: 637
Method: _sanitize_vals
Code: for command_vals in sanitized.pop(fname):
```

### Contexte

- **Module :** `account.tax`
- **Action :** Création de taxe
- **Tentatives :** 5 retries (toutes échouées)
- **Taxes trouvées en SOURCE :** 31
- **Taxes à migrer (test) :** 5

---

## 🔍 Analyse de l'Erreur

### Cause Probable

Les taxes en Odoo v19 ont des champs relationnels One2many complexes :

1. **`invoice_repartition_line_ids`** (Lignes de répartition factures)
2. **`refund_repartition_line_ids`** (Lignes de répartition avoirs)

Ces champs doivent être au format **commandes Odoo** :

```python
# Format attendu
invoice_repartition_line_ids = [
    (0, 0, {'repartition_type': 'base', 'factor_percent': 100.0}),
    (0, 0, {'repartition_type': 'tax', 'factor_percent': 100.0}),
]
```

**Mais** le migrateur générique envoie probablement :
- Un entier (ID)
- Une liste d'IDs `[1, 2, 3]`
- Un format incompatible

### Ligne de Code Problématique (Odoo v19)

```python
# account/models/account_tax.py, ligne 637
def _sanitize_vals(self, vals):
    sanitized = dict(vals)
    for fname in ['invoice_repartition_line_ids', 'refund_repartition_line_ids']:
        if fname in sanitized:
            # ERREUR ICI : sanitized.pop(fname) retourne un INT
            # Mais Odoo attend une LISTE
            for command_vals in sanitized.pop(fname):  # ← TypeError ici
                # ...
```

---

## ✅ Solution à Implémenter

### Option 1 : Exclure Ces Champs (Simple)

Dans le migrateur générique, ajouter une exclusion :

```python
# framework/migrateur_generique.py
CHAMPS_EXCLUS = {
    'account.tax': [
        'invoice_repartition_line_ids',
        'refund_repartition_line_ids',
    ]
}
```

**Conséquence :** Les lignes de répartition ne seront pas migrées, mais les taxes de base oui.

### Option 2 : Transformer Ces Champs (Complet)

Lire les lignes de répartition en SOURCE et les recréer au bon format :

```python
# Lire les lignes en SOURCE
tax_src = read('account.tax', tax_id, [
    'invoice_repartition_line_ids',
    'refund_repartition_line_ids'
])

# Lire les détails des lignes
invoice_lines = read('account.tax.repartition.line', 
                     tax_src['invoice_repartition_line_ids'])

# Recréer au format commandes Odoo
data['invoice_repartition_line_ids'] = [
    (0, 0, {
        'repartition_type': line['repartition_type'],
        'factor_percent': line['factor_percent'],
        'account_id': mapped_account_id,
        # ...
    })
    for line in invoice_lines
]
```

**Conséquence :** Migration complète et précise.

---

## 🔧 Actions à Faire

### Priorité 1 : Solution Rapide (Option 1)

1. ✅ Ajouter exclusion dans `migrateur_generique.py`
2. ✅ Relancer test
3. ✅ Valider que taxes se créent (sans répartition)

### Priorité 2 : Solution Complète (Option 2)

1. ❌ Créer transformation spécifique `account.tax`
2. ❌ Migrer lignes de répartition
3. ❌ Tester avec toutes les taxes

---

## 📊 Ce Qui Fonctionne Déjà

✅ **Connexion SOURCE/DEST** : OK  
✅ **Comptage taxes** : 31 taxes trouvées  
✅ **Initialisation migrateur** : OK  
✅ **Détection automatique d'erreur** : OK  
✅ **Retry automatique** : OK (5 tentatives)  
✅ **Log en temps réel** : OK  

---

## 🎯 Prochaines Étapes

### Demain

1. **Implémenter Option 1** (exclusion champs)
2. **Tester taxes** sans répartition
3. **Tester autres modules** :
   - `res.partner.category` (Tags)
   - `res.country` (Pays)
   - `res.partner` (Partenaires)
   - `product.category` (Catégories produits)

4. **Documenter tous les problèmes** similaires
5. **Créer transformations** spécifiques

---

## 📝 Notes Techniques

### Champs One2many en Odoo

Format des commandes :
- `(0, 0, {...})` : Créer nouvel enregistrement
- `(1, id, {...})` : Modifier enregistrement existant
- `(2, id)` : Supprimer enregistrement
- `(3, id)` : Délier enregistrement
- `(4, id)` : Lier enregistrement existant
- `(5,)` : Délier tous
- `(6, 0, [ids])` : Remplacer par liste d'IDs

### Modèles Liés

- `account.tax` → `account.tax.repartition.line`
- Champs : `repartition_type`, `factor_percent`, `account_id`, `tag_ids`

---

## ✅ Résumé

**Erreur identifiée :** ✅  
**Cause comprise :** ✅  
**Solution connue :** ✅  
**Prêt à corriger :** ✅  

**Le test a parfaitement rempli son rôle : détecter les erreurs AVANT la migration complète ! 🎉**

---

**Session de test du 4 décembre 2025**  
**Base : lysa-migration-2**  
**Module : account.tax**  
**Erreur : TypeError champs One2many**  
**Solution : Exclusion ou transformation**

