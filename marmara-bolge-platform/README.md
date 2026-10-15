# Marmara Bölge Yönetim Platformu

Güzel Enerji · Marmara Bölge Müdürlüğü için web tabanlı proje, ziyaret, bayi ve pazar payı takip platformu.
Excel iş takip dosyasındaki tüm yapı (projeler, alt adımlar, gelişme günlüğü, istasyon ziyaretleri, bayi portföyü,
aksaklıklar, mıntıka analizi, EPDK pazar payı) buraya taşınmıştır; kullanıcı adı ve şifre ile girilir.

---

## 1. Kendi bilgisayarınızda çalıştırma (5 dakika)

### Bir kereye mahsus: Python kurun
<https://www.python.org/downloads/> → **Python 3.10 veya üstü** → kurulumun ilk ekranında
**"Add Python to PATH"** kutusunu işaretleyin.

### Başlatın
| Sistem | Yapmanız gereken |
|---|---|
| **Windows** | Klasördeki **`baslat.bat`** dosyasına çift tıklayın |
| **macOS** | **`baslat.command`** dosyasına çift tıklayın (ilk seferde: sağ tık → Aç) |
| **Linux** | Terminalde `./baslat.sh` |

İlk açılışta gerekli paketler klasördeki `paketler/` dizininden kurulur (internet gerekmez, 1–2 dk). Platform hazır olduğunda tarayıcı kendiliğinden
**<http://127.0.0.1:5000>** adresini açar. Siyah pencere açık kaldığı sürece platform çalışır;
kapatmak için pencereyi kapatın veya `Ctrl + C`.

### Test modu (şu an açık)
Başlatma dosyalarında **`TEST_MODU=1`** ayarlıdır: platform **giriş ekranı sormadan** açılır ve doğrudan
bölge müdürü olarak girer. Soldaki turuncu kutudan kullanıcı değiştirerek saha müdürü ya da ziyaretçi
görünümünü de deneyebilirsiniz (yetkiler gerçek davranır: saha müdürü başka mıntıkayı düzenleyemez).

