@echo off
chcp 65001 >nul
cls

echo ======================================================================
echo TEST MIGRATION COMPLETE - MODE TEST
echo ======================================================================
echo.
echo Ce test va migrer 5 enregistrements COMPLETS de chaque module:
echo.
echo   - account.tax
echo   - account.analytic.plan  
echo   - account.analytic.account
echo   - res.partner.category
echo   - product.pricelist
echo   - crm.team
echo   - project.project
echo.
echo Avec TOUS les champs detectes automatiquement (100%%)
echo.
echo Duree estimee: 2-3 minutes
echo.
echo ======================================================================
pause
echo.

set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8

python test_migration_complete.py

echo.
echo ======================================================================
echo TEST TERMINE
echo ======================================================================
echo.
echo Si le test a reussi, vous pouvez:
echo   - Verifier les resultats: python verifier_mappings_existants.py
echo   - Lancer migration complete: python migration_framework.py
echo   - Completer les existants: python completer_champs_existants.py
echo.
pause

