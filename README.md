# Projet Migration LYSA v19

## Description
Projet de migration des données vers Odoo v19 :
- **Base SOURCE** : lysa-old1 (ancienne base)
- **Base DESTINATION** : lysa-v19 (nouvelle base Odoo 19)

## Nouveautés Odoo v19

Odoo v19 apporte plusieurs changements importants :
- Nouveau moteur comptable optimisé
- Amélioration des performances sur les écritures comptables
- Nouvelles API REST en complément de XML-RPC
- Gestion améliorée des séquences
- Optimisation des règles de validation

## Structure du projet

```
migration_lysa_v19/
├── config_v19.py              # Configuration des bases v19
├── connexion_double_v19.py    # Gestion connexions doubles
├── migration_comptable.py     # Migration des données comptables
├── migration_factures.py      # Migration spécifique factures
├── migration_partenaires.py   # Migration des partenaires
├── verification_v19.py        # Vérifications post-migration
├── utils/
│   ├── __init__.py
│   ├── logger.py             # Système de logs
│   └── helpers.py            # Fonctions utilitaires
├── tests/
│   ├── __init__.py
│   ├── test_connexion.py
│   └── test_migration.py
├── README.md
└── requirements.txt
```

## Configuration

### Bases configurées :

**Base SOURCE :**
- URL: https://lysa-old1.odoo.com/
- DB: lysa-old1-lysa-db-25736325
- User: support@senedoo.com

**Base DESTINATION (v19) :**
- URL: https://lysa-migration.odoo.com/
- DB: lysa-migration (Base SaaS Odoo)
- User: support@senedoo.com

## Installation

```bash
cd migration_lysa_v19
pip install -r requirements.txt
```

## Utilisation

### 1. Test de connexion

```bash
python tests/test_connexion.py
```

### 2. Migration du plan comptable (OBLIGATOIRE EN PREMIER)

```bash
python migration_plan_comptable.py
```

⚠️ **Important** : Le plan comptable doit être migré en premier car les partenaires et factures y font référence.

### 3. Migration des partenaires

```bash
python migration_partenaires.py
```

### 4. Migration des factures

```bash
python migration_factures.py
```

### 5. Vérification post-migration

```bash
python verification_v19.py
```

## Fonctionnalités

### Classe ConnexionDoubleV19

Gestion avancée des connexions avec :
- Reconnexion automatique
- Pool de connexions
- Gestion des erreurs améliorée
- Support API REST et XML-RPC

### Système de logs

Tous les scripts génèrent des logs détaillés dans `logs/` :
- Logs d'information
- Logs d'erreurs
- Rapports de migration
- Statistiques

### Migration par lots

- Traitement par lots configurable
- Parallélisation des opérations
- Gestion des erreurs par lot
- Reprise sur erreur

## Paramètres de migration

Configurables dans `config_v19.py` :
- `BATCH_SIZE`: 200 (taille des lots)
- `PARALLEL_WORKERS`: 5 (workers parallèles)
- `MAX_RETRY`: 3 (tentatives max)
- `TIMEOUT`: 300 (timeout en secondes)
- `LOG_LEVEL`: 'INFO'

## Checklist de migration

- [ ] Connexion aux deux bases testée
- [ ] Sauvegarde de la base source effectuée
- [ ] Migration du plan comptable
- [ ] Migration des partenaires (clients/fournisseurs)
- [ ] Migration des produits
- [ ] Migration des factures clients
- [ ] Migration des factures fournisseurs
- [ ] Vérification des soldes comptables
- [ ] Vérification des séquences
- [ ] Tests de validation
- [ ] Documentation des anomalies

## Auteur

SENEDOO

## Date

Décembre 2025

## Version

1.0.0 - Migration vers Odoo v19

