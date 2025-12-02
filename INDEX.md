# 📑 INDEX - Migration LYSA v19

## 🚀 Démarrage Rapide

**Nouveau sur ce projet ?** Commencez ici :

1. 📖 **[QUICKSTART.md](QUICKSTART.md)** - Guide de démarrage rapide (5 min)
2. 📚 **[README.md](README.md)** - Documentation complète
3. 🏗️ **[STRUCTURE.md](STRUCTURE.md)** - Architecture du projet

## 📁 Navigation du Projet

### 🎯 Par Objectif

**Je veux tester la connexion**
→ `python tests/test_connexion.py`

**Je veux migrer le plan comptable** (en premier !)
→ `python migration_plan_comptable.py`

**Je veux migrer les partenaires**
→ `python migration_partenaires.py`

**Je veux vérifier la migration**
→ `python verification_v19.py`

**Je veux tout migrer**
→ `python migration_complete.py`

### 📚 Documentation

| Document | Contenu | Pour qui ? |
|----------|---------|------------|
| [README.md](README.md) | Documentation complète | Tous |
| [QUICKSTART.md](QUICKSTART.md) | Démarrage rapide | Débutants |
| [STRUCTURE.md](STRUCTURE.md) | Architecture | Développeurs |
| [CHANGELOG.md](CHANGELOG.md) | Historique | Tous |
| [INDEX.md](INDEX.md) | Ce fichier | Tous |

### 🔧 Configuration

| Fichier | Usage |
|---------|-------|
| [config_v19.py](config_v19.py) | Configuration principale |
| [requirements.txt](requirements.txt) | Dépendances Python |

### 💻 Scripts Principaux

| Script | Description | Status |
|--------|-------------|--------|
| [connexion_double_v19.py](connexion_double_v19.py) | Connexion aux bases | ✅ |
| [migration_complete.py](migration_complete.py) | Orchestrateur | ✅ |
| [migration_plan_comptable.py](migration_plan_comptable.py) | Migration plan comptable | ✅ |
| [migration_partenaires.py](migration_partenaires.py) | Migration partenaires | ✅ |
| [verification_v19.py](verification_v19.py) | Vérifications | ✅ |

### 🛠️ Utilitaires

| Module | Fichier |
|--------|---------|
| Logging | [utils/logger.py](utils/logger.py) |
| Helpers | [utils/helpers.py](utils/helpers.py) |

### 🧪 Tests

| Test | Fichier |
|------|---------|
| Connexion | [tests/test_connexion.py](tests/test_connexion.py) |

## 🎓 Tutoriels

### Tutoriel 1 : Premier test (5 min)

```bash
# 1. Installation
pip install -r requirements.txt

# 2. Test de connexion
python tests/test_connexion.py
```

### Tutoriel 2 : Migration basique (20 min)

```bash
# 1. Configurer (éditer config_v19.py)
# 2. Tester la connexion
python connexion_double_v19.py

# 3. Migrer le plan comptable (EN PREMIER!)
python migration_plan_comptable.py

# 4. Migrer les partenaires
python migration_partenaires.py

# 5. Vérifier
python verification_v19.py
```

### Tutoriel 3 : Migration complète

```bash
# Lancer l'orchestrateur complet
python migration_complete.py
```

## 📊 Checklist de Migration

### Avant de commencer

- [ ] Python 3.8+ installé
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Configuration vérifiée dans `config_v19.py`
- [ ] Accès aux deux bases Odoo confirmé
- [ ] Sauvegarde effectuée

### Étape 1 : Tests

- [ ] Test de connexion réussi
- [ ] Version v19 confirmée
- [ ] Comptages initiaux notés

### Étape 2 : Migration

- [ ] Migration du plan comptable (OBLIGATOIRE EN PREMIER)
- [ ] Migration des partenaires
- [ ] Migration des produits (si applicable)
- [ ] Migration des factures (si applicable)

### Étape 3 : Vérification

- [ ] Vérification post-migration exécutée
- [ ] Comptages vérifiés
- [ ] Tests manuels effectués
- [ ] Logs consultés

### Étape 4 : Finalisation

- [ ] Documentation des problèmes
- [ ] Rapport final généré
- [ ] Backup post-migration effectué

## 🆘 En cas de problème

### Erreur de connexion
1. Vérifier `config_v19.py`
2. Tester l'accès web à https://lysa-migration.odoo.com/
3. Vérifier les identifiants
4. Consulter [NOTES_SAAS.md](NOTES_SAAS.md) pour spécificités SaaS

### Erreur de migration
1. Consulter `logs/*.log`
2. Activer le mode simulation
3. Réduire le batch size (SaaS = 50-100)
4. Voir [NOTES_SAAS.md](NOTES_SAAS.md)

### Performance lente
1. Réduire `PARALLEL_WORKERS` (SaaS = 1-2)
2. Augmenter `TIMEOUT` (SaaS = 600-900)
3. Vérifier la connexion réseau
4. Consulter limites API SaaS

## 📞 Ressources

### Liens utiles

- **Documentation Odoo v19** : [odoo.com/documentation](https://www.odoo.com/documentation)
- **Python XML-RPC** : [docs.python.org/3/library/xmlrpc](https://docs.python.org/3/library/xmlrpc.html)

### Support SENEDOO

- **Email** : support@senedoo.com
- **Logs** : Dossier `logs/`

## 🗺️ Roadmap

### Version 1.0.0 (Actuelle) ✅
- [x] Infrastructure de base
- [x] Connexion double
- [x] Migration partenaires
- [x] Vérifications

### Version 1.1.0 (Prochaine)
- [ ] Migration plan comptable
- [ ] Migration journaux
- [ ] Optimisations

### Version 1.2.0
- [ ] Migration produits
- [ ] Migration factures
- [ ] Rapports avancés

### Version 2.0.0
- [ ] Interface graphique
- [ ] API REST
- [ ] Automatisation complète

## 📈 Statistiques

**Projet créé** : 02 Décembre 2025  
**Version actuelle** : 1.0.0  
**Fichiers Python** : 10+  
**Lignes de code** : 2500+  
**Documentation** : 5 fichiers  
**Tests** : 7 tests

## 🎯 Commandes Rapides

```bash
# Tests
python tests/test_connexion.py

# Connexion
python connexion_double_v19.py

# Migration (dans l'ordre!)
python migration_plan_comptable.py  # En premier
python migration_partenaires.py
python migration_complete.py

# Vérification
python verification_v19.py

# Logs
ls logs/  # Voir les logs
```

## 📝 Notes Importantes

⚠️ **Toujours faire une sauvegarde avant migration**

⚠️ **Tester avec MODE_SIMULATION = True d'abord**

⚠️ **Consulter les logs après chaque opération**

⚠️ **Vérifier la version v19 avant de commencer**

---

**Besoin d'aide ?** Consultez d'abord le [QUICKSTART.md](QUICKSTART.md) ou le [README.md](README.md)

**Auteur** : SENEDOO  
**Date** : 02 Décembre 2025  
**Version** : 1.0.0

