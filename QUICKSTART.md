# Guide de Démarrage Rapide - Migration LYSA v19

## Installation rapide

```bash
# 1. Naviguer dans le dossier
cd migration_lysa_v19

# 2. Installer les dépendances
pip install -r requirements.txt
```

## Configuration

Avant de commencer, vérifiez les paramètres dans `config_v19.py` :

- **URL des bases** : Source et destination
- **Identifiants** : Vérifiez les credentials
- **Paramètres de migration** : Batch size, workers, etc.

## Ordre d'exécution recommandé

### 1. Test de connexion (OBLIGATOIRE)

```bash
python tests/test_connexion.py
```

✓ Vérifie que les connexions aux deux bases fonctionnent  
✓ Vérifie la version d'Odoo v19  
✓ Affiche les statistiques initiales

### 2. Connexion double simple

```bash
python connexion_double_v19.py
```

✓ Test simple de connexion aux deux bases  
✓ Affiche les comptages des principaux modèles

### 3. Migration du plan comptable (EN PREMIER)

```bash
python migration_plan_comptable.py
```

✓ Migre tous les comptes comptables  
✓ Génère un fichier de mapping (logs/account_mapping.json)  
✓ Gère les types de comptes v19  

⚠️ **IMPORTANT** : À exécuter AVANT la migration des partenaires !

### 4. Migration des partenaires

```bash
python migration_partenaires.py
```

✓ Migre les clients et fournisseurs  
✓ Gère les doublons automatiquement  
✓ Affiche la progression en temps réel

### 5. Vérification post-migration

```bash
python verification_v19.py
```

✓ Vérifie les comptages  
✓ Vérifie l'intégrité des données  
✓ Génère un rapport de vérification

## Mode simulation

Pour tester sans écrire de données, activez le mode simulation dans `config_v19.py` :

```python
MIGRATION_PARAMS = {
    'MODE_SIMULATION': True,  # Mettre à True pour simuler
    ...
}
```

## Limiter pour les tests

Pour limiter le nombre d'enregistrements lors des tests :

```python
MIGRATION_PARAMS = {
    'MAX_RECORDS': 100,  # Limiter à 100 enregistrements
    ...
}
```

## Logs

Tous les scripts génèrent des logs dans le dossier `logs/` :

- Logs détaillés de chaque exécution
- Horodatage automatique
- Niveaux : DEBUG, INFO, WARNING, ERROR

## Vérifications importantes

### Avant la migration

- [ ] Sauvegarde de la base source effectuée
- [ ] Base destination v19 prête et accessible
- [ ] Connexions testées avec `test_connexion.py`
- [ ] Configuration vérifiée dans `config_v19.py`

### Pendant la migration

- [ ] Surveiller les logs pour détecter les erreurs
- [ ] Vérifier la progression
- [ ] Noter les éventuels avertissements

### Après la migration

- [ ] Exécuter `verification_v19.py`
- [ ] Vérifier les comptages
- [ ] Tester quelques enregistrements manuellement
- [ ] Consulter les logs pour les erreurs

## Commandes utiles

### Voir les logs en temps réel

```bash
# Windows PowerShell
Get-Content logs\migration_v19_*.log -Wait -Tail 50

# Linux/Mac
tail -f logs/migration_v19_*.log
```

### Compter les fichiers de logs

```bash
# Voir tous les logs
ls logs/
```

## En cas de problème

1. **Erreur de connexion**
   - Vérifier les URLs dans `config_v19.py`
   - Vérifier les identifiants
   - Tester l'accès aux bases via navigateur

2. **Erreur de migration**
   - Consulter les logs détaillés
   - Vérifier le mode simulation
   - Réduire le batch size si nécessaire

3. **Performance lente**
   - Réduire `PARALLEL_WORKERS`
   - Augmenter `TIMEOUT`
   - Vérifier la connexion réseau

## Support

Pour toute question ou problème :
- Consulter le `README.md` complet
- Vérifier les logs dans le dossier `logs/`
- Contacter SENEDOO

## Checklist rapide

```
□ Installation des dépendances (pip install -r requirements.txt)
□ Configuration vérifiée (config_v19.py)
□ Test de connexion réussi (test_connexion.py)
□ Sauvegarde effectuée
□ Migration lancée
□ Vérification post-migration effectuée
□ Tests manuels OK
```

## Exemples de commandes complètes

```bash
# Session complète de migration
cd "g:\Mon Drive\SENEDOO\CURSOR\migration_lysa_v19"

# 1. Test
python tests/test_connexion.py

# 2. Migration
python migration_partenaires.py

# 3. Vérification
python verification_v19.py
```

Bonne migration ! 🚀

