# 🌙 LANCER LA MIGRATION DURANT LA NUIT

## ✅ Script Prêt : `migration_simple.py`

Le script est **testé et fonctionnel**. Il migre 5 modules avec external_id.

---

## 🎯 Avant de Lancer

### 1. Modifier le Mode

Ouvrir `migration_simple.py` et changer :

```python
MODE_TEST = False  # False = MIGRATION COMPLETE
```

⚠️ **C'est déjà à False par défaut** - Prêt pour migration complète !

---

## 🚀 Commandes sur PythonAnywhere

### Synchroniser le Code

```bash
cd ~/migration_lysa_v19
git pull
workon migration_lysa
```

### Lancer la Migration en Arrière-Plan

```bash
nohup python -u migration_simple.py > logs/migration_$(date +%Y%m%d_%H%M%S).log 2>&1 &
```

### Noter le PID

```bash
echo $!
# Vous verrez un numéro comme 12345
```

### Vérifier que ça Tourne

```bash
ps aux | grep migration_simple
```

### Surveiller en Temps Réel

```bash
tail -f logs/migration_*.log
# Appuyer sur Ctrl+C pour arrêter le suivi (le script continue)
```

---

## 📊 Ce qui sera Migré

| Module | Quantité Estimée | Durée Estimée |
|--------|-----------------|---------------|
| 1. Plan Comptable | ~2,654 comptes | 15-20 min |
| 2. Partenaires | ~2,757 partenaires | 20-25 min |
| 3. Journaux | ~40 journaux | 2-3 min |
| 4. Employés | ~100 employés | 3-5 min |
| 5. Produits | ~2,080 produits | 15-20 min |

**DURÉE TOTALE ESTIMÉE : 1h - 1h15**

---

## 🔍 Vérifications Durant la Nuit

### Toutes les 10 minutes

```bash
tail -30 logs/migration_*.log
```

Vous devriez voir :
```
[100/2654] 123456 - Nom du compte
  -> Existe deja (ID: 789)

[200/2654] 234567 - Autre compte
  -> Cree (ID: 790)
```

---

## ✅ Au Matin

### 1. Vérifier que c'est Terminé

```bash
tail -50 logs/migration_*.log
```

Vous devriez voir :
```
======================================================================
MIGRATION TEST TERMINEE
======================================================================
Comptes mappes    : 2654
Partenaires mappes: 2757
Journaux mappes   : 40
Employes mappes   : 100
Produits mappes   : 2080
======================================================================
Fin: 2025-12-03 07:30:00
```

### 2. Vérifier les Mappings

```bash
ls -lh logs/*_mapping.json
wc -l logs/*_mapping.json
```

### 3. Vérifier les External_id Copiés

```bash
grep "External_id copie" logs/migration_*.log | wc -l
```

---

## ⚠️ En Cas de Problème

### Le script s'arrête

```bash
# Relancer depuis où il s'est arrêté
python -u migration_simple.py
```

Le script détecte automatiquement ce qui est déjà migré via les external_id !

### Mémoire insuffisante

Modifier `migration_simple.py` :
```python
TEST_LIMIT_PAR_MODULE = 100  # Traiter par lots de 100
MODE_TEST = True
```

Et relancer plusieurs fois.

---

## 🎉 Commande Tout-en-Un

```bash
cd ~/migration_lysa_v19 && \
git pull && \
workon migration_lysa && \
nohup python -u migration_simple.py > logs/migration_complete_$(date +%Y%m%d_%H%M%S).log 2>&1 & \
echo "PID: $!" && \
sleep 5 && \
tail -50 logs/migration_*.log
```

Cette commande :
1. Se place dans le bon dossier
2. Synchronise avec GitHub
3. Active l'environnement Python
4. Lance la migration en arrière-plan
5. Affiche le PID
6. Attend 5 secondes
7. Affiche les premières lignes pour vérifier

---

## 📱 Commande de Surveillance

```bash
watch -n 30 'tail -20 logs/migration_*.log && echo "" && ps aux | grep migration_simple'
```

Affiche toutes les 30 secondes :
- Les 20 dernières lignes du log
- Si le processus tourne toujours

Appuyez sur `Ctrl+C` pour arrêter la surveillance.

