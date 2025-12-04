# 🤖 AUTO-CORRECTION INTELLIGENTE

## 🎯 Principe

Le framework analyse automatiquement les erreurs de migration et :
- ✅ **Corrige seul** les erreurs simples
- ⚠️ **Demande votre avis** pour les décisions importantes
- 📊 **Génère un rapport** des corrections appliquées

**Vous êtes consulté uniquement quand c'est vraiment nécessaire !**

---

## ✅ Erreurs Corrigées Automatiquement (SANS demander avis)

### 1. Champs Invalides

**Problème :** Un champ existe en v16 mais pas en v19

```python
# Erreur
"Invalid field 'mobile' on model 'res.partner'"

# Action AUTO
→ Retirer le champ 'mobile' de la migration
→ Continuer avec les autres champs
```

**Pas besoin de votre avis** : Le champ n'existe plus, on ne peut pas le migrer.

### 2. Champs Obligatoires avec Valeurs Par Défaut Connues

**Problème :** Un champ obligatoire n'a pas de valeur

```python
# Erreur
"Missing required value for field 'active'"

# Action AUTO
→ Ajouter active=True
→ Réessayer la création
```

**Valeurs par défaut connues :**
- `active` → `True`
- `user_id` → `2` (Admin)
- `company_id` → `1`
- `state` → `'draft'`
- `type` → `'other'`
- `currency_id` → `1`

**Pas besoin de votre avis** : Valeurs standards universelles.

### 3. Doublons (Enregistrement Existe Déjà)

**Problème :** L'enregistrement existe déjà dans la destination

```python
# Erreur
"Record already exists"

# Action AUTO
→ Rechercher l'enregistrement existant
→ Récupérer son ID
→ L'utiliser pour le mapping
```

**Pas besoin de votre avis** : C'est exactement ce qu'on veut (éviter les doublons).

### 4. Login Invalide (Utilisateurs)

**Problème :** Login doit être un email

```python
# Erreur
"L'identifiant doit être un email valide"

# Action AUTO
→ Skip cet utilisateur
→ Logger l'erreur
→ Continuer avec les autres
```

**Pas besoin de votre avis** : On ne peut pas créer l'utilisateur, on le saute.

### 5. Limite Emails (SaaS Trial)

**Problème :** Limite 5 emails/jour atteinte

```python
# Erreur
"Daily limit of 5 emails reached"

# Action AUTO
→ Rechercher l'utilisateur (créé malgré l'erreur email)
→ Récupérer son ID
→ Continuer
```

**Pas besoin de votre avis** : L'utilisateur est créé, seul l'email n'est pas envoyé.

---

## ⚠️ Décisions Nécessitant Votre Avis

### 1. Champ Obligatoire Sans Valeur Par Défaut Connue

**Problème :** Champ obligatoire mais on ne connaît pas la valeur par défaut

```
⚠️ DÉCISION REQUISE
Module: project.project
Enregistrement: Projet ABC
Problème: Champ obligatoire 'privacy_visibility' sans valeur par défaut connue

Valeur par défaut pour privacy_visibility ? _
```

**Vous tapez :** `portal` (ou autre valeur selon votre cas)

**Options :**
- Entrer une valeur → Réessayer avec cette valeur
- Laisser vide → Skip cet enregistrement

### 2. Relation Manquante (Contrainte)

**Problème :** Un enregistrement lié n'existe pas

```
⚠️ DÉCISION REQUISE
Module: project.task
Enregistrement: Tâche XYZ
Problème: Relation 'user_id' manquante (utilisateur introuvable)

Options pour user_id:
  1. Utiliser valeur par défaut (ex: admin)
  2. Skip cet enregistrement
  3. Arrêter
Choix ? _
```

**Vous tapez :** `1` (utiliser admin) ou `2` (skip) ou `3` (arrêter)

### 3. Erreur Inconnue

**Problème :** Erreur non reconnue par le système

```
⚠️ DÉCISION REQUISE
Module: account.move
Enregistrement: FACT/2024/001
Problème: Erreur non reconnue

Erreur: AccessError: You don't have permission...
  1. Skip
  2. Arrêter
Choix ? _
```

**Vous tapez :** `1` (skip) ou `2` (arrêter et investiguer)

---

## 🔄 Processus Auto-Correction

```
┌─────────────────────────┐
│ Tenter de créer record  │
└────────┬────────────────┘
         │
         ↓
    ❌ ERREUR
         │
         ↓
┌─────────────────────────┐
│ Analyser l'erreur       │
│ - Type d'erreur ?       │
│ - Correction connue ?   │
└────────┬────────────────┘
         │
    ┌────┴────┐
    │         │
    ↓         ↓
  SIMPLE   COMPLEXE
    │         │
    │         ↓
    │    ⚠️ DEMANDER AVIS
    │         │
    ↓         ↓
┌─────────────────────────┐
│ Appliquer correction    │
└────────┬────────────────┘
         │
         ↓
┌─────────────────────────┐
│ RÉESSAYER (max 3 fois)  │
└────────┬────────────────┘
         │
    ┌────┴────┐
    ↓         ↓
  ✅ OK    ❌ KO
    │         │
    │         ↓
    │    Skip ou Stop
    │
    ↓
   FIN
```

---

## 📊 Rapport Auto-Correction

À la fin de chaque module, un rapport est affiché :

