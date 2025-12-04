@echo off
chcp 65001 >nul
cls

echo ======================================================================
echo MIGRATION PARAMETRES CONFIGURATION
echo ======================================================================
echo.
echo ⚠️ CRITIQUE - A LANCER AVANT LA MIGRATION DES DONNEES
echo.
echo Ce script migre les parametres de configuration:
echo   1. ir.config_parameter (parametres systeme)
echo   2. res.company (parametres societe)
echo   3. ir.sequence (sequences factures, BL, etc.)
echo.
echo Pourquoi c est critique ?
echo   - Les parametres activent des fonctionnalites
echo   - Les fonctionnalites ajoutent des champs
echo   - Les champs doivent exister AVANT de migrer les donnees
echo.
echo Duree: 2-3 minutes
echo.
echo ======================================================================
pause
echo.

set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8

python migrer_parametres_configuration.py

echo.
echo ======================================================================
echo MIGRATION PARAMETRES TERMINEE
echo ======================================================================
echo.
echo Consultez le rapport dans: logs\migration_parametres_*.txt
echo.
echo Prochaine etape:
echo   1. Verifier que les fonctionnalites sont activees dans Odoo DEST
echo   2. Lancer la migration des donnees
echo.
pause

