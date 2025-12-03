# PLAN DE MIGRATION COMPLET ODOO v16 → v19

## Phase 1 : DONNÉES DE BASE (Configuration)

### 1.1 Comptabilité
- [x] Plan comptable (2,654)
- [x] Taxes (31)
- [x] Positions fiscales (3)
- [x] Conditions de paiement (13)
- [x] Journaux (40)
- [ ] Plans analytiques (2)
- [ ] Comptes analytiques (15)
- [ ] Postes budgétaires (si module installé)

### 1.2 Partenaires
- [x] Partenaires (2,891)
- [x] Étiquettes contact (16)
- [x] Secteurs d'activité (21)
- [ ] Titres (si module installé)
- [ ] Banques (1)
- [ ] Comptes bancaires partenaires (1)

### 1.3 Produits
- [x] Catégories produits (54)
- [x] Unités de mesure (25/27)
- [x] Produits (2,110)
- [ ] Listes de prix (57) ✓ mappés
- [ ] Règles de prix (items)

### 1.4 RH
- [x] Utilisateurs (1)
- [x] Départements (6)
- [x] Postes/Fonctions (18)
- [x] Employés (34)
- [ ] Types de congés (6)

### 1.5 Stock
- [x] Entrepôts (20)
- [ ] Emplacements (35/83)
- [ ] Types d'opérations (79/133)
- [ ] Routes

### 1.6 Ventes
- [ ] Équipes commerciales (40)
- [ ] Étapes CRM
- [ ] Modèles de devis

### 1.7 Projets
- [ ] Projets (9)
- [ ] Étapes de tâches (40)

---

## Phase 2 : TRANSACTIONS (Données opérationnelles)

### 2.1 Nomenclatures
- [ ] Nomenclatures de produits (BOM)
- [ ] Composants BOM

### 2.2 Fabrication
- [ ] Ordres de fabrication
- [ ] Ordres de travail

### 2.3 Ventes
- [ ] Devis/Commandes clients
- [ ] Lignes de commande

### 2.4 Achats
- [ ] Demandes de prix
- [ ] Commandes fournisseurs
- [ ] Lignes de commande

### 2.5 Stock
- [ ] Transferts de stock
- [ ] Mouvements de stock
- [ ] Inventaires

### 2.6 Facturation
- [ ] Factures clients
- [ ] Avoirs clients
- [ ] Factures fournisseurs
- [ ] Avoirs fournisseurs

### 2.7 Paiements et Rapprochements
- [ ] Paiements
- [ ] Rapprochements partiels
- [ ] Rapprochements complets
- [ ] Écritures comptables

### 2.8 Analytique et Budgets
- [ ] Lignes analytiques
- [ ] Budgets
- [ ] Lignes budgétaires

### 2.9 Projets et Tâches
- [ ] Tâches
- [ ] Feuilles de temps

### 2.10 RH
- [ ] Allocations de congés
- [ ] Demandes de congés
- [ ] Notes de frais

---

## ORDRE D'EXÉCUTION

### ÉTAPE 1 : Utilisateurs (PRIORITÉ - requis par beaucoup de modules)
1. Utilisateurs (avec leurs groupes de permissions)
   - IMPORTANT: Les projets, produits, équipes commerciales référencent des utilisateurs

### ÉTAPE 2 : Modules de base (sans dépendances)
2. Taxes
3. Étiquettes contact
4. Listes de prix
5. Plans analytiques
6. Types de congés

### ÉTAPE 3 : Modules avec dépendances légères
7. Comptes analytiques (dépend: plans analytiques)
8. Emplacements stock (dépend: entrepôts)
9. Types opérations (dépend: entrepôts, emplacements)
10. Équipes commerciales (dépend: utilisateurs)
11. Projets (dépend: utilisateurs)

### ÉTAPE 4 : Vérification complète
- Comparer comptages source vs destination
- Vérifier intégrité des mappings
- Tester quelques enregistrements manuellement

### ÉTAPE 5 : Transactions (après validation complète des bases)
- Ordre chronologique recommandé
- Par lots avec vérification
- Sauvegarde des mappings à chaque étape

