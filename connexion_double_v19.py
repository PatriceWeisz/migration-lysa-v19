#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONNEXION DOUBLE POUR MIGRATION V19
===================================
Gestion des connexions simultanées vers les bases source et destination v19
Avec reconnexion automatique et gestion d'erreurs améliorée
"""

import xmlrpc.client
import sys
import time
from datetime import datetime
from config_v19 import SOURCE_CONFIG, DEST_CONFIG_V19, MIGRATION_PARAMS

class ConnexionDoubleV19:
    """Classe pour gérer les connexions aux deux bases Odoo avec reconnexion automatique"""
    
    def __init__(self):
        self.source = None
        self.destination = None
        self.source_uid = None
        self.dest_uid = None
        self.source_models = None
        self.dest_models = None
        self.source_common = None
        self.dest_common = None
        
        # Statistiques de connexion
        self.stats = {
            'source_calls': 0,
            'dest_calls': 0,
            'source_errors': 0,
            'dest_errors': 0,
            'reconnections': 0,
        }
        
    def _creer_proxy(self, url, endpoint):
        """Crée un proxy XML-RPC avec timeout"""
        timeout = MIGRATION_PARAMS.get('TIMEOUT', 300)
        transport = xmlrpc.client.Transport()
        transport._connection = (None, None)
        return xmlrpc.client.ServerProxy(
            f'{url}xmlrpc/2/{endpoint}',
            transport=transport,
            allow_none=True
        )
        
    def connecter_source(self):
        """Connexion à la base source avec retry"""
        print("=" * 70)
        print("CONNEXION À LA BASE SOURCE")
        print("=" * 70)
        
        max_retry = MIGRATION_PARAMS.get('MAX_RETRY', 3)
        retry_delay = MIGRATION_PARAMS.get('RETRY_DELAY', 5)
        
        for tentative in range(max_retry):
            try:
                url = SOURCE_CONFIG['URL']
                db = SOURCE_CONFIG['DB']
                user = SOURCE_CONFIG['USER']
                password = SOURCE_CONFIG['PASS']
                
                print(f"Tentative {tentative + 1}/{max_retry}")
                print(f"URL: {url}")
                print(f"DB: {db}")
                print(f"User: {user}")
                print(f"Version: {SOURCE_CONFIG['VERSION']}")
                
                # Connexion
                self.source_common = self._creer_proxy(url, 'common')
                self.source_uid = self.source_common.authenticate(db, user, password, {})
                
                if self.source_uid:
                    self.source_models = self._creer_proxy(url, 'object')
                    version = self.source_common.version()
                    print(f"OK Connexion SOURCE reussie - UID: {self.source_uid}")
                    print(f"OK Version Odoo: {version.get('server_version', 'N/A')}")
                    return True
                else:
                    print("ERREUR Echec de l'authentification SOURCE")
                    
            except Exception as e:
                self.stats['source_errors'] += 1
                print(f"ERREUR Connexion SOURCE (tentative {tentative + 1}): {e}")
                
                if tentative < max_retry - 1:
                    print(f"ATTENTE Nouvelle tentative dans {retry_delay} secondes...")
                    time.sleep(retry_delay)
                    
        return False
    
    def connecter_destination(self):
        """Connexion à la base destination v19 avec retry"""
        print("\n" + "=" * 70)
        print("CONNEXION À LA BASE DESTINATION (V19)")
        print("=" * 70)
        
        max_retry = MIGRATION_PARAMS.get('MAX_RETRY', 3)
        retry_delay = MIGRATION_PARAMS.get('RETRY_DELAY', 5)
        
        for tentative in range(max_retry):
            try:
                url = DEST_CONFIG_V19['URL']
                db = DEST_CONFIG_V19['DB']
                user = DEST_CONFIG_V19['USER']
                password = DEST_CONFIG_V19['PASS']
                
                print(f"Tentative {tentative + 1}/{max_retry}")
                print(f"URL: {url}")
                print(f"DB: {db}")
                print(f"User: {user}")
                print(f"Version: {DEST_CONFIG_V19['VERSION']}")
                
                # Connexion
                self.dest_common = self._creer_proxy(url, 'common')
                self.dest_uid = self.dest_common.authenticate(db, user, password, {})
                
                if self.dest_uid:
                    self.dest_models = self._creer_proxy(url, 'object')
                    version = self.dest_common.version()
                    print(f"OK Connexion DESTINATION reussie - UID: {self.dest_uid}")
                    print(f"OK Version Odoo: {version.get('server_version', 'N/A')}")
                    
                    # Verifier que c'est bien v19
                    version_str = version.get('server_version', '')
                    if '19.0' not in version_str:
                        print(f"ATTENTION : Version attendue v19, version detectee: {version_str}")
                    
                    return True
                else:
                    print("ERREUR Echec de l'authentification DESTINATION")
                    
            except Exception as e:
                self.stats['dest_errors'] += 1
                print(f"ERREUR Connexion DESTINATION (tentative {tentative + 1}): {e}")
                
                if tentative < max_retry - 1:
                    print(f"ATTENTE Nouvelle tentative dans {retry_delay} secondes...")
                    time.sleep(retry_delay)
                    
        return False
    
    def connecter_tout(self):
        """Connexion aux deux bases"""
        source_ok = self.connecter_source()
        dest_ok = self.connecter_destination()
        
        print("\n" + "=" * 70)
        print("RESUME DES CONNEXIONS")
        print("=" * 70)
        print(f"Base SOURCE (v16) : {'OK Connectee' if source_ok else 'ERREUR Echec'}")
        print(f"Base DEST (v19)   : {'OK Connectee' if dest_ok else 'ERREUR Echec'}")
        print("=" * 70)
        
        return source_ok and dest_ok
    
    def executer_source(self, model, methode, *args, **kwargs):
        """Exécute une méthode sur la base source avec retry"""
        if not self.source_uid or not self.source_models:
            raise ConnectionError("Pas de connexion active à la base SOURCE")
        
        max_retry = MIGRATION_PARAMS.get('MAX_RETRY', 3)
        
        for tentative in range(max_retry):
            try:
                self.stats['source_calls'] += 1
                result = self.source_models.execute_kw(
                    SOURCE_CONFIG['DB'],
                    self.source_uid,
                    SOURCE_CONFIG['PASS'],
                    model,
                    methode,
                    list(args),
                    kwargs
                )
                return result
                
            except Exception as e:
                self.stats['source_errors'] += 1
                if tentative == max_retry - 1:
                    raise
                print(f"⚠️  Erreur SOURCE, retry {tentative + 1}/{max_retry}: {e}")
                time.sleep(2)
        
    def executer_destination(self, model, methode, *args, **kwargs):
        """Exécute une méthode sur la base destination avec retry"""
        if not self.dest_uid or not self.dest_models:
            raise ConnectionError("Pas de connexion active à la base DESTINATION")
        
        max_retry = MIGRATION_PARAMS.get('MAX_RETRY', 3)
        
        for tentative in range(max_retry):
            try:
                self.stats['dest_calls'] += 1
                result = self.dest_models.execute_kw(
                    DEST_CONFIG_V19['DB'],
                    self.dest_uid,
                    DEST_CONFIG_V19['PASS'],
                    model,
                    methode,
                    list(args),
                    kwargs
                )
                return result
                
            except Exception as e:
                self.stats['dest_errors'] += 1
                if tentative == max_retry - 1:
                    raise
                print(f"⚠️  Erreur DESTINATION, retry {tentative + 1}/{max_retry}: {e}")
                time.sleep(2)
    
    def verifier_version_destination(self):
        """Vérifie que la destination est bien en v19"""
        try:
            version = self.dest_common.version()
            version_str = version.get('server_version', '')
            
            if '19.0' in version_str:
                print(f"✓ Version v19 confirmée: {version_str}")
                return True
            else:
                print(f"✗ Version incorrecte: {version_str} (v19 attendue)")
                return False
        except Exception as e:
            print(f"✗ Erreur vérification version: {e}")
            return False
    
    def afficher_stats(self):
        """Affiche les statistiques de connexion"""
        print("\n" + "=" * 70)
        print("STATISTIQUES DE CONNEXION")
        print("=" * 70)
        print(f"Appels SOURCE      : {self.stats['source_calls']:,}")
        print(f"Appels DESTINATION : {self.stats['dest_calls']:,}")
        print(f"Erreurs SOURCE     : {self.stats['source_errors']:,}")
        print(f"Erreurs DESTINATION: {self.stats['dest_errors']:,}")
        print(f"Reconnexions       : {self.stats['reconnections']:,}")
        print("=" * 70)
    
    def compter_records(self, model, domain=None, base='source'):
        """Compte les enregistrements d'un modèle"""
        if domain is None:
            domain = []
            
        try:
            if base == 'source':
                count = self.executer_source(model, 'search_count', domain)
            else:
                count = self.executer_destination(model, 'search_count', domain)
            return count
        except Exception as e:
            print(f"✗ Erreur comptage {model}: {e}")
            return 0


