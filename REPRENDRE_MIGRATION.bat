@echo off
chcp 65001 >nul
cls

echo ======================================================================
echo REPRENDRE MIGRATION INTERROMPUE
echo ======================================================================
echo.
echo Ce script va:
echo   - Lire le dernier checkpoint
echo   - Verifier l integrite des modules deja migres
echo   - Reprendre la migration la ou elle s est arretee
echo.
echo Utiliser ce script si:
echo   - Migration interrompue (Ctrl+C, crash, coupure)
echo   - Erreur reseau
echo   - Arret manuel
echo.
echo ======================================================================
pause
echo.

set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8

python reprendre_migration.py

echo.
echo ======================================================================
echo REPRISE TERMINEE
echo ======================================================================
pause

