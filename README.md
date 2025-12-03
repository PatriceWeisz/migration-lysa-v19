# 🚀 Migration Odoo v16 → v19 SaaS

**Projet :** Migration LYSA  
**Source :** Odoo v16 (lysa-old1.odoo.com)  
**Destination :** Odoo v19 SaaS (lysa-migration.odoo.com)

---

## 📊 État Actuel

✅ **7,994 enregistrements de base migrés** (voir `ETAT_MIGRATION.md`)

---

## 📁 Structure du Projet

```
migration_lysa_v19/
│
├── README.md                      ← Ce fichier
├── README_MIGRATION.md            ← 📖 Guide d'utilisation détaillé
├── PLAN_MIGRATION_COMPLET.md      ← 📋 Plan complet de migration
├── MIGRATION_TRANSACTIONS.md      ← 📝 Guide Phase 2 (transactions)
├── ETAT_MIGRATION.md              ← 📊 État actuel détaillé
├── NOTES_SAAS.md                  ← ⚙️ Notes spécifiques SaaS
│
├── config_v19.py                  ← Configuration connexions
├── connexion_double_v19.py        ← Module de connexion
├── requirements.txt               ← Dépendances Python
│
├── orchestrateur_migration.py     ← 🎯 SCRIPT PRINCIPAL
│
├── Scripts de migration (modules de base)
│   ├── migrer_taxes.py
│   ├── migrer_etiquettes_contact.py
│   ├── migrer_listes_prix.py
│   ├── migrer_comptes_analytiques.py
│   ├── migrer_equipes_commerciales.py
│   └── migrer_projets.py
│
├── Scripts de construction mappings
│   ├── construire_mapping_comptes.py
│   ├── construire_mapping_partenaires.py
│   └── construire_mapping_produits.py
│
├── Scripts de vérification
│   ├── verifier_mappings_existants.py
│   └── verifier_modules_base.py
│
├── Scripts utilitaires
│   ├── compter_modules.py
│   └── detecter_modules_studio.py
│
├── utils/
│   ├── external_id_manager.py
│   ├── helpers.py
│   └── logger.py
│
└── logs/
    └── *_mapping.json             ← Mappings source_id → dest_id
```

---

## 🚀 Démarrage Rapide

### 1. Lancer la migration complète

```bash
python orchestrateur_migration.py
```

### 2. Ou module par module

```bash
python migrer_taxes.py
python migrer_etiquettes_contact.py
# etc.
```

### 3. Vérifier l'état

```bash
python verifier_mappings_existants.py
python verifier_modules_base.py
```

---

## 📚 Documentation Complète

- **`README_MIGRATION.md`** : Guide complet d'utilisation
- **`PLAN_MIGRATION_COMPLET.md`** : Plan détaillé Phase 1 + Phase 2
- **`MIGRATION_TRANSACTIONS.md`** : Guide pour migrer les transactions
- **`ETAT_MIGRATION.md`** : État actuel et prochaines étapes
- **`NOTES_SAAS.md`** : Spécificités Odoo SaaS

---

## ✅ Modules Déjà Migrés (100%)

- Plan comptable (2,654)
- Partenaires (2,891)
- Produits (2,110)
- Taxes (31)
- Journaux (40)
- Étiquettes contact (16)
- Listes de prix (57)
- Utilisateurs, Employés, Entrepôts...

---

## 🎯 Prochaines Étapes

1. **Compléter modules de base** (équipes commerciales, projets)
2. **Vérification complète** 
3. **Phase 2 : Transactions** (factures, commandes, stock...)

Voir `ETAT_MIGRATION.md` pour le détail.

---

## 🆘 Support

En cas de problème :
1. Lire `README_MIGRATION.md`
2. Consulter `ETAT_MIGRATION.md`
3. Vérifier les logs dans `logs/`

---

**Dernière mise à jour :** 3 décembre 2025

