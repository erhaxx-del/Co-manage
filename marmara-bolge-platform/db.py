# -*- coding: utf-8 -*-
"""SQLite şeması, bağlantı yönetimi ve ilk veri yükleme."""
import json, os, secrets, sqlite3, datetime as dt
from flask import g, current_app
from werkzeug.security import generate_password_hash
import hesap

SEMA = """
CREATE TABLE IF NOT EXISTS kullanicilar (
  id INTEGER PRIMARY KEY, kullanici_adi TEXT UNIQUE NOT NULL, ad_soyad TEXT NOT NULL,
  rol TEXT NOT NULL CHECK (rol IN ('admin','saha','ziyaretci')), sm_adi TEXT, sm_kodu TEXT,
  sifre_hash TEXT NOT NULL, sifre_degismeli INTEGER DEFAULT 1, hatali_giris INTEGER DEFAULT 0,
  kilit_bitis TEXT, aktif INTEGER DEFAULT 1, son_giris TEXT, olusturma TEXT,
  onay_durumu TEXT DEFAULT 'onaylı', talep_mintika TEXT);

CREATE TABLE IF NOT EXISTS projeler (
  id TEXT PRIMARY KEY, ust_id TEXT REFERENCES projeler(id), ad TEXT NOT NULL, aciklama TEXT,
  sm_adi TEXT NOT NULL, il TEXT, bayi TEXT, departman TEXT, is_konusu TEXT, oncelik TEXT, durum TEXT,
  ilerleme REAL DEFAULT 0, baslangic TEXT, termin TEXT, tamamlanma TEXT, notlar TEXT,
  olusturan TEXT, olusturma TEXT, guncelleyen TEXT, guncelleme TEXT,
  arsiv INTEGER DEFAULT 0, arsiv_tarihi TEXT, arsivleyen TEXT);

CREATE TABLE IF NOT EXISTS gelismeler (
  id INTEGER PRIMARY KEY, proje_id TEXT NOT NULL REFERENCES projeler(id) ON DELETE CASCADE,
  tarih TEXT NOT NULL, asama TEXT, metin TEXT NOT NULL, ilerleme REAL, sonraki_adim TEXT,
  sonraki_tarih TEXT, kaydeden TEXT, olusturan TEXT, olusturma TEXT);

CREATE TABLE IF NOT EXISTS bayiler (
  id INTEGER PRIMARY KEY, ist_kodu TEXT, unvan TEXT NOT NULL, sm_adi TEXT, il TEXT, ilce TEXT,
  marka TEXT, tip TEXT, segment TEXT, mintika_sira INTEGER, ay_hacim REAL, akaryakit REAL,
  otogaz REAL, aktif_gun INTEGER, sifir_gun INTEGER, h1 REAL, h2 REAL,
  ytd26_hacim REAL, ytd25_hacim REAL, ytd26_kar REAL);

CREATE TABLE IF NOT EXISTS kanopiler (
  id INTEGER PRIMARY KEY, ad TEXT, ilce TEXT, il TEXT, marka TEXT, sm_adi TEXT, etiket TEXT);

CREATE TABLE IF NOT EXISTS ziyaretler (
  id INTEGER PRIMARY KEY, tarih TEXT NOT NULL, sm_adi TEXT NOT NULL, bayi_id INTEGER REFERENCES bayiler(id),
  amac TEXT, proje_id TEXT, durum TEXT DEFAULT 'Planlandı', gercek_tarih TEXT, notu TEXT, sonraki TEXT,
  olusturan TEXT, olusturma TEXT, guncelleyen TEXT, guncelleme TEXT);

CREATE TABLE IF NOT EXISTS aksakliklar (
  id INTEGER PRIMARY KEY, onem TEXT, kategori TEXT, sm_adi TEXT, il TEXT, ilce TEXT, unvan TEXT,
  bayi_id INTEGER, marka TEXT, tip TEXT, bulgu TEXT, detay TEXT, departman TEXT, aksiyon TEXT,
  ay_hacim REAL, ytd_hacim REAL, ytd_kar REAL, durum TEXT DEFAULT 'Açık', proje_id TEXT);

CREATE TABLE IF NOT EXISTS pazar_il (
  il TEXT PRIMARY KEY, ge25 REAL, ge26 REAL, s25 REAL, s26 REAL, ist_epdk INTEGER,
  ge_ay25 TEXT, ge_ay26 TEXT, s_ay25 TEXT, s_ay26 TEXT);

CREATE TABLE IF NOT EXISTS sm_il_istasyon (sm_adi TEXT, il TEXT, adet INTEGER, PRIMARY KEY (sm_adi, il));

CREATE TABLE IF NOT EXISTS islem_gecmisi (
  id INTEGER PRIMARY KEY, zaman TEXT, kullanici TEXT, islem TEXT, varlik TEXT, varlik_id TEXT, detay TEXT);

CREATE TABLE IF NOT EXISTS borc (
  id INTEGER PRIMARY KEY, rapor_tarihi TEXT, onceki_tarih TEXT, sap TEXT, unvan TEXT, il TEXT, marka TEXT,
  sm_adi TEXT, sm_kodu TEXT, bayi_id INTEGER REFERENCES bayiler(id),
  onceki REAL, fark REAL, vadesi_gecmis REAL, g1_7 REAL, g8_15 REAL, g16_30 REAL, g31_45 REAL, g45_ustu REAL,
  acik_hesap REAL, vadesi_gelmemis REAL, cek_senet REAL, toplam_risk REAL, aciklama TEXT);

CREATE TABLE IF NOT EXISTS risk_onaylari (
  id INTEGER PRIMARY KEY, zaman TEXT, sm_adi TEXT, yazan TEXT, bayi TEXT, bayi_id INTEGER REFERENCES bayiler(id),
  tur TEXT, metin TEXT, unpaid REAL, limit_tl REAL, risk REAL, siparis REAL, ipotek REAL, btm REAL,
  yanit TEXT, onay_durumu TEXT, yanit_zaman TEXT, sure_dk INTEGER, devralindi INTEGER DEFAULT 0);

CREATE INDEX IF NOT EXISTS ix_borc_sm ON borc(sm_adi);
CREATE INDEX IF NOT EXISTS ix_onay_sm ON risk_onaylari(sm_adi);

CREATE TABLE IF NOT EXISTS talepler (
  id INTEGER PRIMARY KEY, sm_adi TEXT NOT NULL, olusturan TEXT, baslik TEXT NOT NULL, aciklama TEXT,
  departman TEXT, oncelik TEXT, termin TEXT, bayi_id INTEGER, proje_id TEXT,
  durum TEXT DEFAULT 'Yeni', yanit TEXT, tamamlanma TEXT,
  olusturma TEXT, guncelleyen TEXT, guncelleme TEXT);

CREATE TABLE IF NOT EXISTS talep_notlari (
  id INTEGER PRIMARY KEY, talep_id INTEGER NOT NULL REFERENCES talepler(id) ON DELETE CASCADE,
  yazan TEXT, yazan_ad TEXT, rol TEXT, metin TEXT NOT NULL, zaman TEXT);

CREATE INDEX IF NOT EXISTS ix_talep_sm ON talepler(sm_adi);
CREATE INDEX IF NOT EXISTS ix_proje_sm ON projeler(sm_adi);
CREATE INDEX IF NOT EXISTS ix_gel_proje ON gelismeler(proje_id);
CREATE INDEX IF NOT EXISTS ix_ziy_sm ON ziyaretler(sm_adi);
CREATE INDEX IF NOT EXISTS ix_bayi_sm ON bayiler(sm_adi);
"""

