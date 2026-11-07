# Kütüphane Yönetim Sistemi

Katalog, üyelik, fiziksel teslim, iade, uzatma ve gecikme cezası işlemlerini tek Django uygulamasında birleştiren ders projesi. Bu README `feature/catalog-management-ui` sürümünü anlatır.

## Yerel kurulum

Python 3.12, Django 6.1.2 ve Django Templates kullanılır. Varsayılan yerel veritabanı SQLite'tır. Eşzamanlı personel işlemleri için PostgreSQL kullanın.

```bash
git clone --branch feature/catalog-management-ui https://github.com/Aysimacil/library-management-system.git
cd library-management-system
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py sync_library_roles
python manage.py seed_library_demo
python manage.py runserver
```

Windows PowerShell'de sanal ortamı `.\.venv\Scripts\Activate.ps1` ile etkinleştirin. Ana sayfa `http://127.0.0.1:8000/` adresindedir. Demo komutu iki hesaba kullanılabilir parola atamaz. Giriş yapmak için yerel terminalde `python manage.py changepassword demo_okur` veya `python manage.py changepassword demo_gorevli` çalıştırın. Yönetici hesabı için `python manage.py createsuperuser` kullanın.

## Kullanım

| Kullanıcı | Ekran ve işlemler |
|---|---|
| Ziyaretçi | Ana sayfada başlık, yazar, ISBN ve demirbaş araması; kategori, müsaitlik, sıralama ve detay. |
| Üye | `/hesap/kayit/` ve `/hesap/giris/`. Kitap detayından teslim talebi, profilde talebi iptal, kendi ödünçleri, uzatma, iade geçmişi ve cezaları. Talep fiziksel kopyayı ayırmaz. |
| Kütüphaneci | `/islemler/` üzerinden üye ve demirbaş arama, fiziksel teslim onayı, iade, uzatma, gecikenler, demo ödeme. `/admin/` üzerinden katalog bakımı. Hesabı Kütüphaneci grubuna ekleyin; admin girişi için staff bayrağını açın. |
| Yönetici | Django superuser; `/hesap/yonetim/` üzerinde canlı kitap, kopya, üye, aktif ve gecikmiş ödünç sayıları. Kullanıcı ve grup yönetimi için `/admin/`. |

`seed_library_demo` yalnız geliştirmede kullanılır. Üç kitap, beş kopya, örnek üye/personel, bir aktif ve bir iade edilmiş ödünç kurar. Tekrar çalıştırma mevcut ödünç geçmişini korur. Yalnız katalog verisi için `seed_catalog` kullanılabilir.

## Veritabanı ve yapılandırma

`.env.example` değişkenleri belgeler. Ayarlar süreç ortamını okur. macOS/Linux için örneği `.env` olarak kopyalayıp kendi değerlerinizi düzenledikten sonra güvenilen dosyayı `set -a; . ./.env; set +a` ile yükleyin. Özel karakterli değerleri kabuğa uygun tırnaklayın. PowerShell'de `$env:DB_ENGINE = "postgresql"` gibi süreç değişkenleri kullanın. Gerçek `.env` Git tarafından yok sayılır.

