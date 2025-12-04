# ⚙️ MIGRATION PARAMÈTRES CONFIGURATION

## 🎯 Pourquoi C'est CRITIQUE

**Question :** Pourquoi migrer les paramètres AVANT les données ?

**Réponse :** **Les paramètres activent des fonctionnalités qui ajoutent des champs !**

---

## ❌ Exemple de Problème

### Scénario Sans Migration Paramètres

```
SOURCE (v16):
  ✅ Comptabilité anglo-saxonne activée
     → Ajoute champs: stock_input_account_id, stock_output_account_id
  ✅ Double validation achats activée
     → Ajoute champs: approval_required, approved_by
  ✅ Signature portail activée
     → Ajoute champs: signature, signed_by, signed_on

DESTINATION (v19):
  ❌ Comptabilité anglo-saxonne DÉSACTIVÉE
     → Champs absents !
  ❌ Double validation DÉSACTIVÉE
     → Champs absents !
  ❌ Signature portail DÉSACTIVÉE
     → Champs absents !
```

### Résultat Migration

```
Migration product.template:
  ❌ ERREUR: Invalid field 'stock_input_account_id'
  ❌ ERREUR: Invalid field 'stock_output_account_id'

Migration purchase.order:
  ❌ ERREUR: Invalid field 'approval_required'
  ❌ ERREUR: Invalid field 'approved_by'

Migration sale.order:
  ❌ ERREUR: Invalid field 'signature'
  ❌ ERREUR: Invalid field 'signed_by'
```

**Vous perdez ces données ! 😱**

---

## ✅ Solution : Migrer Paramètres D'ABORD

### Ordre Correct

```
1. ⚙️ MIGRER PARAMÈTRES
   └─ Active fonctionnalités
   └─ Ajoute champs aux modèles

2. 📊 MIGRER DONNÉES
   └─ Champs disponibles
   └─ Migration OK
```

---

## 📋 Paramètres Migrés

### 1. ir.config_parameter (Paramètres Système)

**Exemples :**
- `sale.default_deposit_product_id`
- `account.use_anglo_saxon`
- `purchase.use_po_lead`
- `stock.propagation_minimum_delta`
- `mrp.manufacturing_lead`
- etc.

**Total :** 50-100 paramètres selon modules installés

### 2. res.company (Paramètres Société)

**Comptabilité :**
- `fiscalyear_last_day` / `fiscalyear_last_month`
- `period_lock_date` / `fiscalyear_lock_date` / `tax_lock_date`
- `anglo_saxon_accounting` ⚠️ **Active champs stock**
- `bank_account_code_prefix` / `cash_account_code_prefix`
- `account_purchase_tax_id` / `account_sale_tax_id`
- `tax_calculation_rounding_method`

**Ventes :**
- `sale_quotation_validity_days`
- `portal_confirmation_sign` ⚠️ **Active signature**
- `portal_confirmation_pay` ⚠️ **Active paiement en ligne**

**Achats :**
- `po_lead`
- `po_lock`
- `po_double_validation` ⚠️ **Active double validation**
- `po_double_validation_amount`

**Stock :**
- `security_lead`
- `propagation_minimum_delta`

**Fabrication :**
- `manufacturing_lead`

**RH :**
- `resource_calendar_id`
- `hr_presence_control_email`
- `hr_presence_control_ip`

**Total :** 20-30 paramètres

### 3. ir.sequence (Séquences)

**Exemples :**
- Factures clients : `account.move.out_invoice`
- Factures fournisseurs : `account.move.in_invoice`
- Commandes clients : `sale.order`
- Commandes fournisseurs : `purchase.order`
- Bons de livraison : `stock.picking.out`
- Réceptions : `stock.picking.in`
- Ordres de fabrication : `mrp.production`
- etc.

**Paramètres migrés :**
- Préfixe (ex: `FACT/2024/`)
- Suffixe
- Padding (nombre de zéros)
- Prochain numéro
- Incrément

**Total :** 30-50 séquences

---

## 🚀 Lancer la Migration Paramètres

### Méthode 1 : Batch (Simple)

**Double-cliquez :**
```
MIGRER_PARAMETRES.bat
```

### Méthode 2 : Terminal

```bash
python migrer_parametres_configuration.py
```

### Durée

**2-3 minutes**

---

## 📊 Résultat Attendu

