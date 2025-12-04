@echo off
chcp 65001 >nul
cls

echo ======================================================================
echo TEST COMPLET DU FRAMEWORK - DETECTION ERREURS
echo ======================================================================
echo.
echo Ce test va:
echo   - Tester TOUS les modules configures
echo   - Detecter les erreurs de codage
echo   - Detecter les erreurs de champs (v16 vs v19)
echo   - Detecter les erreurs de transformation
echo   - Detecter les erreurs de relations
echo   - Generer un rapport detaille
echo.
echo Mode: TEST (5 enregistrements par module)
echo Duree estimee: 10-15 minutes
echo.
echo ======================================================================
pause
echo.

set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8

python test_complet_framework.py

echo.
echo ======================================================================
echo TEST TERMINE
echo ======================================================================
echo.
echo Consultez le rapport dans: logs\test_complet_*.log
echo.
echo Si TOUS LES TESTS REUSSIS:
echo   - Le framework est pret
echo   - Vous pouvez lancer: python migration_framework.py
echo.
echo Si ERREURS DETECTEES:
echo   - Consultez le rapport
echo   - Corrigez les erreurs
echo   - Relancez ce test
echo.
pause

