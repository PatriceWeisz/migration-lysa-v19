# ORDRE DE MIGRATION COMPLET v16 → v19

## 📋 Ordre d'Exécution des Scripts

### ✅ Phase 1 : Données de Base (TERMINÉ)

1. **Plan Comptable** (2,654 comptes)
   ```bash
   python migration_plan_comptable.py
   ```
   - Génère : `logs/account_mapping.json`

2. **Partenaires** (2,757 partenaires)
   ```bash
   python migration_partenaires.py
   ```
   - Génère : `logs/partner_mapping.json`

3. **Journaux** (40 journaux)
   ```bash
   python migration_journaux.py
   ```

### ⏳ Phase 2 : Utilisateurs et Employés (EN COURS)

4. **Utilisateurs** (avec groupes d'accès)
   ```bash
   python migration_users.py
   ```
   - Génère : `logs/user_mapping.json`
   - **IMPORTANT** : Les mots de passe sont réinitialisés à `ChangeMeNow123!`
   - Les utilisateurs doivent changer leur mot de passe à la première connexion

5. **Employés** (lié aux utilisateurs)
   ```bash
   python migration_employes.py
   ```
   - Génère : `logs/employe_mapping.json`
   - Nécessite : `user_mapping.json`, `partner_mapping.json`

### ⏳ Phase 3 : Stock et Entrepôts

6. **Entrepôts**
   ```bash
   python migration_entrepots.py
   ```
   - Génère : `logs/warehouse_mapping.json`
   - Nécessite : `partner_mapping.json`

### ⏳ Phase 4 : Produits

7. **Produits** (2,080 produits)
   ```bash
   python migration_produits.py
   ```
   - Génère : `logs/product_mapping.json`, `logs/product_category_mapping.json`
   - Nécessite : `account_mapping.json`, `employe_mapping.json`, `warehouse_mapping.json`
   - **Note** : Actuellement en mode TEST (10 produits)
   - Pour migrer TOUS les produits : Modifier `TEST_MODE = False` dans le script

### ⏳ Phase 5 : Transactions (À FAIRE)

8. **Factures** (130,746 écritures)
9. **Paiements**
10. **Mouvements de stock**

---

## 🔄 Dépendances entre Modules

```
Plan Comptable
    ↓
Partenaires ─────────┬─────────────┐
    ↓                ↓             ↓
Journaux      Utilisateurs    Entrepôts
                ↓
             Employés
                ↓
            Produits
                ↓
            Factures
```

---

## 📝 Fichiers de Mapping Générés

| Fichier | Description | Généré par |
|---------|-------------|------------|
| `account_mapping.json` | Comptes comptables | migration_plan_comptable.py |
| `partner_mapping.json` | Partenaires/Contacts | migration_partenaires.py |
| `user_mapping.json` | Utilisateurs | migration_users.py |
| `employe_mapping.json` | Employés | migration_employes.py |
| `warehouse_mapping.json` | Entrepôts | migration_entrepots.py |
| `product_category_mapping.json` | Catégories produits | migration_produits.py |
| `product_mapping.json` | Produits | migration_produits.py |

---

## ⚠️ Points d'Attention

### Utilisateurs
- **Mots de passe** : Tous réinitialisés à `ChangeMeNow123!`
- **Groupes** : Migrés automatiquement via external_id
- **Admin** : Non migré (ID=1 exclu)

### Produits Stockables
- Type `product` (v16) → `type='consu'` + `is_storable=True` (v19)
- Nécessite les employés pour le `responsible_id`
- Nécessite les entrepôts pour les routes de stock

### Champs Incompatibles v16 → v19
- **Partenaires** : `mobile` n'existe plus (fusionné dans `phone`)
- **Comptes** : `deprecated` n'existe plus (remplacé par `active`)
- **Produits** : `uom_po_id` n'existe plus
- **Catégories** : `property_valuation` et `property_cost_method` changés

---

## 🚀 Commandes Rapides

### Sur PythonAnywhere

```bash
# Se connecter et activer l'environnement
cd ~/migration_lysa_v19
workon migration_lysa

# Synchroniser avec GitHub
git pull

# Lancer une migration
python migration_users.py

# Vérifier les logs
tail -f logs/migration_users.log
```

### En Local (Windows)

```bash
# Synchroniser
git pull

# Lancer une migration
python migration_users.py
```

---

## 📊 État Actuel

| Module | Statut | Éléments | Durée |
|--------|--------|----------|-------|
| Plan Comptable | ✅ Terminé | 2,654 comptes | ~20 min |
| Partenaires | ✅ Terminé | 2,757 partenaires | ~18 min |
| Journaux | ✅ Terminé | 40 journaux | ~5 min |
| Utilisateurs | ⏳ À faire | ? utilisateurs | ? |
| Employés | ⏳ À faire | ? employés | ? |
| Entrepôts | ⏳ À faire | ? entrepôts | ? |
| Produits | 🧪 Test OK | 10/2,080 produits | 8 sec |
| Factures | ⏳ À faire | 130,746 écritures | ? |

---

## 🎯 Prochaine Étape

**Migrer les utilisateurs avec leurs groupes d'accès**

```bash
cd ~/migration_lysa_v19
git pull
workon migration_lysa
python migration_users.py
```

