# Structure du Projet Migration LYSA v19

## 📁 Arborescence complète

```
migration_lysa_v19/
│
├── 📄 README.md                    # Documentation principale complète
├── 📄 QUICKSTART.md                # Guide de démarrage rapide
├── 📄 CHANGELOG.md                 # Journal des modifications
├── 📄 STRUCTURE.md                 # Ce fichier (structure du projet)
├── 📄 requirements.txt             # Dépendances Python
├── 📄 .gitignore                   # Fichiers à ignorer par Git
│
├── ⚙️  config_v19.py                # Configuration centrale
│
├── 🔌 connexion_double_v19.py      # Gestion des connexions
│
├── 🚀 migration_complete.py        # Orchestrateur principal
├── 👥 migration_partenaires.py     # Migration des partenaires
├── ✅ verification_v19.py          # Vérifications post-migration
│
├── 📂 utils/                       # Utilitaires
│   ├── __init__.py
│   ├── logger.py                   # Système de logging
│   └── helpers.py                  # Fonctions helper
│
├── 📂 tests/                       # Tests
│   ├── __init__.py
│   └── test_connexion.py           # Tests de connexion
│
└── 📂 logs/                        # Logs (générés automatiquement)
    └── .gitkeep
```

## 📋 Description des fichiers

### 📄 Documentation

| Fichier | Description |
|---------|-------------|
| `README.md` | Documentation complète du projet avec tous les détails |
| `QUICKSTART.md` | Guide rapide pour démarrer en 5 minutes |
| `ORDRE_MIGRATION.md` | **Ordre obligatoire de migration** (IMPORTANT) |
| `NOTES_SAAS.md` | Notes spécifiques pour base SaaS |
| `CHANGELOG.md` | Historique des versions et modifications |
| `STRUCTURE.md` | Ce fichier - structure du projet |

### ⚙️ Configuration

| Fichier | Description |
|---------|-------------|
| `config_v19.py` | Configuration centralisée :<br>- URLs des bases<br>- Paramètres de migration<br>- Mapping des modèles<br>- Filtres de données |
| `requirements.txt` | Liste des dépendances Python à installer |
| `.gitignore` | Fichiers à exclure du versioning |

### 🔌 Connexion

| Fichier | Description |
|---------|-------------|
| `connexion_double_v19.py` | Gestion des connexions :<br>- Connexion source et destination<br>- Reconnexion automatique<br>- Retry en cas d'erreur<br>- Statistiques de connexion |

### 🚀 Scripts de migration

| Fichier | Description | Status |
|---------|-------------|--------|
| `migration_complete.py` | Orchestrateur principal de la migration | ✅ Complet |
| `migration_plan_comptable.py` | Migration du plan comptable (EN PREMIER) | ✅ Complet |
| `migration_partenaires.py` | Migration des clients/fournisseurs | ✅ Complet |
| `migration_factures.py` | Migration des factures | ⏳ À créer |
| `migration_produits.py` | Migration des produits | ⏳ À créer |

### ✅ Vérification

| Fichier | Description |
|---------|-------------|
| `verification_v19.py` | Vérifications post-migration :<br>- Comptages<br>- Intégrité des données<br>- Soldes comptables<br>- Rapport détaillé |

### 🛠️ Utilitaires (utils/)

| Fichier | Description |
|---------|-------------|
| `logger.py` | Système de logging :<br>- Logs colorés console<br>- Logs fichiers<br>- Niveaux configurables |
| `helpers.py` | Fonctions utilitaires :<br>- Formatage<br>- Progress tracking<br>- Découpage en lots<br>- Validation |

### 🧪 Tests (tests/)

| Fichier | Description |
|---------|-------------|
| `test_connexion.py` | Tests de connexion :<br>- Test source<br>- Test destination<br>- Test version v19<br>- Test comptages |

## 🔄 Flux d'exécution

```
┌─────────────────────────────────────────────┐
│         MIGRATION COMPLÈTE v19              │
└─────────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  1. Vérification       │
        │     Prérequis          │
        └────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  2. Connexion          │
        │     Source + Dest      │
        └────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  3. Plan comptable     │
        │     (à implémenter)    │
        └────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  4. Journaux           │
        │     (à implémenter)    │
        └────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  5. Partenaires        │
        │     ✅ Implémenté       │
        └────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  6. Produits           │
        │     (à implémenter)    │
        └────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  7. Factures           │
        │     (à implémenter)    │
        └────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  8. Vérification       │
        │     finale             │
        └────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │  9. Rapport            │
        │     final              │
        └────────────────────────┘
```

## 🎯 Points d'entrée

### Pour démarrer rapidement

1. **Test de connexion** (recommandé en premier)
   ```bash
   python tests/test_connexion.py
   ```

2. **Connexion simple**
   ```bash
   python connexion_double_v19.py
   ```

3. **Migration des partenaires**
   ```bash
   python migration_partenaires.py
   ```

4. **Vérification**
   ```bash
   python verification_v19.py
   ```

5. **Migration complète** (orchestrateur)
   ```bash
   python migration_complete.py
   ```

## 📊 Dépendances

```
Python 3.8+
├── xmlrpc.client (stdlib)
├── pandas
├── openpyxl
├── colorlog
├── tqdm
├── pytest
├── pydantic
└── python-dateutil
```

## 🔐 Fichiers sensibles (ignorés par Git)

- `config_prod.py` - Configuration production
- `*.secret` - Fichiers secrets
- `logs/*.log` - Fichiers de logs
- `*.xlsx`, `*.csv` - Rapports générés
- `__pycache__/` - Cache Python

## 📈 Statistiques du projet

- **Fichiers Python** : 10+
- **Lignes de code** : ~2500+
- **Documentation** : 4 fichiers MD
- **Tests** : 7 tests unitaires
- **Fonctions utilitaires** : 20+

## 🚦 Status des modules

| Module | Status | Priorité | Ordre |
|--------|--------|----------|-------|
| Configuration | ✅ Complet | ⭐⭐⭐ | - |
| Connexion | ✅ Complet | ⭐⭐⭐ | - |
| Logging | ✅ Complet | ⭐⭐⭐ | - |
| Helpers | ✅ Complet | ⭐⭐⭐ | - |
| Tests connexion | ✅ Complet | ⭐⭐⭐ | - |
| **Migration plan comptable** | ✅ **Complet** | ⭐⭐⭐ | **1️⃣** |
| Migration partenaires | ✅ Complet | ⭐⭐⭐ | 2️⃣ |
| Vérification | ✅ Complet | ⭐⭐⭐ | - |
| Orchestrateur | ✅ Complet | ⭐⭐⭐ | - |
| Migration journaux | ⏳ À faire | ⭐⭐ | 3️⃣ |
| Migration produits | ⏳ À faire | ⭐⭐ | 4️⃣ |
| Migration factures | ⏳ À faire | ⭐⭐⭐ | 5️⃣ |

## 🎨 Conventions de code

- **Encodage** : UTF-8
- **Style** : PEP 8
- **Docstrings** : Google style
- **Langue** : Français (commentaires et logs)
- **Nommage** : snake_case pour les fonctions/variables

## 📞 Support

Pour toute question :
- Consulter la documentation complète dans `README.md`
- Vérifier les logs dans `logs/`
- Contacter SENEDOO

---

**Version** : 1.0.0  
**Date** : 02 Décembre 2025  
**Auteur** : SENEDOO

