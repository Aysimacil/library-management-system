# Admin teması — kütüphane arayüzüyle tutarlılık

Dal: `feature/admin-theme-consistency`; başlangıç: `feature/catalog-management-ui`
/ `29bc1dc`. Bu çalışma yalnız sunum ve kullanılabilirlik kapsamındadır.

## Yaklaşım ve kapsanan ekranlar

`templates/admin/base_site.html`, Django'nun `admin/base.html` şablonunu
miras alır. Marka ve başlık “Kütüphane Yönetimi” olur; ana kataloğa dönüş
bağlantısı eklenir. Giriş, ana sayfa, kitap/yazar/kategori/kopya listeleri ve
formları, kullanıcı/grup yönetimi, parola ekranı, ödünç/ceza defterleri ve
ilişkili kayıt popup'ları aynı CSS'i alır. Ayrı bir dashboard veya form sistemi
kurulmadı. Django paketleri ve .venv içeriği değiştirilmedi.

`admin-theme.css`, responsive bloğunda yerleşik sayfa ve responsive CSS'inden
sonra yüklenir. Public `catalog.css` Admin'e toptan eklenmez; global public
seçicilerin Admin widget'larını bozması önlenir. Mevcut tasarım değerleri kullanılır:

| Amaç | Değer |
|---|---|
| Krem zemin | #f7f6f1 |
| Yeşil vurgu/başlık/buton | #244f40; hover #193e30 |
| Metin / ikincil metin | #223b34 / #626d67 |
| Yumuşak yüzey / sınır | #eff2ea / #e1e5dd |
| Klavye odağı | #ab593b |
| Hata metni / yüzeyi | #913d2b / #faeee8 |
| Başlık / gövde | Georgia / sistem sans-serif |

Admin bilinçli olarak **açık temadır**. Dark-mode CSS'i ve theme.js bu şablonda
yüklenmez; yanıltıcı renk değiştirme butonu yerine “Açık tema” notu gösterilir.
CSS hem root hem eski data-theme light/dark değerlerini aynı palete eşler ve
color-scheme: light belirtir. Kullanıcının işletim sistemi veya ana uygulama
teması değiştirilmez; global localStorage temizlenmez.

Tablolar kendi sonuç kapsayıcısında yatay kaydırılır; sütunlar/sıralama/eylemler
saklanmaz. Dar ekranda arama esner, form alanları ve Select2 kutuları kapsayıcıya
sığar, kullanıcı/grup çoklu seçimleri alt alta yerleşir. Kaydet/sil/ara gibi
birincil butonlar en az 44px yüksekliğindedir; odak halkası ve hata metinleri
korunur. Yerleşik breadcrumb, sidebar toggle ve responsive davranışlar kullanılır.

## İşlev ve güvenlik sınırı

ModelAdmin kayıtları, izinler/gruplar, view'lar, servisler, modeller ve migration'lar
aynıdır. Auth/login/logout/CSRF formları kopyalanıp yeniden uygulanmaz; Django'dan
miras alınır. Autocomplete, ilişkili kayıt popup'ları, SelectFilter2, kapak input'u,
form.media ve native JavaScript korunur. Loan/Fine readonly kuralları, geçmişli
kopya korumaları ve kayıt doğrulamaları tema tarafından değiştirilmez.

## Doğrulama — 10 Kasım 2026

- `manage.py check`: başarılı.
- `manage.py makemigrations --check --dry-run`: yeni değişiklik yok.
- `manage.py test`: **118 test; 114 geçti, PostgreSQL'e özel 4 test atlandı**.
  Bu tema görevinde PostgreSQL yeniden başlatılmadı; eski PostgreSQL sonuçları
  yeni sürümde çalıştırılmış gibi raporlanmaz.
- Dört yeni test; 15 Admin sayfasında tema/yerleşik responsive yükleme sırası,
  login ve hatalı login, form hataları/popup, multipart kapak ve autocomplete,
  grup seçim scriptleri, izin ve CSRF reddini doğrular.
- `findstatic` ve ayrı hedefte `collectstatic` ile özel CSS'in bulunması doğrulanır.

Gerçek Chrome'da ayrı gizli oturumda yeni dalın `127.0.0.1:18084` sunucusu
kullanıldı: giriş, ana sayfa, kitap ekleme, kullanıcı listesi ve ana kataloğa
geri dönüş açıldı. Örnek veriler/yönetici yalnız yapay yerel test kaydıdır.
375×667 iPhone SE emülasyonunda kullanıcı araması ve kitap formu incelendi;
keşfedilen dar arama ve taşan Select2/textarea alanları CSS ile düzeltildi.
Karanlık renk tercihi DevTools emülasyonunda da açık palet korundu.
Bunlar gerçek cihaz veya tüm tarayıcı motorları için doğrulama değildir.

Ekran görüntüleri yerel `/private/tmp/library-admin-preview/screenshots/`
altında: login.png, home.png, book-form.png, users.png, users-mobile.png,
book-form-mobile.png, users-mobile-dark-preference.png, form-errors.png ve
public-catalog.png. Ekranlarda kişisel/üretim verisi kullanılmadı.

## Yeni sürümü yerelde açma

Mevcut kirli/staging çalışma alanında branch değiştirmek yerine ayrı worktree:

```bash
git fetch origin
git worktree add -b preview/admin-theme ../library-admin-theme origin/feature/admin-theme-consistency
cd ../library-admin-theme
# Bu dizin için README'deki Python ortamı ve requirements kurulumunu yapın.
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:18084
```

`http://127.0.0.1:18084/admin/` adresine yerel yöneticiyle giriş yapın.
Çalışan önizleme zaten bu portu kullanıyorsa ikinci sunucuyu farklı portta
başlatın. Kendi DB/medya dizinlerinizi kullanın; canlı veride test çalıştırmayın.
Dağıtımda `collectstatic` sonrası statik dosya sunumunu ve gerekirse önbelleği
kontrol edin. Yeni paket veya migration gerekmez.

Bu dal için mevcut CI branch filtresi yeni çalışma üretmeyebilir; yukarıdaki
sonuçlar yerel kontrollerdir, yeni GitHub Actions başarısı iddia edilmez.
