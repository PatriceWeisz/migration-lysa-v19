# 🌙 MIGRATION COMPLETE DURANT LA NUIT

## 📋 Script de Migration Complète

Le script `migration_nuit.py` migre TOUS les modules dans l'ordre avec gestion des external_id.

---

## 🚀 Lancement sur PythonAnywhere

### 1️⃣ Se connecter et synchroniser

```bash
cd ~/migration_lysa_v19
git pull
workon migration_lysa
```

### 2️⃣ Lancer la migration en arrière-plan avec nohup

```bash
nohup python -u migration_nuit.py > logs/migration_nuit_$(date +%Y%m%d_%H%M%S).log 2>&1 &
```

**Cette commande va :**
- Lancer le script en arrière-plan
- Sauvegarder TOUTE la sortie dans un fichier log
- Continuer même si vous fermez le terminal
- Retourner immédiatement le contrôle

### 3️⃣ Noter le numéro de processus

```bash
echo $!  # Affiche le PID du processus
ps aux | grep migration_nuit  # Voir si ça tourne
```

### 4️⃣ Surveiller la progression

```bash
# Voir les dernières lignes du log
tail -f logs/migration_nuit_*.log

# Appuyer sur Ctrl+C pour arrêter le suivi (le script continue)
```

---

## 📊 Modules Migrés

Le script migre dans cet ordre :

1. **Plan Comptable** (account.account) - ~2,654 comptes
2. **Partenaires** (res.partner) - ~2,890 partenaires  
3. **Journaux** (account.journal) - ~40 journaux
4. **Départements RH** (hr.department)
5. **Postes/Fonctions** (hr.job)
6. **Employés** (hr.employee)
7. **Entrepôts** (stock.warehouse)
8. **Catégories Produits** (product.category)
9. **Produits** (product.template) - ~2,080 produits

---

## ⏱️ Durée Estimée

- **Plan Comptable** : ~15-20 min
- **Partenaires** : ~20-25 min
- **Journaux** : ~2-3 min
- **Modules RH** : ~5 min
- **Produits** : ~15-20 min

**TOTAL ESTIMÉ : 1h - 1h30**

---

## 🔍 Vérifier si le script tourne

```bash
# Liste des processus Python
ps aux | grep python

# Surveiller le log en temps réel
tail -f logs/migration_nuit_*.log

# Voir les dernières 50 lignes
tail -50 logs/migration_nuit_*.log
```

---

## 🛑 Arrêter le script (si nécessaire)

```bash
# Trouver le PID
ps aux | grep migration_nuit

# Arrêter proprement
kill PID_NUMBER

# Forcer l'arrêt si nécessaire
kill -9 PID_NUMBER
```

---

## ✅ Vérifier les Résultats

### Après la migration, vérifier :

```bash
# Voir le résumé final
tail -100 logs/migration_nuit_*.log

# Vérifier les mappings générés
ls -lh logs/*_mapping.json

# Compter les enregistrements
wc -l logs/*_mapping.json
```

### Fichiers de mapping générés :

- `logs/account_account_mapping.json` - Comptes comptables
- `logs/res_partner_mapping.json` - Partenaires
- `logs/account_journal_mapping.json` - Journaux
- `logs/hr_department_mapping.json` - Départements
- `logs/hr_job_mapping.json` - Postes
- `logs/hr_employee_mapping.json` - Employés
- `logs/stock_warehouse_mapping.json` - Entrepôts
- `logs/product_category_mapping.json` - Catégories produits
- `logs/product_template_mapping.json` - Produits

---

## 📱 Commandes Rapides

### Lancer et détacher immédiatement

```bash
cd ~/migration_lysa_v19 && git pull && workon migration_lysa && nohup python -u migration_nuit.py > logs/migration_$(date +%Y%m%d_%H%M%S).log 2>&1 &
```

### Surveiller

```bash
watch -n 10 'tail -20 logs/migration_nuit_*.log'
```

### Statistiques en temps réel

```bash
watch -n 30 'grep -E "OK|ERREUR|TERMINE" logs/migration_nuit_*.log | tail -20'
```

---

## ⚠️ Points d'Attention

1. **Ne PAS fermer le terminal** pendant 2-3 min après le lancement (laisser le processus bien démarrer)

2. **Vérifier que ça démarre** :
   ```bash
   sleep 30 && tail -50 logs/migration_nuit_*.log
   ```

3. **En cas d'erreur** : Le script continue sur les autres modules

4. **External_id** : Tous les external_id source sont copiés automatiquement

---

## 🎯 Après la Migration

Lancer les scripts de vérification :

```bash
python verifier_codes_journaux.py
python verifier_produits.py
python verifier_employes.py
```

---

## 📞 En Cas de Problème

Le script crée un log détaillé dans `logs/migration_nuit_YYYYMMDD_HHMMSS.log`

Envoyez ce fichier pour diagnostic.

