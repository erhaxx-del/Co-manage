#!/usr/bin/env bash
# Marmara Bölge Yönetim Platformu — macOS / Linux başlatıcı
cd "$(dirname "$0")"
PY=""
for c in python3 python; do
  if command -v $c >/dev/null && $c -c "import sys; sys.exit(0 if sys.version_info>=(3,10) else 1)" 2>/dev/null; then PY=$c; break; fi
done
[ -n "$PY" ] || { echo "Python 3.10+ bulunamadı: https://www.python.org/downloads/"; read -p "Enter'a basın..."; exit 1; }
[ -x .venv/bin/python ] || { echo "İlk kurulum yapılıyor..."; $PY -m venv .venv || exit 1; }
VPY=.venv/bin/python
if ! $VPY -c "import flask, waitress, openpyxl" 2>/dev/null; then
  echo "Gerekli paketler kuruluyor..."
  $VPY -m pip install -q --disable-pip-version-check --no-index --find-links paketler -r requirements.txt 2>/dev/null \
    || $VPY -m pip install -q --disable-pip-version-check -r requirements.txt
fi
# TEST MODU: 1 = giriş ekranı atlanır (deneme için). Canlıya alırken 0 yapın.
TARAYICI_AC=1 TEST_MODU=1 $VPY app.py
