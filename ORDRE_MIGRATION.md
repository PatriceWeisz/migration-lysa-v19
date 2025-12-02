# Ordre de Migration - IMPORTANT

## ⚠️ Ordre Obligatoire

La migration doit être effectuée dans un ordre précis à cause des dépendances entre les données.

## 📋 Ordre Complet de Migration

### 1️⃣ Plan Comptable (OBLIGATOIRE EN PREMIER)

**Script** : `migration_plan_comptable.py`

**Pourquoi en premier ?**
- Les partenaires font référence à des comptes (411xxx pour clients, 401xxx pour fournisseurs)
- Les factures utilisent des comptes comptables
- Les journaux nécessitent des comptes par défaut

**Ce qui est migré :**
- Tous les comptes du plan comptable (`account.account`)
- Mapping des types de comptes v16 → v19
- Génération du fichier `logs/account_mapping.json`

**Commande :**
```bash
python migration_plan_comptable.py
```

---

### 2️⃣ Journaux Comptables

**Script** : `migration_journaux.py` (à créer)

**Pourquoi après le plan comptable ?**
- Les journaux font référence à des comptes par défaut
- Nécessite le mapping des comptes

**Ce qui sera migré :**
- Journaux de vente
- Journaux d'achat
- Journaux de banque
- Journal des opérations diverses

---

### 3️⃣ Partenaires (Clients et Fournisseurs)

**Script** : `migration_partenaires.py` ✅

**Pourquoi après le plan comptable ?**
- Les partenaires peuvent avoir des comptes comptables spécifiques
- Dépend du mapping des comptes

**Ce qui est migré :**
- Clients (avec compte 411xxx)
- Fournisseurs (avec compte 401xxx)
- Informations de contact
- Données fiscales (TVA, etc.)

**Commande :**
```bash
python migration_partenaires.py
```

---

### 4️⃣ Produits

**Script** : `migration_produits.py` (à créer)

**Pourquoi après partenaires ?**
- Les produits peuvent avoir des fournisseurs par défaut
- Certains comptes comptables par défaut

**Ce qui sera migré :**
- Articles et services
- Catégories de produits
- Prix et coûts
- Comptes comptables associés

---

### 5️⃣ Factures Clients

**Script** : `migration_factures_clients.py` (à créer)

**Pourquoi après plan comptable ET partenaires ET produits ?**
- Fait référence aux clients (partenaires)
- Utilise des comptes comptables
- Contient des lignes avec des produits

**Ce qui sera migré :**
- Factures clients validées
- Lignes de factures
- Taxes
- Écritures comptables associées

---

### 6️⃣ Factures Fournisseurs

**Script** : `migration_factures_fournisseurs.py` (à créer)

**Pourquoi après plan comptable ET partenaires ET produits ?**
- Fait référence aux fournisseurs (partenaires)
- Utilise des comptes comptables
- Contient des lignes avec des produits

**Ce qui sera migré :**
- Factures fournisseurs validées
- Lignes de factures
- Taxes
- Écritures comptables associées

---

### 7️⃣ Avoirs Clients

**Script** : `migration_avoirs.py` (à créer)

**Pourquoi après les factures ?**
- Les avoirs peuvent être liés à des factures
- Mêmes dépendances que les factures

---

### 8️⃣ Avoirs Fournisseurs

**Script** : `migration_avoirs.py` (à créer)

**Pourquoi après les factures ?**
- Les avoirs peuvent être liés à des factures
- Mêmes dépendances que les factures

---

### 9️⃣ Paiements

**Script** : `migration_paiements.py` (à créer)

**Pourquoi en dernier ?**
- Les paiements sont liés aux factures
- Nécessite que toutes les factures existent

**Ce qui sera migré :**
- Paiements clients
- Paiements fournisseurs
- Lettrage avec les factures

---

## 🚀 Migration Automatique

Pour migrer dans le bon ordre automatiquement :

```bash
python migration_complete.py
```

Ce script orchestre toute la migration dans l'ordre correct.

## ⚠️ Erreurs Courantes

### Erreur : "Account does not exist"

**Cause** : Plan comptable pas migré en premier  
**Solution** : Exécuter `python migration_plan_comptable.py`

### Erreur : "Partner does not exist"

**Cause** : Partenaires pas migrés avant les factures  
**Solution** : Exécuter `python migration_partenaires.py`

### Erreur : "Product does not exist"

**Cause** : Produits pas migrés avant les factures  
**Solution** : Exécuter `python migration_produits.py`

## 📊 Graphique des Dépendances

```
┌─────────────────────┐
│  Plan Comptable     │ ◄── COMMENCE ICI
└──────────┬──────────┘
           │
           ├──────────────┬──────────────┐
           │              │              │
           ▼              ▼              ▼
    ┌──────────┐   ┌──────────┐   ┌──────────┐
    │ Journaux │   │Partenaires│   │ Produits │
    └─────┬────┘   └─────┬─────┘   └────┬─────┘
          │              │              │
          └──────────┬───┴──────────────┘
                     │
                     ▼
            ┌────────────────┐
            │    Factures    │
            └────────┬───────┘
                     │
                     ▼
            ┌────────────────┐
            │     Avoirs     │
            └────────┬───────┘
                     │
                     ▼
            ┌────────────────┐
            │   Paiements    │
            └────────────────┘
```

## ✅ Checklist de Migration

### Avant de commencer
- [ ] Sauvegarde effectuée
- [ ] Connexion testée
- [ ] Configuration vérifiée

### Ordre de migration
1. - [ ] Plan comptable migré
2. - [ ] Journaux migrés
3. - [ ] Partenaires migrés
4. - [ ] Produits migrés
5. - [ ] Factures clients migrées
6. - [ ] Factures fournisseurs migrées
7. - [ ] Avoirs migrés
8. - [ ] Paiements migrés

### Après chaque étape
- [ ] Vérifier les logs
- [ ] Compter les enregistrements
- [ ] Tester quelques exemples

### Finalisation
- [ ] Vérification complète
- [ ] Tests manuels
- [ ] Documentation des anomalies

## 🎯 Commandes Rapides

```bash
# 1. Plan comptable (EN PREMIER!)
python migration_plan_comptable.py

# 2. Partenaires
python migration_partenaires.py

# 3. Vérification après chaque étape
python verification_v19.py

# OU tout en automatique
python migration_complete.py
```

## 📝 Notes Importantes

1. **Ne jamais sauter le plan comptable** : C'est la base de tout
2. **Respecter l'ordre** : Les dépendances sont critiques
3. **Vérifier après chaque étape** : Plus facile de corriger au fur et à mesure
4. **Consulter les logs** : Fichiers dans `logs/`
5. **Mode simulation** : Tester d'abord avec `MODE_SIMULATION = True`

## 🆘 En cas de problème

Si vous avez migré dans le mauvais ordre :
1. Nettoyer la base destination
2. Recommencer dans le bon ordre
3. Ou corriger manuellement les références

---

**Auteur** : SENEDOO  
**Date** : 02 Décembre 2025

