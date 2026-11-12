# Geliştirme ve sürüm doğrulama

## Migration sırası

`books.0001_initial` korunmuştur. `circulation.0001_initial` bu katalogla kullanıcı modeline bağlıdır. `books.0002_copy_history_guard` ödünç tablosu oluştuktan sonra SQLite veya PostgreSQL tetikleyicisini kurar. `circulation.0002_checkoutrequest` talep kayıtlarını, `recommendations.0001_initial` kota sayaçlarını ekler. Mevcut katalog verilerini silmezler.

Geçişten önce yedek alın ve geri yüklemeyi ayrı DB'de deneyin. Önce `showmigrations` ve `migrate --plan`, ardından `migrate` kullanın. Mevcut siteyi boş bir veritabanıyla değiştirmeyin. Tetikleyici migration'ının geri işlemi yalnız tetikleyiciyi kaldırır. Ödünç veya ödeme alınmaya başlandıktan sonra tabloları silen ters migration'ları canlı veriye uygulamayın.

## Entegrasyon testi

1. Ayrı bir test DB'si oluşturabilecek kullanıcıyla PostgreSQL ortamını README'ye göre ayarlayın.
2. `python manage.py test circulation.test_services.ConcurrentLoanTests -v 2` çalıştırın. Ayrı bağlantılardaki istekler aynı kopya ve aynı üye limiti için yarışır. Üçüncü test raf değişikliğini teslimle birlikte çalıştırır.
3. `python manage.py test` tüm modülleri ve üretim profilinin ayrı süreçlerde başlangıcını doğrular. Sağlayıcı testlerinde HTTPS istemcisi taklit edilir.
4. Demo kurulumunda üye olarak kitap talep edin; personel olarak üye adı ve demirbaş koduyla teslimi onaylayın. Üye panelindeki son günü ve katalogdaki müsaitliği karşılaştırın. İadeden sonra stok geri gelmelidir.
5. Öneri anahtarını yalnız dağıtım ortamına tanımlayın. Canlı servis denemesini kişisel veri içermeyen sorgu ve harcama sınırlarıyla ayrıca gerçekleştirin.

## 7 Kasım 2026 doğrulama kaydı

Python 3.12.14 / Django 6.1.2 ile ayrı sanal ortamda requirements kurulumu,
temiz SQLite migration'ı, 59 test (PostgreSQL'e özel 3 test atlandı) ve
collectstatic (133 dosya) başarılı. Gerçek PostgreSQL 18.6 üzerinde 59 testin
tamamı geçti. Örnek veri iki kez yüklenince 5 kopya ve 2 ödünç kaydı korundu.

Üretim başlangıç profili HSTS kurulumu için W004 uyarısı veriyor. TLS doğrulanmış
profil değerleriyle check --deploy --fail-level WARNING başarılı. Canlı HTTPS,
SMTP teslimi ve Gemini hesabı doğrulanmadı.

WebKit iPhone profili ve Chromium personel tarayıcısı birlikte kullanılarak
üye kaydı → kitap talebi → personel teslimi → üyeden uzatma → personel iadesi →
üyenin geçmişi akışı doğrulandı. Üye personel ekranından 403 aldı. API anahtarı
olmadan öneri ekranı anlaşılır hata gösterdi. Dar profilde yatay taşma görülmedi.