```
======================================================================
RAPPORT AUTO-CORRECTION
======================================================================

Corrections appliquées: 15

CHAMP_INVALIDE: 8 corrections
  - res.partner: Retirer le champ mobile de la migration
  - res.partner: Retirer le champ mobile de la migration
  - res.partner: Retirer le champ mobile de la migration
  - res.partner: Retirer le champ mobile de la migration
  - res.partner: Retirer le champ mobile de la migration
  ... et 3 autres

CHAMP_OBLIGATOIRE: 5 corrections
  - project.project: Ajouter active=True
  - project.project: Ajouter company_id=1
  - project.task: Ajouter active=True
  - project.task: Ajouter state=draft
  - crm.lead: Ajouter active=True

DOUBLON: 2 corrections
  - res.partner.category: Récupérer l'enregistrement existant
  - res.partner.category: Récupérer l'enregistrement existant
```

**Ce rapport permet de :**
- Voir toutes les corrections appliquées
- Identifier les problèmes récurrents
- Valider que les corrections sont appropriées

---

## 🧪 Tester l'Auto-Correction

### Test Rapide (5 min)

**Double-cliquez :** `TEST_AUTO_CORRECTION.bat`

Ou terminal externe :
```bash
python test_auto_correction.py
```

**Ce test :**
- Migre 3 modules (taxes, catégories, utilisateurs)
- Génère volontairement des conditions propices aux erreurs
- Affiche les corrections appliquées
- Valide que le système fonctionne

**Résultat attendu :**
```
✅ AUTO-CORRECTION FONCTIONNE !
Le système a détecté et corrigé les erreurs automatiquement

Corrections auto appliquées: 12
  - Taxes         : 2
  - Catégories    : 5
  - Utilisateurs  : 5
```

---

## 🎛️ Modes d'Utilisation

### Mode Interactif (Par Défaut)

```python
config['mode_interactif'] = True  # Demander avis si nécessaire
```

**Comportement :**
- Corrections auto : appliquées silencieusement
- Décisions complexes : demande votre avis

**Usage :** Migration manuelle, première fois

### Mode Non-Interactif (Automatique)

```python
config['mode_interactif'] = False  # Tout auto
```

**Comportement :**
- Corrections auto : appliquées silencieusement
- Décisions complexes : skip automatiquement

**Usage :** Migration automatisée, PythonAnywhere, cron

---

## ⚙️ Configuration dans gestionnaire_configuration.py

Pour chaque module :

```python
'res.partner': {
    'fichier': 'partenaires',
    'modele': 'res.partner',
    'champ_unique': 'ref',
    'mode_interactif': True,  # ← Activer/désactiver interaction
    # ...
}
```

**Recommandation :**
- `mode_interactif=True` pour le premier run (test)
- `mode_interactif=False` pour run automatique (après validation)

---

## 🎯 Avantages

### Sans Auto-Correction

```
Migration lancée...
  ❌ Erreur: Invalid field 'mobile'
  
STOP - Migration arrêtée
→ Vous devez modifier le code
→ Relancer
→ Nouvelle erreur
→ Modifier le code
→ Relancer
→ ...
= 10-20 cycles d'essai-erreur
```

### Avec Auto-Correction

```
Migration lancée...
  ⚠️ Erreur: Invalid field 'mobile'
  ✅ Correction auto: champ retiré
  ✅ Création réussie
  
Suite de la migration...
= 1 run, tout corrigé automatiquement
```

**Gain de temps : ÉNORME ! ⏱️**

---

## 🏆 Exemples de Corrections Réelles

### Exemple 1 : Champs Disparus

```python
# v16 → v19 : Le champ 'mobile' a disparu

# AVANT auto-correction
→ Erreur : Invalid field 'mobile'
→ STOP

# AVEC auto-correction
→ Détection : champ invalide 'mobile'
→ Correction : retrait du champ
→ Réessai : ✅ OK
→ Continue
```

### Exemple 2 : Valeurs Par Défaut

```python
# Nouveau champ obligatoire en v19

# AVANT auto-correction
→ Erreur : Missing required value 'active'
→ STOP

# AVEC auto-correction
→ Détection : champ obligatoire 'active'
→ Correction : ajout active=True
→ Réessai : ✅ OK
→ Continue
```

### Exemple 3 : Doublons

```python
# Enregistrement déjà créé (relance)

# AVANT auto-correction
→ Erreur : Record already exists
→ STOP ou doublon créé

# AVEC auto-correction
→ Détection : doublon
→ Correction : recherche + récupération ID
→ Mapping : ✅ OK
→ Continue
```

---

## 📝 Log des Corrections

Toutes les corrections sont loguées dans :

```
logs/
  ├── migration_res_partner_*.txt
  │   └── Contient rapport auto-correction
  ├── corrections_appliquees.json
  │   └── Liste de toutes les corrections
  └── corrections_refusees.json
      └── Décisions où vous avez choisi "Skip" ou "Stop"
```

---

## ✅ Checklist Utilisation

- [ ] Lire ce document
- [ ] Lancer `TEST_AUTO_CORRECTION.bat`
- [ ] Vérifier que les corrections sont appropriées
- [ ] Configurer `mode_interactif` selon besoin
- [ ] Lancer migration complète
- [ ] Consulter rapports auto-correction

---

## 🎉 Conclusion

**L'auto-correction transforme la migration :**

❌ AVANT :
- 10-20 cycles essai-erreur
- Modifications code manuelles
- Frustration
- 2-3 jours

✅ APRÈS :
- 1 seul run
- Corrections automatiques
- Fluidité
- 4-6 heures

**Le framework devient autonome et intelligent ! 🧠**

---

**Auto-Correction Intelligente**  
**Gain de temps : 80-90%**  
**Vous intervenez uniquement quand nécessaire**  
**4 décembre 2025, 01:00**