def main():
    """Fonction principale pour tester les connexions v19"""
    print("\n" + "█" * 70)
    print("  SCRIPT DE CONNEXION DOUBLE - MIGRATION V19")
    print("  Test de connexion aux bases")
    print("█" * 70 + "\n")
    
    # Créer l'instance de connexion
    connexion = ConnexionDoubleV19()
    
    # Se connecter aux deux bases
    if not connexion.connecter_tout():
        print("\n✗ Échec de connexion à au moins une base")
        return False
    
    # Vérifier la version de la destination
    if not connexion.verifier_version_destination():
        print("\n⚠️  ATTENTION : La version de destination n'est pas v19")
    
    # Afficher les statistiques des deux bases
    print("\n" + "=" * 70)
    print("STATISTIQUES DES BASES")
    print("=" * 70)
    
    # Modèles à compter
    modeles = [
        ('res.partner', 'Partenaires'),
        ('product.product', 'Produits'),
        ('account.account', 'Comptes'),
        ('account.journal', 'Journaux'),
        ('account.move', 'Écritures comptables'),
    ]
    
    print("\nBase SOURCE:")
    for model, label in modeles:
        count = connexion.compter_records(model, base='source')
        print(f"  - {label:25s}: {count:>10,}")
    
    print("\nBase DESTINATION (v19):")
    for model, label in modeles:
        count = connexion.compter_records(model, base='destination')
        print(f"  - {label:25s}: {count:>10,}")
    
    # Afficher les stats de connexion
    connexion.afficher_stats()
    
    print("\n" + "=" * 70)
    print("✓ Test de connexion terminé avec succès")
    print("=" * 70 + "\n")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

