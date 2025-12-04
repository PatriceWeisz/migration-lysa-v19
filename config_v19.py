#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CONFIGURATION POUR MIGRATION LYSA V19
=====================================
Configuration des bases source et destination pour la migration vers Odoo v19
"""

import os
from datetime import datetime

# ============================================================================
# CONFIGURATION BASE SOURCE
# ============================================================================
SOURCE_CONFIG = {
    'URL': 'https://lysa-old1.odoo.com/',
    'DB': 'lysa-old1-lysa-db-25736325',
    'USER': 'support@senedoo.com',
    'PASS': 'Senedoo@2025',
    'VERSION': 'v16',  # Version Odoo source
}

# ============================================================================
# CONFIGURATION BASE DESTINATION (ODOO V19) - SAAS
# ============================================================================
DEST_CONFIG_V19 = {
    'URL': 'https://lysa-migration-2.odoo.com/',
    'DB': 'lysa-migration-2',  # Base SaaS Odoo (NOUVELLE BASE PROPRE)
    'USER': 'support@senedoo.com',
    'PASS': 'senedoo@2025',
    'VERSION': 'v19',  # Version Odoo destination
    'TYPE': 'SAAS',  # Type de base (SAAS ou ON-PREMISE)
}

# ============================================================================
# PARAMÈTRES DE MIGRATION
# ============================================================================
MIGRATION_PARAMS = {
    # Limites et lots (optimisé pour base SaaS)
    'BATCH_SIZE': 100,              # Taille des lots (réduit pour SaaS)
    'MAX_RECORDS': None,            # None = tous, ou nombre limite pour tests
    'PARALLEL_WORKERS': 2,          # Nombre de workers (réduit pour éviter throttling SaaS)
    
    # Retry et timeout (optimisé pour base SaaS)
    'MAX_RETRY': 5,                 # Nombre de tentatives max (augmenté pour SaaS)
    'RETRY_DELAY': 10,              # Délai entre tentatives (augmenté pour SaaS)
    'TIMEOUT': 600,                 # Timeout requêtes (augmenté pour SaaS - 10 min)
    
    # Journaux et comptes
    'JOURNAL_CODE': 'MIGV19',
    'JOURNAL_NAME': 'Migration v19',
    'COMPTE_CONTREPARTIE': '471000',
    'COMPTE_ECART': '658000',       # Compte pour écarts de migration
    
    # Types de données à migrer
    'MIGRER_PLAN_COMPTABLE': True,
    'MIGRER_PARTENAIRES': True,
    'MIGRER_PRODUITS': True,
    'MIGRER_FACTURES_CLIENTS': True,
    'MIGRER_FACTURES_FOURNISSEURS': True,
    'MIGRER_PAIEMENTS': True,
    
    # Options de migration
    'VERIFIER_DOUBLONS': True,      # Vérifier doublons avant insertion
    'CREER_SEQUENCES': True,        # Recréer les séquences
    'MAPPER_COMPTES': True,         # Mapper anciens/nouveaux comptes
    'CONSERVER_DATES': True,        # Conserver dates originales
    'MODE_SIMULATION': False,       # True = simulation sans écriture
    
    # Cache et optimisation
    'CACHE_ENABLED': True,
    'CACHE_SIZE': 10000,
    'PREFETCH_DATA': True,
    
    # Logs
    'LOG_LEVEL': 'INFO',            # DEBUG, INFO, WARNING, ERROR
    'LOG_TO_FILE': True,
    'LOG_DIR': 'logs',
}

# ============================================================================
# MAPPING DES MODÈLES (V16 -> V19)
# ============================================================================
# Certains modèles peuvent avoir changé entre les versions
MODELS_MAPPING = {
    'account.move': 'account.move',           # Inchangé
    'account.move.line': 'account.move.line', # Inchangé
    'res.partner': 'res.partner',             # Inchangé
    'product.product': 'product.product',     # Inchangé
    'account.account': 'account.account',     # Inchangé
    'account.journal': 'account.journal',     # Inchangé
    # Ajouter ici les modèles qui auraient changé
}

# ============================================================================
# CHAMPS SPÉCIFIQUES V19
# ============================================================================
# Nouveaux champs ou champs modifiés dans Odoo v19
V19_NEW_FIELDS = {
    'account.move': [
        # Ajouter les nouveaux champs spécifiques à v19
        # 'nouveau_champ_v19',
    ],
    'account.move.line': [
        # Nouveaux champs pour les lignes d'écriture
    ],
    'res.partner': [
        # Nouveaux champs partenaires
    ],
}

# Champs obsolètes (à ne pas migrer)
V19_DEPRECATED_FIELDS = {
    'account.move': [
        # Champs qui n'existent plus en v19
    ],
    'account.move.line': [],
    'res.partner': [],
}

# ============================================================================
# CONFIGURATION DES LOGS
# ============================================================================
LOG_CONFIG = {
    'DIR': os.path.join(os.path.dirname(__file__), 'logs'),
    'FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'DATE_FORMAT': '%Y-%m-%d %H:%M:%S',
    'FILE_PREFIX': f'migration_v19_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
    'MAX_SIZE': 10 * 1024 * 1024,  # 10 MB
    'BACKUP_COUNT': 5,
}

# ============================================================================
# FILTRES DE DONNÉES
# ============================================================================
# Filtres pour sélectionner les données à migrer
DATA_FILTERS = {
    'factures_clients': [
        ('move_type', '=', 'out_invoice'),
        ('state', '=', 'posted'),
        # ('date', '>=', '2023-01-01'),  # Exemple : depuis une date
    ],
    'factures_fournisseurs': [
        ('move_type', '=', 'in_invoice'),
        ('state', '=', 'posted'),
    ],
    'avoirs_clients': [
        ('move_type', '=', 'out_refund'),
        ('state', '=', 'posted'),
    ],
    'avoirs_fournisseurs': [
        ('move_type', '=', 'in_refund'),
        ('state', '=', 'posted'),
    ],
}

# ============================================================================
# ORDRE DE MIGRATION
# ============================================================================
# Ordre dans lequel migrer les données (important pour les dépendances)
MIGRATION_ORDER = [
    'plan_comptable',     # 1. Plan comptable en premier
    'journaux',           # 2. Journaux comptables
    'partenaires',        # 3. Clients et fournisseurs
    'produits',           # 4. Produits et services
    'factures_clients',   # 5. Factures clients
    'factures_fournisseurs',  # 6. Factures fournisseurs
    'avoirs_clients',     # 7. Avoirs clients
    'avoirs_fournisseurs', # 8. Avoirs fournisseurs
    'paiements',          # 9. Paiements
]

# ============================================================================
# VALIDATION POST-MIGRATION
# ============================================================================
VALIDATION_CONFIG = {
    'VERIFIER_SOLDES': True,
    'VERIFIER_SEQUENCES': True,
    'VERIFIER_EQUILIBRE': True,
    'VERIFIER_PARTENAIRES': True,
    'TOLERANCE_ECART': 0.01,  # Tolérance pour écarts (centimes)
}

# ============================================================================
# HELPERS
# ============================================================================

def get_source_url():
    """Retourne l'URL complète de la base source"""
    return SOURCE_CONFIG['URL']

