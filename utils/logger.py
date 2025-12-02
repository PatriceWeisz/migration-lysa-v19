#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SYSTÈME DE LOGGING POUR MIGRATION V19
=====================================
Gestion centralisée des logs avec couleurs et fichiers
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Essayer d'importer colorlog pour les logs colorés
try:
    import colorlog
    COLORLOG_AVAILABLE = True
except ImportError:
    COLORLOG_AVAILABLE = False

# Ajouter le répertoire parent au path pour importer config_v19
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_v19 import LOG_CONFIG

class MigrationLogger:
    """Classe pour gérer les logs de migration"""
    
    def __init__(self, name='migration_v19', log_to_file=True, log_level='INFO'):
        self.name = name
        self.log_to_file = log_to_file
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger = None
        self._setup_logger()
        
    def _setup_logger(self):
        """Configure le logger"""
        # Créer le logger
        self.logger = logging.getLogger(self.name)
        self.logger.setLevel(self.log_level)
        
        # Éviter les doublons
        if self.logger.handlers:
            return
        
        # Format des logs
        log_format = LOG_CONFIG['FORMAT']
        date_format = LOG_CONFIG['DATE_FORMAT']
        
        # Handler console avec couleurs
        if COLORLOG_AVAILABLE:
            console_handler = colorlog.StreamHandler()
            console_formatter = colorlog.ColoredFormatter(
                '%(log_color)s%(asctime)s - %(levelname)-8s%(reset)s - %(message)s',
                datefmt=date_format,
                log_colors={
                    'DEBUG': 'cyan',
                    'INFO': 'green',
                    'WARNING': 'yellow',
                    'ERROR': 'red',
                    'CRITICAL': 'red,bg_white',
                }
            )
            console_handler.setFormatter(console_formatter)
        else:
            console_handler = logging.StreamHandler()
            console_formatter = logging.Formatter(log_format, datefmt=date_format)
            console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(console_handler)
        
        # Handler fichier
        if self.log_to_file:
            log_dir = Path(LOG_CONFIG['DIR'])
            log_dir.mkdir(exist_ok=True)
            
            log_file = log_dir / f"{LOG_CONFIG['FILE_PREFIX']}_{self.name}.log"
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_formatter = logging.Formatter(log_format, datefmt=date_format)
            file_handler.setFormatter(file_formatter)
            
            self.logger.addHandler(file_handler)
            self.logger.info(f"Logs sauvegardés dans: {log_file}")
    
    def debug(self, message):
        """Log niveau DEBUG"""
        self.logger.debug(message)
    
    def info(self, message):
        """Log niveau INFO"""
        self.logger.info(message)
    
    def warning(self, message):
        """Log niveau WARNING"""
        self.logger.warning(message)
    
    def error(self, message):
        """Log niveau ERROR"""
        self.logger.error(message)
    
    def critical(self, message):
        """Log niveau CRITICAL"""
        self.logger.critical(message)
    
    def section(self, title):
        """Affiche une section"""
        separator = "=" * 70
        self.info(separator)
        self.info(title.center(70))
        self.info(separator)
    
    def subsection(self, title):
        """Affiche une sous-section"""
        separator = "-" * 70
        self.info(separator)
        self.info(title)
        self.info(separator)


def setup_logger(name='migration_v19', log_to_file=True, log_level='INFO'):
    """Crée et configure un logger"""
    return MigrationLogger(name, log_to_file, log_level)


def get_logger(name='migration_v19'):
    """Récupère un logger existant"""
    return logging.getLogger(name)


# Logger par défaut
default_logger = setup_logger()


if __name__ == "__main__":
    # Test du logger
    logger = setup_logger('test_logger')
    
    logger.section("TEST DU SYSTÈME DE LOGGING")
    logger.info("Ceci est un message INFO")
    logger.debug("Ceci est un message DEBUG")
    logger.warning("Ceci est un message WARNING")
    logger.error("Ceci est un message ERROR")
    logger.critical("Ceci est un message CRITICAL")
    
    logger.subsection("Test des sous-sections")
    logger.info("Les logs sont sauvegardés automatiquement")

