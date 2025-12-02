# 🚀 Guide de Déploiement sur PythonAnywhere

## Étape 1 : Préparation (Sur votre PC)

### 1.1 Créer un fichier .gitignore (si pas déjà fait)

Le fichier `.gitignore` existe déjà, mais vérifiez qu'il contient bien :
```
__pycache__/
*.pyc
logs/
*.log
config_prod.py
*.secret
```

### 1.2 Créer un repository Git (optionnel mais recommandé)

```bash
# Dans le dossier migration_lysa_v19
git init
git add .
git commit -m "Initial commit - Migration LYSA v19"
```

Ou utilisez GitHub/GitLab pour plus de facilité.

---

## Étape 2 : Connexion à PythonAnywhere

### 2.1 Accéder à la console

1. Connectez-vous sur [www.pythonanywhere.com](https://www.pythonanywhere.com)
2. Cliquez sur **"Consoles"** → **"Bash"**

### 2.2 Configuration initiale

Dans la console Bash :

```bash
# Vérifier la version Python
python3.11 --version

# Créer un virtualenv
mkvirtualenv migration_lysa --python=python3.11

# Le virtualenv devrait s'activer automatiquement
# Vous verrez : (migration_lysa) username@pythonanywhere.com:~$
```

---

## Étape 3 : Upload des Fichiers

### Option A : Via Git (Recommandé si vous avez un repo)

```bash
# Cloner votre repository
git clone <URL-DE-VOTRE-REPO> migration_lysa_v19
cd migration_lysa_v19
```

### Option B : Upload Manuel

1. Allez dans **"Files"** sur PythonAnywhere
2. Créez un dossier `migration_lysa_v19`
3. Uploadez tous vos fichiers via l'interface web
4. OU utilisez le script que j'ai créé (voir section suivante)

### Option C : Via le script d'upload automatique

J'ai créé un script `upload_to_pythonanywhere.py` (voir ci-dessous).

---

## Étape 4 : Installation des Dépendances

Dans la console Bash PythonAnywhere :

```bash
# Activer le virtualenv (si pas déjà activé)
workon migration_lysa

# Aller dans le dossier
cd ~/migration_lysa_v19

# Installer les dépendances
pip install -r requirements.txt

# Vérifier l'installation
pip list
```

---

## Étape 5 : Configuration

### 5.1 Vérifier la configuration

Éditez le fichier `config_v19.py` directement sur PythonAnywhere :

```bash
nano config_v19.py
```

Ou via l'interface web : **Files** → `migration_lysa_v19` → `config_v19.py`

### 5.2 Paramètres importants pour PythonAnywhere

```python
# Dans config_v19.py
MIGRATION_PARAMS = {
    'BATCH_SIZE': 50,          # Réduire pour PythonAnywhere
    'PARALLEL_WORKERS': 1,     # 1 seul worker sur compte gratuit
    'TIMEOUT': 900,            # 15 minutes max
    'LOG_TO_FILE': True,       # Garder les logs
}
```

---

## Étape 6 : Test d'Exécution

### 6.1 Test de connexion

```bash
cd ~/migration_lysa_v19
python tests/test_connexion.py
```

### 6.2 Test du debug

```bash
python debug_plan_comptable.py
```

### 6.3 Migration du plan comptable

```bash
python migration_plan_comptable.py
```

---

## Étape 7 : Configuration des Tâches Planifiées

### 7.1 Créer une tâche planifiée

1. Allez dans **"Tasks"** sur PythonAnywhere
2. Section **"Scheduled tasks"**
3. Cliquez sur **"Create a new scheduled task"**

### 7.2 Configuration de la tâche

**Heure** : Choisir quand exécuter (ex: 02:00 UTC)

**Commande** :
```bash
/home/VOTRE_USERNAME/.virtualenvs/migration_lysa/bin/python /home/VOTRE_USERNAME/migration_lysa_v19/run_migration_scheduled.py
```

Remplacez `VOTRE_USERNAME` par votre nom d'utilisateur PythonAnywhere.

### 7.3 Fréquence

- **Daily** : Tous les jours
- **Weekly** : Une fois par semaine
- **Hourly** : Toutes les heures (compte payant uniquement)

---

## Étape 8 : Monitoring et Logs

### 8.1 Voir les logs

```bash
cd ~/migration_lysa_v19/logs
ls -lah
tail -f migration_v19_*.log
```

### 8.2 Vérifier les tâches

```bash
# Voir l'historique des tâches planifiées
# Via l'interface web : Tasks → Task logs
```

### 8.3 Script de monitoring

J'ai créé un script `check_migration_status.py` :

```bash
python check_migration_status.py
```

---

## 🔧 Scripts Utilitaires Fournis

### 1. `run_migration_scheduled.py`
Script wrapper pour les tâches planifiées avec :
- Gestion des erreurs
- Notifications
- Logs structurés

### 2. `upload_to_pythonanywhere.py`
Upload automatique des fichiers via SFTP

### 3. `check_migration_status.py`
Vérification du statut de migration

### 4. `deploy.sh`
Script de déploiement automatique

---

## 📋 Checklist de Déploiement

- [ ] Compte PythonAnywhere créé
- [ ] Virtualenv créé (`migration_lysa`)
- [ ] Fichiers uploadés dans `~/migration_lysa_v19`
- [ ] Dépendances installées (`pip install -r requirements.txt`)
- [ ] Configuration vérifiée (`config_v19.py`)
- [ ] Test de connexion réussi
- [ ] Migration test exécutée manuellement
- [ ] Tâche planifiée créée
- [ ] Logs vérifiés

---

## ⚠️ Limitations PythonAnywhere (Compte Gratuit)

### Limitations :
- **CPU** : Limité à 100 secondes/jour
- **Tâches planifiées** : 1 seule tâche
- **Timeout** : 300 secondes max par script
- **Connexions externes** : Liste blanche uniquement

### Solutions :
1. **Upgrade à $5/mois** (Hacker) pour :
   - Plus de CPU
   - Timeout plus long
   - Connexions illimitées
   
2. **Optimiser les scripts** :
   - Réduire `BATCH_SIZE`
   - Traiter par petits lots
   - Utiliser `MAX_RECORDS` pour limiter

---

## 🆘 Dépannage

### Problème : "ImportError"

```bash
# Vérifier le virtualenv
workon migration_lysa
pip list
pip install -r requirements.txt
```

### Problème : "Permission Denied"

```bash
# Corriger les permissions
chmod +x migration_plan_comptable.py
```

### Problème : "Connection Timeout"

Dans `config_v19.py` :
```python
MIGRATION_PARAMS = {
    'TIMEOUT': 900,  # Augmenter
    'BATCH_SIZE': 20,  # Réduire
}
```

### Problème : "CPU Time Exceeded"

Compte gratuit limité. Solutions :
1. Réduire la charge de travail
2. Upgrade à compte payant
3. Exécuter manuellement en plusieurs fois

---

## 📞 Support

### Logs détaillés
```bash
cd ~/migration_lysa_v19/logs
ls -lah
cat migration_v19_*.log
```

### Erreurs système
Consultez : **Tasks** → **Task logs** sur PythonAnywhere

---

## 🎯 Commandes Rapides

```bash
# Activer l'environnement
workon migration_lysa

# Aller au projet
cd ~/migration_lysa_v19

# Mettre à jour
git pull  # Si vous utilisez Git

# Tester
python tests/test_connexion.py

# Exécuter migration
python migration_plan_comptable.py

# Voir les logs
tail -f logs/migration_v19_*.log

# Statut
python check_migration_status.py
```

---

## 🚀 Prochaines Étapes

Après le déploiement :

1. ✅ Migration du plan comptable
2. ✅ Migration des partenaires
3. ✅ Vérifications post-migration
4. ✅ Configuration monitoring
5. ✅ Alertes email (optionnel)

---

**Auteur** : SENEDOO  
**Date** : 02 Décembre 2025  
**Version** : 1.0.0

