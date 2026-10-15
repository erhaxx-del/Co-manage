# -*- coding: utf-8 -*-
"""Sabit listeler ve iş kuralı hesapları (zaman durumu, öncelik skoru, ID üretimi, pazar payı)."""
import datetime as dt

SAHA_MUDURLERI = [
    ("OZAN SELBUZ", "NW11"), ("TUNAHAN DEMİRHAN", "NW12"), ("ENGİN ÜSTÜNYER", "NW13"),
    ("SALİH KOSİF", "NW14"), ("BEDİR EREN KÖSEOĞLU", "NW15"), ("YÜKSEL AYDINOL", "NW16"),
]
SM_ADLARI = [s for s, _ in SAHA_MUDURLERI]
SM_KOD = dict(SAHA_MUDURLERI)
BOLGE_KODU = "NW1"
BOLGE_ADI = "Güney Bölge"

DEPARTMANLAR = ["Bayi Geliştirme", "Satış", "Kredi-Risk / Tahsilat", "Operasyon-İkmal",
                "Teknik-Yatırım", "HSE (İSG-Çevre)", "Pazarlama", "İdari-Hukuk"]
IS_KONULARI = ["Yeni Bayi Görüşmesi", "Sözleşme Yenileme", "Bayi Devri / Fesih", "Hacim Artırma Aksiyonu",
               "Fiyat / İskonto Görüşmesi", "Müşteri Ziyareti", "Teminat Güncelleme", "Gecikmiş Alacak Takibi",
               "Risk Limiti Revizyonu", "İkmal / Lojistik Sorunu", "Stok & Sayım", "Otomasyon / EPDK Bildirim",
               "Tank / Pompa Bakımı", "Yatırım Keşfi", "Tabela & İmaj Yenileme", "İSG Denetimi",
               "Çevre İzni / Belgesi", "Kampanya Uygulaması", "Sadakat Programı", "Ruhsat / İzin Takibi",
               "Dava / İhtarname", "Eğitim & Toplantı"]
ONCELIKLER = ["Kritik", "Yüksek", "Orta", "Düşük"]
DURUMLAR = ["Yapılacak", "Devam Ediyor", "Beklemede", "Tamamlandı", "İptal"]
ASAMALAR = ["Başlangıç", "İlerleme", "Engel", "Karar", "Revizyon", "Tamamlandı"]
ZIYARET_AMACLARI = ["Rutin Ziyaret", "Satış / Hacim Görüşmesi", "Tahsilat / Cari Mutabakat", "HSE Denetimi",
                    "Teknik Kontrol", "Sözleşme Görüşmesi", "Şikâyet / Sorun Çözümü", "Kampanya Uygulaması",
                    "Eğitim", "Yeni Bayi Görüşmesi", "İmaj / Tabela Kontrolü", "Stok & Sayım"]
ZIYARET_DURUMLARI = ["Planlandı", "Gerçekleşti", "Ertelendi", "İptal"]
AKSAKLIK_DURUMLARI = ["Açık", "Projeye dönüştü", "Kapandı"]
GUNLER = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
AYLAR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos",
         "Eylül", "Ekim", "Kasım", "Aralık"]
MARMARA_ILLERI = ["Balıkesir", "Bilecik", "Bursa", "Edirne", "İstanbul", "Kırklareli",
                  "Kocaeli", "Sakarya", "Tekirdağ", "Yalova", "Çanakkale"]
ONCELIK_AGIRLIK = {"Kritik": 4, "Yüksek": 3, "Orta": 2, "Düşük": 1}
ONEM_SIRA = {"Kritik": 0, "Yüksek": 1, "Orta": 2, "Bilgi": 3}


def bugun():
    return dt.date.today()


def tarih(s):
    if not s:
        return None
    if isinstance(s, dt.date):
        return s
    try:
        return dt.date.fromisoformat(str(s)[:10])
    except ValueError:
        return None


def tr_tarih(s, gun=False):
    d = tarih(s)
    if not d:
        return ""
    t = d.strftime("%d.%m.%Y")
    return f"{t} {GUNLER[d.weekday()]}" if gun else t


def hafta_basi(d=None):
    d = d or bugun()
    return d - dt.timedelta(days=d.weekday())