Canlıya alırken kapatın: `baslat.bat` içindeki `set "TEST_MODU=1"` satırını `0` yapın
(macOS/Linux'ta `baslat.sh` / `baslat.command` içindeki `TEST_MODU=1`). Kapatıldığında aşağıdaki
giriş ve kayıt akışı devreye girer. Docker ve bulut kurulumunda test modu zaten kapalıdır.

### İlk giriş (bölge müdürü — Erhan Başaçar)
İlk açılışta yalnızca **bölge müdürü hesabı** oluşturulur. Bu hesabın **kurulum kodu** (ilk şifresi) iki yere
yazılır: açılan siyah pencereye ve **`instance/ilk_sifreler.txt`** dosyasına. İki yoldan birini seçin:

- **Kayıt ekranından (önerilen):** "Kayıt olun" → **NW1 · Erhan Başaçar** kartı → kurulum kodunu girin →
  kendi kullanıcı adınızı ve şifrenizi belirleyin. Onay beklemeden hesabınız hazır olur.
- **Doğrudan giriş:** kullanıcı adı `erhan` + kurulum kodu ile girip yeni şifre belirleyin.

Hesap bir kez sahiplenildikten sonra NW1 kartı kayıt ekranında kapanır; kimse ikinci kez sahiplenemez.

### Saha müdürlerinin ve ziyaretçilerin kaydı
1. Giriş ekranında **"Kayıt olun"** (veya **"Ziyaretçi hesabı isteyin"**) bağlantısına tıklanır.
2. Kullanıcı türü seçilir: **mıntıka kartı** (NW11 Ozan Selbuz … NW16 Yüksel Aydınol — her kartta illeri yazar)
   ya da **Ziyaretçi** (yalnızca görüntüleme).
3. Ad soyad, **kullanıcı adı** ve **şifre** belirlenir.
4. Başvuru, bölge müdürünün **Yönetim → Kullanıcılar** ekranına düşer (menüde kırmızı sayı rozeti).
   Bölge müdürü rolü ve mıntıkayı kontrol edip **Onayla** veya **Reddet** der; seçilen mıntıkada zaten aktif
   bir hesap varsa ekran uyarır.
5. Onaydan sonra kişi kendi belirlediği kullanıcı adı ve şifreyle giriş yapar.

> Onay adımı güvenlik içindir: onaylanan kişi seçtiği mıntıkanın proje, gelişme ve ziyaret kayıtlarını
> değiştirebilir. Bölge müdürü ayrıca Kullanıcılar ekranından doğrudan hesap da açabilir.

> Yerel kurulumda platforma yalnızca sizin bilgisayarınızdan erişilir. Ekibin girebilmesi için
> aşağıdaki **4. bölüme** (bulut veya şirket sunucusu) bakın.

---

## 2. Yetkiler

| | Bölge Müdürü | Saha Müdürü | Ziyaretçi |
|---|---|---|---|
| Tüm bölgeyi görme (pano, projeler, ziyaretler, bayiler, analizler) | ✔ | ✔ | ✔ |
| Kendi mıntıkasının proje / gelişme / ziyaret kaydı | ✔ | ✔ | ✖ |
| Başka mıntıkanın kaydını değiştirme | ✔ | ✖ (403) | ✖ |
| Projeleri seçip toplu arşivleme / silme | ✔ (tümü) | ✔ (yalnız kendi) | ✖ |
| Bölge müdürüne iş atama | – | ✔ | ✖ |
| Atanan işlerin durumunu değiştirme / yanıtlama | ✔ | ✖ (not yazabilir) | ✖ |
| Excel'e aktarma | ✔ | ✔ | ✖ |
| Kayıt başvurularını onaylama / reddetme | ✔ | ✖ | ✖ |
| Kullanıcı ekleme, şifre sıfırlama, pasif yapma | ✔ | ✖ | ✖ |
| İşlem geçmişi ve veritabanı yedeği | ✔ | ✖ | ✖ |

Saha müdürü yeni proje açtığında proje otomatik olarak kendi koduyla numaralanır; başka bir müdür
adına kayıt açamaz, başka müdürün bayisine ziyaret planlayamaz.

---

## 3. Sayfalar

| Sayfa | İçerik |
|---|---|
| **Giriş / Kayıt** | Kullanıcı adı + şifre ile giriş; "Kayıt olun" ile Bölge Müdürü (kurulum kodu), mıntıka veya Ziyaretçi seçip hesap açma. |
| **Pano** | 8 gösterge, saha müdürü performans tablosu (proje + gelişme + ziyaret + pazar payı), öncelikli 15 iş, bu haftanın ziyaret planı, risk ısı haritası, grafikler. Saha müdürlerine ayrıca **"Benim listem"** kutusu. |
| **Projeler** | Süzme (saha müdürü, departman, öncelik, durum, zaman, seviye, arama), **her sütuna göre sıralama**, **toplu seçim** (tek tek ya da başlıktaki kutuyla tümü) → **Arşivle / Arşivden çıkar / Sil**. "Görünüm" filtresiyle Aktif / Arşiv / Tümü. |
| **Bölge Müdürüne İşler** (saha) / **Saha'dan Gelen İşler** (bölge müdürü) | Saha müdürü bölge müdüründen beklediği onay, karar, destek veya ziyareti iş olarak atar (öncelik, istenen tarih, ilgili bayi/proje). Bölge müdürü durumu günceller (Yeni → İnceleniyor → Devam Ediyor → Tamamlandı / Reddedildi), yanıt ve not yazar; iki taraf aynı kartta yazışır. Menüde yeni iş sayısı rozeti, panoda özet kutusu. Saha müdürü yalnızca kendi atadığı işleri görür. |
| **Proje kartı** | Künye, alt adımlar, **adım adım gelişme günlüğü**, gelişme ekleme formu, ilgili ziyaretler. Giriş ve güncellemeler buradan yapılır. |
| **İstasyon Ziyaretleri** | Saha müdürü × gün **haftalık plan ızgarası**, liste görünümü, gecikmiş planlar, tek tıkla "Gerçekleşti". |
| **Aksaklıklar** | 143 bulgu; **"Projeye dönüştür"** tek tıkla bulgudan proje açar. |
| **Kredi-Risk** | Vadesi geçmiş borç raporu + WhatsApp onay yazışmaları: mıntıka kırılımı, gün aşımı (yaşlandırma), haftalık değişim, risk skoruna göre borçlu bayiler, onay akışı (unpaid / limit / risk / sipariş, sonuç, yanıt süresi). Bayi kartında da borç künyesi ve o bayinin onay geçmişi görünür. |
| **Bayi Portföyü** | 227 bayi: hacim, sıfır satış günü, trend, yıllık değişim, kâr, son ziyaret, risk. Bayi kartında bulgu ve ziyaret geçmişi. |
| **Mıntıka Analizi** | 6 mıntıkanın 30 ölçütte karşılaştırması (bulgu sayıları canlı). |
| **Pazar Payı** | EPDK verisiyle bölge / saha müdürü / şehir kırılımı ve aylık seyir. |
| **Excel'e Aktar** | Projeler (arşiv sütunuyla), gelişmeler, ziyaretler, aksaklıklar, kredi-risk (borç + onaylar) ve bölge müdürüne atanan işlerin güncel hâli tek .xlsx dosyada. |

**Arşiv ve silme:** Arşivlenen proje panodan, göstergelerden ve listelerden çıkar ama silinmez; istediğiniz
zaman "Arşivden çıkar" ile geri gelir. **Silme kalıcıdır**: proje, alt adımları ve gelişme kayıtlarıyla birlikte
silinir (bağlı aksaklıklar "Açık"a döner). Ana proje seçildiğinde alt adımları da işleme girer.

Proje numaraları otomatik önerilir: ana proje `NW14-4`, alt adım `NW14-41`.
Formlarda **önce saha müdürü seçilir**, il ve bayi listeleri o mıntıkaya göre daralır.

---

## 4. Ekibe açmak (sonraki adım)

### A) GitHub + Render (bulut, en kolay)
1. GitHub'da **Private (gizli)** bir depo açın — `data/seed_data.json` bayi ünvanları ve kârlılık gibi
   ticari veriler içerir; **depo kesinlikle herkese açık olmamalı.**
2. Bu klasörü depoya yükleyin (`instance/` klasörü `.gitignore` ile zaten dışarıda kalır).
3. <https://render.com> → *New → Web Service* → depoyu seçin → **Docker** ortamı.
4. *Disks* bölümünden `/app/instance` yoluna kalıcı disk bağlayın (veritabanı burada durur).
5. Ortam değişkeni: `GUVENLI_CEREZ=1`. Yayına alındıktan sonra bölge müdürünün ilk şifresi Render'ın
   *Logs* ekranında görünür; saha müdürleri site adresinden kendileri kaydolur.

Her `git push`'ta `.github/workflows/ci.yml` testleri otomatik çalıştırır.

### B) Şirket sunucusu (Docker)
```bash
docker compose up -d --build        # http://sunucu:8000
```
Veriler sunucudaki `./instance` klasöründe kalır. Dışarıya açılacaksa önüne HTTPS (IT'nin
ters vekil sunucusu) konmalı ve `GUVENLI_CEREZ=1` yapılmalıdır.

---

## Sorun giderme

| Belirti | Sebep ve çözüm |
|---|---|
| Tarayıcıda **"127.0.0.1 bağlanmayı reddetti"** | Platform o anda çalışmıyor. **Siyah pencereye bakın:** "PLATFORM ÇALIŞIYOR" yazıyorsa tarayıcıda **F5** ile yenileyin. Pencere kapandıysa veya hata yazıyorsa aşağıdaki satırlara bakın. Siyah pencereyi kapatırsanız platform da kapanır. |
| "Dosyalar zip içinden çalıştırılıyor" | Zip'e sağ tık → **Tümünü ayıkla**, sonra açılan klasördeki `baslat.bat`. |
| "Python bulunamadı" veya Microsoft Store açılıyor | python.org'dan Python kurun, ilk ekranda **Add python.exe to PATH** kutusunu işaretleyin. |
| "Gerekli paketler kurulamadı" | Paketler `paketler/` klasöründe hazır gelir, normalde internet gerekmez. Yine de hata çıkarsa pencerenin ekran görüntüsünü paylaşın. |
| Port 5000 dolu | Platform otomatik olarak 5001, 5002… dener; doğru adres siyah pencerede yazar. |
| Windows "Bilinmeyen yayımcı / SmartScreen" uyarısı | "Ek bilgi" → "Yine de çalıştır". |

---

## 5. Güvenlik

- Şifreler **hash'lenerek** saklanır (Werkzeug / PBKDF2); kimse mevcut bir şifreyi göremez, yalnızca sıfırlayabilir.
- Kayıt olan her hesap bölge müdürü onayından geçmeden giriş yapamaz.
- Şifre en az 8 karakter, harf + rakam; kayıt denemeleri IP başına saatte 10 ile sınırlı.
- 5 hatalı denemede hesap 10 dakika kilitlenir.
- Tüm formlarda CSRF koruması; oturum çerezi HttpOnly + SameSite; güvenlik başlıkları (CSP, X-Frame-Options).
- Her ekleme / değişiklik / silme / giriş **İşlem Geçmişi**'ne yazılır (kim, ne zaman, neyi).

## 6. Yedekleme

Tüm veri tek dosyadadır: **`instance/platform.db`**.
- Bölge müdürü menüsünde **Veritabanı Yedeği** → o anki kopyayı indirir.
- Geri yüklemek için: platformu kapatın, yedeği `instance/platform.db` adıyla yerine koyun, yeniden başlatın.

## 6.1 Kredi-Risk verisinin güncellenmesi

Kredi-Risk bölümü iki kaynaktan beslenir:

| Kaynak | Dosya | İçerik |
|---|---|---|
| Vadesi geçmiş borç raporu | `İstasyonlar Vadesi Geçmiş Borç Raporu ...xlsx` (`aged` sayfası) | NW1 satırları; N11–N16 kodları saha müdürlerine eşlenir, bayi portföyüyle unvan/il üzerinden eşleştirilir |
| WhatsApp onay grubu | `WhatsApp Chat - NW 1.zip` (medya olmadan dışa aktarım) | Saha müdürlerinin onay talepleri, tutarlar (unpaid / limit / risk / sipariş / ipotek / BTM), bölge müdürünün yanıtı ve yanıt süresi |

Yeni rapor geldiğinde iki dosya da aynı isimlerle paylaşılır; veriler `data/seed_data.json` içine yeniden üretilip platform güncellenir.
Otomatik çıkarım olduğu için iki noktada pay bırakın: borç raporundaki bayi unvanları 25 karakterde kesildiğinden
portföyle eşleşmeyen satırlar "portföyle eşleşmedi" etiketiyle görünür; WhatsApp'ta bayi adı geçmeyen takip
mesajları ("yarın kapatacaktır" gibi) aynı saha müdürünün son 6 saatteki bayisine bağlanır, bağlanamazsa bayi
sütunu boş kalır. Tutarlar yazışmalarda **bin TL (ktl)** birimindedir.

## 7. Örnek veriler

Projeler, gelişmeler ve ziyaretler Excel dosyasındaki **örnek kayıtlardır**; kurulum haftasına kaydırılarak
yüklenir ki pano güncel görünsün. Bayi portföyü, aksaklıklar ve pazar payı **gerçek rapor verisidir**
(Ağustos 2026 pompa satışı, 2025–2026 Ocak–Temmuz gelir tablosu, EPDK 2026 Ocak–Temmuz).

Canlı kullanıma temiz başlamak için: platformu kapatın, `instance/platform.db` dosyasını silin ve
**`ORNEK_VERI=0`** ortam değişkeniyle başlatın (Windows: `set ORNEK_VERI=0` sonra `baslat.bat`).
Bayi, aksaklık ve pazar payı verileri yine yüklenir; projeler / gelişmeler / ziyaretler boş gelir.

## 8. Proje yapısı

```
app.py            rotalar ve sayfa mantığı
db.py             SQLite şeması, ilk kurulum, veri yükleme
hesap.py          sabit listeler ve iş kuralları (zaman durumu, öncelik skoru, ID üretimi, pazar payı)
guvenlik.py       oturum, yetki, CSRF, hesap kilitleme
wsgi.py           sunucu giriş noktası (waitress / gunicorn)
templates/        sayfa şablonları (Jinja2)
static/           CSS, JS, Chart.js (internetsiz çalışır)
paketler/         Windows için Python paketleri (kurulum internetsiz/proxy arkasında da çalışır)
data/seed_data.json   Excel dosyasından aktarılan ilk veriler
tests/            otomatik testler (pytest)
```

Geliştirme: `pip install -r requirements-dev.txt` · testler: `pytest -q`
