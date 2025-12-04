#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VÉRIFICATION MODULES INSTALLÉS
================================
Vérifie que tous les modules de la SOURCE sont installés dans la DESTINATION
CRITIQUE avant de lancer la migration !
"""

import sys
import os

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', buffering=1)

from pathlib import Path
from datetime import datetime
from connexion_double_v19 import ConnexionDoubleV19

def afficher(msg=""):
    sys.stdout.write(str(msg) + '\n')
    sys.stdout.flush()

afficher("="*70)
afficher("VÉRIFICATION MODULES INSTALLÉS")
afficher("="*70)
afficher("")
afficher("⚠️ CRITIQUE : Vérifie que les modules de la source")
afficher("   sont installés dans la destination")
afficher("")
afficher("="*70)

# Connexion
conn = ConnexionDoubleV19()
if not conn.connecter_tout():
    sys.exit(1)

afficher("OK Connexion\n")

# Créer rapport
LOGS_DIR = Path('logs')
LOGS_DIR.mkdir(exist_ok=True)
RAPPORT = LOGS_DIR / f'verification_modules_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'

rapport = open(RAPPORT, 'w', encoding='utf-8')

def ecrire(msg):
    rapport.write(msg + '\n')
    rapport.flush()

ecrire("="*70)
ecrire("VÉRIFICATION MODULES INSTALLÉS")
ecrire(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
ecrire("="*70)

# =============================================================================
# RÉCUPÉRER MODULES INSTALLÉS
# =============================================================================

afficher("Récupération modules SOURCE...")
modules_source = conn.executer_source('ir.module.module', 'search_read',
                                     [('state', 'in', ['installed', 'to upgrade'])],
                                     fields=['name', 'state', 'category_id', 'shortdesc'])

afficher(f"  -> {len(modules_source)} modules installés\n")

afficher("Récupération modules DESTINATION...")
modules_dest = conn.executer_destination('ir.module.module', 'search_read',
                                        [('state', 'in', ['installed', 'to upgrade'])],
                                        fields=['name', 'state', 'category_id', 'shortdesc'])

afficher(f"  -> {len(modules_dest)} modules installés\n")

# Index par nom
dest_index = {m['name']: m for m in modules_dest}

# =============================================================================
# ANALYSER DIFFÉRENCES
# =============================================================================

afficher("="*70)
afficher("ANALYSE MODULES")
afficher("="*70)

modules_manquants = []
modules_ok = []
modules_ignores = []

# Modules système à ignorer (installés par défaut partout)
MODULES_SYSTEME = {
    'base', 'web', 'bus', 'mail', 'base_setup', 'web_tour',
    'base_import', 'base_import_module', 'web_editor'
}

# Modules techniques à ignorer
MODULES_TECHNIQUES = {
    'auth_oauth', 'auth_ldap', 'auth_signup', 'portal',
    'web_unsplash', 'web_kanban_gauge'
}

for module in modules_source:
    nom = module['name']
    desc = module.get('shortdesc', nom)
    
    # Ignorer modules système
    if nom in MODULES_SYSTEME or nom in MODULES_TECHNIQUES:
        modules_ignores.append({
            'nom': nom,
            'desc': desc,
            'raison': 'Système'
        })
        continue
    
    # Ignorer modules Studio custom (commencent par studio_customization_)
    if nom.startswith('studio_customization_'):
        modules_ignores.append({
            'nom': nom,
            'desc': desc,
            'raison': 'Studio custom'
        })
        continue
    
    # Vérifier si installé en destination
    if nom not in dest_index:
        modules_manquants.append({
            'nom': nom,
            'desc': desc,
            'categorie': module.get('category_id', [False, 'N/A'])[1] if module.get('category_id') else 'N/A'
        })
    else:
        modules_ok.append(nom)

# =============================================================================
# AFFICHER RÉSULTATS
# =============================================================================

afficher(f"\nModules SOURCE installés : {len(modules_source)}")
afficher(f"Modules DEST installés   : {len(modules_dest)}")
afficher(f"Modules OK               : {len(modules_ok)}")
afficher(f"Modules MANQUANTS        : {len(modules_manquants)}")
afficher(f"Modules ignorés (système): {len(modules_ignores)}")

ecrire(f"\nSTATISTIQUES:")
ecrire(f"  Modules SOURCE : {len(modules_source)}")
ecrire(f"  Modules DEST   : {len(modules_dest)}")
ecrire(f"  Modules OK     : {len(modules_ok)}")
ecrire(f"  MANQUANTS      : {len(modules_manquants)}")

# =============================================================================
# MODULES MANQUANTS (CRITIQUE)
# =============================================================================

if modules_manquants:
    afficher("\n" + "="*70)
    afficher("⚠️ MODULES MANQUANTS DANS LA DESTINATION")
    afficher("="*70)
    
    ecrire("\n" + "="*70)
    ecrire("MODULES MANQUANTS")
    ecrire("="*70)
    
    # Grouper par catégorie
    par_categorie = {}
    for mod in modules_manquants:
        cat = mod['categorie']
        if cat not in par_categorie:
            par_categorie[cat] = []
        par_categorie[cat].append(mod)
    
    for categorie, mods in sorted(par_categorie.items()):
        afficher(f"\n{categorie} ({len(mods)} modules):")
        ecrire(f"\n{categorie}:")
        
        for mod in mods:
            afficher(f"  ❌ {mod['nom']:40s} {mod['desc']}")
            ecrire(f"  - {mod['nom']:40s} {mod['desc']}")
    
    afficher("\n" + "="*70)
    afficher("⚠️ ACTION REQUISE !")
    afficher("="*70)
    afficher("\nVous DEVEZ installer ces modules dans la destination AVANT la migration.")
    afficher("")
    afficher("Options:")
    afficher("  1. Installer manuellement dans Odoo (Apps > Installer)")
    afficher("  2. Demander à l'administrateur Odoo SaaS")
    afficher("  3. Ignorer ces modules (données non migrées)")
    afficher("")
    afficher("⚠️ Si vous ignorez, les données de ces modules NE SERONT PAS MIGRÉES !")
    afficher("")
    
    ecrire("\nACTION REQUISE:")
    ecrire("Ces modules doivent être installés dans la destination avant migration")
    ecrire("Sinon les données de ces modules ne pourront pas être migrées")

# =============================================================================
# MODULES OK
# =============================================================================

if modules_ok:
    afficher("\n" + "="*70)
    afficher("✅ MODULES OK (Installés partout)")
    afficher("="*70)
    afficher(f"\n{len(modules_ok)} modules OK (échantillon de 20):\n")
    
    ecrire("\n" + "="*70)
    ecrire("MODULES OK")
    ecrire("="*70)
    
    for nom in sorted(modules_ok)[:20]:
        afficher(f"  ✅ {nom}")
        ecrire(f"  - {nom}")
    
    if len(modules_ok) > 20:
        afficher(f"  ... et {len(modules_ok) - 20} autres")
        ecrire(f"  ... et {len(modules_ok) - 20} autres")

# =============================================================================
# MODULES DESTINATION UNIQUEMENT (INFO)
# =============================================================================

source_names = {m['name'] for m in modules_source}
modules_dest_uniquement = [m for m in modules_dest if m['name'] not in source_names]

if modules_dest_uniquement:
    afficher("\n" + "="*70)
    afficher("ℹ️ MODULES UNIQUEMENT EN DESTINATION")
    afficher("="*70)
    afficher(f"\n{len(modules_dest_uniquement)} modules installés en DEST mais pas en SOURCE")
    afficher("(Normal: modules v19, modules SaaS, etc.)\n")
    
    ecrire("\n" + "="*70)
    ecrire("MODULES UNIQUEMENT EN DESTINATION")
    ecrire("="*70)
    
    for mod in sorted(modules_dest_uniquement, key=lambda x: x['name'])[:20]:
        afficher(f"  ℹ️ {mod['name']}")
        ecrire(f"  - {mod['name']}")
    
    if len(modules_dest_uniquement) > 20:
        afficher(f"  ... et {len(modules_dest_uniquement) - 20} autres")
        ecrire(f"  ... et {len(modules_dest_uniquement) - 20} autres")

# =============================================================================
# RECOMMANDATIONS
# =============================================================================

afficher("\n" + "="*70)
afficher("RECOMMANDATIONS")
afficher("="*70)

if modules_manquants:
    afficher("\n⚠️ NE PAS LANCER LA MIGRATION MAINTENANT")
    afficher("")
    afficher("1. Installez les modules manquants dans la destination")
    afficher("2. Relancez ce script pour vérifier")
    afficher("3. Quand tous les modules sont OK, lancez la migration")
    afficher("")
    ecrire("\nRECOMMANDATION: Installer les modules manquants avant migration")
    
    # Code de sortie d'erreur
    rapport.close()
    afficher(f"\nRapport: {RAPPORT}")
    sys.exit(1)
else:
    afficher("\n✅ TOUS LES MODULES SONT INSTALLÉS")
    afficher("")
    afficher("Vous pouvez lancer la migration en toute sécurité:")
    afficher("")
    afficher("  python migration_framework.py")
    afficher("")
    afficher("ou")
    afficher("")
    afficher("  Double-clic: LANCER_MIGRATION.bat")
    afficher("")
    ecrire("\nRECOMMANDATION: OK pour lancer la migration")

# =============================================================================
# GÉNÉRATION SCRIPT INSTALLATION (Bonus)
# =============================================================================

if modules_manquants:
    afficher("\n" + "="*70)
    afficher("SCRIPT INSTALLATION")
    afficher("="*70)
    
    script_install = LOGS_DIR / 'installer_modules_manquants.py'
    
    with open(script_install, 'w', encoding='utf-8') as f:
        f.write('#!/usr/bin/env python3\n')
        f.write('# -*- coding: utf-8 -*-\n')
        f.write('"""\n')
        f.write('INSTALLATION MODULES MANQUANTS\n')
        f.write('Installe les modules manquants dans la destination\n')
        f.write('"""\n\n')
        f.write('from connexion_double_v19 import ConnexionDoubleV19\n\n')
        f.write('conn = ConnexionDoubleV19()\n')
        f.write('if not conn.connecter_destination():\n')
        f.write('    exit(1)\n\n')
        f.write('modules_a_installer = [\n')
        for mod in modules_manquants:
            f.write(f"    '{mod['nom']}',  # {mod['desc']}\n")
        f.write(']\n\n')
        f.write('print(f"Installation de {len(modules_a_installer)} modules...")\n\n')
        f.write('for module_name in modules_a_installer:\n')
        f.write('    try:\n')
        f.write('        module_ids = conn.executer_destination(\n')
        f.write("            'ir.module.module', 'search',\n")
        f.write("            [('name', '=', module_name), ('state', '=', 'uninstalled')]\n")
        f.write('        )\n')
        f.write('        \n')
        f.write('        if module_ids:\n')
        f.write("            conn.executer_destination('ir.module.module', 'button_immediate_install', module_ids)\n")
        f.write('            print(f"  ✅ {module_name}")\n')
        f.write('        else:\n')
        f.write('            print(f"  ⚠️ {module_name} (déjà installé ou indisponible)")\n')
        f.write('    except Exception as e:\n')
        f.write('        print(f"  ❌ {module_name}: {e}")\n\n')
        f.write('print("\\nTerminé !")\n')
    
    afficher(f"\n✅ Script d'installation généré: {script_install}")
    afficher("")
    afficher("⚠️ ATTENTION: Ce script peut NE PAS FONCTIONNER sur Odoo SaaS")
    afficher("   (permissions restreintes)")
    afficher("")
    afficher("Utilisez plutôt l'interface Odoo (Apps > Installer)")
    ecrire(f"\nScript installation généré: {script_install}")
    ecrire("(Peut ne pas fonctionner sur SaaS - permissions)")

afficher("\n" + "="*70)
afficher(f"Rapport complet: {RAPPORT}")
afficher("="*70)

rapport.close()

