@echo off
chcp 65001 >nul
cls

echo ======================================================================
echo RAPPORT DES DIFFERENCES DE CHAMPS v16 -^> v19
echo ======================================================================
echo.
echo Ce rapport analyse les differences entre v16 et v19:
echo   - Champs renames
echo   - Champs disparus
echo   - Nouveaux champs obligatoires
echo   - Transformations necessaires
echo.
echo Duree: 1-2 minutes
echo.
echo ======================================================================
pause
echo.

set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8

python rapport_differences_champs.py

echo.
echo ======================================================================
echo RAPPORT TERMINE
echo ======================================================================
pause

