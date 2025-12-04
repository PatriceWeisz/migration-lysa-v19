@echo off
chcp 65001 >nul
cls

echo ======================================================================
echo VERIFICATION DES STATUTS
echo ======================================================================
echo.
echo Ce script verifie que les statuts sont preserves:
echo   - Factures comptabilisees (posted)
echo   - Commandes confirmees (sale)
echo   - BL/Receptions faits (done)
echo   - OF termines (done)
echo   - Conges valides (validate)
echo   - etc.
echo.
echo CRITIQUE pour l integrite des donnees !
echo.
echo Duree: 2-3 minutes
echo.
echo ======================================================================
pause
echo.

set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8

python verifier_statuts.py

echo.
echo ======================================================================
echo VERIFICATION TERMINEE
echo ======================================================================
echo.
echo Consultez le rapport dans: logs\verification_statuts_*.txt
echo.
pause

