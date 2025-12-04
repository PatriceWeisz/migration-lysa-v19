# 🚀 PROJET : FRAMEWORK DE MIGRATION COMPLET ET RÉUTILISABLE

## 🎯 Vision

Créer un framework de migration Odoo **professionnel, complet et réutilisable** pour migrer :
- ✅ TOUS les modules standard
- ✅ TOUS les modules Studio customisés
- ✅ TOUS les champs de chaque module
- ✅ TOUS les paramétrages système
- ✅ TOUTES les transactions
- ✅ Vérifications et validations complètes

**Objectif : Utilisable pour d'autres migrations Odoo**

---

## 📋 Plan d'Exécution

### PHASE 0 : ANALYSE COMPLÈTE (2-3 heures)

#### 0.1 Inventaire Complet
```bash
python compter_modules.py          # Déjà fait
python detecter_modules_studio.py  # Modules customisés
python analyser_champs_modules.py  # Tous les champs
```

**Résultat attendu :**
- Liste complète de tous les modèles
- Modules Studio identifiés
- Champs migrables par module

#### 0.2 Paramétrages Système

**Modules à analyser :**
- `res.company` - Paramètres entreprise
- `res.config.settings` - Configurations modules
- `ir.config_parameter` - Paramètres système
- `ir.module.module` - Modules installés
- `ir.sequence` - Séquences
- `decimal.precision` - Précisions décimales

#### 0.3 Dépendances

Créer un graphe de dépendances :
```
res.users
  └─> hr.employee
      └─> project.project
          └─> project.task
```

---

### PHASE 1 : FRAMEWORK GÉNÉRIQUE (1 jour)

#### 1.1 Classe de Base `MigrateurGenerique`

```python
class MigrateurGenerique:
    """Classe générique pour migrer n'importe quel module"""
    
    def __init__(self, conn, model, config):
        self.conn = conn
        self.model = model
        self.config = config
        # config = {
        #     'nom': 'Taxes',
        #     'fichier': 'tax',
        #     'unique_field': 'name',
        #     'champs': [...],  # Tous les champs
        #     'relations': {     # Relations à mapper
        #         'user_id': 'user_mapping.json',
        #         'partner_id': 'partner_mapping.json'
        #     },
        #     'valeurs_defaut': {...},  # Valeurs par défaut
        #     'skip_conditions': [...], # Conditions de skip
        # }
    
    def migrer(self):
        """Migre automatiquement le module"""
        pass
    
    def obtenir_champs_automatiques(self):
        """Obtient automatiquement tous les champs migrables"""
        pass
```

#### 1.2 Gestionnaire de Relations

```python
class GestionnaireRelations:
    """Gère automatiquement les relations many2one, many2many"""
    
    def mapper_relation(self, field_name, source_id):
        """Mappe automatiquement une relation"""
        pass
```

#### 1.3 Gestionnaire d'External IDs

```python
class GestionnaireExternalIds:
    """Gère les external_id pour tous les modules"""
    
    def copier_external_ids(self, model, source_id, dest_id):
        """Copie les external_id de la source"""
        pass
```

---

### PHASE 2 : PARAMÉTRAGES SYSTÈME (3-4 heures)

#### 2.1 Entreprise (res.company)

**Champs critiques :**
- Logo, nom, adresse
- Devise, langue
- **Comptabilité analytique activée**
- Plans comptables
- Exercices fiscaux
- TVA intra, SIRET

#### 2.2 Configurations Modules (res.config.settings)

**Par module :**
- Comptabilité : analytique, écart de change, etc.
- Stock : tracking, valorisation
- Ventes : devis automatiques, etc.
- Achats : approbations, etc.
- RH : congés, notes de frais
- Fabrication : ordres automatiques

#### 2.3 Paramètres Système (ir.config_parameter)

Tous les paramètres clés/valeurs système

#### 2.4 Séquences (ir.sequence)

Toutes les séquences de numérotation (factures, commandes, etc.)

---

### PHASE 3 : MODULES DE BASE COMPLETS (2 jours)

