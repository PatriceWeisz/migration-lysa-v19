# 👥 STRATÉGIE : UTILISATEURS INACTIFS

## 🎯 Problème

Les utilisateurs inactifs sont référencés par :
- Projets (responsable)
- Produits (responsable stock)
- Équipes commerciales (chef d'équipe)
- Employés (manager, coach)
- etc.

**Impossible de créer ces enregistrements si les utilisateurs n'existent pas.**

---

## ✅ Solution Adoptée

### Phase 1 : Migration (début)

**Créer TOUS les utilisateurs en mode ACTIF**
- Même ceux qui étaient inactifs dans la source
- Cela permet de créer toutes les dépendances
- Script : `migrer_utilisateurs.py`

```python
# Dans le script
data = {
    'active': True  # TOUJOURS actif
}
```

### Phase 2 : Dépendances (milieu)

**Migrer les modules dépendants**
- Projets → référencent des utilisateurs ✅
- Produits → référencent responsables stock ✅
- Équipes → référencent chefs ✅
- Employés → référencent managers ✅

### Phase 3 : Finalisation (fin)

**Désactiver les utilisateurs qui étaient inactifs**
- Script : `finaliser_utilisateurs.py`
- À lancer **APRÈS toute la migration**
- Compare avec la source et désactive

```bash
python finaliser_utilisateurs.py
```

---

## 📋 Ordre d'Exécution

```bash
# 1. Migrer les utilisateurs (TOUS actifs)
python migrer_utilisateurs.py

# 2. Migrer tous les autres modules
python migrer_projets.py
python migrer_produits.py
# ... etc

# 3. PHASE 2 : Transactions
python migrer_factures.py
python migrer_commandes.py
# ... etc

# 4. FINALISATION : Désactiver les inactifs
python finaliser_utilisateurs.py
```

---

## ⚠️ Important

**NE PAS lancer `finaliser_utilisateurs.py` avant la fin complète !**

Si vous désactivez les utilisateurs trop tôt :
- ❌ Les migrations suivantes échoueront
- ❌ Les dépendances seront cassées
- ❌ Il faudra tout recommencer

**Lancer UNIQUEMENT quand :**
- ✅ Tous les modules de base sont migrés
- ✅ Toutes les transactions sont migrées
- ✅ Tous les tests sont OK
- ✅ La migration est 100% terminée

---

## 📊 Vérification

Pour vérifier le statut avant finalisation :

```bash
python analyser_utilisateurs.py
```

Cela affiche :
- Utilisateurs actifs dans la source
- Utilisateurs inactifs dans la source
- Utilisateurs référencés dans les projets/produits
- etc.

---

## 🔄 En Cas d'Erreur

Si vous avez lancé la finalisation trop tôt :

```python
# Script pour réactiver tous les utilisateurs
python -c "
from connexion_double_v19 import ConnexionDoubleV19
conn = ConnexionDoubleV19()
conn.connecter_tout()

users = conn.executer_destination('res.users', 'search', [('active', '=', False)])
for user_id in users:
    conn.executer_destination('res.users', 'write', [user_id], {'active': True})
print(f'{len(users)} utilisateurs réactivés')
"
```

Puis relancer les migrations qui ont échoué.

---

**Date de création :** 3 décembre 2025  
**Stratégie validée :** ✅ Testée et approuvée