- PostgreSQL'de uygulamaya ait boş bir veritabanı ve sahibi olan kullanıcı oluşturun. `DB_ENGINE=postgresql`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` değerlerini verip `migrate` ve `sync_library_roles` çalıştırın. Otomatik test kullanıcısı ayrı test veritabanı oluşturabilmelidir. Üretim veritabanında test çalıştırmayın.
- Hizmet günleri pazartesi–cuma. Ek kapalı günler `LIBRARY_CLOSED_DATES` içinde virgülle ayrılmış ISO tarihleriyle verilir. Teslim 14 gün; kapalı vade ilk açık güne geçer. Tek uzatma mevcut vadeye 7 gün ekler. Üye başına en çok üç aktif kopya. Borç veya gecikme yeni teslim ve uzatmayı engeller; iade mümkündür.
- Günlük ücret 5 TL, ödünç başına üst sınır 100 TL. Tarife teslimde sabitlenir. Para hesabı Decimal, tarih hesabı Europe/Istanbul kullanır. İadede tutar kesinleşir; demo ödeme görevliyi ve zamanı kaydeder.
- Üretimde `DJANGO_ENV=production`, `DEBUG=false`, güçlü benzersiz `SECRET_KEY`, açık `ALLOWED_HOSTS` ve gerekiyorsa tam HTTPS `CSRF_TRUSTED_ORIGINS` tanımlayın. Yerelde anahtar verilmezse her süreç geçici anahtar üretir. Oturumların yeniden başlatmada korunması için süreç ortamında kalıcı bir yerel anahtar kullanın.
- Üretimde PostgreSQL ve STARTTLS SMTP varsayılandır. SMTP için `SMTP_HOST`, `SMTP_PORT`, gerekiyorsa `SMTP_USER` ve `SMTP_PASSWORD` verin. Veritabanı TLS ayarı `DB_SSLMODE` olup üretim varsayılanı `require` değeridir; güvenilir CA ve doğrulanmış sunucu adında `verify-full` seçin.
- HTTPS yönlendirme ve güvenli çerezler üretimde açıktır. Yalnız proxy gelen istemci başlığını silip kendisi yazıyorsa ve uygulamaya doğrudan erişim kapalıysa `TRUST_PROXY_HTTPS=true` kullanın. HSTS varsayılanı sıfırdır; gerçek TLS doğrulandıktan sonra `HSTS_SECONDS` değerini kademeli artırın. Tüm alt alanlar hazır olmadan `HSTS_INCLUDE_SUBDOMAINS` veya `HSTS_PRELOAD` açmayın.
- Üretim ayarlarıyla `python manage.py check --deploy` ve `python manage.py collectstatic --noinput` çalıştırın. HTTPS, SMTP teslimi, dağıtım ve yedekten geri yükleme hedef altyapıda ayrıca doğrulanmalıdır.

## Gemini önerileri

Oturum açılmış `/oneriler/` ekranında konu, tür veya yazarla yerel katalogdan en çok 10 aday seçilir. Gemini'ye yalnızca aday katalog verileri gider. Okuyucunun serbest metni, hesabı, ödünç geçmişi ve borcu gönderilmez. Dönen kimlikler sunucuda doğrulanır; en çok üç kitabın güncel başlığı ve müsaitliği veritabanından okunur.

`LLM_PROVIDER=gemini`, kullanılabilir bir `LLM_MODEL` ve sunucu tarafında `LLM_API_KEY` gerekir. Önerilen model adı şablonda verilmiştir; erişim sağlayıcı hesabında doğrulanmalıdır. Girdi sınırı 500 karakter, ağ zaman aşımı 10 saniye, üye kotası dakika/gün başına 5/20, uygulama kotası günde 100 çağrıdır. Anahtar olmadan katalog ve dolaşım kullanılabilir. Bu sürümde sağlayıcı çağrısı taklit yanıtlarla test edilmiştir; gerçek model kalitesi, hesap kotası ve canlı API teslimi doğrulanmamıştır.

## Kontroller ve ekip çalışması

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