KULLANICILAR = [
    ("erhan", "Erhan Başaçar", "admin", None, "NW1"),
    ("ozan", "Ozan Selbuz", "saha", "OZAN SELBUZ", "NW11"),
    ("tunahan", "Tunahan Demirhan", "saha", "TUNAHAN DEMİRHAN", "NW12"),
    ("engin", "Engin Üstünyer", "saha", "ENGİN ÜSTÜNYER", "NW13"),
    ("salih", "Salih Kosif", "saha", "SALİH KOSİF", "NW14"),
    ("bedir", "Bedir Eren Köseoğlu", "saha", "BEDİR EREN KÖSEOĞLU", "NW15"),
    ("yuksel", "Yüksel Aydınol", "saha", "YÜKSEL AYDINOL", "NW16"),
]


def simdi():
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def baglan():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["VERITABANI"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def kapat(_=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def rastgele_sifre():
    alfabe = "abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    while True:
        s = "".join(secrets.choice(alfabe) for _ in range(10))
        if any(c.isdigit() for c in s) and any(c.isalpha() for c in s):
            return s


def _f(v):
    try:
        return None if v in (None, "") else float(v)
    except (TypeError, ValueError):
        return None


def goc(con):
    """Eski sürümle oluşturulmuş veritabanlarına yeni sütunları ekler (veri kaybı olmadan)."""
    sut = {r[1] for r in con.execute("PRAGMA table_info(kullanicilar)")}
    if "onay_durumu" not in sut:
        con.execute("ALTER TABLE kullanicilar ADD COLUMN onay_durumu TEXT DEFAULT 'onaylı'")
    if "talep_mintika" not in sut:
        con.execute("ALTER TABLE kullanicilar ADD COLUMN talep_mintika TEXT")
    psut = {r[1] for r in con.execute("PRAGMA table_info(projeler)")}
    for ad, tip in (("arsiv", "INTEGER DEFAULT 0"), ("arsiv_tarihi", "TEXT"), ("arsivleyen", "TEXT")):
        if ad not in psut:
            con.execute(f"ALTER TABLE projeler ADD COLUMN {ad} {tip}")
    # 'ziyaretci' rolü: SQLite CHECK kısıtını değiştiremediği için tablo yeniden kurulur
    tsql = con.execute("SELECT sql FROM sqlite_master WHERE name='kullanicilar'").fetchone()[0]
    if "ziyaretci" not in tsql:
        con.execute("ALTER TABLE kullanicilar RENAME TO _kullanicilar_eski")
        yeni = SEMA.split("CREATE TABLE IF NOT EXISTS projeler")[0]
        con.executescript(yeni)
        sutunlar = ", ".join(r[1] for r in con.execute("PRAGMA table_info(_kullanicilar_eski)"))
        con.execute(f"INSERT INTO kullanicilar ({sutunlar}) SELECT {sutunlar} FROM _kullanicilar_eski")
        con.execute("DROP TABLE _kullanicilar_eski")
    con.commit()


def kur(veritabani, seed_yolu, sifre_dosyasi, ornek_veri=True, sabit_sifre=None, hazir_kullanicilar=False):
    """Veritabanı yoksa oluşturur ve ilk verileri yükler. İlk şifreleri döndürür."""
    yeni = not os.path.exists(veritabani)
    con = sqlite3.connect(veritabani)
    con.row_factory = sqlite3.Row
    con.executescript(SEMA)
    goc(con)
    if not yeni and con.execute("SELECT COUNT(*) FROM kullanicilar").fetchone()[0] > 0:
        con.close()
        return None
    now = simdi()
    sifreler = {}
    olusacak = KULLANICILAR if hazir_kullanicilar else [k for k in KULLANICILAR if k[2] == "admin"]
    for ka, ad, rol, sm, kod in olusacak:
        s = sabit_sifre or rastgele_sifre()
        sifreler[ka] = s
        con.execute("INSERT INTO kullanicilar (kullanici_adi, ad_soyad, rol, sm_adi, sm_kodu, sifre_hash,"
                    " sifre_degismeli, olusturma) VALUES (?,?,?,?,?,?,1,?)",
                    (ka, ad, rol, sm, kod, generate_password_hash(s), now))
    S = json.load(open(seed_yolu, encoding="utf-8"))

    # bayiler (portföy)
    unvan_id = {}
    for b in S["bayi_portfoy"]:
        cur = con.execute(
            "INSERT INTO bayiler (ist_kodu, unvan, sm_adi, il, ilce, marka, tip, segment, mintika_sira, ay_hacim,"
            " akaryakit, otogaz, aktif_gun, sifir_gun, h1, h2, ytd26_hacim, ytd25_hacim, ytd26_kar)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (b["İst. Kodu"], b["Bayi Ünvanı"], b["Saha Müdürü"], b["İl"], b["İlçe"], b["Marka"], b["Tip"],
             b["Segment"], b["Mıntıka Sırası"], _f(b["Ağustos Hacim m³"]), _f(b["Akaryakıt m³"]),
             _f(b["Otogaz m³"]), b["Aktif Gün"], b["Sıfır Gün"], _f(b["1-15 Ağu m³/gün"]),
             _f(b["16-31 Ağu m³/gün"]), _f(b["2026 YTD Hacim m³"]), _f(b["2025 YTD Hacim m³"]),
             _f(b["2026 YTD Kâr TL"])))
        unvan_id.setdefault(b["Bayi Ünvanı"], cur.lastrowid)

    # kredi-risk: vadesi geçmiş borç raporu
    for x in S.get("borc", []):
        con.execute(
            "INSERT INTO borc (rapor_tarihi, onceki_tarih, sap, unvan, il, marka, sm_adi, sm_kodu, bayi_id,"
            " onceki, fark, vadesi_gecmis, g1_7, g8_15, g16_30, g31_45, g45_ustu, acik_hesap, vadesi_gelmemis,"
            " cek_senet, toplam_risk, aciklama) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (x["rapor_tarihi"], x["onceki_tarih"], x["sap"], x["unvan"], x["il"], x["marka"], x["sm_adi"],
             x["sm_kodu"], x.get("bayi_id"), x["onceki"], x["fark"], x["vadesi_gecmis"], x["g1_7"], x["g8_15"],
             x["g16_30"], x["g31_45"], x["g45_ustu"], x["acik_hesap"], x["vadesi_gelmemis"], x["cek_senet"],
             x["toplam_risk"], x["aciklama"]))

    # kredi-risk: WhatsApp onay yazışmaları
    for k in S.get("risk_onaylari", []):
        con.execute(
            "INSERT INTO risk_onaylari (zaman, sm_adi, yazan, bayi, bayi_id, tur, metin, unpaid, limit_tl, risk,"
            " siparis, ipotek, btm, yanit, onay_durumu, yanit_zaman, sure_dk, devralindi)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (k["zaman"], k["sm_adi"], k["yazan"], k["bayi"], k.get("bayi_id"), k["tur"], k["metin"], k["unpaid"],
             k["limit"], k["risk"], k["siparis"], k["ipotek"], k["btm"], k["yanit"], k["onay_durumu"],
             k["yanit_zaman"], k["sure_dk"], k.get("devralindi", 0)))

    # kanopiler (proje bayi listesi, saha müdürüne göre kademeli)
    gorulen = {}
    for k in S["kanopiler"]:
        ad = (k["Bayi Adı"] or "").strip()
        et = ad if ad and ad != "-" else f"{k['İlçe']} ({k['İl']})"
        sm = k["Saha Müdürü"]
        kume = gorulen.setdefault(sm, set())
        e2, n = et, 2
        while e2 in kume:
            e2 = f"{et} ({n})"; n += 1
        kume.add(e2)
        con.execute("INSERT INTO kanopiler (ad, ilce, il, marka, sm_adi, etiket) VALUES (?,?,?,?,?,?)",
                    (ad, k["İlçe"], k["İl"], k["Marka"], sm, e2))

    # Örnek kayıtlar 14.09.2026 haftasına göre hazırlandı; demo her zaman "güncel" görünsün diye
    # tarihler kurulum haftasına tam hafta olarak kaydırılır (haftanın günleri korunur).
    ref = dt.date(2026, 9, 14)
    kay = max(0, (hesap.hafta_basi() - ref).days)
    def k(t):
        if not t or not kay:
            return t
        try:
            return (dt.date.fromisoformat(str(t)[:10]) + dt.timedelta(days=kay)).isoformat()
        except ValueError:
            return t
    if ornek_veri:
        for p in S["projeler"]:
            con.execute(
                "INSERT INTO projeler (id, ust_id, ad, aciklama, sm_adi, il, bayi, departman, is_konusu, oncelik,"
                " durum, ilerleme, baslangic, termin, tamamlanma, notlar, olusturan, olusturma, guncelleyen,"
                " guncelleme) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (p["Proje ID"], p["Üst Proje ID"], p["Proje Adı"], p["Açıklama"], p["Saha Müdürü"], p["İl"],
                 p["Bayi"], p["Departman"], p["İş Konusu"], p["Öncelik"], p["Durum"], _f(p["İlerleme %"]) or 0,
                 k(p["Başlangıç"]), k(p["Termin"]), k(p["Tamamlanma"]), p["Notlar"], "içe aktarım", now,
                 "içe aktarım", k(p["Son Güncelleme"] or now[:10]) + " 00:00:00"))
        for gk in S["gelismeler"]:
            con.execute(
                "INSERT INTO gelismeler (proje_id, tarih, asama, metin, ilerleme, sonraki_adim, sonraki_tarih,"
                " kaydeden, olusturan, olusturma) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (gk["Proje ID"], k(gk["Tarih"]), gk["Aşama"], gk["Gelişme / Yapılan İş"], _f(gk["İlerleme %"]),
                 gk["Sonraki Adım"], k(gk["Sonraki Adım Tarihi"]), gk["Kaydeden"], "içe aktarım", now))
        for z in S["ziyaretler"]:
            con.execute(
                "INSERT INTO ziyaretler (tarih, sm_adi, bayi_id, amac, proje_id, durum, gercek_tarih, notu,"
                " sonraki, olusturan, olusturma) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (k(z["Planlanan Tarih"]), z["Saha Müdürü"], unvan_id.get(z["Bayi / İstasyon"]), z["Ziyaret Amacı"],
                 z["İlgili Proje ID"], z["Durum"], k(z["Gerçekleşen Tarih"]), z["Ziyaret Notu"],
                 k(z["Sonraki Ziyaret"]), "içe aktarım", now))
    for a in S["aksakliklar"]:
        con.execute(
            "INSERT INTO aksakliklar (onem, kategori, sm_adi, il, ilce, unvan, bayi_id, marka, tip, bulgu, detay,"
            " departman, aksiyon, ay_hacim, ytd_hacim, ytd_kar) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (a["Önem"], a["Kategori"], a["Saha Müdürü"], a["İl"], a["İlçe"], a["Bayi Ünvanı"],
             unvan_id.get(a["Bayi Ünvanı"]), a["Marka"], a["Tip"], a["Bulgu"], a["Detay"],
             a["Sorumlu Departman"], a["Önerilen Aksiyon"], _f(a["Ağustos m³"]), _f(a["2026 YTD m³"]),
             _f(a["2026 YTD Kâr TL"])))
    for il, o in S["epdk"].items():
        con.execute("INSERT INTO pazar_il VALUES (?,?,?,?,?,?,?,?,?,?)",
                    (il, o["ge25"], o["ge26"], o["s25"], o["s26"], int(o.get("ist26") or 0),
                     json.dumps(o["ge_ay25"]), json.dumps(o["ge_ay26"]),
                     json.dumps(o["s_ay25"]), json.dumps(o["s_ay26"])))
    for sm, iller in S["sm_il_istasyon"].items():
        for il, adet in iller.items():
            if adet:
                con.execute("INSERT INTO sm_il_istasyon VALUES (?,?,?)", (sm, il, adet))
    con.execute("INSERT INTO islem_gecmisi (zaman, kullanici, islem, varlik, detay) VALUES (?,?,?,?,?)",
                (now, "sistem", "kurulum", "platform", "İlk veriler Excel iş takip dosyasından yüklendi"))
    con.commit()
    con.close()
    if sifre_dosyasi:
        with open(sifre_dosyasi, "w", encoding="utf-8") as f:
            f.write("MARMARA BÖLGE YÖNETİM PLATFORMU — İLK GİRİŞ ŞİFRESİ\n")
            f.write("İlk girişte kendi şifrenizi belirlemek zorundasınız. Bu dosyayı sonra silin.\n")
            f.write("Saha müdürleri giriş ekranındaki 'Kayıt ol' ile mıntıkalarını seçip kendileri kaydolur;\n")
            f.write("başvuruları Yönetim → Kullanıcılar ekranında sizin onayınıza düşer.\n\n")
            for ka, ad, rol, sm, kod in olusacak:
                f.write(f"{ad:24s} kullanıcı adı: {ka:10s} ilk şifre: {sifreler[ka]}\n")
    return sifreler


def logla(kullanici, islem, varlik, varlik_id=None, detay=None):
    db = baglan()
    db.execute("INSERT INTO islem_gecmisi (zaman, kullanici, islem, varlik, varlik_id, detay) VALUES (?,?,?,?,?,?)",
               (simdi(), kullanici, islem, varlik, varlik_id, detay))
