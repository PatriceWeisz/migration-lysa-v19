# 📋 MODULES À MIGRER - ANALYSE COMPLÈTE

## 🎯 Modules par Ordre de Dépendances

### PHASE 1 : Données de Référence (PAS de dépendances)

1. **res.country** - Pays (données standard Odoo)
2. **res.currency** - Devises (données standard Odoo)
3. **uom.uom** - Unités de mesure (données standard Odoo)
4. **product.category** - Catégories de produits

### PHASE 2 : Comptabilité de Base

5. **account.account** - Plan comptable
6. **account.journal** - Journaux comptables
   - Dépend de: account.account

### PHASE 3 : Partenaires

7. **res.partner** - Partenaires/Contacts
   - Dépend de: res.country

### PHASE 4 : Utilisateurs et RH

8. **res.groups** - Groupes d'accès (mapper via external_id)
9. **res.users** - Utilisateurs
   - Dépend de: res.partner, res.groups
10. **hr.department** - Départements RH
11. **hr.job** - Postes/Fonctions
    - Dépend de: hr.department
12. **hr.employee** - Employés
    - Dépend de: res.users, hr.department, hr.job, res.partner

### PHASE 5 : Stock et Entrepôts

13. **stock.location** - Emplacements de stock
14. **stock.warehouse** - Entrepôts
    - Dépend de: res.partner, stock.location
15. **stock.route** - Routes de stock
    - Dépend de: stock.warehouse

### PHASE 6 : Produits

16. **product.template** - Modèles de produits
    - Dépend de: product.category, uom.uom, account.account
17. **product.product** - Variantes de produits
    - Dépend de: product.template

### PHASE 7 : Nomenclatures et Fabrication

18. **mrp.bom** - Nomenclatures (Bill of Materials)
    - Dépend de: product.template
19. **mrp.bom.line** - Lignes de nomenclature
    - Dépend de: mrp.bom, product.product
20. **mrp.workcenter** - Centres de travail
21. **mrp.routing** - Gammes de fabrication
    - Dépend de: mrp.workcenter
22. **mrp.production** - Ordres de fabrication
    - Dépend de: product.template, mrp.bom, stock.location
23. **mrp.workorder** - Ordres de travail
    - Dépend de: mrp.production, mrp.workcenter

### PHASE 8 : Ventes

24. **sale.order** - Commandes de vente
    - Dépend de: res.partner, product.template
25. **sale.order.line** - Lignes de commande vente
    - Dépend de: sale.order, product.product

### PHASE 9 : Achats

26. **purchase.order** - Commandes d'achat
    - Dépend de: res.partner, product.template
27. **purchase.order.line** - Lignes de commande achat
    - Dépend de: purchase.order, product.product

### PHASE 10 : Mouvements de Stock

28. **stock.picking** - Transferts de stock
    - Dépend de: res.partner, stock.location, stock.picking.type
29. **stock.move** - Mouvements de stock
    - Dépend de: stock.picking, product.product, stock.location
30. **stock.move.line** - Lignes détaillées de mouvement
    - Dépend de: stock.move

### PHASE 11 : Factures et Comptabilité

31. **account.move** - Factures/Écritures comptables
    - Dépend de: res.partner, account.journal
    - Types: out_invoice, in_invoice, out_refund, in_refund, entry
32. **account.move.line** - Lignes d'écriture
    - Dépend de: account.move, account.account, product.product
33. **account.payment** - Paiements
    - Dépend de: res.partner, account.journal, account.move

### PHASE 12 : Liens et Rapprochements

34. **account.partial.reconcile** - Rapprochements partiels
    - Dépend de: account.move.line
35. **sale.order + stock.picking** - Liens commandes/livraisons
36. **purchase.order + stock.picking** - Liens achats/réceptions
37. **stock.picking + account.move** - Valorisation des stocks

---

## ⚠️ Modules Standards Odoo (NE PAS migrer)

- **res.company** - Société (créé à l'installation)
- **ir.sequence** - Séquences (recréées automatiquement)
- **decimal.precision** - Précisions décimales (standard)
- **res.lang** - Langues (standard)

---

## 🎯 Ordre de Migration Optimal

```
1. Plan comptable (account.account)
2. Partenaires (res.partner)
3. Journaux (account.journal)
4. Utilisateurs (res.users) avec groupes
5. Départements RH (hr.department)
6. Postes (hr.job)
7. Employés (hr.employee)
8. Emplacements stock (stock.location)
9. Entrepôts (stock.warehouse)
10. Routes stock (stock.route)
11. Catégories produits (product.category)
12. Produits (product.template + product.product)
13. Nomenclatures (mrp.bom + mrp.bom.line)
14. Centres de travail (mrp.workcenter)
15. Gammes fabrication (mrp.routing)
16. Commandes de vente (sale.order + sale.order.line)
17. Commandes d'achat (purchase.order + purchase.order.line)
18. Transferts stock (stock.picking + stock.move + stock.move.line)
19. Ordres de fabrication (mrp.production)
20. Ordres de travail (mrp.workorder)
21. Factures (account.move + account.move.line)
22. Paiements (account.payment)
23. Rapprochements (account.partial.reconcile)
```

---

## 📊 Estimation de Volumes

| Module | Quantité Estimée | Priorité |
|--------|-----------------|----------|
| account.account | 2,654 | 🔴 Critique |
| res.partner | 2,757 | 🔴 Critique |
| account.journal | 40 | 🔴 Critique |
| res.users | 10-20 | 🔴 Critique |
| hr.employee | 100 | 🟡 Important |
| product.template | 2,080 | 🔴 Critique |
| account.move | 130,746+ | 🔴 Critique |
| account.move.line | 400,000+ | 🔴 Critique |
| stock.move | ? | 🟡 Important |
| sale.order | ? | 🟡 Important |
| purchase.order | ? | 🟡 Important |
| mrp.production | ? | 🟢 Optionnel |

---

## ⚠️ Modules Très Volumineux

- **account.move.line** : Peut avoir 400,000+ lignes
- **stock.move.line** : Peut avoir 200,000+ lignes
- Nécessitent traitement par lots et beaucoup de temps

---

## 💡 Recommandation

### Migration Prioritaire (Nuit 1) :
1-13 : Données de référence, RH, Produits

### Migration Secondaire (Nuit 2) :
14-23 : Transactions, Factures, Mouvements

