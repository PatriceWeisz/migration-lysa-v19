@echo off
chcp 65001 >nul
cls

echo ======================================================================
echo TEST DU FRAMEWORK DE MIGRATION
echo ======================================================================
echo.
echo Ce test va:
echo   1. Tester la connexion aux bases
echo   2. Tester le framework sur 5 taxes
echo   3. Afficher le resultat
echo.
echo Duree estimee: 30 secondes
echo.
echo ======================================================================
pause
echo.

set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8

python test_framework.py

echo.
echo ======================================================================
echo TEST TERMINE
echo ======================================================================
echo.
echo Si le test a reussi, vous pouvez lancer:
echo   - TEST_FRAMEWORK.bat (ce fichier)
echo   - LANCER_MIGRATION.bat (menu complet)
echo   - Ou ouvrir un terminal externe (voir INSTRUCTIONS_TERMINAL_EXTERNE.md)
echo.
echo ======================================================================
pause

