@echo off
chcp 65001 >nul
cls

echo ======================================================================
echo TEST MIGRATION AVEC LOG TEMPS REEL
echo ======================================================================
echo.
echo Ce script va:
echo   1. Lancer la migration test
echo   2. Ouvrir le fichier log automatiquement
echo.
echo Vous pourrez suivre la progression EN TEMPS REEL dans le fichier !
echo.
echo ======================================================================
pause
echo.

echo Demarrage du test...
echo.

REM Créer le dossier logs si nécessaire
if not exist logs mkdir logs

REM Lancer le test en arrière-plan
start /B python test_avec_log_temps_reel.py

REM Attendre 2 secondes que le fichier soit créé
timeout /t 2 /nobreak >nul

REM Ouvrir le fichier log dans Notepad
echo Ouverture du fichier log...
start notepad "logs\test_migration_temps_reel.log"

echo.
echo ======================================================================
echo Le fichier log est ouvert !
echo ======================================================================
echo.
echo Le test tourne en arriere-plan.
echo Suivez la progression dans le fichier Notepad.
echo.
echo Appuyez sur une touche pour attendre la fin du test...
pause >nul

echo.
echo Test termine !
echo.
pause