Pour CHAQUE module, migrer **TOUS** les champs :

#### 3.1 Comptabilité
- account.account (tous champs)
- account.tax (tous champs)
- account.journal (tous champs + séquences + comptes liés)
- account.fiscal.position (+ rules)
- account.payment.term (+ lines)
- account.analytic.plan
- account.analytic.account (tous champs)

#### 3.2 Partenaires
- res.partner (tous champs + adresses)
- res.partner.bank (tous champs)
- res.partner.category
- res.partner.industry
- res.partner.title

#### 3.3 Produits
- product.category (tous champs)
- uom.category
- uom.uom
- product.template (tous champs)
- product.product (variantes)
- product.pricelist (+ items)
- product.supplierinfo

#### 3.4 RH
- res.users (tous champs + droits)
- res.groups (permissions)
- hr.department
- hr.job
- hr.employee (tous champs)
- hr.leave.type
- hr.contract.type

#### 3.5 Stock
- stock.location (tous champs)
- stock.warehouse (configuration complète)
- stock.picking.type (tous champs)
- stock.route
- stock.rule

#### 3.6 Ventes
- crm.team (tous champs)
- crm.stage
- product.pricelist (tous champs)
- sale.quote.template

#### 3.7 Projets
- project.project (tous champs)
- project.task.type
- project.tags

---

### PHASE 4 : MODULES STUDIO (1-2 jours)

#### 4.1 Modèles Customisés
```bash
python detecter_modules_studio.py
```

Pour chaque modèle Studio (`x_*`) :
- Identifier tous les champs
- Créer script de migration
- Migrer données

#### 4.2 Champs Customisés

Sur modèles standard avec champs `x_*` :
- res.partner avec champs custom
- product.template avec champs custom
- etc.

#### 4.3 Vues et Actions Studio

- ir.ui.view (vues customisées)
- ir.actions.act_window (actions)
- ir.ui.menu (menus)

---

### PHASE 5 : TRANSACTIONS (1 semaine)

Voir `MIGRATION_TRANSACTIONS.md`

---

### PHASE 6 : VÉRIFICATION COMPLÈTE (2 jours)

#### 6.1 Vérifications Techniques
- Comptages source vs destination
- Intégrité des mappings
- External IDs

#### 6.2 Vérifications Métier
- Balance comptable
- Stocks physiques
- Chiffre d'affaires
- Tests utilisateurs

---

## 🛠️ Outils à Créer

### 1. Générateur Automatique de Scripts

```python
python generer_migration.py --model project.project --nom Projets
# Génère automatiquement migrer_projets_v2.py avec TOUS les champs
```

### 2. Validateur de Migration

```python
python valider_migration.py --model project.project
# Compare TOUS les champs source vs destination
```

### 3. Orchestrateur Intelligent

```python
python orchestrateur_complet.py
# Lance TOUTE la migration dans le bon ordre
# Gère les dépendances automatiquement
```

---

## 📊 Estimation Temps

| Phase | Durée | Description |
|-------|-------|-------------|
| Phase 0 | 3h | Analyse complète |
| Phase 1 | 1j | Framework générique |
| Phase 2 | 4h | Paramétrages |
| Phase 3 | 2j | Modules base complets |
| Phase 4 | 2j | Modules Studio |
| Phase 5 | 1sem | Transactions |
| Phase 6 | 2j | Vérifications |
| **TOTAL** | **~2 semaines** | Migration professionnelle complète |

---

## 🎯 Par Où Commencer ?

**OPTION A : Méthodique (recommandé)**
1. Finir Phase 0 (analyse complète)
2. Créer le framework (Phase 1)
3. Appliquer à tous les modules

**OPTION B : Pragmatique**
1. Identifier les 10 champs les plus critiques par module
2. Les ajouter aux scripts existants
3. Affiner progressivement

**OPTION C : Hybride**
1. Créer le framework générique
2. L'utiliser pour régénérer les scripts actuels
3. Continuer avec les nouveaux modules

---

**Quelle approche préférez-vous ?** 🤔