def get_dest_url():
    """Retourne l'URL complète de la base destination"""
    return DEST_CONFIG_V19['URL']

def is_simulation_mode():
    """Vérifie si on est en mode simulation"""
    return MIGRATION_PARAMS.get('MODE_SIMULATION', False)

def get_log_file():
    """Retourne le chemin du fichier de log"""
    log_dir = LOG_CONFIG['DIR']
    os.makedirs(log_dir, exist_ok=True)
    prefix = LOG_CONFIG['FILE_PREFIX']
    return os.path.join(log_dir, f'{prefix}.log')

if __name__ == "__main__":
    print("=" * 70)
    print("CONFIGURATION MIGRATION LYSA V19")
    print("=" * 70)
    print(f"\nBase SOURCE:")
    print(f"  URL: {SOURCE_CONFIG['URL']}")
    print(f"  DB:  {SOURCE_CONFIG['DB']}")
    print(f"  Version: {SOURCE_CONFIG['VERSION']}")
    print(f"\nBase DESTINATION:")
    print(f"  URL: {DEST_CONFIG_V19['URL']}")
    print(f"  DB:  {DEST_CONFIG_V19['DB']}")
    print(f"  Version: {DEST_CONFIG_V19['VERSION']}")
    print(f"\nParamètres:")
    print(f"  Batch size: {MIGRATION_PARAMS['BATCH_SIZE']}")
    print(f"  Workers: {MIGRATION_PARAMS['PARALLEL_WORKERS']}")
    print(f"  Mode simulation: {is_simulation_mode()}")
    print(f"\nFichier log: {get_log_file()}")
    print("=" * 70)

