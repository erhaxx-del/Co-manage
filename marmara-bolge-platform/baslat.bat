@echo off
chcp 65001 >nul
title Marmara Bolge Yonetim Platformu
cd /d "%~dp0"
echo.
echo  ============================================================
echo    MARMARA BOLGE YONETIM PLATFORMU
echo  ============================================================
echo.

REM --- 1) Zip icinden mi calistiriliyor? ---
if not exist "app.py" (
  echo  [HATA] Dosyalar zip icinden calistiriliyor.
  echo.
  echo  Zip dosyasina SAG TIKLAYIN - "Tumunu ayikla" deyin,
  echo  sonra acilan KLASORUN ICINDEKI baslat.bat dosyasini calistirin.
  echo.
  pause
  exit /b 1
)

REM --- 2) Python var mi? (Microsoft Store kisayolu gercek Python degildir) ---
set "PY="
python -c "import sys; sys.exit(0 if sys.version_info>=(3,10) else 1)" >nul 2>nul && set "PY=python"
if not defined PY py -3 -c "import sys; sys.exit(0 if sys.version_info>=(3,10) else 1)" >nul 2>nul && set "PY=py -3"
if not defined PY (
  echo  [HATA] Python 3.10 veya ustu bulunamadi.
  echo.
  echo  1^) https://www.python.org/downloads/ adresinden Python indirin.
  echo  2^) Kurulumun ILK ekraninda "Add python.exe to PATH" kutusunu isaretleyin.
  echo  3^) Kurulum bitince bu pencereyi kapatip baslat.bat dosyasini yeniden calistirin.
  echo.
  echo  Not: Microsoft Store acilirsa o gercek Python degildir, python.org surumunu kurun.
  echo.
  pause
  exit /b 1
)
echo  [1/3] Python bulundu: %PY%

REM --- 3) Sanal ortam ---
if not exist ".venv\Scripts\python.exe" (
  echo  [2/3] Ilk kurulum yapiliyor, 1-2 dakika surebilir...
  %PY% -m venv .venv
  if errorlevel 1 (
    echo  [HATA] Sanal ortam olusturulamadi. Klasoru Masaustu veya Belgeler altina tasiyip tekrar deneyin.
    pause
    exit /b 1
  )
) else (
  echo  [2/3] Kurulum mevcut
)
set "VPY=.venv\Scripts\python.exe"

REM --- 4) Paketler: once klasordeki paketlerden (internet/proxy gerekmez), olmazsa internetten ---
"%VPY%" -c "import flask, waitress, openpyxl" >nul 2>nul
if errorlevel 1 (
  echo        Gerekli paketler kuruluyor...
  "%VPY%" -m pip install --quiet --disable-pip-version-check --no-index --find-links paketler -r requirements.txt
  if errorlevel 1 "%VPY%" -m pip install --quiet --disable-pip-version-check -r requirements.txt
)
"%VPY%" -c "import flask, waitress, openpyxl" >nul 2>nul
if errorlevel 1 (
  echo  [HATA] Gerekli paketler kurulamadi.
  echo  Bu pencerenin ekran goruntusunu paylasin.
  pause
  exit /b 1
)
echo  [3/3] Paketler hazir

REM --- 5) Calistir (tarayici, sunucu hazir olunca kendiliginden acilir) ---
set "TARAYICI_AC=1"
REM TEST MODU: 1 = giris ekrani atlanir (deneme icin). Canliya alirken 0 yapin.
set "TEST_MODU=1"
"%VPY%" app.py
echo.
echo  Platform durdu. Yukarida bir hata mesaji varsa bu pencerenin ekran goruntusunu paylasin.
pause
