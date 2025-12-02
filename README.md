# 🚀 Migration LYSA vers Odoo v19

Projet de migration des données LYSA de l'ancienne base Odoo v16 vers la nouvelle base Odoo v19 SaaS.

## 📋 Description

Migration automatisée comprenant :
- ✅ Plan comptable (2,654 comptes)
- ✅ Partenaires (2,890 clients/fournisseurs)
- ⏳ Produits (2,080 articles)
- ⏳ Factures (130,746 écritures)

## 🎯 Stack Technique

- **Python 3.11+**
- **Odoo v16** (source) → **Odoo v19** (destination)
- **XML-RPC API**
- **Base SaaS** : lysa-migration.odoo.com

## 📦 Installation

### Prérequis

```bash
Python 3.11+
pip (gestionnaire de packages)
```

### Installation Locale

```bash
# Cloner le repository
git clone https://github.com/PatriceWeisz/migration-lysa-v19.git
cd migration-lysa-v19

# Créer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Installer les dépendances
pip install -r requirements.txt
```

### Installation sur PythonAnywhere

```bash
# Cloner le repository
git clone https://github.com/PatriceWeisz/migration-lysa-v19.git migration_lysa_v19
cd migration_lysa_v19

# Lancer le script de déploiement
bash deploy.sh
```

## 🚀 Utilisation

### Tests

```bash
# Test de connexion aux deux bases
python tests/test_connexion.py

# Test du plan comptable
python tests/test_plan_comptable.py
```

### Migration

```bash
# 1. Plan comptable (EN PREMIER)
python migration_plan_comptable.py

# 2. Partenaires
python migration_partenaires.py

# 3. Vérification
python verification_v19.py
```

### Migration Complète

```bash
# Tout en automatique (dans l'ordre correct)
python migration_complete.py
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Guide de démarrage rapide
- **[SETUP_GIT.md](SETUP_GIT.md)** - Configuration Git et GitHub
- **[DEPLOIEMENT_PYTHONANYWHERE.md](DEPLOIEMENT_PYTHONANYWHERE.md)** - Déploiement PythonAnywhere
- **[ORDRE_MIGRATION.md](ORDRE_MIGRATION.md)** - Ordre obligatoire de migration
- **[NOTES_SAAS.md](NOTES_SAAS.md)** - Spécificités bases SaaS

## ⚙️ Configuration

Éditez `config_v19.py` pour configurer :

```python
# Bases Odoo
SOURCE_CONFIG = {...}
DEST_CONFIG_V19 = {...}

# Paramètres de migration
MIGRATION_PARAMS = {
    'BATCH_SIZE': 100,
    'PARALLEL_WORKERS': 2,
    'MODE_SIMULATION': False,
    ...
}
```

## 📊 Fonctionnalités

### Migration du Plan Comptable
- ✅ Mapping automatique des types de comptes v16 → v19
- ✅ Gestion des doublons
- ✅ Génération fichier de mapping JSON
- ✅ Progress tracking en temps réel

### Migration des Partenaires
- ✅ Clients et fournisseurs
- ✅ Détection automatique des doublons
- ✅ Validation des données
- ✅ Statistiques détaillées

### Vérifications
- ✅ Validation version Odoo
- ✅ Vérification des comptages
- ✅ Contrôle d'intégrité
- ✅ Rapport de vérification

## 🔧 Outils Fournis

### Scripts Principaux

| Script | Description |
|--------|-------------|
| `migration_plan_comptable.py` | Migration plan comptable |
| `migration_partenaires.py` | Migration partenaires |
| `verification_v19.py` | Vérifications post-migration |
| `migration_complete.py` | Orchestrateur complet |

### Scripts Utilitaires

| Script | Description |
|--------|-------------|
| `debug_plan_comptable.py` | Debug plan comptable |
| `check_migration_status.py` | Vérifier le statut |
| `run_migration_scheduled.py` | Pour tâches planifiées |
| `deploy.sh` | Déploiement automatique |

## 📁 Structure du Projet

```
migration_lysa_v19/
├── config_v19.py              # Configuration
├── connexion_double_v19.py    # Gestion connexions
├── migration_*.py             # Scripts de migration
├── verification_v19.py        # Vérifications
├── utils/                     # Utilitaires
│   ├── logger.py
│   └── helpers.py
├── tests/                     # Tests unitaires
├── logs/                      # Logs (générés)
└── docs/                      # Documentation
```

## 🔒 Sécurité

- ⚠️ **NE PAS** commiter les mots de passe
- ⚠️ Utiliser des variables d'environnement pour les credentials
- ⚠️ Toujours tester en mode simulation d'abord
- ⚠️ Faire des sauvegardes avant migration

## 📝 Logs

Les logs sont automatiquement générés dans `logs/` :

```bash
# Voir les derniers logs
tail -f logs/migration_v19_*.log

# Vérifier le statut
python check_migration_status.py
```

## 🤝 Contribution

Projet interne SENEDOO.

## 📄 Licence

Usage interne SENEDOO uniquement.

## 👤 Auteur

**SENEDOO**
- GitHub: [@PatriceWeisz](https://github.com/PatriceWeisz)

## 📞 Support

En cas de problème :
1. Consultez la documentation dans les fichiers `.md`
2. Vérifiez les logs dans `logs/`
3. Utilisez les scripts de debug

## 🎯 Roadmap

- [x] Migration plan comptable
- [x] Migration partenaires
- [x] Vérifications post-migration
- [ ] Migration produits
- [ ] Migration factures clients
- [ ] Migration factures fournisseurs
- [ ] Migration paiements

## ⚡ Quick Start

```bash
# Installation
git clone https://github.com/PatriceWeisz/migration-lysa-v19.git
cd migration-lysa-v19
pip install -r requirements.txt

# Configuration
cp config_v19.py config_v19_local.py
# Éditer config_v19_local.py avec vos paramètres

# Test
python tests/test_connexion.py

# Migration
python migration_plan_comptable.py
```

---

**Version** : 1.0.0  
**Date** : Décembre 2025  
**Status** : ✅ Production Ready

