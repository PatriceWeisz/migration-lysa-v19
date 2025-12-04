# ⚠️ VÉRIFICATION MODULES PRÉ-MIGRATION

## 🎯 Pourquoi C'est CRITIQUE

**Question :** Un module installé en SOURCE mais pas en DESTINATION = quoi ?

**Réponse :** **Les données de ce module NE PEUVENT PAS être migrées !**

---

## ❌ Exemple de Problème

### Scénario

```
SOURCE (v16):
  ✅ account (Comptabilité)
  ✅ sale (Ventes)
  ✅ purchase (Achats)
  ✅ mrp (Fabrication)
  ✅ project (Projets)

DESTINATION (v19):
  ✅ account
  ✅ sale
  ❌ purchase (PAS INSTALLÉ)
  ✅ mrp
  ❌ project (PAS INSTALLÉ)
```

### Résultat Migration

```
✅ Comptabilité : migrée OK
✅ Ventes : migrées OK
❌ ACHATS : IMPOSSIBLE (module absent)
✅ Fabrication : migrée OK
❌ PROJETS : IMPOSSIBLE (module absent)
```

**Vous perdez toutes les commandes fournisseurs et tous les projets ! 😱**

---

## ✅ Solution : Vérifier AVANT

### Étape 1 : Lancer la Vérification

**Double-cliquez :**
```
VERIFIER_MODULES.bat
```

Ou terminal externe :
```bash
python verifier_modules_installes.py
```

### Étape 2 : Lire le Résultat

#### Cas 1 : Tous OK ✅

```
======================================================================
✅ TOUS LES MODULES SONT INSTALLÉS
======================================================================

Vous pouvez lancer la migration en toute sécurité:

  python migration_framework.py
```

**→ Vous pouvez migrer !**

#### Cas 2 : Modules Manquants ⚠️

```
======================================================================
⚠️ MODULES MANQUANTS DANS LA DESTINATION
======================================================================

Achats (2 modules):
  ❌ purchase                      Achats
  ❌ purchase_stock                Achats et stock

Projets (3 modules):
  ❌ project                       Gestion de projets
  ❌ project_timesheet             Feuilles de temps
  ❌ hr_timesheet                  Feuilles de temps

======================================================================
⚠️ ACTION REQUISE !
======================================================================

Vous DEVEZ installer ces modules dans la destination AVANT la migration.
```

**→ NE PAS migrer maintenant !**

---

## 🛠️ Installer les Modules Manquants

### Méthode 1 : Interface Odoo (Recommandé)

1. **Connectez-vous** à la destination (v19)
2. **Allez dans** : Apps (Applications)
3. **Recherchez** le module (ex: "purchase")
4. **Cliquez** sur "Installer"
5. **Attendez** l'installation
6. **Répétez** pour chaque module manquant

### Méthode 2 : Script Automatique (Si Permissions)

Un script est généré automatiquement :
```bash
python logs/installer_modules_manquants.py
```

**⚠️ ATTENTION :** Ce script peut NE PAS fonctionner sur Odoo SaaS (permissions restreintes).

### Méthode 3 : Contacter l'Admin Odoo

Si vous êtes sur Odoo SaaS :
1. Contactez votre administrateur Odoo
2. Demandez l'installation des modules manquants
3. Attendez la confirmation

---

## 🔄 Après Installation

### Re-Vérifier

```bash
python verifier_modules_installes.py
```

**Résultat attendu :**
```
✅ TOUS LES MODULES SONT INSTALLÉS

Modules OK : 45/45
Modules MANQUANTS : 0
```

**→ OK pour migrer !**

---

## 📊 Types de Modules

### Modules Métier (À installer)

**Exemples :**
- `purchase` (Achats)
- `mrp` (Fabrication)
- `project` (Projets)
- `hr_expense` (Notes de frais)
- `fleet` (Parc automobile)
- `maintenance` (Maintenance)
- etc.

**→ DOIVENT être installés si utilisés en SOURCE**

### Modules Système (Ignorés)

**Exemples :**
- `base` (Base)
- `web` (Interface web)
- `mail` (Messagerie)
- `portal` (Portail)

**→ Installés par défaut partout, ignorés par le script**

### Modules Studio (Ignorés)

**Exemples :**
- `studio_customization_*`

**→ Customisations Studio, ignorées (les champs seront migrés quand même)**

---

## 🎯 Cas Particuliers

### Modules Renommés v16→v19

Si un module a changé de nom entre versions :

```
v16 : stock_account
v19 : stock_account → intégré dans stock
```

**→ Le script peut signaler "manquant" alors qu'il est intégré**

