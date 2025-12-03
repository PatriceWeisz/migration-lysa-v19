@echo off
chcp 65001 >nul
cls

echo ======================================================================
echo MIGRATION DES UTILISATEURS
echo ======================================================================
echo.
echo [ETAPE 1/3] Affichage de ce message... OK
echo [ETAPE 2/3] Chargement Python... EN COURS (10-15 secondes)
echo.
echo PATIENTEZ SVP - NE PAS FERMER
echo.

set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8

python migrer_utilisateurs.py

echo.
echo ======================================================================
echo TERMINE - Appuyez sur une touche pour fermer
echo ======================================================================
pause >nul