SQLite ve PostgreSQL test işleri [CI workflow'unda](.github/workflows/tests.yml) tanımlıdır. Satır kilidi ve yarış testlerini PostgreSQL'de çalıştırın. Katalog PR #3 ve güvenli ortam dalı ayrı kalır; bu dal iki çalışmayı birlikte denemek içindir. Ana dala geçiş ekip onayına bağlıdır.

- [Modüller ve veri sahipliği](docs/architecture.md)
- [Şema ve ER diyagramı](docs/er-diagram.md)
- [Geliştirme, test ve migration notları](docs/development.md)
- [Katalog veri modeli](docs/catalog-data-model.md)
- [Orijinal ders kapsamı ve yol haritası](docs/project-brief.md)

Rezervasyon kuyruğu, gerçek para tahsilatı, otomatik e-posta bildirimi ve canlı dağıtım bu sürümün dışındadır.

## Katalog ve arayüz geliştirmeleri

Katalog yazar, kategori, yıl aralığı ve müsaitlik ile filtrelenebilir. Geçersiz yıl
aralıkları formda gösterilir. Detaydan dönüşte filtreler ve sayfa seçimi korunur.
Yönetici ekranı 7/30/90 günlük teslim, iade ve demo tahsilatları; günlük hareketleri,
ödünçteki stok oranını ve en çok ödünç alınan kitapları gerçek kayıtlardan hesaplar.

Yetkili personel Django Admin kitap formundan JPEG, PNG veya WebP kapak yükleyebilir.
Girdi en fazla 4 MB / 12 milyon piksel olabilir. Dosya içeriği Pillow ile açılır,
yeniden boyutlandırılır, metadata'sız JPEG olarak rastgele adla saklanır.
SVG ve harici kapak URL'si kabul edilmez. Dosyalar `MEDIA_ROOT` altında tutulur
(varsayılan `media/`); bu klasör Git dışında ve çalıştırma yetkisi olmayan kalıcı
depolamada olmalıdır. Kapaklar `/kapak/<kitap-id>/` üzerinden JPEG ve nosniff
başlıklarıyla sunulur. Eksik kapakta başlığı içeren yer tutucu görünür.
Kapak yazma ve eski dosya temizliği commit sonrasında kalıcı kuyrukla yürütülür.
Paylaşılan kapaklar korunur; başarısız dosya işlemleri yeniden denenebilir.

Öneri ekranında kategori, hariç tutulan kategori, müsaitlik ve okuma düzeyi seçilebilir.
Yerel puanlama başlık, yazar, kategori ve açıklama eşleşmelerini sıralar. Sağlayıcıya
yalnız katalogda bulunan kavramlar, seçimler ve adayların eşleşme puanı gider;
serbest girdi ve hesap bilgileri paylaşılmaz. Taklit API testleri canlı Gemini
bağlantısını doğrulamaz. Anahtar ve model erişimi hedef hesapta ayrıca denenmelidir.

## Üretime hazırlık

Üretimde mutlak ve release dışındaki `MEDIA_ROOT`, doğrulanan `MEDIA_VOLUME_ID` işaretçisi ve
`DEFAULT_FROM_EMAIL` zorunludur. Dağıtım dosyaları `deploy/` altındadır.
Gunicorn, HTTPS Nginx proxy'si, kalıcı medya alanı ve kuyruk timer'ı için
[üretim ve geri yükleme yönergesini](docs/production.md) izleyin.

```bash
python manage.py process_cover_operations
python manage.py reconcile_covers
python manage.py backup_library --output /srv/backups/library.zip
python manage.py restore_library_backup --archive /srv/backups/library.zip --target /srv/restore/prova
python manage.py smoke_gemini
```

Son komut anahtar veya --live izni olmadan SKIPPED döndürür. Sağlık rotaları
`/health/live/` ve `/health/ready/` şeklindedir. Canlı sunucu, HTTPS sertifikası,
SMTP ve gerçek Gemini teslimi kendi hedef ortamlarında ayrıca doğrulanmalıdır.

## Uygulama içi Katalog Yönetimi

Personel menüsündeki **Katalog Yönetimi** bağlantısı `/katalog-yonetimi/`
adresini açar. Kitap arama/filtreleme, kapak ve stok; kitap ekleme/düzenleme;
yazar/kategori ekleme-düzenleme; fiziksel kopya ve raf yönetimi kullanılabilir.
Django Admin alternatif yönetim yolu olarak korunur.

Önce `python manage.py sync_library_roles` çalıştırın. Yerel kullanıcıyı yetkili
Django Admin hesabıyla Kütüphaneci grubuna ekleyin ve `is_staff` bayrağını açın.
Parolasını yerel terminalde `python manage.py changepassword <kullanici>` ile
belirleyin. Giriş `/hesap/giris/`, yeni kitap `/katalog-yonetimi/yeni/` adresindedir.
Üye ve izinsiz staff hesapları yönetim ekranlarına erişemez.

[İzinler, ekranlar ve B03 doğrulama notları](docs/catalog-management.md).