**Solution :** Vérifier la documentation Odoo v19

### Modules Enterprise non disponibles

Si vous aviez Enterprise en v16 mais Community en v19 :

```
❌ account_accountant (Enterprise)
❌ mrp_plm (Enterprise)
```

**→ Ces modules ne peuvent pas être migrés**

**Solution :** Passer à Enterprise v19 ou accepter la perte

### Modules Obsolètes

Si un module n'existe plus en v19 :

```
❌ website_twitter (obsolète en v19)
```

**→ Données ne peuvent pas être migrées**

**Solution :** Exporter les données manuellement avant migration

---

## 📋 Checklist Pré-Migration

- [ ] ✅ Exécuter `VERIFIER_MODULES.bat`
- [ ] ✅ Lire le rapport
- [ ] ✅ Si modules manquants :
  - [ ] Installer via interface Odoo
  - [ ] OU contacter admin
  - [ ] OU accepter perte de données
- [ ] ✅ Re-vérifier après installation
- [ ] ✅ Attendre résultat "TOUS OK"
- [ ] ✅ ALORS seulement, lancer migration

---

## 🚨 Erreurs Fréquentes

### Erreur 1 : Migrer sans vérifier

```
❌ Lancer migration_framework.py sans vérifier
→ Découvrir APRÈS que des modules manquent
→ Données perdues !
```

**Solution :** TOUJOURS vérifier d'abord

### Erreur 2 : Ignorer les avertissements

```
⚠️ "3 modules manquants"
→ "Bof, on verra plus tard"
→ Migration lancée
→ Données de ces modules perdues !
```

**Solution :** Traiter TOUS les modules manquants

### Erreur 3 : Ne pas re-vérifier

```
✅ Installer les modules
❌ Relancer migration sans re-vérifier
→ L'installation a peut-être échoué
→ Données perdues !
```

**Solution :** TOUJOURS re-vérifier après installation

---

## 📊 Rapport Généré

Le script génère un rapport détaillé :
```
logs/verification_modules_YYYYMMDD_HHMMSS.txt
```

**Contient :**
- Liste complète des modules SOURCE
- Liste complète des modules DESTINATION
- Modules OK (installés partout)
- Modules MANQUANTS (avec catégorie et description)
- Modules uniquement en DEST (info)
- Recommandations

**Conservez ce rapport pour traçabilité !**

---

## 🔗 Intégration Workflow

### Workflow COMPLET (Mis à Jour)

```
1. Sauvegarder (1 min)
   └─ COMMIT_ET_PUSH.bat

2. ⭐ VÉRIFIER MODULES (2 min) ← NOUVEAU !
   └─ VERIFIER_MODULES.bat
   └─ Si manquants → Installer → Re-vérifier
   └─ Attendre "TOUS OK"

3. Analyser (5 min)
   └─ python analyser_avant_migration.py

4. Test Auto-Correction (5 min)
   └─ TEST_AUTO_CORRECTION.bat

5. Test Complet (15 min)
   └─ python test_complet_framework.py

6. Migration (4-6h)
   └─ python migration_framework.py

7. Vérifications (1h)
   └─ verifier_statuts.py
   └─ verifier_integrite_complete.py
   └─ verifier_comptabilite.py

8. Tests Utilisateurs (2h)
```

**⚠️ ÉTAPE 2 EST CRITIQUE ! Ne pas sauter !**

---

## 🎯 Résumé

### Pourquoi Vérifier ?

✅ Éviter perte de données  
✅ Détecter problèmes AVANT  
✅ Installation ciblée  
✅ Migration complète garantie  

### Quand Vérifier ?

⚠️ **AVANT** de lancer la migration  
⚠️ **APRÈS** installation de modules  
⚠️ **À CHAQUE** nouvelle tentative  

### Comment Vérifier ?

```bash
# Option 1 (Simple)
Double-clic: VERIFIER_MODULES.bat

# Option 2 (Terminal)
python verifier_modules_installes.py
```

---

## ✅ Résultat Attendu

```
======================================================================
✅ TOUS LES MODULES SONT INSTALLÉS
======================================================================

Modules SOURCE installés : 47
Modules DEST installés   : 52
Modules OK               : 42
Modules MANQUANTS        : 0
Modules ignorés (système): 5

✅ TOUS LES MODULES SONT INSTALLÉS

Vous pouvez lancer la migration en toute sécurité:

  python migration_framework.py
```

**→ Feu vert pour la migration ! 🚀**

---

**Vérification Modules Pré-Migration**  
**CRITIQUE - Ne JAMAIS sauter cette étape**  
**Évite la perte de données**  
**4 décembre 2025, 02:15**

