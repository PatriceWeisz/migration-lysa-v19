@echo off
chcp 65001 >nul
cls

echo ======================================================================
echo TEST MIGRATION AUTO - AFFICHAGE EN TEMPS REEL
echo ======================================================================
echo.
echo Base: lysa-migration-2.odoo.com
echo Mode: TEST (5-10 enregistrements par module)
echo Auto-correction: ACTIVEE
echo.
echo ======================================================================
echo.
pause

set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8

python test_migration_complete_auto.py

echo.
echo ======================================================================
echo TEST TERMINE
echo ======================================================================
echo.
pause

