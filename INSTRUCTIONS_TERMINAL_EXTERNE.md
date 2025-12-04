# 🖥️ INSTRUCTIONS TERMINAL EXTERNE

## Problème Terminal Cursor

Le terminal PowerShell de Cursor bufferise toute la sortie jusqu'à la fin du script.
Pour voir l'affichage en temps réel, utiliser un terminal externe.

---

## Solution : CMD Windows

### Étape 1 : Ouvrir CMD

1. Appuyez sur `Win + R`
2. Tapez `cmd`
3. Appuyez sur `Entrée`

### Étape 2 : Naviguer vers le Projet

```cmd
cd /d "G:\Mon Drive\SENEDOO\CURSOR\migration_lysa_v19"
```

### Étape 3 : Lancer les Scripts

#### Test de connexion
```cmd
python test_connexion.py
```

#### Inventaire complet
```cmd
python inventaire_complet.py
```

#### Test du framework
```cmd
python migration_framework.py
```

#### Migration d'un module spécifique
```cmd
python migrer_utilisateurs.py
python migrer_projets.py
python migrer_equipes_commerciales.py
```

---

## Vérifier les Résultats

```cmd
python verifier_mappings_existants.py
```

---

## Sauvegarder sur GitHub

```cmd
git add -A
git commit -m "Framework complet créé"
git push
```

---

## 💡 Astuce

Pour voir la sortie en continu ET la sauvegarder :

```cmd
python inventaire_complet.py 2>&1 | tee logs\inventaire.log
```

(Nécessite d'avoir `tee` installé ou utilisez PowerShell externe au lieu de CMD)

---

## Alternative : PowerShell Externe

Si vous préférez PowerShell :

1. `Win + R`
2. Tapez `powershell`
3. Naviguez : `cd "G:\Mon Drive\SENEDOO\CURSOR\migration_lysa_v19"`
4. Lancez avec Tee-Object :

```powershell
python inventaire_complet.py 2>&1 | Tee-Object logs\inventaire.log
```

---

## Fichiers à Tester en Priorité

1. ✅ `test_connexion.py` - Test rapide (10s)
2. ✅ `inventaire_complet.py` - Inventaire (~5min)
3. ✅ `migration_framework.py` - Migration complète (~30min)

---

**Tout est prêt pour continuer dans un terminal externe ! 🚀**

