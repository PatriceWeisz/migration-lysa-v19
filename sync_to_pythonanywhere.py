#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SYNCHRONISATION AUTOMATIQUE VERS PYTHONANYWHERE
===============================================
Script pour synchroniser les fichiers locaux vers PythonAnywhere via SFTP
"""

import os
import sys
from pathlib import Path

try:
    import paramiko
    from scp import SCPClient
except ImportError:
    print("❌ Modules manquants. Installation...")
    print("   pip install paramiko scp")
    sys.exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================
PYTHONANYWHERE_CONFIG = {
    'host': 'ssh.pythonanywhere.com',
    'username': 'VOTRE_USERNAME',  # À MODIFIER avec votre username PythonAnywhere
    'password': 'VOTRE_MOT_DE_PASSE',  # À MODIFIER (ou utilisez une clé SSH)
    'remote_path': '/home/VOTRE_USERNAME/migration_lysa_v19',  # À MODIFIER
    'port': 22
}

# Fichiers/dossiers à ignorer
IGNORE_PATTERNS = [
    '__pycache__',
    '.git',
    '.venv',
    '*.pyc',
    'logs',
    '.gitignore',
    'sync_to_pythonanywhere.py',  # Ne pas s'auto-uploader
]

# ============================================================================
# FONCTIONS
# ============================================================================

def should_ignore(path_str):
    """Vérifie si un fichier doit être ignoré"""
    path = Path(path_str)
    
    for pattern in IGNORE_PATTERNS:
        if pattern.startswith('*'):
            # Pattern avec wildcard
            if path.name.endswith(pattern[1:]):
                return True
        else:
            # Pattern exact
            if pattern in str(path):
                return True
    
    return False


def create_ssh_client(config):
    """Crée un client SSH"""
    print(f"📡 Connexion à {config['host']}...")
    
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        client.connect(
            hostname=config['host'],
            username=config['username'],
            password=config['password'],
            port=config['port']
        )
        print("✓ Connexion SSH établie")
        return client
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return None


def sync_files(ssh_client, config):
    """Synchronise les fichiers"""
    local_path = Path(__file__).parent
    remote_path = config['remote_path']
    
    print(f"\n📂 Synchronisation de {local_path} vers {remote_path}...")
    
    # Créer le dossier distant s'il n'existe pas
    stdin, stdout, stderr = ssh_client.exec_command(f'mkdir -p {remote_path}')
    stdout.channel.recv_exit_status()
    
    # Créer le client SCP
    with SCPClient(ssh_client.get_transport()) as scp:
        files_synced = 0
        files_skipped = 0
        
        # Parcourir tous les fichiers
        for item in local_path.rglob('*'):
            if item.is_file():
                relative_path = item.relative_to(local_path)
                
                if should_ignore(str(relative_path)):
                    files_skipped += 1
                    continue
                
                remote_file = f"{remote_path}/{relative_path.as_posix()}"
                
                # Créer les dossiers parents si nécessaire
                remote_dir = str(Path(remote_file).parent)
                stdin, stdout, stderr = ssh_client.exec_command(f'mkdir -p {remote_dir}')
                stdout.channel.recv_exit_status()
                
                # Upload le fichier
                try:
                    scp.put(str(item), remote_file)
                    print(f"  ✓ {relative_path}")
                    files_synced += 1
                except Exception as e:
                    print(f"  ✗ {relative_path}: {e}")
    
    print(f"\n📊 Résumé:")
    print(f"  - Fichiers synchronisés: {files_synced}")
    print(f"  - Fichiers ignorés: {files_skipped}")
    
    return files_synced


def main():
    """Fonction principale"""
    print("\n" + "=" * 70)
    print("  SYNCHRONISATION VERS PYTHONANYWHERE")
    print("=" * 70 + "\n")
    
    # Vérifier la configuration
    if PYTHONANYWHERE_CONFIG['username'] == 'VOTRE_USERNAME':
        print("❌ Erreur: Veuillez configurer votre username PythonAnywhere")
        print("   Éditez ce fichier et modifiez PYTHONANYWHERE_CONFIG")
        return False
    
    if PYTHONANYWHERE_CONFIG['password'] == 'VOTRE_MOT_DE_PASSE':
        print("❌ Erreur: Veuillez configurer votre mot de passe")
        print("   Éditez ce fichier et modifiez PYTHONANYWHERE_CONFIG")
        return False
    
    # Créer la connexion SSH
    ssh_client = create_ssh_client(PYTHONANYWHERE_CONFIG)
    if not ssh_client:
        return False
    
    try:
        # Synchroniser les fichiers
        files_synced = sync_files(ssh_client, PYTHONANYWHERE_CONFIG)
        
        if files_synced > 0:
            print("\n✓ Synchronisation terminée avec succès!")
            
            # Redémarrer le virtualenv (optionnel)
            print("\n⚠️  N'oubliez pas de redémarrer vos scripts sur PythonAnywhere")
            print("   si nécessaire.")
            
            return True
        else:
            print("\n⚠️  Aucun fichier synchronisé")
            return False
            
    finally:
        ssh_client.close()
        print("\n🔒 Connexion fermée")


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