# ── Projeler ────────────────────────────────────────────────────────────────
def proje_zaman_durumu(p, today=None):
    today = today or bugun()
    if p["durum"] == "Tamamlandı":
        return "Tamamlandı"
    if p["durum"] == "İptal":
        return "İptal"
    t = tarih(p["termin"])
    if not t:
        return "Tarihsiz"
    if t < today:
        return "Geciken"
    if t == today:
        return "Bugün"
    if t <= today + dt.timedelta(days=7):
        return "Bu Hafta"
    ay_sonu = (today.replace(day=28) + dt.timedelta(days=4))
    ay_sonu = ay_sonu - dt.timedelta(days=ay_sonu.day)
    if t <= ay_sonu:
        return "Bu Ay"
    return "İleride"


def proje_zenginlestir(p, today=None, gelisme_ozet=None):
    """sqlite3.Row → dict + hesaplanan alanlar."""
    today = today or bugun()
    d = dict(p)
    d["seviye"] = "Alt Adım" if d.get("ust_id") else "Ana Proje"
    d["zaman"] = proje_zaman_durumu(d, today)
    t = tarih(d["termin"])
    acik = d["durum"] not in ("Tamamlandı", "İptal")
    d["kalan_gun"] = (t - today).days if (t and acik) else None
    if not t:
        d["gecikme"] = 0
    elif d["durum"] == "Tamamlandı":
        tm = tarih(d["tamamlanma"])
        d["gecikme"] = max(0, (tm - t).days) if tm else 0
    elif d["durum"] == "İptal":
        d["gecikme"] = 0
    else:
        d["gecikme"] = max(0, (today - t).days)
    if acik:
        etki = max(-400, min(400, (today - t).days)) if t else 0
        d["skor"] = ONCELIK_AGIRLIK.get(d["oncelik"], 1) * 1000 + etki
    else:
        d["skor"] = 0
    if gelisme_ozet is not None:
        g = gelisme_ozet.get(d["id"], {})
        d["gelisme_sayisi"] = g.get("n", 0)
        d["son_gelisme_tarihi"] = g.get("son")
        d["son_gelisme"] = g.get("metin")
        ref = tarih(g.get("son")) or tarih(d["baslangic"])
        d["temassiz"] = max(0, (today - ref).days) if (acik and ref) else None
    return d


def sonraki_ana_id(db, sm_adi):
    kod = SM_KOD.get(sm_adi, BOLGE_KODU)
    rows = db.execute("SELECT id FROM projeler WHERE ust_id IS NULL AND id LIKE ?", (kod + "-%",)).fetchall()
    mx = 0
    for r in rows:
        tail = r["id"].split("-", 1)[1]
        if tail.isdigit():
            mx = max(mx, int(tail))
    return f"{kod}-{mx + 1}"


def sonraki_alt_id(db, ust_id):
    rows = db.execute("SELECT id FROM projeler WHERE ust_id = ?", (ust_id,)).fetchall()
    mx = 0
    for r in rows:
        tail = r["id"][len(ust_id):]
        if tail.isdigit():
            mx = max(mx, int(tail))
    return f"{ust_id}{mx + 1}"


def kod_uyumlu(proje_id, sm_adi):
    kod = SM_KOD.get(sm_adi)
    return bool(kod) and proje_id.startswith(kod + "-")


# ── Ziyaretler ──────────────────────────────────────────────────────────────
def ziyaret_zaman_durumu(z, today=None):
    today = today or bugun()
    if z["durum"] in ("Gerçekleşti", "İptal", "Ertelendi"):
        return z["durum"]
    t = tarih(z["tarih"])
    if not t:
        return "Tarihsiz"
    hb = hafta_basi(today)
    if t < today:
        return "Gecikmiş Plan"
    if t < hb + dt.timedelta(days=7):
        return "Bu Hafta"
    if t < hb + dt.timedelta(days=14):
        return "Gelecek Hafta"
    return "İleride"


# ── Pazar payı ──────────────────────────────────────────────────────────────
def pp_satiri(ge25, ge26, s25, s26):
    pp25 = ge25 / s25 if s25 else 0
    pp26 = ge26 / s26 if s26 else 0
    bp = (pp26 - pp25) * 10000
    return {
        "ge25": ge25, "ge26": ge26, "s25": s25, "s26": s26,
        "ge_buy": (ge26 / ge25 - 1) if ge25 else None,
        "s_buy": (s26 / s25 - 1) if s25 else None,
        "pp25": pp25, "pp26": pp26, "bp": bp,
        "degerlendirme": "Pay kazandı" if bp >= 50 else ("Pay kaybetti" if bp <= -50 else "Yatay"),
    }


