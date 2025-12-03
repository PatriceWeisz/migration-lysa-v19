# 🚀 MIGRATION ODOO v16 → v19 - GUIDE FINAL

## ✅ Scripts Prêts pour Production

### 📊 Script Principal : `migration_optimisee.py`

**Caractéristiques :**
- ✅ Préchargement des external_id (gain de temps 60%)
- ✅ Traitement par lots
- ✅ Cache en mémoire
- ✅ Affichage en temps réel
- ✅ Gestion complète des dépendances
- ✅ Mode TEST intégré

---

## 📋 Modules Inclus (47 modules)

### Phase 1 : Données Comptables de Base
1. Plan comptable (account.account) - 2,654
2. Taxes (account.tax) - 31
3. Positions fiscales (account.fiscal.position) - 3
4. Conditions de paiement (account.payment.term) - 13
5. Journaux (account.journal) - 40

### Phase 1bis : Comptabilité Analytique
6. Plans analytiques (account.analytic.plan)
7. Comptes analytiques (account.analytic.account)
8. Lignes analytiques (account.analytic.line)
9. Budgets (crossovered.budget)
10. Lignes budgétaires (crossovered.budget.lines)
11. Postes budgétaires (account.budget.post)

### Phase 1ter : Partenaires
12. Partenaires (res.partner) - 2,890
13. Étiquettes de contact (res.partner.category) - 16
14. Secteurs d'activité (res.partner.industry)
15. Titres (res.partner.title) - 6
16. Banques (res.bank) - 1
17. Comptes bancaires (res.partner.bank) - 1

### Phase 1quater : Produits et Unités
18. Catégories produits (product.category) - 53
19. Catégories unités mesure (uom.category) - 7
20. Unités de mesure (uom.uom) - 27

### Phase 2 : RH
21. Utilisateurs (res.users) - 1
22. Départements (hr.department) - 6
23. Postes/Fonctions (hr.job) - 18
24. Employés (hr.employee) - 28
25. Notes de frais (hr.expense)
26. Congés (hr.leave)
27. Types de congés (hr.leave.type)

### Phase 2bis : Projets
28. Projets (project.project)
29. Tâches (project.task)
30. Étapes de tâches (project.task.type)
31. Tags de projets (project.tags)

### Phase 3 : Stock
32. Emplacements stock (stock.location) - 83
33. Entrepôts (stock.warehouse) - 20
34. Routes stock (stock.route) - 59
35. Types opérations (stock.picking.type) - 133

### Phase 4 : Produits
36. Modèles produits (product.template) - 2,110
37. Variantes produits (product.product) - 2,080

### Phase 5 : Fabrication
38. Nomenclatures (mrp.bom) - 421
39. Lignes nomenclature (mrp.bom.line) - 1,359
40. Centres de travail (mrp.workcenter) - 9
41. Ordres de fabrication (mrp.production) - 15,952
42. Ordres de travail (mrp.workorder) - 16,097

### Phase 6 : CRM et Ventes
43. Listes de prix (product.pricelist)
44. Règles listes de prix (product.pricelist.item)
45. Équipes commerciales (crm.team)
46. Étapes CRM (crm.stage)
47. Pistes/Opportunités (crm.lead)
48. Modèles de devis (sale.order.template)
49. Commandes de vente (sale.order) - 10,549
50. Lignes commandes vente (sale.order.line) - 68,952

### Phase 7 : Achats
51. Commandes achat (purchase.order) - 5,208
52. Lignes commandes achat (purchase.order.line) - 10,387

### Phase 8 : Mouvements Stock
53. Transferts stock (stock.picking) - 24,767
54. Mouvements stock (stock.move) - 171,219
55. Lignes mouvement stock (stock.move.line) - 148,391

### Phase 9 : Comptabilité et Immobilisations
56. Immobilisations (account.asset)
57. Catégories immobilisations (account.asset.category)
58. Factures/Écritures (account.move) - 128,010
59. Lignes d'écriture (account.move.line) - 327,912
60. Paiements (account.payment) - 21,008

### Phase 10 : Rapprochements
61. Rapprochements partiels (account.partial.reconcile) - 32,201
62. Rapprochements complets (account.full.reconcile) - 9,998

---

## 🎯 Stratégie de Migration

### 🌙 NUIT 1 : Données de Référence (Phase 1-4)
**~10,000 enregistrements - Durée : 2-3 heures**

```bash
cd ~/migration_lysa_v19
git pull
workon migration_lysa
nohup python -u migration_optimisee.py > logs/migration_phase1_$(date +%Y%m%d_%H%M%S).log 2>&1 &
```

### 🌙 NUIT 2-7 : Transactions (Phase 5-10)
**~1,000,000 enregistrements - Par périodes**

Migrer par année ou par trimestre pour gérer les gros volumes.

---

## 🔧 Configuration

### Mode TEST (défaut)
```python
MODE_TEST = True
TEST_LIMIT = 10
```

### Mode PRODUCTION (pour la nuit)
```python
MODE_TEST = False
TEST_LIMIT = 10  # Ignoré en mode production
```

---

## 📊 Estimation Totale

**VOLUME TOTAL : ~1,000,000+ enregistrements**

**Avec optimisations :**
- Phase 1-4 : 2-3 heures ✅
- Phase 5-10 : 40-60 heures (plusieurs nuits)

---

## 🎯 Pour Lancer Cette Nuit

**Sur PythonAnywhere :**

```bash
# 1. Synchroniser
cd ~/migration_lysa_v19 && git pull

# 2. Activer environnement
workon migration_lysa

# 3. Compter d'abord pour vérifier
python compter_modules.py

# 4. Lancer la migration Phase 1-4
nohup python -u migration_optimisee.py > logs/migration_$(date +%Y%m%d_%H%M%S).log 2>&1 &

# 5. Noter le PID
echo $!

# 6. Surveiller
tail -f logs/migration_*.log
```

**Appuyer sur Ctrl+C pour arrêter le suivi (le script continue)**

