@echo off
chcp 65001 >nul
cls

echo ======================================================================
echo TEST AUTO-CORRECTION
echo ======================================================================
echo.
echo Ce test verifie le systeme d auto-correction:
echo.
echo   1. Detection automatique des erreurs
echo   2. Correction auto des erreurs simples:
echo      - Champs invalides (retires)
echo      - Valeurs par defaut (ajoutees)
echo      - Doublons (recuperes)
echo.
echo   3. Demande avis utilisateur pour decisions importantes:
echo      - Relations manquantes
echo      - Erreurs inconnues
echo.
echo Duree: 3-5 minutes
echo.
echo ======================================================================
pause
echo.

set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8

python test_auto_correction.py

echo.
echo ======================================================================
echo TEST TERMINE
echo ======================================================================
echo.
echo Si le test a reussi:
echo   - Le framework peut corriger automatiquement la plupart des erreurs
echo   - Vous serez consulte uniquement pour decisions importantes
echo.
echo Vous pouvez maintenant lancer la migration complete avec confiance !
echo.
pause

