@echo off
chcp 65001 >nul

echo ======================================================================
echo LANCEMENT DES MIGRATIONS - MODULES DE BASE
echo ======================================================================
echo.

set PYTHONUNBUFFERED=1
set PYTHONIOENCODING=utf-8

:MENU
cls
echo ======================================================================
echo MENU MIGRATION
echo ======================================================================
echo.
echo 1. Migrer utilisateurs (89 users)
echo 2. Migrer plans analytiques (2)
echo 3. Migrer comptes analytiques (15)
echo 4. Migrer equipes commerciales (40)
echo 5. Test connexion
echo 6. Verifier mappings
echo.
echo 0. Quitter
echo.
echo ======================================================================
set /p choix="Votre choix : "

if "%choix%"=="1" goto USERS
if "%choix%"=="2" goto PLANS
if "%choix%"=="3" goto COMPTES
if "%choix%"=="4" goto EQUIPES
if "%choix%"=="5" goto TEST
if "%choix%"=="6" goto VERIF
if "%choix%"=="0" goto FIN
goto MENU

:USERS
echo.
echo Lancement migration utilisateurs...
echo.
python migrer_utilisateurs.py
pause
goto MENU

:PLANS
echo.
echo Lancement migration plans analytiques...
echo.
python migrer_plans_analytiques.py
pause
goto MENU

:COMPTES
echo.
echo Lancement migration comptes analytiques...
echo.
python migrer_comptes_analytiques.py
pause
goto MENU

:EQUIPES
echo.
echo Lancement migration equipes commerciales...
echo.
python migrer_equipes_commerciales.py
pause
goto MENU

:TEST
echo.
echo Test connexion...
echo.
python test_connexion.py
pause
goto MENU

:VERIF
echo.
echo Verification mappings...
echo.
python verifier_mappings_existants.py
pause
goto MENU

:FIN
echo.
echo Au revoir!
exit

