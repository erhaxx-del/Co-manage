# -*- coding: utf-8 -*-
"""Oturum, yetki ve CSRF koruması."""
import datetime as dt, secrets
from functools import wraps
from flask import session, redirect, url_for, request, abort, g, flash, current_app
import db as vt

MAX_HATALI = 5
KILIT_DAKIKA = 10


def test_modu():
    """Test modunda giriş ekranı atlanır (yalnızca yerel kurulumda kullanılmalı)."""
    return bool(current_app.config.get("TEST_MODU"))


def aktif_kullanici():
    if "kullanici" in g:
        return g.kullanici
    uid = session.get("uid")
    g.kullanici = None
    if uid:
        r = vt.baglan().execute("SELECT * FROM kullanicilar WHERE id=? AND aktif=1", (uid,)).fetchone()
        g.kullanici = dict(r) if r else None
    if g.kullanici is None and test_modu():
        r = vt.baglan().execute("SELECT * FROM kullanicilar WHERE aktif=1 AND rol='admin' ORDER BY id LIMIT 1").fetchone()
        if r:
            g.kullanici = dict(r)
            g.kullanici["sifre_degismeli"] = 0
    return g.kullanici


def giris_gerekli(f):
    @wraps(f)
    def sar(*a, **k):
        u = aktif_kullanici()
        if not u:
            return redirect(url_for("giris", sonra=request.path))
        if u["sifre_degismeli"] and not test_modu() and request.endpoint not in ("sifre_degistir", "cikis", "static"):
            flash("Devam etmeden önce kendi şifrenizi belirlemelisiniz.", "uyari")
            return redirect(url_for("sifre_degistir"))
        return f(*a, **k)
    return sar


def admin_gerekli(f):
    @wraps(f)
    @giris_gerekli
    def sar(*a, **k):
        if aktif_kullanici()["rol"] != "admin":
            abort(403)
        return f(*a, **k)
    return sar


def duzenleyebilir(sm_adi):
    """Bölge müdürü her şeyi, saha müdürü yalnızca kendi mıntıkasını düzenler."""
    u = aktif_kullanici()
    if not u:
        return False
    if u["rol"] == "ziyaretci":
        return False
    return u["rol"] == "admin" or bool(sm_adi and u["sm_adi"] == sm_adi)


# Ziyaretçinin açabileceği değişiklik sayfaları yok; yalnızca bunlara POST atabilir
ZIYARETCI_SERBEST = {"giris", "cikis", "sifre_degistir", "static"}
ZIYARETCI_YASAK_SAYFA = {"proje_yeni", "proje_duzenle", "ziyaret_yeni", "ziyaret_duzenle", "yedek", "disa_aktar",
                         "talepler", "talep_yeni", "talep_kart", "talep_duzenle"}


def ziyaretci_kontrol():
    """Ziyaretçi (salt okunur) hesabı hiçbir kayıt oluşturamaz / değiştiremez."""
    u = aktif_kullanici()
    if not u or u["rol"] != "ziyaretci":
        return
    if request.endpoint in ZIYARETCI_SERBEST:
        return
    if request.method != "GET" or request.endpoint in ZIYARETCI_YASAK_SAYFA:
        abort(403)


def duzenleme_kontrol(sm_adi):
    if not duzenleyebilir(sm_adi):
        abort(403)


def sifre_uygun(s):
    if len(s) < 8:
        return "Şifre en az 8 karakter olmalı."
    if not any(c.isdigit() for c in s) or not any(c.isalpha() for c in s):
        return "Şifre hem harf hem rakam içermeli."
    return None


def kilitli_mi(u):
    kb = u.get("kilit_bitis")
    if not kb:
        return False
    return dt.datetime.fromisoformat(kb) > dt.datetime.now()


def hatali_giris_kaydet(u):
    d = vt.baglan()
    n = (u["hatali_giris"] or 0) + 1
    kilit = None
    if n >= MAX_HATALI:
        kilit = (dt.datetime.now() + dt.timedelta(minutes=KILIT_DAKIKA)).isoformat(timespec="seconds")
        n = 0
    d.execute("UPDATE kullanicilar SET hatali_giris=?, kilit_bitis=? WHERE id=?", (n, kilit, u["id"]))
    d.commit()
    return kilit


# ── CSRF ────────────────────────────────────────────────────────────────────
def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_urlsafe(32)
    return session["_csrf"]


def csrf_kontrol():
    if request.method == "POST":
        t = request.form.get("_csrf") or request.headers.get("X-CSRF-Token")
        if not t or t != session.get("_csrf"):
            abort(400, "Güvenlik doğrulaması başarısız (CSRF). Sayfayı yenileyip tekrar deneyin.")
