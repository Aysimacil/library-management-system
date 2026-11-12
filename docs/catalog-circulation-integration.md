# B04 — Katalog ve dolaşım entegrasyonu

Başlangıç: `feature/admin-theme-consistency` / `4ffb15d`.
Görev dalı: `feature/catalog-circulation-integration`.

## Değişiklik ve sorumluluk sınırı

Kitap talebi stok ayırmaz. Personel, talep üzerinden üyeyi ve kitap aramasını
seçer; sonuçlardan müsait fiziksel kopyayı seçip teslimi onaylar. Kopya seçimi
üye ve arama bilgisini, üye seçimi kopya ve arama bilgisini korur. Teslim formunda
seçilen kitabın adı, demirbaş kodu, durumu, güncel stok ve detay bağlantısı görünür.
Ödünçteki arama sonuçları teslim seçeneği sunmaz. Arama sonuçlarındaki fazladan
kapanan `section` etiketi kaldırılarak ödünç tablosunun panel yapısı düzeltildi.

Bu görünüm anlık bir bilgi sunar; kopyayı rezerve etmez. Son doğrulama mevcut
transaction ve kilit kullanan dolaşım servisindedir. Stok BookCopy kayıtlarından
hesaplanır; elle artırılıp azaltılmaz. Loan, ceza, izin, raf kaydetme servisleri,
model ve migration'lar değiştirilmedi. Katalog kopya kimliğini/rafını yönetir;
teslim ve iade durum geçişlerini dolaşım servisi yürütür.

## Çalıştırılan kontroller — 10 Kasım 2026

| Kontrol | Sonuç |
|---|---|
| SQLite, tüm Django testleri | 124 bulundu; 118 geçti, PostgreSQL gerektiren 6 test atlandı |
| PostgreSQL 18, tüm Django testleri | 124/124 geçti |
| PostgreSQL, yeni entegrasyon ve mevcut eşzamanlılık testleri | 9/9 geçti |
| `python manage.py check` | SQLite ve PostgreSQL'de başarılı |
| `python manage.py makemigrations --check --dry-run` | Her iki veritabanında değişiklik yok |

Altı yeni test `circulation/test_catalog_integration.py` dosyasındadır:

1. Yönetim formlarıyla kitap ve üç kopya oluşturma; yinelenen talebin tek kayıtta
   kalması; teslim, profil, iade ve geçmiş; tüm katalog ekranlarında stok 3 → 2 → 3.
2. Yinelenen iade; kopya başka üyeye yeniden teslim edildikten sonra eski iadenin
   tekrar gönderilmesi stok, yeni aktif ödünç veya ceza oluşturmaz/değiştirmez.
3. Raf formuna durum/kimlik alanı gönderilmesi aktif ödüncü değiştirmez; ödünçteki
   kopyayı tekrar teslim isteği HTTP 400 alır ve ikinci Loan oluşmaz.
4. Kopya kaydetme hatası enjekte edildiğinde Loan, talep karşılama ve stok birlikte
   geri alınır. Testte görülen kasıtlı RuntimeError günlüğü beklenen hata yoludur.
5. PostgreSQL'de ayrı bağlantılardan iki eşzamanlı teslim HTTP isteği: biri 302,
   diğeri 400; tek aktif Loan ve iki müsait kopya.
6. PostgreSQL'de eşzamanlı gerçek raf formu ve teslim HTTP istekleri: ikisi de 302;
   yeni raf ve ON_LOAN birlikte korunur.

Yeniden çalıştırma (README'deki izole test ortamı ve DB ayarlarıyla):

```bash
python manage.py test circulation.test_catalog_integration circulation.test_services.ConcurrentLoanTests -v 2
python manage.py test
python manage.py check
python manage.py makemigrations --check --dry-run
```

SQLite kilit yarışlarını doğrulamaz; bu testler PostgreSQL bağlantısıyla ayrıca
çalıştırılmalıdır. Test kullanıcısı izole test veritabanı oluşturabilmelidir.
GitHub Actions sonucu yerel test sonucu yerine geçmez; bu dalın push tetikleyicisi
mevcut CI branch filtresine bağlıdır.

## Gerçek tarayıcı doğrulaması

Chrome Misafir oturumunda, bu dalın `b7eae60` koduyla çalışan ayrı Django sunucusu
ve `library_b04_preview` PostgreSQL veritabanı kullanıldı. Sunucu çalışma dizini
`/private/tmp/library-b04`, adresi `http://127.0.0.1:18085/` idi. Eski Admin tema
önizlemesi (18084) kullanılmadı. Yalnız yapay yerel hesap ve kayıtlar kullanıldı.

| Tarayıcı işlemi | Görülen sonuç |
|---|---|
| Kütüphaneci kitap formunu ve üç kopya formunu kaydetti | Gökyüzü ve Işık; iki yazar, iki kategori; 3 toplam / 3 müsait |
| Üye kitap detayından talep etti | Profilde tek bekleyen talep; stok 3 |
| Kütüphaneci talebi ve S1-001 kopyasını seçip teslim etti | Aktif 1, bekleyen 0; katalog, detay, yönetim listesi ve yönetim detayında stok 2/3 |
| S1-001 rafı A-01 → A-99 güncellendi | Ödünçte durumu ve stok 2/3 korundu |
| Üye yeniden giriş yaptı | Profilde S1-001 aktif ödüncü ve son teslim tarihi |
| Kütüphaneci İade al işlemini yaptı | Aktif 0; yönetim detayında ve public katalog/detayda stok 3/3 |
| Üye yeniden giriş yaptı | Aktif 0; kitap teslim ve iade tarihleriyle okuma geçmişinde |

Veritabanının salt okunur son kontrolünde bir kitap, üç müsait kopya, iade tarihi
dolu tek Loan, bu Loan'a bağlı FULFILLED talep ve sıfır ceza doğrulandı.

Yerel ekran görüntüleri `/private/tmp/library-b04-preview/screenshots/` altında:
`01-stock-3.png`, `02-member-request.png`, `03-staff-issued.png`,
`03b-shelf-stock-2.png`, `04-member-active.png`, `05-return-stock-3.png`,
`06-member-history.png`. Mevcut krem/yeşil tasarım ve kart yapısı korundu.

Eşzamanlılık, tekrarlanan iade ve enjekte edilen hata otomatik HTTP/servis
testleridir; iki fiziksel tarayıcıdan yapılmış yarış veya canlı ortam denemesi
olarak değerlendirilmemelidir. Bu görevde yeni mobil/çoklu tarayıcı matrisi,
gerçek üye verisi, SMTP veya Gemini canlı çağrısı test edilmedi.

## Yerel inceleme

Çalışan önizlemede `/hesap/giris/` üzerinden yerel demo kütüphaneci hesabıyla
giriş yapıp `/katalog-yonetimi/` ve `/islemler/` açılabilir; üye hesabıyla
`/hesap/profil/` üzerinden geçmiş görülebilir. Geçici veritabanı ve sunucu
kapatılırsa önizleme sona erer; bu bir dağıtım adresi değildir. Demo parolaları
Git'e eklenmez. Başka makinede README kurulumunu ayrı worktree ve boş test
veritabanıyla uygulayıp `sync_library_roles` ve kendi yerel hesaplarınızı kullanın.
