@echo off
chcp 65001 >nul
cls

echo ======================================================================
echo TEST TAXES AVEC AFFICHAGE IMMEDIAT
echo ======================================================================
echo.
echo Base: lysa-migration-2.odoo.com
echo Mode: TEST (5 taxes uniquement)
echo.
echo ======================================================================
pause

set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8

python test_simple_taxes.py

echo.
echo ======================================================================
echo TEST TERMINE - Appuyez sur une touche pour fermer
echo ======================================================================
pause