```
======================================================================
MIGRATION PARAMÈTRES CONFIGURATION
======================================================================

1. PARAMÈTRES SYSTÈME (ir.config_parameter)
Paramètres SOURCE: 87
  ✅ NEW: sale.default_deposit_product_id = 42
  ✅ MAJ: account.use_anglo_saxon = True
  ✅ NEW: purchase.use_po_lead = 7.0
  ... (87 paramètres)

Résultat:
  Nouveaux   : 45
  Mis à jour : 38
  Ignorés    : 4
  Erreurs    : 0

2. PARAMÈTRES MODULES (res.config.settings)
ℹ️ res.config.settings est un modèle transient
   Les paramètres sont déjà migrés via:
   - ir.config_parameter (ci-dessus)
   - Champs des modèles (ex: res.company)

3. PARAMÈTRES SOCIÉTÉ (res.company)
Champs configuration disponibles: 23
✅ 23 paramètres société migrés:
  - fiscalyear_last_day: 31
  - fiscalyear_last_month: 12
  - anglo_saxon_accounting: True
  - sale_quotation_validity_days: 30
  - portal_confirmation_sign: True
  - po_double_validation: True
  - po_double_validation_amount: 5000.0
  ... (23 paramètres)

4. PARAMÈTRES SPÉCIFIQUES MODULES
ℹ️ Paramètres spécifiques déjà migrés via res.company (ci-dessus)
  - account: 6 paramètres
  - sale: 3 paramètres
  - purchase: 4 paramètres
  - stock: 2 paramètres
  - mrp: 1 paramètres

5. SÉQUENCES (ir.sequence)
⚠️ Les séquences définissent les numéros de factures, BL, etc.

Séquences SOURCE: 42
  ✅ MAJ: Factures clients
  ✅ MAJ: Factures fournisseurs
  ✅ MAJ: Commandes clients
  ✅ NEW: Ordres de fabrication
  ... (42 séquences)

Résultat:
  Nouveaux   : 8
  Mis à jour : 34
  Erreurs    : 0

======================================================================
RÉSUMÉ MIGRATION PARAMÈTRES
======================================================================

1. ir.config_parameter:
   - Nouveaux   : 45
   - Mis à jour : 38

2. res.company:
   - Paramètres migrés

3. ir.sequence:
   - Nouveaux   : 8
   - Mis à jour : 34

======================================================================
✅ MIGRATION PARAMÈTRES TERMINÉE
======================================================================

⚠️ IMPORTANT:
   Les paramètres ont été migrés.
   Certains peuvent nécessiter un redémarrage d'Odoo
   pour activer toutes les fonctionnalités.

Prochaine étape:
   1. Vérifier que les fonctionnalités sont activées
   2. Lancer la migration des données
```

---

## ⚠️ Paramètres Critiques

### Comptabilité Anglo-Saxonne

```python
anglo_saxon_accounting = True
```

**Impact :**
- Ajoute champs `stock_input_account_id`, `stock_output_account_id` sur `product.template`
- Ajoute champs `stock_valuation_account_id` sur `product.category`
- Change la logique de valorisation stock

**Si absent en DEST :** Migration produits échoue !

### Double Validation Achats

```python
po_double_validation = True
po_double_validation_amount = 5000.0
```

**Impact :**
- Ajoute champs `approval_required`, `approved_by`, `approved_date` sur `purchase.order`
- Active workflow de validation

**Si absent en DEST :** Migration commandes achats échoue !

### Signature Portail

```python
portal_confirmation_sign = True
```

**Impact :**
- Ajoute champs `signature`, `signed_by`, `signed_on` sur `sale.order`
- Active signature électronique

**Si absent en DEST :** Migration commandes clients échoue !

### Lots et Numéros de Série

```python
group_stock_production_lot = True
group_stock_tracking_lot = True
```

**Impact :**
- Ajoute champs `tracking` sur `product.template`
- Ajoute modèle `stock.production.lot`
- Active traçabilité

**Si absent en DEST :** Migration produits avec lots échoue !

---

## 🔍 Vérifier Après Migration Paramètres

### 1. Vérifier Fonctionnalités Activées

**Odoo DEST > Paramètres > [Module]**

Exemples :
- **Comptabilité** : Vérifier "Comptabilité anglo-saxonne"
- **Ventes** : Vérifier "Signature en ligne"
- **Achats** : Vérifier "Double validation"
- **Stock** : Vérifier "Lots et numéros de série"

### 2. Vérifier Champs Disponibles

```bash
python obtenir_tous_champs.py product.template
```

Vérifier présence de :
- `stock_input_account_id` (si anglo-saxon)
- `tracking` (si lots activés)
- etc.

### 3. Vérifier Séquences

**Odoo DEST > Paramètres > Séquences**

Vérifier :
- Préfixes corrects
- Prochains numéros corrects

---

## 🔄 Ordre Complet Migration

### NOUVEAU Workflow (Mis à Jour)

```
1. Sauvegarder (1 min)
   └─ COMMIT_ET_PUSH.bat

2. Vérifier Modules (2 min)
   └─ VERIFIER_MODULES.bat
   └─ Installer modules manquants
   └─ Re-vérifier

3. ⚙️ MIGRER PARAMÈTRES (3 min) ← NOUVEAU !
   └─ MIGRER_PARAMETRES.bat
   └─ Vérifier fonctionnalités activées

4. Analyser (5 min)
   └─ python analyser_avant_migration.py

5. Test Auto-Correction (5 min)
   └─ TEST_AUTO_CORRECTION.bat

6. Test Complet (15 min)
   └─ python test_complet_framework.py

7. Migration Données (4-6h)
   └─ python migration_framework.py

8. Vérifications (1h)
   └─ verifier_statuts.py
   └─ verifier_integrite_complete.py
   └─ verifier_comptabilite.py

9. Tests Utilisateurs (2h)
```

