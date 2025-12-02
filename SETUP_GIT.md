# 🔧 Setup Git - Migration LYSA v19

## Configuration GitHub pour PatriceWeisz

---

## Étape 1 : Initialisation Git (Sur votre PC)

Ouvrez PowerShell ou Terminal dans le dossier du projet :

```powershell
# Aller dans le dossier du projet
cd "g:\Mon Drive\SENEDOO\CURSOR\migration_lysa_v19"

# Initialiser Git (si pas encore fait)
git init

# Configurer votre identité (une seule fois)
git config user.name "PatriceWeisz"
git config user.email "VOTRE_EMAIL@exemple.com"  # À remplacer

# Ajouter tous les fichiers
git add .

# Premier commit
git commit -m "Initial commit - Migration LYSA v19"
```

---

## Étape 2 : Créer le Repository sur GitHub

### Option A : Via l'interface web (Recommandé)

1. Allez sur https://github.com/PatriceWeisz
2. Cliquez sur **"New"** (nouveau repository)
3. Nom du repository : **`migration-lysa-v19`**
4. Description : **"Migration LYSA vers Odoo v19"**
5. Sélectionnez **"Private"** (recommandé pour les données sensibles)
6. **NE PAS** cocher "Initialize with README" (on a déjà des fichiers)
7. Cliquez **"Create repository"**

### Option B : Via GitHub CLI (si installé)

```bash
gh repo create migration-lysa-v19 --private --source=. --remote=origin --push
```

---

## Étape 3 : Lier le Repository Local à GitHub

```powershell
# Ajouter le remote GitHub
git remote add origin https://github.com/PatriceWeisz/migration-lysa-v19.git

# Vérifier
git remote -v

# Pousser vers GitHub
git branch -M main
git push -u origin main
```

**Si demandé, entrez vos identifiants GitHub.**

---

## Étape 4 : Cloner sur PythonAnywhere

### Dans la console Bash PythonAnywhere :

```bash
# Aller dans votre dossier home
cd ~

# Cloner le repository
git clone https://github.com/PatriceWeisz/migration-lysa-v19.git migration_lysa_v19

# Aller dans le dossier
cd migration_lysa_v19

# Lancer le script de déploiement
bash deploy.sh
```

**Note** : Si le repository est privé, GitHub vous demandera vos identifiants ou un Personal Access Token.

---

## Étape 5 : Workflow de Travail

### Quand je modifie des fichiers :

**Sur votre PC :**

```powershell
cd "g:\Mon Drive\SENEDOO\CURSOR\migration_lysa_v19"

# Voir les fichiers modifiés
git status

# Ajouter les modifications
git add .

# Commiter
git commit -m "Modifications du [date] - [description]"

# Pousser vers GitHub
git push
```

**Sur PythonAnywhere :**

```bash
cd ~/migration_lysa_v19

# Récupérer les modifications
git pull

# Relancer le script si nécessaire
python migration_plan_comptable.py
```

---

## 🚀 Commandes Rapides

### Sur PC (après mes modifications)

```powershell
cd "g:\Mon Drive\SENEDOO\CURSOR\migration_lysa_v19"
git add . && git commit -m "MAJ" && git push
```

### Sur PythonAnywhere

```bash
cd ~/migration_lysa_v19 && git pull
```

**C'est tout !** ✨

---

## 🔐 Configuration Token GitHub (Pour Repository Privé)

Si votre repository est privé, vous aurez besoin d'un Personal Access Token.

### Créer un Token :

1. GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Cliquez **"Generate new token"** → **"Generate new token (classic)"**
3. Note : `PythonAnywhere Migration`
4. Expiration : **90 days** (ou plus)
5. Scopes : Cochez **`repo`** (full control)
6. Cliquez **"Generate token"**
7. **COPIEZ LE TOKEN** (vous ne le verrez qu'une fois)

### Utiliser le Token sur PythonAnywhere :

```bash
# Au lieu de votre mot de passe, utilisez le token
git clone https://github.com/PatriceWeisz/migration-lysa-v19.git

# Quand demandé :
# Username: PatriceWeisz
# Password: [COLLEZ VOTRE TOKEN ICI]
```

### Sauvegarder les identifiants (optionnel) :

```bash
# Pour ne pas redemander à chaque fois
git config --global credential.helper store

# Puis faire un git pull
git pull
# Entrez vos identifiants une fois, ils seront sauvegardés
```

---

## 📋 Checklist Setup

- [ ] Git initialisé sur PC
- [ ] Repository créé sur GitHub
- [ ] Premier push effectué
- [ ] Repository cloné sur PythonAnywhere
- [ ] Script `deploy.sh` exécuté
- [ ] Test `git pull` réussi
- [ ] Workflow compris

---

## 🆘 Résolution de Problèmes

### Erreur : "remote origin already exists"

```powershell
git remote remove origin
git remote add origin https://github.com/PatriceWeisz/migration-lysa-v19.git
```

### Erreur : "Authentication failed"

- Vérifiez votre mot de passe GitHub
- Ou utilisez un Personal Access Token (voir section ci-dessus)

### Erreur : "Permission denied"

```bash
# Sur PythonAnywhere
chmod +x deploy.sh
bash deploy.sh
```

### Conflits lors du pull

```bash
# Sauvegarder vos modifications locales
git stash

# Récupérer les changements
git pull

# Réappliquer vos modifications
git stash pop
```

---

## 🎯 Commandes Git Essentielles

| Commande | Description |
|----------|-------------|
| `git status` | Voir les fichiers modifiés |
| `git add .` | Ajouter tous les changements |
| `git commit -m "message"` | Créer un commit |
| `git push` | Envoyer vers GitHub |
| `git pull` | Récupérer de GitHub |
| `git log --oneline` | Voir l'historique |
| `git diff` | Voir les différences |

---

## 📞 Support

Si vous rencontrez un problème, envoyez-moi :
1. La commande que vous avez exécutée
2. Le message d'erreur complet
3. Sur quel système (PC ou PythonAnywhere)

Je vous aiderai immédiatement ! 🚀

---

**Repository GitHub** : https://github.com/PatriceWeisz/migration-lysa-v19  
**Auteur** : SENEDOO  
**Date** : 02 Décembre 2025

