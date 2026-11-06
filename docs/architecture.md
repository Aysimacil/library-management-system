# Uygulama mimarisi

Ekip incelemesine sunulan tasarım, tek Django projesi ve ortak ilişkisel veritabanı kullanır. Django view'ları HTTP isteklerini karşılar, şablonlar sayfaları gösterir, ORM modelleri kayıtları ve veritabanı kısıtlarını tanımlar. Birden çok kaydı birlikte değiştiren ödünç ve iade kuralları dolaşım servisinde toplanacaktır.

| Alan | Sorumlu | Bugünkü durum ve sonraki teslim |
|---|---|---|
| `library_system`, ortak şablonlar | 1. kişi | Proje ayarları ve ana URL yapılandırması mevcut. Ortak PostgreSQL kurulumu ve sayfa düzeni planlanıyor. Varsayılan yerel bağlantı SQLite. |
| `books` | 2. kişi | PR #3 kitap, yazar, kategori, fiziksel kopya, yönetim paneli ve okuyucu kataloğunu içeriyor. Stok, müsait kopyaların sayısından hesaplanıyor. |
| `accounts`, `circulation` | 3. kişi | Planlanan hesap, izin, ödünç, iade ve ceza modülleri. Üye ilişkisi için Django'nun yapılandırılmış kullanıcı modeli (`settings.AUTH_USER_MODEL`), roller için gruplar ve model izinleri öneriliyor. |
| `recommendations` | 1. kişi | Planlanan öneri servisi adayları katalogdan okuyacak, dönen kitap kimliklerini doğrulayacak. Harici servis kesintisinde katalog ve dolaşım çalışmaya devam edecek. |

## Katalog ile dolaşım arasındaki sözleşme

- Katalog her fiziksel nüshayı benzersiz demirbaş koduyla oluşturur. Yeni `BookCopy` kaydının durumu `AVAILABLE` olur. Katalog formu durum alanını düzenlemeye kapatır.
- Planlanan `Loan.copy` ilişkisi, fiziksel nüshayı birincil anahtarıyla referans alır (`ForeignKey("books.BookCopy", on_delete=PROTECT)`). Böylece geçmiş ödüncü bulunan kopyalar korunur. İlgili migration, katalog migration'ından sonra uygulanmalıdır.
- Teslimde dolaşım servisi PostgreSQL üzerinde tek işlem içinde üye ve kopya kayıtlarını tutarlı sırayla kilitler. Üyenin limiti ve borç durumu ile kopyanın müsaitliğini kontrol eder, ödüncü oluşturur ve durumu `ON_LOAN` yapar. Kopya başına tek aktif ödünç için koşullu benzersizlik kısıtı planlanır.
- İadede aynı servis ödüncü kapatır, gerekiyorsa o ödünce ait tek cezayı kesinleştirir ve kopyayı `AVAILABLE` yapar. Hata durumunda işlem bütünüyle geri alınır. Tekrarlanan iade ikinci ceza oluşturmamalıdır.
- Kabul senaryosu: iki müsait kopyadan biri teslim edildiğinde katalogda bir, iade edildiğinde iki müsait kopya görünmelidir. Aynı kopyaya eşzamanlı iki teslim isteğinde yalnızca biri başarılı olmalıdır. Bu senaryolar dolaşım modülü eklendiğinde PostgreSQL üzerinde test edilecektir.

## Birleştirme ve sonraki işler

1. Birinci kişi katalog rotalarının ve şablonlarının ortak gezinmeyle uyumunu inceler. İkinci kişi katalog migration'ını ve stok hesabını gösterir. Üçüncü kişi kopya kimliği, durum geçişleri ve geçmişin korunması üzerinde anlaşır.
2. PR #3 ekip incelemesinden geçince katalog ortak dala alınır. Sonra ortak PostgreSQL kurulumu, rol izinleri ve ilk teslim–iade akışı tamamlanır.
3. Süre, uzatma ve ceza hesaplarında README'deki iş kuralları kullanılır. Katalog birleştirildikten sonra öneri servisi ayrı dalda geliştirilebilir. Son kabul testi tüm rolleri ve uçtan uca akışı kapsar.

[Katalog veri modeli ve yapılan doğrulamalar](catalog-data-model.md) · [İş kuralları](../README.md#is-kurallari)

### PR #3 için inceleme adımları

| Kim | Deneme | Beklenen sonuç |
|---|---|---|
| 1. kişi | Demo verisiyle ana sayfada “Atlası” arat, müsaitlik filtresini seç, detayı aç ve katalog bağlantısıyla dön. | Aynı kitap, arama ve müsaitlik seçimi korunur. |
| 2. kişi | Geçici geliştirme veritabanında migration'ları uygula, `seed_catalog` komutunu iki kez çalıştır ve `python manage.py test books` komutunu çalıştır. | Üç demo kitabı ve üç fiziksel kopya bulunur, katalog testleri geçer. |
| 3. kişi | `books/models.py` ve ilk migration'da `BookCopy` kimliğini, kitap ilişkisini ve durum değerlerini kontrol et. | Ödünç modelinde referans alınacak anahtar `BookCopy.pk` olarak netleşir. |

Üçüncü kişinin bu aşamadaki teslimi model ilişkisinin gözden geçirilmesidir. İki eşzamanlı teslim isteğinin PostgreSQL üzerinde denenmesi dolaşım servisiyle birlikte yapılacaktır.