**⚠️ ÉTAPE 3 EST CRITIQUE ! Ne pas sauter !**

---

## 🎯 Cas Particuliers

### Paramètres Spécifiques à l'Instance

Certains paramètres sont **ignorés** car spécifiques à l'instance :

- `database.uuid` (UUID unique de la base)
- `database.secret` (Secret unique)
- `web.base.url` (URL de l'instance)
- `mail.catchall.domain` (Domaine email)
- `mail.bounce.alias` (Alias bounce)
- `ribbon.name` (Nom du ruban)

**Ces paramètres ne doivent PAS être migrés.**

### Paramètres Nécessitant Redémarrage

Certains paramètres nécessitent un **redémarrage d'Odoo** :

- Activation de modules
- Changement de mode comptabilité
- Activation de fonctionnalités système

**Sur Odoo SaaS :** Redémarrage automatique (peut prendre 1-2 min)

### Paramètres Nécessitant Upgrade

Certains paramètres nécessitent un **upgrade de module** :

```bash
# En ligne de commande (si accès serveur)
odoo-bin -u all -d database_name
```

**Sur Odoo SaaS :** Contacter support Odoo

---

## 📋 Checklist Migration Paramètres

- [ ] ✅ Modules installés vérifiés (`VERIFIER_MODULES.bat`)
- [ ] ✅ Lancer migration paramètres (`MIGRER_PARAMETRES.bat`)
- [ ] ✅ Consulter rapport (`logs/migration_parametres_*.txt`)
- [ ] ✅ Vérifier fonctionnalités activées (Odoo DEST > Paramètres)
- [ ] ✅ Vérifier champs disponibles (`obtenir_tous_champs.py`)
- [ ] ✅ Vérifier séquences (Odoo DEST > Séquences)
- [ ] ✅ Si OK → Lancer migration données

---

## 🚨 Erreurs Fréquentes

### Erreur 1 : Migrer données sans paramètres

```
❌ Lancer migration_framework.py sans migrer paramètres
→ Champs manquants
→ Migration échoue
→ Données perdues
```

**Solution :** TOUJOURS migrer paramètres d'abord

### Erreur 2 : Ignorer vérification fonctionnalités

```
✅ Paramètres migrés
❌ Ne pas vérifier si fonctionnalités activées
→ Champs toujours absents
→ Migration échoue
```

**Solution :** Vérifier dans Odoo DEST > Paramètres

### Erreur 3 : Oublier séquences

```
✅ Paramètres système migrés
❌ Séquences pas migrées
→ Numéros factures recommencent à 1
→ Doublons !
```

**Solution :** Script migre aussi les séquences automatiquement

---

## 📊 Rapport Généré

Le script génère un rapport détaillé :
```
logs/migration_parametres_YYYYMMDD_HHMMSS.txt
```

**Contient :**
- Tous les paramètres migrés
- Paramètres nouveaux vs mis à jour
- Paramètres ignorés (avec raison)
- Erreurs éventuelles
- Recommandations

**Conservez ce rapport pour traçabilité !**

---

## 🎯 Résumé

### Pourquoi Migrer Paramètres ?

✅ Active fonctionnalités  
✅ Ajoute champs aux modèles  
✅ Prépare base pour migration données  
✅ Évite erreurs "champ invalide"  

### Quand Migrer Paramètres ?

⚠️ **AVANT** migration données  
⚠️ **APRÈS** installation modules  
⚠️ **AVANT** tests  

### Comment Migrer Paramètres ?

```bash
# Option 1 (Simple)
Double-clic: MIGRER_PARAMETRES.bat

# Option 2 (Terminal)
python migrer_parametres_configuration.py
```

### Vérifier Après ?

✅ Fonctionnalités activées (Odoo DEST > Paramètres)  
✅ Champs disponibles (`obtenir_tous_champs.py`)  
✅ Séquences correctes (Odoo DEST > Séquences)  

---

## ✅ Résultat Attendu

```
✅ MIGRATION PARAMÈTRES TERMINÉE

1. ir.config_parameter: 45 nouveaux, 38 MAJ
2. res.company: 23 paramètres migrés
3. ir.sequence: 8 nouveaux, 34 MAJ

Prochaine étape:
   1. Vérifier fonctionnalités activées
   2. Lancer migration données
```

**→ Prêt pour migration données ! 🚀**

---

**Migration Paramètres Configuration**  
**CRITIQUE - À lancer AVANT migration données**  
**Active fonctionnalités et ajoute champs**  
**4 décembre 2025, 02:30**

