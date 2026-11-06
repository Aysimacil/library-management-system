# Entegrasyon mimarisi

Tek Django projesi ve ortak ilişkisel veritabanı kullanılır. Tarayıcı Django Templates ile çalışır. Alan sahipliği ve ekip sorumlulukları aşağıdadır.

| Alan | Sorumlu | Giriş noktası ve veri sahipliği |
|---|---|---|
| Ortak altyapı ve arayüz | Üye 1 | `library_system/settings.py`, `library_system/urls.py`, `templates/base.html`; profil, ortam, gezinme ve hata ekranları. |
| Katalog | Üye 2 | `books/models.py`, `views.py`, `admin.py`; kitap, yazar, kategori, demirbaş ve raf bilgisi. Müsaitlik kopyalardan hesaplanır. |
| Hesap | Üye 3 | Django User, Group ve Permission; kayıt otomatik Üye rolü verir. Kütüphaneciye yalnız katalog ve dolaşım izinleri tanınır. Superuser kullanıcı ve rol yönetir. |
| Dolaşım | Üye 3 | `circulation/services.py`; teslim/iade/uzatma, tek seferlik ceza ve demo ödeme. Hesap ve personel sayfaları aynı servisleri kullanır. |
| Öneriler | Üye 1 | `recommendations/services.py`; yerel aday seçimi, kota, sağlayıcı bağlantısı ve kimlik doğrulaması. Kataloğu salt okunur kullanır. |

## Katalog ile dolaşımın sınırı

`Loan.copy` fiziksel kopyanın birincil anahtarına bağlıdır ve silmeyi korur. Ödünç tarihçesi olan kopyanın kitap ilişkisini değiştirmek veritabanı tetikleyicisiyle engellenir. Django Admin kopya değişiklik isteğinde kaydı kilitler ve metadata kaydında yalnız değişen alanları yazar. Stok durumunun sahipliği dolaşım servisindedir.

Teslim, iade ve uzatma işlemleri üye → kopya → mevcut ödünç sırasıyla kilit alır. Üye limiti ve borç kontrolü aynı işlemde yapılır. Kopyanın aktif ödünç benzersizliği koşullu DB kısıtıdır. İade edilen kayda yeniden iade gönderildiğinde servis eski sonucu döndürür; kopya yeniden ödünce çıkmış olsa da durumuna dokunulmaz. Ödeme işleminde kilitlenen ceza, ilk görevliyi ve zamanı korur.

Üye kitap için bir teslim talebi oluşturabilir veya bekleyen talebini iptal edebilir. Talep stoğu azaltmaz. Görevli aynı üye ve kitap için fiziksel teslimi onayladığında talep ve ödünç aynı veritabanı işleminde eşleşir.

## Ekip kabulü

1. Üye 1 temiz ortamı, oturumları, ortak gezinmeyi ve sağlayıcı kesintisi davranışını inceler.
2. Üye 2 katalog filtrelerini, demirbaş aramasını, geçmişi olan kopyayı ve eşzamanlı raf güncellemesini kontrol eder.
3. Üye 3 gerçek PostgreSQL üzerindeki 2 → 1 → 2 stok akışını, eşzamanlı teslimi, borç engelini, vade ve tekrarlı iade/ödeme kurallarını doğrular.
