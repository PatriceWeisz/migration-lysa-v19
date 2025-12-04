# 📄 MIGRATION DES RAPPORTS PDF

## Modules Concernés

Le framework migre automatiquement tous les modèles d'impression :

---

## 1️⃣ report.paperformat (Formats de Papier)

**Configuration des formats d'impression**

**Champs migrés :**
- name, default, format
- page_height, page_width
- orientation, margin_top, margin_bottom, margin_left, margin_right
- header_line, header_spacing
- dpi, disable_shrinking
- report_ids

**Exemples :**
- Format A4
- Format US Letter
- Format Facture personnalisé
- Format Étiquette

---

## 2️⃣ ir.actions.report (Modèles d'Impression)

**Les rapports PDF eux-mêmes**

**Champs migrés :**
- name, model, report_name, report_type
- paperformat_id, print_report_name
- binding_model_id, binding_type
- groups_id (qui peut imprimer)
- attachment, attachment_use
- multi (impression multiple)

**Exemples de rapports migrés :**
- Factures (account.move)
- Devis (sale.order)
- Bons de commande (purchase.order)
- Bons de livraison (stock.picking)
- Fiches employés (hr.employee)
- Étiquettes produits (product.template)
- Contrats
- Rapports personnalisés

---

## 3️⃣ Vues QWeb (Templates des Rapports)

Les templates QWeb sont dans `ir.ui.view` avec `type='qweb'`

**Note :** Les vues des rapports seront migrées avec les vues générales.

---

## 4️⃣ mail.template (Modèles d'Emails avec PDF)

**Modèles d'emails qui génèrent des PDF**

**Champs migrés :**
- name, model_id, subject, body_html
- email_from, email_to, email_cc
- partner_to, reply_to
- report_name, report_template
- attachment_ids, auto_delete
- lang, use_default_to

**Exemples :**
- Email facture avec PDF attaché
- Email devis avec PDF
- Email bon de livraison

---

## 5️⃣ Ordre de Migration

```
1. report.paperformat         # Formats d'abord
2. ir.actions.report          # Puis les rapports
3. mail.template              # Puis les templates email
4. ir.attachment              # Pièces jointes liées
```

**Tous configurés dans le framework avec le bon ordre ! ✅**

---

## 🔍 Vérification Après Migration

### Compter les Rapports

```python
from connexion_double_v19 import ConnexionDoubleV19

conn = ConnexionDoubleV19()
conn.connecter_tout()

# Formats
formats = conn.executer_destination('report.paperformat', 'search_count', [])
print(f'Formats de papier: {formats}')

# Rapports
rapports = conn.executer_destination('ir.actions.report', 'search_count', [])
print(f'Rapports PDF: {rapports}')

# Templates email
templates = conn.executer_destination('mail.template', 'search_count', [])
print(f'Templates email: {templates}')
```

### Tester un Rapport

1. Aller dans Odoo v19
2. Ouvrir une facture
3. Cliquer "Imprimer"
4. Vérifier que le PDF se génère correctement
5. Vérifier le format (marges, logo, etc.)

---

## ⚠️ Attention

### Rapports Personnalisés avec QWeb

Si vous avez des rapports **très personnalisés** avec du code QWeb complexe :
- Le template sera migré
- **MAIS** il faudra vérifier la compatibilité v19
- Possibles ajustements de syntaxe QWeb

### Rapports Studio

Les rapports créés avec **Odoo Studio** seront migrés automatiquement avec les modules Studio.

---

## 🎯 Pour Migrer Maintenant

Le framework migrera automatiquement ces modules :

```bash
# Dans terminal externe
python migration_framework.py
```

Le framework :
1. ✅ Migrera report.paperformat (ordre 910)
2. ✅ Migrera ir.actions.report (ordre 915)
3. ✅ Migrera mail.template (ordre 920)
4. ✅ Avec TOUS les champs
5. ✅ Avec toutes les relations mappées

---

## 📊 Modules d'Impression dans la Source

Pour compter combien vous avez :

```bash
python compter_modules.py
```

Cherchez :
- `report.paperformat`
- `ir.actions.report`
- `mail.template`

---

## ✅ Inclus dans le Framework

Tous ces modules sont **déjà configurés** dans le framework.

Quand vous lancez `migration_framework.py`, ils seront migrés automatiquement ! 🚀

---

**Les rapports PDF sont couverts à 100% ! ✅**

