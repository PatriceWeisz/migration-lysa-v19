@echo off
chcp 65001 >nul
cls

echo ======================================================================
echo VERIFICATION MODULES INSTALLES
echo ======================================================================
echo.
echo ⚠️ CRITIQUE AVANT MIGRATION
echo.
echo Ce script verifie que tous les modules de la BASE SOURCE
echo sont bien installes dans la BASE DESTINATION.
echo.
echo Si des modules manquent:
echo   - Leurs donnees NE POURRONT PAS etre migrees
echo   - Vous devez les installer AVANT de lancer la migration
echo.
echo Duree: 1-2 minutes
echo.
echo ======================================================================
pause
echo.

set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8

python verifier_modules_installes.py

echo.
echo ======================================================================
echo VERIFICATION TERMINEE
echo ======================================================================
echo.
echo Consultez le rapport dans: logs\verification_modules_*.txt
echo.
pause

