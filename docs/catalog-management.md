# Uygulama içi katalog yönetimi — B03

Başlangıç `feature/catalog-category-search` / b1eb746; geliştirme dalı
`feature/catalog-management-ui`. Var olan books modelleri, arama sorgusu,
ModelForm validasyonu ve transactional kapak altyapısı kullanılır. Yeni şema,
framework, stok sayacı veya migration yoktur. Django Admin korunmuştur.

## Ekranlar ve izinler

Bütün ekranlar oturum + **is_staff** ve aşağıdaki Django iznini ister.
Staff bayrağı tek başına yetki vermez; aynı izinlere sahip staff olmayan üye de
bu yönetim yollarına erişemez. `sync_library_roles` Kütüphaneci grubunu hazırlar.
Kullanıcı/rol yönetimi mevcut Django Admin üzerinden yetkili yöneticiye aittir.

| URL | İşlem | books izni |
|---|---|---|
| /katalog-yonetimi/ | Arama, filtreler, kapak ve stoklu kitap listesi | view_book |
| /katalog-yonetimi/yeni/ | Çoklu yazar/kategorili kitap ve kapak ekleme | add_book |
| /katalog-yonetimi/kitap/ID/ | Kitap özeti | view_book |
| Aynı sayfada kopya listesi | Demirbaş, raf ve durum görüntüleme | ayrıca view_bookcopy |
| /katalog-yonetimi/kitap/ID/duzenle/ | Kitap bilgileri ve kapak güncelleme/temizleme | change_book |
| /katalog-yonetimi/kitap/ID/kopya-ekle/ | Demirbaş ve rafla yeni AVAILABLE kopya | add_bookcopy |
| /katalog-yonetimi/kopya/ID/raf/ | Yalnız raf güncelleme | change_bookcopy |
| /katalog-yonetimi/authors/ | Yazar listesi ve Türkçe ad araması | view_author |
| /katalog-yonetimi/authors/yeni/ | Yazar ekleme | add_author |
| /katalog-yonetimi/authors/ID/ | Ad/biyografi düzenleme | change_author |
| /katalog-yonetimi/categories/ | Kategori listesi ve arama | view_category |
| /katalog-yonetimi/categories/yeni/ | Kategori ekleme | add_category |
| /katalog-yonetimi/categories/ID/ | Ad/açıklama düzenleme | change_category |

Normal Kütüphaneci grubu listeleme ve yazma izinlerini birlikte alır. Özel
kısıtlı rollerde kayıt sonrası yönlendirilen liste/detay için görüntüleme
izinlerini de verin. Yazma endpoint'leri kendi işlem iznini ayrıca kontrol eder.
CSRF zorunludur. Bu panelde silme işlemi sunulmaz; geçmişi etkileyen işlemler
ve stok değişiklikleri bu görev kapsamında genişletilmez.

## Kullanım

1. `/hesap/giris/` üzerinden yetkili personel hesabıyla giriş yapın.
2. Personel menüsünden Katalog Yönetimi → Yazarlar/Kategoriler; eksik tanımları
   kitap formunu doldurmadan önce oluşturun. Düzenleme bağlı kitaplarda ortak
   tanımı günceller; bu etki form üzerinde açıklanır.
3. Yeni Kitap Ekle'de en az bir yazar, isteğe bağlı çoklu kategori, ISBN/yıl,
   açıklama ve kapak seçin. ISBN kontrol basamağı ve yıl aralığı korunur.
4. Kaydet sonrası kitap envanterine yönlenir. Her fiziksel kitap için benzersiz
   demirbaş ve rafla bir kopya ekleyin. Stok elle girilmez.
5. Rafı düzenle yalnız shelf_location + updated_at yazar; kopya satırı POST'ta
   kilitlenir. İstemci book/status/inventory_code gönderse bile bunlar kaydedilmez.
6. Teslim/iade/uzatma için mevcut personel masasını kullanın. Loan/Fine ve
   geçmiş korumaları aynen kalır. Kitap kapağı değiştirme/temizleme mevcut
   commit sonrası kuyruk, ortak dosya ve rollback kurallarını kullanır.

## Doğrulama — 7 Kasım 2026

İlk uygulama commit'i `6ef43ff`. Ayrı worktree `/private/tmp/library-b03` içinde
SQLite + yerel medya ile yeni sunucu `127.0.0.1:18083` portunda başlatıldı;
eski proje sunucusu/DB'si kullanılmadı. Bu adres yalnız yerel önizlemedir.

Chrome Misafir oturumunda gerçek giriş ve form gönderimleriyle:

- İpek Çağrı / Deniz Örnek yazarları, Mühendislik / Bilim kategorileri oluşturuldu.
- Gökyüzü ve Işık, ISBN 9780306406157, yıl 2001, iki yazar ve iki kategoriyle
  eklendi; yerel yapay PNG kapak forma seçilip güvenli JPEG olarak sunuldu.
- S1-001/A-01, S1-002/B-02, S1-003/C-03 tek tek panelden eklendi.
  Sonuç: **1 kitap, 2 yazar, 2 kategori, 3 toplam, 3 müsait kopya**.
- Açıklama kitap düzenleme formuyla değiştirildi. S1-002 rafı B-22 yapılıp
  ardından B-02'ye döndürüldü; üç müsait kopya değişmedi.
- Chrome iPhone SE emülasyonunda 375×667 görünümde navigasyon, arama ve
  kitap kartı görsel olarak kontrol edildi. Bu gerçek cihaz testi değildir.
- Kitap ekleme, kopya ekleme, envanter ve yönetim listesi gerçek ekran görüntüleri
  yerel `/private/tmp/library-b03-preview/screenshots/` altında alındı.
  Bunlar yapay verilerdir; kullanıcı parolaları Git'e eklenmez.

11 yeni otomatik test: ekranlar ve menü, anonim/üye/yetkisiz staff,
her işlem için ayrı permission ve staff kontrolü, CSRF, çoklu ilişkili
kapaklı kayıt, ISBN/yazar/yıl/sahte görsel hataları, kapak değiştirme ve geçmişli
kopya kimliği, mükerrer demirbaş/3 müsait kopya, geçmişli raf değişiminde
manipüle alanları yok sayma, yazar/kategori ekleme-düzenleme ve filtre/stok.

- SQLite tüm paket: **114 keşfedildi; 110 geçti, PostgreSQL'e özel 4 atlandı**.
- İzole PostgreSQL 18.6: **114/114 geçti**; books paketi **74/74**.
- `manage.py check` ve `makemigrations --check --dry-run`: başarılı; yeni migration yok.
- Gerçek Gemini, canlı sunucu veya gerçek üye verisi kullanılmadı.

## Sınırlar

Bütün özel rol kombinasyonları için kayıt sonrası sayfalara view izinlerini
birlikte yapılandırın. Yazar/kategori sayısı çok büyürse checkbox listesi yerine
seçim deneyimi ayrıca değerlendirilebilir; şimdi yeni JS/framework eklenmedi.
Eşzamanlı dolaşım testleri mevcut PostgreSQL paketinde geçiyor; yeni raf yolu
satır kilidi ve dar update_fields kullanır. Ekip review'u/kabulü ve merge ayrı
adımlardır. Bu dal için mevcut workflow yeni CI tetiklemeyebilir; yerel test
sonuçları GitHub Actions başarısı olarak raporlanmaz.
