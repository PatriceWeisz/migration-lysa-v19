# Notes Spécifiques Base SaaS - lysa-migration.odoo.com

## 🌐 Configuration Base SaaS

**URL** : https://lysa-migration.odoo.com/  
**Type** : Base SaaS Odoo (hébergée par Odoo.com)  
**Version** : Odoo v19

## ⚠️ Limitations SaaS

### Accès et Permissions

Les bases SaaS Odoo ont certaines limitations par rapport aux installations on-premise :

1. **Modules installables**
   - Seuls les modules approuvés Odoo sont disponibles
   - Pas d'accès direct au système de fichiers
   - Pas de modules personnalisés (sauf via Odoo Studio)

2. **Accès à la base de données**
   - ✅ API XML-RPC : Accessible (utilisé dans ce projet)
   - ✅ API REST (si activée)
   - ❌ Accès SQL direct : Non disponible
   - ❌ Accès shell : Non disponible

3. **Limites de performance**
   - Limites API : Possibles throttling selon l'offre
   - Timeout : Peut être plus strict que on-premise
   - Connexions simultanées : Limitées selon l'offre

### Configuration pour SaaS

Dans `config_v19.py`, la configuration a été adaptée :

```python
DEST_CONFIG_V19 = {
    'URL': 'https://lysa-migration.odoo.com/',
    'DB': 'lysa-migration',
    'USER': 'support@senedoo.com',
    'PASS': 'senedoo@2025',
    'VERSION': 'v19',
    'TYPE': 'SAAS',  # Indique que c'est une base SaaS
}
```

## 🔧 Adaptations Recommandées

### 1. Paramètres de Migration Optimisés pour SaaS

Pour éviter les timeouts et throttling sur une base SaaS :

```python
MIGRATION_PARAMS = {
    'BATCH_SIZE': 100,              # Réduit pour SaaS (au lieu de 200)
    'PARALLEL_WORKERS': 2,          # Réduit pour éviter throttling (au lieu de 5)
    'MAX_RETRY': 5,                 # Augmenté pour SaaS (au lieu de 3)
    'RETRY_DELAY': 10,              # Augmenté pour SaaS (au lieu de 5)
    'TIMEOUT': 600,                 # Augmenté pour SaaS (au lieu de 300)
}
```

### 2. Nom de la Base de Données

Pour une base SaaS, le nom de la base peut être :
- Simplement `lysa-migration`
- Ou un nom complet comme `lysa-migration-main-123456`

**Pour vérifier le nom exact** :
1. Se connecter à https://lysa-migration.odoo.com/
2. Aller dans Paramètres → Technique → Système → Base de données
3. Noter le nom exact de la DB

### 3. Authentification

Les bases SaaS utilisent généralement :
- Email + mot de passe (standard)
- Possiblement 2FA (à désactiver temporairement pour la migration API)
- Clés API (si disponibles dans votre offre)

## 🔍 Vérifications SaaS

### Avant la Migration

- [ ] Vérifier que l'API XML-RPC est activée
- [ ] Confirmer les droits d'administration
- [ ] Vérifier l'espace disponible
- [ ] Noter la version exacte d'Odoo
- [ ] Désactiver la 2FA si activée (pour API)

### Nom Exact de la Base

```bash
# Tester le nom de la base avec ce script
python -c "
import xmlrpc.client
url = 'https://lysa-migration.odoo.com/'
common = xmlrpc.client.ServerProxy(f'{url}xmlrpc/2/common')
print('Version:', common.version())
"
```

### Connexion de Test

```bash
# Test avec le script fourni
python connexion_double_v19.py
```

Si erreur d'authentification :
1. Vérifier le nom exact de la DB
2. Essayer avec juste : `lysa-migration`
3. Ou essayer de laisser le champ DB vide (certaines SaaS)

## 🚨 Problèmes Courants SaaS

### Erreur "Database does not exist"

**Solution** : Le nom de la base est incorrect.

Essayer dans cet ordre :
1. `lysa-migration`
2. `main` (nom par défaut SaaS)
3. Se connecter via web et vérifier le nom exact

### Erreur "API Rate Limit"

**Solution** : Réduire les paramètres :
- `BATCH_SIZE`: 50
- `PARALLEL_WORKERS`: 1
- `RETRY_DELAY`: 15

### Timeouts Fréquents

**Solution** : Augmenter les timeouts :
- `TIMEOUT`: 900 (15 minutes)
- `RETRY_DELAY`: 15

## 📝 Configuration Optimale SaaS

Voici une configuration recommandée pour la base SaaS :

```python
# Dans config_v19.py

DEST_CONFIG_V19 = {
    'URL': 'https://lysa-migration.odoo.com/',
    'DB': 'lysa-migration',  # À ajuster si nécessaire
    'USER': 'support@senedoo.com',
    'PASS': 'senedoo@2025',
    'VERSION': 'v19',
    'TYPE': 'SAAS',
}

MIGRATION_PARAMS = {
    # Optimisé pour SaaS
    'BATCH_SIZE': 100,
    'MAX_RECORDS': None,
    'PARALLEL_WORKERS': 2,
    
    # Retry optimisé pour SaaS
    'MAX_RETRY': 5,
    'RETRY_DELAY': 10,
    'TIMEOUT': 600,
    
    # Reste identique
    'JOURNAL_CODE': 'MIGV19',
    'JOURNAL_NAME': 'Migration v19',
    'COMPTE_CONTREPARTIE': '471000',
    'COMPTE_ECART': '658000',
    
    'MIGRER_PLAN_COMPTABLE': True,
    'MIGRER_PARTENAIRES': True,
    'MIGRER_PRODUITS': True,
    'MIGRER_FACTURES_CLIENTS': True,
    'MIGRER_FACTURES_FOURNISSEURS': True,
    'MIGRER_PAIEMENTS': True,
    
    'VERIFIER_DOUBLONS': True,
    'CREER_SEQUENCES': True,
    'MAPPER_COMPTES': True,
    'CONSERVER_DATES': True,
    'MODE_SIMULATION': False,
    
    'CACHE_ENABLED': True,
    'CACHE_SIZE': 10000,
    'PREFETCH_DATA': True,
    
    'LOG_LEVEL': 'INFO',
    'LOG_TO_FILE': True,
    'LOG_DIR': 'logs',
}
```

## ✅ Checklist SaaS

Avant de lancer la migration sur la base SaaS :

- [ ] URL confirmée : https://lysa-migration.odoo.com/
- [ ] Nom de base vérifié (tester avec script de test)
- [ ] Identifiants vérifiés
- [ ] Paramètres optimisés pour SaaS
- [ ] Test de connexion réussi
- [ ] Mode simulation testé d'abord
- [ ] Sauvegarde manuelle effectuée (export Odoo)
- [ ] Espace disponible vérifié

## 🎯 Commande de Test

```bash
# Test complet de connexion SaaS
cd "g:\Mon Drive\SENEDOO\CURSOR\migration_lysa_v19"
python tests/test_connexion.py
```

## 📞 Support Odoo SaaS

En cas de problème avec la base SaaS :
- Support Odoo : https://www.odoo.com/help
- Documentation API : https://www.odoo.com/documentation/17.0/developer/reference/external_api.html

---

**Note** : Cette base SaaS a été détectée lors de la configuration du projet.  
**Date** : 02 Décembre 2025  
**Auteur** : SENEDOO

