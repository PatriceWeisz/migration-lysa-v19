#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCRIPT POUR TÂCHES PLANIFIÉES PYTHONANYWHERE
=============================================
Wrapper pour exécuter les migrations via tâches planifiées
avec gestion d'erreurs et notifications
"""

import sys
import os
import traceback
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Ajouter le répertoire du script au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configuration
NOTIFICATION_EMAIL = "support@senedoo.com"  # Email pour recevoir les notifications
SEND_EMAIL_ON_ERROR = False  # Activer pour recevoir des emails en cas d'erreur
SEND_EMAIL_ON_SUCCESS = False  # Activer pour recevoir des emails de succès

def send_notification(subject, message, is_error=False):
    """Envoie une notification email (si configuré)"""
    if not SEND_EMAIL_ON_ERROR and is_error:
        return
    if not SEND_EMAIL_ON_SUCCESS and not is_error:
        return
    
    try:
        # Configuration SMTP (à adapter selon votre fournisseur)
        # Pour PythonAnywhere, vous pouvez utiliser un service externe comme SendGrid
        print(f"\n📧 Notification: {subject}")
        print(f"Message: {message[:200]}...")
        
        # TODO: Implémenter l'envoi d'email réel si nécessaire
        # msg = MIMEMultipart()
        # msg['From'] = NOTIFICATION_EMAIL
        # msg['To'] = NOTIFICATION_EMAIL
        # msg['Subject'] = subject
        # msg.attach(MIMEText(message, 'plain'))
        
    except Exception as e:
        print(f"Erreur envoi notification: {e}")


def log_execution(message, is_error=False):
    """Log l'exécution dans un fichier"""
    log_file = os.path.join(
        os.path.dirname(__file__),
        'logs',
        'scheduled_tasks.log'
    )
    
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    level = 'ERROR' if is_error else 'INFO'
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}] {level}: {message}\n")


def run_migration():
    """Exécute la migration complète"""
    print("\n" + "=" * 70)
    print("EXÉCUTION TÂCHE PLANIFIÉE - MIGRATION LYSA v19")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")
    
    try:
        # Import des modules nécessaires
        from migration_plan_comptable import main as migrate_plan_comptable
        from migration_partenaires import main as migrate_partenaires
        from verification_v19 import main as verify_migration
        
        log_execution("Démarrage de la tâche planifiée")
        
        # 1. Migration du plan comptable
        print("\n📊 Étape 1/3 : Migration du plan comptable...")
        success_plan = migrate_plan_comptable()
        
        if not success_plan:
            error_msg = "Échec de la migration du plan comptable"
            log_execution(error_msg, is_error=True)
            send_notification(
                "❌ Erreur Migration LYSA v19",
                error_msg,
                is_error=True
            )
            return False
        
        log_execution("Plan comptable migré avec succès")
        
        # 2. Migration des partenaires
        print("\n👥 Étape 2/3 : Migration des partenaires...")
        success_partners = migrate_partenaires()
        
        if not success_partners:
            error_msg = "Échec de la migration des partenaires"
            log_execution(error_msg, is_error=True)
            send_notification(
                "⚠️ Erreur Partielle Migration LYSA v19",
                f"{error_msg}\nLe plan comptable a été migré avec succès.",
                is_error=True
            )
            return False
        
        log_execution("Partenaires migrés avec succès")
        
        # 3. Vérification
        print("\n✅ Étape 3/3 : Vérification...")
        success_verify = verify_migration()
        
        if not success_verify:
            warning_msg = "Vérification a détecté des problèmes"
            log_execution(warning_msg, is_error=True)
            send_notification(
                "⚠️ Vérification Migration LYSA v19",
                warning_msg,
                is_error=True
            )
        
        # Succès complet
        success_msg = "Migration complète exécutée avec succès"
        log_execution(success_msg)
        send_notification(
            "✅ Migration LYSA v19 Réussie",
            success_msg,
            is_error=False
        )
        
        print("\n" + "=" * 70)
        print("✅ TÂCHE PLANIFIÉE TERMINÉE AVEC SUCCÈS")
        print("=" * 70 + "\n")
        
        return True
        
    except Exception as e:
        error_msg = f"Erreur critique: {str(e)}\n{traceback.format_exc()}"
        log_execution(error_msg, is_error=True)
        send_notification(
            "🚨 Erreur Critique Migration LYSA v19",
            error_msg,
            is_error=True
        )
        
        print("\n" + "=" * 70)
        print("❌ ERREUR CRITIQUE")
        print("=" * 70)
        print(error_msg)
        
        return False


def main():
    """Point d'entrée principal"""
    try:
        success = run_migration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Tâche interrompue par l'utilisateur")
        log_execution("Tâche interrompue par l'utilisateur", is_error=True)
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erreur fatale: {e}")
        log_execution(f"Erreur fatale: {e}", is_error=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