def guzel_ad(s):
    """Türkçe büyük harfli adı düzgün yazar: 'TUNAHAN DEMİRHAN' → 'Tunahan Demirhan', 'SALİH KOSİF' → 'Salih Kosif'."""
    def kucuk(t):
        return t.replace("I", "ı").replace("İ", "i").lower()
    return " ".join(w[:1] + kucuk(w[1:]) for w in (s or "").split())


# ── Bölge müdürüne atanan işler (saha → bölge müdürü talepleri) ─────────────
TALEP_DURUMLARI = ["Yeni", "İnceleniyor", "Devam Ediyor", "Tamamlandı", "Reddedildi"]
TALEP_KAPALI = ("Tamamlandı", "Reddedildi")


def talep_zenginlestir(t, today):
    t = dict(t)
    t["kalan_gun"] = None
    t["zaman"] = "Kapalı" if t["durum"] in TALEP_KAPALI else "Tarihsiz"
    if t.get("termin") and t["durum"] not in TALEP_KAPALI:
        try:
            kg = (dt.date.fromisoformat(t["termin"][:10]) - today).days
            t["kalan_gun"] = kg
            t["zaman"] = "Geciken" if kg < 0 else ("Bu Hafta" if kg <= 7 else "İleride")
        except ValueError:
            pass
    return t


# ── kredi-risk ──────────────────────────────────────────────────────────────
YAS_KOLONLARI = [("g1_7", "1–7 gün"), ("g8_15", "8–15 gün"), ("g16_30", "16–30 gün"),
                 ("g31_45", "31–45 gün"), ("g45_ustu", "45 gün+")]
YAS_AGIRLIK = {"g1_7": 1, "g8_15": 2, "g16_30": 4, "g31_45": 7, "g45_ustu": 12}
ONAY_DURUMLARI = ["Onaylandı", "Koşullu onay", "Onaylanmadı / beklet", "Not / talimat", "Yanıt bekliyor"]


def borc_zenginlestir(r):
    """Borç satırına risk skoru, yaş kırılımı yüzdesi ve uyarı etiketi ekler."""
    b = dict(r)
    vg = b.get("vadesi_gecmis") or 0
    b["skor"] = round(sum((b.get(k) or 0) * a for k, a in YAS_AGIRLIK.items()) / 1_000_000, 1)
    b["eskiyen"] = (b.get("g31_45") or 0) + (b.get("g45_ustu") or 0)
    b["eskiyen_pay"] = (b["eskiyen"] / vg) if vg else 0
    b["artti"] = (b.get("fark") or 0) > 0
    if vg <= 0:
        b["seviye"] = "Temiz"
    elif b["eskiyen"] > 0:
        b["seviye"] = "Kritik"
    elif vg >= 1_000_000:
        b["seviye"] = "Yüksek"
    else:
        b["seviye"] = "İzlenecek"
    return b


def _tr(x, ond=0):
    return f"{x:,.{ond}f}".replace(",", "#").replace(".", ",").replace("#", ".")


def bin_tl(v, sifir="–"):
    """TL tutarını okunur biçime çevirir (1.234.567 → 1,2 mn)."""
    if v is None:
        return sifir
    v = float(v)
    if abs(v) < 1000:
        return sifir if abs(v) < 1 else _tr(v)
    if abs(v) >= 1_000_000:
        return _tr(v / 1_000_000, 1) + " mn"
    return _tr(v / 1000) + " bin"


def fark_tl(v):
    """Haftalık değişim: işaretli, 1.000 TL altındaki oynamalar gösterilmez."""
    if not v or abs(v) < 1000:
        return "–"
    return ("+" if v > 0 else "") + bin_tl(v)


def sure_fmt(dk):
    """Yanıt süresi: 45 dk · 3 sa · 2 gün."""
    if dk is None:
        return "–"
    if dk < 60:
        return f"{int(dk)} dk"
    if dk < 1440:
        return f"{dk / 60:.0f} sa"
    return f"{dk / 1440:.0f} gün"
