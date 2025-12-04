#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TEST AVEC LOG TEMPS RÉEL
=========================
Écrit dans un fichier que vous pouvez suivre en temps réel
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Créer fichier de log
LOG_FILE = Path('logs') / 'test_migration_live.txt'
LOG_FILE.parent.mkdir(exist_ok=True)

# Ouvrir fichier de log
log_file = open(LOG_FILE, 'w', encoding='utf-8', buffering=1)

def log(msg):
    """Écrit dans le fichier ET à l'écran"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    line = f"[{timestamp}] {msg}"
    print(line)
    log_file.write(line + '\n')
    log_file.flush()
    sys.stdout.flush()

log("="*70)
log("TEST MIGRATION AVEC LOG TEMPS RÉEL")
log("="*70)
log("")
log(f"📁 Fichier de log: {LOG_FILE.absolute()}")
log("   Ouvrez ce fichier avec Notepad++ pour suivre en temps réel !")
log("")
log("="*70)
log("")

try:
    # Import
    log("📦 Import des modules Python...")
    from connexion_double_v19 import ConnexionDoubleV19
    from framework.migrateur_generique import MigrateurGenerique
    from framework.gestionnaire_configuration import GestionnaireConfiguration
    log("✅ Imports OK")
    log("")
    
    # Connexion
    log("="*70)
    log("🔌 CONNEXION AUX BASES")
    log("="*70)
    log("")
    
    conn = ConnexionDoubleV19()
    
    log("Connexion SOURCE...")
    if not conn.connecter_source():
        log("❌ Connexion SOURCE échouée")
        sys.exit(1)
    log("✅ SOURCE connectée")
    
    log("Connexion DESTINATION (lysa-migration-2)...")
    if not conn.connecter_destination():
        log("❌ Connexion DESTINATION échouée")
        sys.exit(1)
    log("✅ DESTINATION connectée")
    log("")
    
    # Test simple sur TAXES
    log("="*70)
    log("📊 TEST MODULE: account.tax (TAXES)")
    log("="*70)
    log("")
    
    # Compter
    log("Comptage taxes SOURCE...")
    count = conn.executer_source('account.tax', 'search_count', [])
    log(f"✅ {count} taxes trouvées en SOURCE")
    log("")
    
    # Configuration
    log("Configuration migration...")
    configs = GestionnaireConfiguration.obtenir_toutes_configs()
    config = configs['account.tax'].copy()
    config['mode_test'] = True
    config['limite_test'] = 5
    config['mode_interactif'] = False
    log(f"✅ Mode TEST: 5 premières taxes")
    log("")
    
    # Création migrateur
    log("Initialisation du migrateur...")
    migrateur = MigrateurGenerique(conn, 'account.tax', config)
    log("✅ Migrateur initialisé")
    log("")
    
    # Migration
    log("="*70)
    log("🚀 LANCEMENT MIGRATION")
    log("="*70)
    log("")
    log("⏳ Migration en cours...")
    log("   (Cela peut prendre 30-60 secondes)")
    log("   (Le fichier de log se met à jour automatiquement)")
    log("")
    
    stats = migrateur.migrer()
    
    log("")
    log("="*70)
    log("📊 RÉSULTATS MIGRATION")
    log("="*70)
    log(f"Nouveaux    : {stats['nouveaux']}")
    log(f"Existants   : {stats['existants']}")
    log(f"Erreurs     : {stats['erreurs']}")
    log(f"Skippés     : {stats['skipped']}")
    log("")
    
    # Auto-corrections
    if hasattr(migrateur, 'auto_correcteur'):
        corrections = migrateur.auto_correcteur.corrections_appliquees
        if corrections:
            log(f"🤖 Auto-corrections appliquées: {len(corrections)}")
            log("")
            types = {}
            for corr in corrections:
                t = corr.get('type', 'N/A')
                types[t] = types.get(t, 0) + 1
            for t, count in types.items():
                log(f"   - {t}: {count}")
            log("")
    
    # Conclusion
    if stats['erreurs'] == 0:
        log("="*70)
        log("✅ MIGRATION RÉUSSIE !")
        log("="*70)
        log("")
        log("Les 5 premières taxes ont été migrées avec succès.")
        log("Vous pouvez maintenant lancer la migration complète.")
    else:
        log("="*70)
        log(f"⚠️ MIGRATION AVEC {stats['erreurs']} ERREUR(S)")
        log("="*70)
        log("")
        log("Consultez les détails dans les logs.")

except Exception as e:
    log("")
    log("="*70)
    log("❌ ERREUR")
    log("="*70)
    log(f"Type: {type(e).__name__}")
    log(f"Message: {str(e)}")
    log("")
    
    import traceback
    log("Traceback complet:")
    for line in traceback.format_exc().split('\n'):
        log(line)

finally:
    log("")
    log("="*70)
    log("🏁 TEST TERMINÉ")
    log("="*70)
    log(f"Heure de fin: {datetime.now().strftime('%H:%M:%S')}")
    log("")
    log(f"📁 Log complet dans: {LOG_FILE.absolute()}")
    log("")
    log_file.close()

print("")
print("="*70)
print("IMPORTANT:")
print("="*70)
print(f"Le fichier de log est: {LOG_FILE.absolute()}")
print("")
print("Vous pouvez maintenant le consulter !")
print("="*70)
