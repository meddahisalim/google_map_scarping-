@echo off
setlocal enabledelayedexpansion
title Google Maps Lead Scraper - Lanceur
cd /d "%~dp0"

echo ============================================
echo   Google Maps Lead Scraper - Demarrage
echo ============================================
echo.

REM --- 1. Verifier que Python est installe ---
where python >nul 2>nul
if errorlevel 1 (
    echo [ERREUR] Python n'est pas installe ou pas dans le PATH.
    echo.
    echo Merci d'installer Python 3.9+ depuis https://www.python.org/downloads/
    echo IMPORTANT : cocher "Add python.exe to PATH" pendant l'installation.
    echo.
    pause
    exit /b 1
)

REM --- 2. Creer l'environnement virtuel s'il n'existe pas ---
if not exist "venv\" (
    echo [1/6] Creation de l'environnement virtuel...
    python -m venv venv
    if errorlevel 1 (
        echo [ERREUR] Impossible de creer l'environnement virtuel.
        pause
        exit /b 1
    )
) else (
    echo [1/6] Environnement virtuel deja present.
)

REM --- 3. Activer l'environnement virtuel ---
call venv\Scripts\activate.bat

REM --- 4. Installer / mettre a jour les dependances ---
echo [2/6] Verification des dependances...
python -m pip install --upgrade pip >nul 2>nul
echo [3/6] Installation / mise a jour des dependances...
pip install -r requirements.txt --upgrade
if errorlevel 1 (
    echo [ERREUR] Echec de l'installation des dependances.
    pause
    exit /b 1
)
REM Nettoyage : si l'ancienne dependance webdriver-manager est presente
REM (source du bug "WinError 193"), on la desinstalle proprement.
pip show webdriver-manager >nul 2>nul
if not errorlevel 1 (
    echo Suppression de l'ancienne dependance webdriver-manager...
    pip uninstall -y webdriver-manager >nul 2>nul
)

REM --- 5. Verifier que Google Chrome est installe ---
echo [4/6] Verification de Google Chrome...
set CHROME_FOUND=0
if exist "%ProgramFiles%\Google\Chrome\Application\chrome.exe" set CHROME_FOUND=1
if exist "%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe" set CHROME_FOUND=1
if exist "%LocalAppData%\Google\Chrome\Application\chrome.exe" set CHROME_FOUND=1

if !CHROME_FOUND! == 0 (
    echo.
    echo [ATTENTION] Google Chrome n'a pas ete detecte sur ce PC.
    echo Le scraper a besoin de Chrome pour fonctionner.
    echo Telecharge-le ici : https://www.google.com/chrome/
    echo.
    pause
)

REM --- 6. Creer un raccourci sur le Bureau (icone, lancement sans console) ---
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\Google Maps Lead Scraper.lnk"
if not exist "%SHORTCUT%" (
    echo [5/6] Creation du raccourci sur le Bureau...
    powershell -NoProfile -ExecutionPolicy Bypass -Command ^
      "$ws = New-Object -ComObject WScript.Shell;" ^
      "$sc = $ws.CreateShortcut('%SHORTCUT%');" ^
      "$sc.TargetPath = '%~dp0lancer_silencieux.vbs';" ^
      "$sc.WorkingDirectory = '%~dp0';" ^
      "$sc.IconLocation = '%~dp0assets\icon.ico';" ^
      "$sc.Description = 'Google Maps Lead Scraper';" ^
      "$sc.Save()"
    if exist "%SHORTCUT%" (
        echo Raccourci cree : tu pourras desormais lancer l'app directement
        echo depuis l'icone sur ton Bureau, sans repasser par ce fichier.
    )
) else (
    echo [5/6] Raccourci Bureau deja present.
)

REM --- 7. Lancer l'application ---
echo [6/6] Lancement de l'application...
echo.
python main.py

REM --- 8. Garder la fenetre ouverte en cas d'erreur ---
if errorlevel 1 (
    echo.
    echo [ERREUR] L'application s'est fermee avec une erreur.
    pause
)

endlocal
