# 🚨 LIMITE CRITIQUE ODOO SAAS TRIAL

## ⚠️ DÉCOUVERTE MAJEURE

```
You have reached your daily limit of 5 messages.
Paid subscriptions receive an increased limit of 200.
```

**Odoo SaaS en mode TRIAL limite la création à :**
- ❌ **5 utilisateurs par jour maximum**
- ✅ 200 utilisateurs par jour avec abonnement payant

---

## 📊 Impact sur la Migration

**Utilisateurs à migrer : 89**
- Temps nécessaire en mode trial : **18 jours** (89 ÷ 5 = 17.8)
- Temps avec abonnement payant : **1 jour** (89 ÷ 200 < 1)

---

## 🎯 Solutions Possibles

### Solution 1 : Migrer 5 utilisateurs par jour (LENT)

```bash
# Jour 1 : Créer 5 users
python migrer_utilisateurs.py  # En mode TEST avec LIMIT=5

# Jour 2 : 5 de plus
# ... modifier le script pour skip les premiers
# Répéter 18 jours
```

**Inconvénients :**
- ❌ 18 jours pour migrer les users
- ❌ Les projets, produits, équipes ne pourront pas être migrés correctement
- ❌ Processus très lent et fastidieux

### Solution 2 : Passer en Abonnement Payant (RECOMMANDÉ)

**Avantages :**
- ✅ Limite à 200 créations/jour
- ✅ Migration complète en 1 jour
- ✅ Pas de blocage
- ✅ De toute façon nécessaire pour la production

### Solution 3 : Ne migrer que les utilisateurs critiques

**Identifier les 5 utilisateurs les plus importants :**
- Admin principal
- Responsables de départements
- Utilisateurs référencés dans projets/produits actifs
- Comptables
- Responsables stock

**Migrer seulement ces 5, les autres plus tard**

---

## 🔍 Vérification des Utilisateurs Déjà Créés

D'après le log, le script a commencé à créer et s'est arrêté à la limite.

Vérifions combien ont été créés :

```bash
python -c "
import json
m = json.load(open('logs/user_mapping.json'))
print(f'Utilisateurs mappés: {len(m)}')
"
```

---

## 📋 Recommandation Immédiate

**OPTION A : Mode Payant**
- Contacter Odoo pour passer en mode payant
- Limite passera à 200/jour
- Migration complète possible

**OPTION B : Migration Sélective**
- Identifier les 5 users critiques par jour
- Les migrer progressivement
- Adapter les autres modules pour utiliser admin par défaut

**OPTION C : Import Direct SQL**
- Si accès à la base de données
- Bypass les limites API
- Nécessite expertise SQL Odoo

---

## ⚠️ Impact sur le Projet

**Cette limitation affecte TOUT :**
- Utilisateurs : 89 → limite 5/jour
- Probablement d'autres modèles aussi
- La migration complète peut prendre des **semaines** en mode trial

**Il FAUT passer en mode payant pour une migration professionnelle.**

---

**Date découverte :** 3 décembre 2025, 22:47  
**Criticité :** 🔴 BLOQUANT pour migration complète

