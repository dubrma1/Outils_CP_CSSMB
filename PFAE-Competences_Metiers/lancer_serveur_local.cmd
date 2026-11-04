@echo off
chcp 65001 >nul
title Répertoire des Métiers Semi-Spécialisés
echo ======================================================================
echo   RÉPERTOIRE DES MÉTIERS SEMI-SPÉCIALISÉS (FMS/PFAE)
echo   Démarrage du serveur web local sur le port 8000...
echo ======================================================================
echo.
echo Ouverture de votre navigateur à l'adresse : http://localhost:8000/index.html
start "" "http://localhost:8000/index.html"
python -m http.server 8000
if %errorlevel% neq 0 (
  echo Python n'est pas installé ou a rencontré une erreur.
  echo Vous pouvez aussi ouvrir directement index.html dans votre navigateur.
  pause
)
