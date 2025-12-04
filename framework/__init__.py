"""
FRAMEWORK DE MIGRATION ODOO
============================
Framework professionnel et réutilisable pour migrations Odoo
Gère automatiquement les différences de champs entre versions
"""

from .migrateur_generique import MigrateurGenerique
from .gestionnaire_configuration import GestionnaireConfiguration
from .analyseur_differences_champs import AnalyseurDifferencesChamps

__all__ = [
    'MigrateurGenerique', 
    'GestionnaireConfiguration',
    'AnalyseurDifferencesChamps'
]

