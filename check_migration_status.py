#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VÉRIFICATION DU STATUT DE MIGRATION
===================================
Script pour vérifier l'état de la migration en cours ou terminée
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

def check_logs():
    """Vérifie les logs de migration"""
    print("\n" + "=" * 70)
    print("VÉRIFICATION DES LOGS")
    print("=" * 70)
    
    logs_dir = Path(__file__).parent / 'logs'
    
    if not logs_dir.exists():
        print("❌ Aucun dossier de logs trouvé")
        return False
    
    # Trouver les logs récents (dernières 24h)
    recent_logs = []
    cutoff_time = datetime.now() - timedelta(days=1)
    
    for log_file in logs_dir.glob('*.log'):
        mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
        if mtime > cutoff_time:
            recent_logs.append((log_file, mtime))
    
    if not recent_logs:
        print("⚠️  Aucun log récent (dernières 24h)")
        return False
    
    # Trier par date
    recent_logs.sort(key=lambda x: x[1], reverse=True)
    
    print(f"\n✓ {len(recent_logs)} log(s) récent(s) trouvé(s):\n")
    
    for log_file, mtime in recent_logs[:5]:  # Afficher les 5 plus récents
        size_kb = log_file.stat().st_size / 1024
        time_ago = datetime.now() - mtime
        hours_ago = time_ago.total_seconds() / 3600
        
        print(f"📄 {log_file.name}")
        print(f"   Taille: {size_kb:.1f} KB")
        print(f"   Modifié: il y a {hours_ago:.1f}h")
        
        # Afficher les dernières lignes
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                last_lines = lines[-5:] if len(lines) >= 5 else lines
                
                has_error = any('ERROR' in line or '✗' in line for line in last_lines)
                has_success = any('✓' in line or 'SUCCESS' in line or 'succès' in line.lower() for line in last_lines)
                
                if has_error:
                    print("   Status: ❌ Erreurs détectées")
                elif has_success:
                    print("   Status: ✅ Succès")
                else:
                    print("   Status: ⏳ En cours ou incomplet")
                
                print("   Dernières lignes:")
                for line in last_lines:
                    print(f"   {line.rstrip()[:70]}")
        except Exception as e:
            print(f"   ⚠️  Impossible de lire: {e}")
        
        print()
    
    return True


def check_mapping_files():
    """Vérifie les fichiers de mapping"""
    print("=" * 70)
    print("VÉRIFICATION DES FICHIERS DE MAPPING")
    print("=" * 70)
    
    logs_dir = Path(__file__).parent / 'logs'
    mapping_files = {
        'account_mapping.json': 'Mapping des comptes comptables',
        'partner_mapping.json': 'Mapping des partenaires',
    }
    
    found = False
    for filename, description in mapping_files.items():
        filepath = logs_dir / filename
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
            print(f"\n✓ {description}")
            print(f"  Fichier: {filename}")
            print(f"  Taille: {size_kb:.1f} KB")
            print(f"  Modifié: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
            found = True
        else:
            print(f"\n⚠️  {description} non trouvé")
    
    return found


def check_scheduled_tasks_log():
    """Vérifie le log des tâches planifiées"""
    print("\n" + "=" * 70)
    print("VÉRIFICATION DES TÂCHES PLANIFIÉES")
    print("=" * 70)
    
    log_file = Path(__file__).parent / 'logs' / 'scheduled_tasks.log'
    
    if not log_file.exists():
        print("⚠️  Aucune tâche planifiée n'a encore été exécutée")
        return False
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            print("⚠️  Fichier de log vide")
            return False
        
        print(f"\n✓ {len(lines)} entrée(s) dans le log\n")
        print("Dernières exécutions:\n")
        
        # Afficher les 10 dernières lignes
        for line in lines[-10:]:
            if 'ERROR' in line:
                print(f"❌ {line.rstrip()}")
            elif 'INFO' in line:
                print(f"ℹ️  {line.rstrip()}")
            else:
                print(f"   {line.rstrip()}")
        
        # Statistiques
        errors = sum(1 for line in lines if 'ERROR' in line)
        infos = sum(1 for line in lines if 'INFO' in line)
        
        print(f"\nStatistiques:")
        print(f"  Total: {len(lines)} entrées")
        print(f"  Infos: {infos}")
        print(f"  Erreurs: {errors}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lecture log: {e}")
        return False


def get_system_info():
    """Affiche les informations système"""
    print("\n" + "=" * 70)
    print("INFORMATIONS SYSTÈME")
    print("=" * 70)
    
    print(f"\nPython: {sys.version.split()[0]}")
    print(f"Plateforme: {sys.platform}")
    print(f"Dossier actuel: {os.getcwd()}")
    print(f"Date/Heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


def main():
    """Fonction principale"""
    print("\n" + "█" * 70)
    print("  VÉRIFICATION DU STATUT DE MIGRATION LYSA v19")
    print("█" * 70)
    
    get_system_info()
    check_logs()
    check_mapping_files()
    check_scheduled_tasks_log()
    
    print("\n" + "=" * 70)
    print("VÉRIFICATION TERMINÉE")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()

