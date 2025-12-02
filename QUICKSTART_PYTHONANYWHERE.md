# ⚡ Démarrage Rapide - PythonAnywhere

## 🚀 En 5 Minutes

### Étape 1 : Upload des Fichiers (2 min)

**Option A : Via l'interface web**
1. Sur PythonAnywhere : **Files** → **Upload a file**
2. Créer le dossier `migration_lysa_v19`
3. Uploader TOUS les fichiers du projet

**Option B : Via Git (recommandé)**
```bash
# Dans la console Bash PythonAnywhere
git clone VOTRE_URL_GIT migration_lysa_v19
```

---

### Étape 2 : Configuration (2 min)

```bash
# Console Bash PythonAnywhere

# 1. Créer virtualenv
mkvirtualenv migration_lysa --python=python3.11

# 2. Aller au projet
cd ~/migration_lysa_v19

# 3. Lancer le script d'installation
bash deploy.sh
```

Le script `deploy.sh` va :
- ✅ Vérifier le virtualenv
- ✅ Installer les dépendances
- ✅ Créer les dossiers nécessaires
- ✅ Configurer les permissions
- ✅ Tester la connexion

---

### Étape 3 : Premier Test (1 min)

```bash
# Activer l'environnement
workon migration_lysa

# Aller au projet
cd ~/migration_lysa_v19

# Tester la connexion
python tests/test_connexion.py
```

**Résultat attendu :**
```
✓ Connexion SOURCE réussie
✓ Connexion DESTINATION réussie
✓ Version v19 confirmée
```

---

## 🎯 Commandes Essentielles

### Exécution Manuelle

```bash
# 1. Activer l'environnement
workon migration_lysa

# 2. Aller au projet
cd ~/migration_lysa_v19

# 3. Migrer le plan comptable
python migration_plan_comptable.py

# 4. Migrer les partenaires
python migration_partenaires.py

# 5. Vérifier
python verification_v19.py

# 6. Voir le statut
python check_migration_status.py
```

### Tâche Planifiée

**Configurer sur PythonAnywhere :**

1. **Tasks** → **Scheduled tasks** → **Create a new scheduled task**

2. **Heure** : `02:00` (2h du matin UTC)

3. **Commande** :
```bash
/home/VOTRE_USERNAME/.virtualenvs/migration_lysa/bin/python /home/VOTRE_USERNAME/migration_lysa_v19/run_migration_scheduled.py
```

Remplacez `VOTRE_USERNAME` par votre nom d'utilisateur.

---

## 📊 Monitoring

### Voir les Logs

```bash
# Console Bash
cd ~/migration_lysa_v19/logs

# Lister les logs
ls -lah

# Voir le dernier log
tail -50 $(ls -t *.log | head -1)

# Suivre en temps réel
tail -f migration_v19_*.log
```

### Vérifier le Statut

```bash
cd ~/migration_lysa_v19
python check_migration_status.py
```

---

## ⚙️ Configuration

### Optimiser pour PythonAnywhere

Éditez `config_v19.py` via **Files** ou `nano` :

```python
MIGRATION_PARAMS = {
    # Optimisé pour PythonAnywhere
    'BATCH_SIZE': 50,          # Réduire pour compte gratuit
    'PARALLEL_WORKERS': 1,     # 1 seul worker
    'TIMEOUT': 900,            # 15 minutes
    'LOG_TO_FILE': True,       # Garder les logs
    'MODE_SIMULATION': False,  # False pour migrer vraiment
}
```

---

## 🆘 Problèmes Courants

### Erreur : "No module named 'xxx'"

```bash
workon migration_lysa
pip install -r requirements.txt
```

### Erreur : "Permission denied"

```bash
chmod +x migration_plan_comptable.py
chmod +x *.py
```

### CPU Time Exceeded (compte gratuit)

Solutions :
1. Réduire `BATCH_SIZE` à 20-30
2. Utiliser `MAX_RECORDS` pour limiter
3. Upgrade à compte Hacker ($5/mois)

---

## 📞 Support

### Fichiers Utiles

| Fichier | Description |
|---------|-------------|
| `deploy.sh` | Installation automatique |
| `run_migration_scheduled.py` | Pour tâches planifiées |
| `check_migration_status.py` | Vérifier l'état |
| `DEPLOIEMENT_PYTHONANYWHERE.md` | Guide complet |

### Logs

```bash
cd ~/migration_lysa_v19/logs
ls -lah
cat scheduled_tasks.log
```

---

## ✅ Checklist

- [ ] Compte PythonAnywhere créé
- [ ] Fichiers uploadés
- [ ] `deploy.sh` exécuté
- [ ] Test de connexion OK
- [ ] Migration test réussie
- [ ] Tâche planifiée configurée
- [ ] Monitoring en place

---

**Tout est prêt ? Lancez la migration !** 🚀

```bash
workon migration_lysa
cd ~/migration_lysa_v19
python migration_plan_comptable.py
```

---

**Besoin d'aide ?** Consultez `DEPLOIEMENT_PYTHONANYWHERE.md` pour le guide complet.

