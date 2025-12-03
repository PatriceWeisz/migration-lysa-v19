# MIGRATION DES TRANSACTIONS

## ⚠️ IMPORTANT

**Ne migrer les transactions QU'APRÈS avoir migré et vérifié TOUS les modules de base !**

Les transactions dépendent des mappings de :
- Comptes
- Partenaires  
- Produits
- Journaux
- Taxes
- Utilisateurs
- Entrepôts
- etc.

---

## 📋 Liste des Scripts de Transaction à Créer

### 1. Nomenclatures (Manufacturing)

```bash
migrer_bom.py                    # Bills of Materials
migrer_bom_lines.py              # Lignes de nomenclatures
```

**Ordre :** BOM → BOM Lines

**Dépendances :** produits

---

### 2. Ordres de Fabrication

```bash
migrer_manufacturing_orders.py   # Ordres de fabrication
migrer_work_orders.py            # Ordres de travail
```

**Ordre :** Manufacturing Orders → Work Orders

**Dépendances :** BOM, produits, emplacements

---

### 3. Ventes

```bash
migrer_sale_orders.py            # Commandes clients
migrer_sale_order_lines.py       # Lignes de commande
```

**Ordre :** Sale Orders → Lines

**Dépendances :** partenaires, produits, listes de prix, équipes commerciales

---

### 4. Achats

```bash
migrer_purchase_orders.py        # Commandes fournisseurs
migrer_purchase_order_lines.py   # Lignes de commande
```

**Ordre :** Purchase Orders → Lines

**Dépendances :** partenaires, produits

---

### 5. Stock

```bash
migrer_stock_pickings.py         # Transferts de stock
migrer_stock_moves.py            # Mouvements de stock
migrer_stock_move_lines.py       # Lignes de mouvement détaillées
migrer_stock_inventories.py      # Inventaires
```

**Ordre :** Pickings → Moves → Move Lines

**Dépendances :** entrepôts, emplacements, types d'opérations, produits

**ATTENTION :** 
- Volumes très importants
- Migrer par lots (par exemple : 1 mois à la fois)
- Vérifier les quantités après chaque lot

---

### 6. Factures

```bash
migrer_account_moves.py          # Factures + Avoirs (clients et fournisseurs)
migrer_account_move_lines.py    # Lignes de facture/comptables
```

**Ordre :** Account Moves → Lines

**Dépendances :** partenaires, comptes, journaux, taxes, produits

**Types de moves :**
- `out_invoice` : Factures clients
- `out_refund` : Avoirs clients
- `in_invoice` : Factures fournisseurs
- `in_refund` : Avoirs fournisseurs
- `entry` : Écritures manuelles

**ATTENTION :**
- Ne PAS migrer les écritures "Draft"
- Migrer dans l'ordre chronologique
- Vérifier les totaux après

---

### 7. Paiements et Rapprochements

```bash
migrer_account_payments.py       # Paiements
migrer_account_partial_reconcile.py  # Rapprochements partiels
migrer_account_full_reconcile.py     # Rapprochements complets
```

**Ordre :** Payments → Partial Reconcile → Full Reconcile

**Dépendances :** factures, journaux, comptes

**ATTENTION :**
- Les rapprochements doivent référencer des moves déjà migrés
- Vérifier les balances après

---

### 8. Analytique

```bash
migrer_analytic_lines.py         # Lignes analytiques
```

**Dépendances :** comptes analytiques, partenaires, factures

---

### 9. Budgets

```bash
migrer_crossovered_budgets.py    # Budgets
migrer_budget_lines.py           # Lignes budgétaires
```

**Ordre :** Budgets → Lines

**Dépendances :** comptes analytiques, postes budgétaires

---

### 10. Projets et Tâches

```bash
migrer_project_tasks.py          # Tâches
migrer_account_analytic_lines_timesheet.py  # Feuilles de temps
```

**Dépendances :** projets, utilisateurs, étapes de tâches

---

### 11. CRM

```bash
migrer_crm_leads.py              # Leads/Opportunités
migrer_crm_activities.py         # Activités
```

**Dépendances :** équipes commerciales, étapes CRM, partenaires

---

### 12. RH

```bash
migrer_hr_leave_allocations.py  # Allocations de congés
migrer_hr_leaves.py              # Demandes de congés
migrer_hr_expenses.py            # Notes de frais
```

**Dépendances :** employés, types de congés

---

## 🎯 Stratégie de Migration Recommandée

### Étape 1 : Migration de Test (1 mois)

1. Choisir une période test (ex: janvier 2024)
2. Migrer TOUTES les transactions de ce mois
3. Vérifier l'intégrité complète
4. Corriger les problèmes

### Étape 2 : Migration Progressive

1. Migrer par trimestre
2. Vérifier après chaque trimestre
3. Sauvegarder les mappings

### Étape 3 : Vérification Finale

1. Comparer les totaux globaux
2. Vérifier les balances comptables
3. Tester quelques flux complets
4. Valider avec les utilisateurs clés

---

## 📊 Volumes Estimés (à mesurer avec compter_modules.py)

Exécuter pour connaître les volumes exacts :

```bash
python compter_modules.py
```

Cela vous donnera le nombre d'enregistrements pour :
- `sale.order`
- `purchase.order`
- `stock.picking`
- `stock.move`
- `account.move`
- `account.move.line`
- `account.payment`
- etc.

**IMPORTANT :** Si > 10,000 enregistrements → migrer par lots !

---

## ⚡ Optimisations pour Gros Volumes

### 1. Batch Processing

```python
BATCH_SIZE = 100
for i in range(0, len(records), BATCH_SIZE):
    batch = records[i:i+BATCH_SIZE]
    # Traiter le batch
```

### 2. Pre-loading Mappings

```python
# Charger TOUS les mappings en mémoire au début
partner_mapping = charger_mapping('partner')
product_mapping = charger_mapping('product')
account_mapping = charger_mapping('account')
# etc.
```

### 3. Parallel Processing (si applicable)

```python
from multiprocessing import Pool

def migrer_batch(batch):
    # Migrer un batch
    pass

with Pool(4) as p:
    results = p.map(migrer_batch, batches)
```

---

## 🔍 Vérifications Critiques

Après migration des transactions, vérifier :

### Comptabilité
```sql
-- Balance générale
SELECT account_id, SUM(debit), SUM(credit)
FROM account_move_line
WHERE move_id IN (SELECT id FROM account_move WHERE state = 'posted')
GROUP BY account_id
```

### Stock
```sql
-- Quantités en stock
SELECT product_id, location_id, SUM(quantity)
FROM stock_move_line
WHERE state = 'done'
GROUP BY product_id, location_id
```

### Ventes
```sql
-- Chiffre d'affaires
SELECT DATE_TRUNC('month', date_order), SUM(amount_total)
FROM sale_order
WHERE state IN ('sale', 'done')
GROUP BY DATE_TRUNC('month', date_order)
ORDER BY 1
```

---

## 🆘 En Cas de Problème

### Rollback d'une migration de transaction

1. Les données de base ne sont PAS affectées
2. Supprimer les enregistrements créés en destination
3. Supprimer le fichier mapping correspondant
4. Relancer la migration

### Performance lente

1. Migrer par plus petits lots
2. Exécuter la nuit (moins de charge)
3. Utiliser PythonAnywhere avec des pauses
4. Considérer l'exécution en base directe (SQL) pour très gros volumes

---

**Ces migrations représentent la Phase 2 du projet.**

**Ne commencer qu'après validation complète de la Phase 1 (modules de base).**

