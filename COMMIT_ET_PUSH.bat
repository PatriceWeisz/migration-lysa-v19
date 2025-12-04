@echo off
chcp 65001 >nul
cls

echo ======================================================================
echo SAUVEGARDE SUR GITHUB
echo ======================================================================
echo.
echo Ce script va:
echo   1. Ajouter tous les fichiers
echo   2. Committer avec le message prepare
echo   3. Pusher vers GitHub
echo.
echo ======================================================================
pause
echo.

git add -A

echo.
echo Fichiers a committer:
git status --short

echo.
echo ======================================================================
pause
echo.

git commit -F COMMIT_MESSAGE.txt

echo.
echo ======================================================================
echo COMMIT CREE
echo ======================================================================
pause
echo.

git push

echo.
echo ======================================================================
echo POUSSE VERS GITHUB - TERMINE
echo ======================================================================
pause

