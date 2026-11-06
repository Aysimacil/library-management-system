# Katalog veri modeli — ilk uygulama

Bu belge ikinci ekip üyesinin katalog ve fiziksel kopya çalışmasını açıklar.
Mevcut `books` uygulaması korunmuştur; README'deki `catalog` adı hedef yapı önerisidir.

## Uygulanan alanlar ve ilişkiler

| Model | Alanlar ve kurallar |
|---|---|
| `Author` | Ad, isteğe bağlı biyografi. Aynı adlı farklı yazarlara izin verilir. |
| `Category` | Benzersiz ad, isteğe bağlı açıklama. |
| `Book` | Başlık, isteğe bağlı ISBN/yayın yılı/açıklama, yazarlar, kategoriler, kayıt zamanları. |
| `BookCopy` | Kitap, benzersiz demirbaş kodu, isteğe bağlı raf konumu, durum, kayıt zamanları. |

- `Book.authors` ve `Book.categories` çoktan çoğa ilişkilerdir. Formlarda en az bir yazar gerekir; kategori isteğe bağlıdır.
- `BookCopy.book`, `Book.copies` ters ilişkisini sunar. Fiziksel kopyası olan kitap `PROTECT` ile silinmeye karşı korunur.
- ISBN tire/boşluk içermeyen ISBN-10 veya ISBN-13 biçimindedir. Model/form doğrulaması kontrol basamağını da denetler; ISBN-10 son basamağında büyük `X` kabul edilir.
- ISBN girildiyse veritabanında benzersizdir. ISBN'siz birden fazla kitap eklenebilir. ISBN-10 ile aynı yayının ISBN-13 karşılığı ayrı değerlerdir; otomatik dönüştürme yapılmaz.
- Yayın yılı bilinmiyorsa `NULL`; girildiyse 1–9999 aralığındadır. Yıl ve kopya durumu veritabanı kısıtlarıyla da korunur.
- Kopyalar `AVAILABLE` olarak oluşturulur. İlk sürüm durumları `AVAILABLE` ve `ON_LOAN`'dır. Durum alanı katalog formlarında düzenlenemez.
- Kullanılabilir stok `book.available_copy_count` ile `AVAILABLE` kopyalardan hesaplanır; bağımsız stok sayacı yoktur. Kitap listesi geliştirilirken toplu sayım sorguları kullanılmalıdır.

## Diğer ekip üyeleriyle bağlantı

- Üçüncü ekip üyesinin `Loan` modeli kitap başlığı yerine `books.BookCopy` modeline bağlanmalıdır. Geçmişi korumak için bu ilişkide `on_delete=PROTECT` kullanılmalıdır.
- Ödünç/iade servisi `BookCopy.status` alanını ödünç kaydıyla aynı atomik işlemde güncellemelidir. Alanın katalog formlarında kapalı olması tek başına eşzamanlılık güvencesi sağlamaz; kilitleme ve aktif ödünç benzersizliği dolaşım aşamasında uygulanacaktır.
- Kullanıcı modeli veya rol yapısı bu paket tarafından değiştirilmez. Yönetim paneli Django'nun mevcut model izinlerini kullanır.
- Birinci ekip üyesi PostgreSQL bağlantısını ve ortak ortam ayarlarını tamamladığında migration'lar PostgreSQL üzerinde de doğrulanmalıdır.

## Bu aşamanın kapsamı

Veri modeli, ilk migration, model testleri ve Django Admin yönetimi uygulanmıştır.
Üyelere yönelik katalog ekranları/arama, ödünç/iade, ceza ve LLM sonraki aşamalardır.
`Model.save()` otomatik `full_clean()` çağırmaz; programatik veri girişinde
model doğrulaması ayrıca çalıştırılmalıdır.

## Yönetim paneli

- `/admin/` altında yazar, kategori, kitap ve fiziksel kopyalar yönetilebilir. Erişim için `is_staff` ve ilgili Django model izinleri gerekir; yalnızca staff olmak yetmez.
- Kitaplar başlık, ISBN ve yazar adına göre aranabilir; kategoriye göre filtrelenebilir. Toplam ve müsait kopya sayıları toplu sorguyla hesaplanır.
- Kopyalar demirbaş kodu, kitap adı veya ISBN ile aranabilir; duruma göre filtrelenebilir.
- Kopya durumu katalog panelinde değiştirilemez. Ödünçteki kopyanın kitabı/demirbaş kodu da değiştirilemez ve bu kopya silinemez. Kopyalarda toplu silme kapalıdır.
- Bu panelin arama alanı, üyelere yönelik katalog ekranlarının yerini tutmaz. Üye ekranları sonraki aşamada eklenecektir.

Kontrol komutları:

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test books
```
