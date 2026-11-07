# Sprint 1 — Üye 2 katalog ve fiziksel envanter kabulü

Amaç: Mevcut katalog sistemini gerçek kullanıcı senaryolarıyla doğrulamak,
eksik P0'ları belirlemek ve **yalnız gereken düzeltmeleri** geliştirmek.
Taban a29b535; uygulama sorumlusu Üye 2. Dolaşım servisi/testi Üye 3;
ortak kurulum/UI Üye 1. Bu belge yeni modül uygulamaz.

## Başlamadan önce

1. [B01](github-backlog.md) kapsamında kapsam ve desteklenen yazma akışı teyit edilir.
2. Ekip, [entegrasyon stratejisi](architecture-review.md) ile ortak tabanı seçer.
   Yeni kod dalı o SHA'dan kısa ömürlü açılır; mevcut dallara force push yok.
3. Yerel/izole test DB; yalnız yapay veriler. PostgreSQL yarış DB kullanıcısının
   test DB oluşturma izni olmalı; canlı DB'de test çalıştırılmaz.
4. `migrate`, `sync_library_roles` ve test başlangıç sonucu kaydedilir.
   Bu sprint yeni tarife, ödeme, staging veya deployment işi almaz.
5. Üye 2 önce mevcut testleri okur: `books/tests.py`, `test_catalog.py`,
   `test_enhancements.py`, `test_media_lifecycle.py`; Üye 3 ile
   `circulation/test_services.py:ConcurrentLoanTests` paylaşılır.

## Ortak yapay test verisi

- Kitap: **Gökyüzü ve Işık — Deneme Kataloğu**, ISBN-13 **9780306406157**, yıl 2001,
  açıklama “Astronomi ve mühendislik için yapay test kitabı.”
- Yazarlar: **İpek Çağrı**, **Deniz Örnek** (kurmaca test adları).
- Kategoriler: **Mühendislik**, **Bilim**; ilişki iki kategori + iki yazar.
- Kopyalar: `S1-001 / A-01`, `S1-002 / B-02`, `S1-003 / C-03`; başlangıç AVAILABLE.
- Diğer kitap: **Başka Deneme**, farklı kategori/yazar; yanlış eşleşme kontrolü.
- Hesaplar: yapay Üye-A ve Üye-B; Kütüphaneci grubu + is_staff görevli;
  is_staff olup izinsiz ayrı kullanıcı; yönetici. Demo/parola gerçek hesaplardan alınmaz.
- Sayfalama alt testi için 13+ yapay kitap. Geçmiş senaryosu için yeni Loan
  servisle oluşturulup yine servisle iade edilir; doğrudan status yazılmaz.

## S1-01 — Görevli iki yazar, iki kategori ve üç kopya ekler

**Bağ:** FR-03,05; B03. **Veri:** Ortak veri seti; başlangıçta ilgili kayıtlar yok.

**Kullanıcı adımları:**

1. Görevli gerçek login formuyla giriş yapar, `/admin/` kayıt yönetimini açar.
2. İki yazar ve kategoriyi ekler; Book formunda ikisini de seçer; ISBN/yıl/açıklama kaydeder.
3. Aynı kitaba üç farklı demirbaş/rafla kopya ekler.
4. Kitap açıklamasını ve ikinci kopyanın rafını `B-22` olarak düzenler.
5. Katalog listesi/detayına geçer; ilişkiler, rafın yetkili görünümü ve stok karşılaştırılır.

**Başlangıç → işlem → sonuç:** Kopyasız kitap → üç kopya ekleme → toplam 3,
müsait 3; iki yazar/iki kategori tam görünür. Raf/açıklama güncellemesi kitap
kimliğini, ilişkileri ve stock'u bozmaz. Kopyalar AVAILABLE başlar.

**Otomatik test:** Mevcut `CatalogModelTests.test_book_supports_multiple_authors_and_categories`
ve `CatalogAdminTests.test_authorized_staff_can_create_book_and_copy` korunur.
Yeni birleşik Admin POST senaryosu 2 M2M + 3 kopya + update sonrasını DB ve
BookDetail context'i üzerinden assert eder. Test adı/konumu sonraki PR'da yazılacak;
burada varmış gibi gösterilmez.

**Manuel doğrulama:** Görevli formu, Admin liste ve kitap detayı gerçek ekranları;
rol, commit, tarayıcı/görünüm genişliği ve sonuç kaydı. Form işinin anlaşılır olup
olmadığını Üye 1 gözlemler. Yeni özel katalog paneli ihtiyaç kanıtı olmadan açılmaz.

**Kabul kriteri:** M2M sayıları 2/2, kopyalar 3, demirbaş/raf eşleşmeleri doğru,
stock 3/3; izinli görevli işlemleri tamamlanır; başka üyenin review kaydı var.

## S1-02 — Üye başlık, yazar ve demirbaşla arar; detayı görür

**Bağ:** FR-04,05; B02. **Veri:** S1-01 + Başka Deneme + 13+ kitaplık sayfalama.

**Kullanıcı adımları:**

1. Üye katalogda `GÖKYÜZÜ`, `ışık`, `ipek`, `ÇAĞRI` ve `S1-002` sorgularını ayrı dener.
2. ISBN `9780306406157` ve yalnız kategori adı `Mühendislik` ile arar.
3. Kategori+yazar+2000–2005+müsait filtrelerini birleştirir, yıl/başlık sıralamasını değiştirir.
4. 2. sayfadan detaya geçip geri döner; filtre/sayfa korunmasını kontrol eder.
5. Olmayan sorgu ve ters yıl aralığında sonucu/hata metnini kontrol eder.

**Başlangıç → işlem → sonuç:** 3 müsait kopyalı kitap → her geçerli sorgu/uygun
filtre → **tek kitap**, stok 3/3; eşleşmeyen sorgu boş sonuç. Demirbaş araması
aynı bibliyografik kitabı getirir, başka üyelerin özel kaydını açmaz.

**Bilinen mevcut fark:** Kategori adı q alanında 0 sonuç veriyor; kategori
seçimiyle 1 sonuç var. Başlık/yazar/Türkçe/filtre/sayfalama kodu mevcut; tekrar
yazılmayacak. Önce kategori sorgusu için başarısız regresyon testi yazılacak.

**Otomatik test:** `CatalogScreenTests` ve
`CatalogEnhancementTests.test_author_year_and_stock_filters_together_and_validation`
korunur. Yeni kategori/ISBN/demirbaş örnekleri; iki yazar ve iki kategoriyle
sonuç tekilliği; her stock count doğru; iki DB motorunda 13+ kitap sayfalama.
Düzeltilen arama mevcut yıl validation ve detail-return testlerini bozmamalı.

**Manuel doğrulama:** Gerçek tarayıcıda sorgu/filtre/sonuç/detay/geri dönüş;
320px ve masaüstü, boş ve hatalı filtre mesajları. Türkçe sözlük sıralaması
isteniyorsa ayrı öneri olarak kararlaştırılır; mevcut lower çözümü o garantiyi vermez.

**Kabul kriteri:** Temel sorgular aynı doğru kitabı bulur; kategori açığı kapanır;
çoğalan satır yok; doğru 3/3; geriye dönüş korunur; üye yazma yetkisi kazanmaz.

## S1-03 — Fiziksel teslim ve iade ile stok 3 → 2 → 3

**Bağ:** FR-05,06,07; B04. **Veri:** Üç AVAILABLE kopya, borçsuz/gecikmesiz Üye-A,
personel. Üye 3 mevcut servisleri kullanır; katalog status'u elle değiştirmez.

**Kullanıcı adımları:**

1. Üye-A detaydan talep gönderir. Stock hâlâ 3 olmalı; talep rezervasyon değildir.
2. Görevli Üye-A ve `S1-001` demirbaşını seçip teslimi onaylar.
3. Üye profili, görevli masası ve katalog detayındaki veriler karşılaştırılır.
4. Görevli iade alır; aynı iade isteğini tekrar gönderir.

**Başlangıç → işlem → sonuç:** 3 AVAILABLE → talep → 3; fiziksel teslim → 2,
tek aktif Loan ve S1-001 ON_LOAN, PENDING talep FULFILLED/Loan eşleşmiş;
iade → 3, returned_at dolu; tekrarlı iade → yine 3, yeni Fine yok.

**Otomatik test:** `LoanTests.test_stock_and_repeated_return` mevcut 2→1→2
senaryosudur ve korunur. `DeskTests.test_request_checkout_and_return_at_staff_desk`
korunur. Yeni ortak üç kopya senaryosu HTTP sonrası DB Loan/status/stock/list/detail
ve talep eşleşmesini kontrol eder; metadata ve ilişkiler değişmez.

**Manuel doğrulama:** İki ayrı oturumda üye/personel; talep, teslim, profil ve
katalog, iade/geçmiş ekranları; tarihler gerçek sunucu yerel tarihine göre.

**Kabul kriteri:** Her aşamada yukarıdaki stock ve Loan/talep değerleri tutarlı;
Üye 2 stok görünümünü, Üye 3 atomik kaydı inceler; kimse sayacı elle düzeltmez.
İlk ortak test **S1-01 fixture ve rol kurulumu hazır olur olmaz**, Sprint 3'ü
beklemeden çalıştırılabilir; B02 arama düzeltmesine teknik olarak bağlı değildir.

## S1-04 — Geçersiz, mükerrer ve yetkisiz işlem ile geçmiş müdahalesi reddedilir

**Bağ:** FR-02,03,05,13; B03/05/06. **Veri:** S1-01; ISBN son basamağı bozuk
`9780306406158`; mevcut `S1-001`; staff-izinsiz, Üye-A; başka kitap; servisle
oluşturulup iade edilmiş geçmişli S1-001.

**Kullanıcı adımları:**

1. Görevli bozuk ISBN ve sonra mükerrer demirbaş kaydını dener.
2. Üye ve izinsiz staff Admin add/change/delete adreslerine doğrudan POST yollar.
3. Geçmişli kopyayı silmeyi/başka kitaba atamayı dener; raf güncellemesini ayrıca dener.
4. Geçmişli demirbaş kimliği readonly olmalı; doğrudan ORM değişiminin politikası
   B05'te karara bağlanır, bugün DB seviyesinde engelliymiş gibi iddia edilmez.

**Başlangıç → işlem → sonuç:** Geçerli veri → hatalı ISBN/duplicate → form hatası,
yeni kayıt yok; yetkisiz POST → erişim reddi, veri değişmez; history→delete/book
reassign→reddedilir; yetkili raf güncellemesi geçmiş/kopya ilişkisini bozmaz.

**Otomatik test:** `CatalogModelTests` ISBN/unique; `CatalogAdminTests` form/izin,
readonly/status/delete; `LoanTests.test_history_protected_after_return` ORM
ProtectedError/trigger kanıtı. Boşluk varsa HTTP POST tüm CRUD izinleri ve
geçmişli Admin alanlarının değerlerini doğrulayan dar testler eklenir. Yeni
migration yalnız B05 kararı zorunlu kılarsa sonraki ayrı PR'da, eski dosyalara dokunmadan.

**Manuel doğrulama:** Mesajlar anlaşılır mı, sayfa çökmesi yerine form hatası mı,
geçmişli kitap/kopya görünümü doğru mu? Rol ve sonuç ekranı kaydedilir.

**Kabul kriteri:** Reddedilen her işlemde önce/sonra DB aynı; geçerli raf güncellemesi
tek alanı değiştirir. Bozuk ISBN model validation, duplicate DB unique ve history
trigger/PROTECT katmanları raporda birbirinden ayrılır.

## S1-05 — Raf değişimi ile teslim eşzamanlı gerçekleşir

**Bağ:** FR-05,07; B04. **Veri:** PostgreSQL izole test DB, S1-001 AVAILABLE;
iki ayrı DB bağlantısı/iş parçacığı; borçsuz Üye-A ve yetkili görevli.

**Kullanıcı adımları:**

1. Bir personel oturumu S1-001 Admin düzenleme formunu açar (eski AVAILABLE görünümü).
2. Ayrı personel oturumu aynı kopyayı Üye-A'ya teslim ederken ilk oturum rafı A-99 kaydeder.
3. DB ve katalog/masa tazelenir. Ters işlem sırası da kontrollü otomatik yarışta denenir.
4. Ayrı alt senaryoda Üye-A ve Üye-B için aynı kopyaya iki teslim yarışır.

**Başlangıç → işlem → sonuç:** AVAILABLE/A-01 → eşzamanlı raf ve teslim →
**ON_LOAN/A-99**, tek aktif Loan; stock 2. İki teslim yarışı → yalnız biri başarılı,
diğeri kopya uygun değil hatası; yine tek aktif Loan ve stock 2.

**Otomatik test:** Mevcut `ConcurrentLoanTests.test_stale_admin_shelf_update_and_issue`
ve `test_double_issue` PostgreSQL üzerinde korunur. İlk test stale instance ile
Admin.save_model çağrısını sınar; tam Admin POST/queryset kilidi/form temizliği
ayrı test/prova ile tamamlanır. Yeni testte senkronizasyon Barrier/event ve ayrı
bağlantı; sonsuz sleep yerine timeout; işlem sonrası close connections. Gerekli
assert'ler Loan count, status, shelf ve available count'tur.

**Manuel doğrulama:** İki ayrı tarayıcı oturumu ve kontrollü işlem sırası; kanıt
DB/test çıktısı ile desteklenir, manuel aynı anda tıklama tek başına yarış kanıtı değildir.

**Kabul kriteri:** PostgreSQL'de iki desteklenen kayıt akışı veri kaybı yaratmaz;
status/raf doğru, tek aktif Loan; SQLite atlanan test olarak raporlanır. Başarısız
veya timeout olan test gizlenmez; B04 tamamlanmaz.

## Uygulama sırası ve dar commit planı

1. **Kanıt/fixture:** B01 kararını ve ortak SHA'yı kaydet; mevcut kitap/test/admin
   işlerini tekrar geliştirmeden yukarıdaki senaryolarla test boşluklarını belirle.
2. **İlk gerçek kod işi B02:** Kategori adı q=Mühendislik için failing test;
   `BookList.get_queryset` içine gerekli kategori eşleşmesini minimal ekle;
   join/count/sayfalama testleriyle yeşile getir. Önerilen dal
   `feature/catalog-category-search`, commit konusu `fix: include categories in catalog search`.
3. **Arama kanıtı:** ISBN/demirbaş ve çoklu ilişki regresyonlarını tamamla;
   mevcut Türkçe aramayı koru. Mantıklı test commit'i.
4. **Admin/CRUD kabulü B03:** Eksik birleşik 2/2/3 ve invalid/unauthorized
   testlerini ekle; test hatası bulmadan form/ekranı yeniden yazma.
5. **Ortak stok/yarış B04:** Üye 3 ile S1-03/05; mevcut servisleri kullan;
   yalnız kanıtlı hata varsa en dar modülde düzelt. PostgreSQL kanıtı ayrı kaydedilir.
6. **B05 karar:** Geçmişli demirbaş/ORM politikası; P1 olarak kabul veya ertele.
   Bu karar kesinleşmeden yeni trigger veya migration tasarlama.
7. **Kapanış:** Her iki DB test sonucu, gerçek manuel ekranlar ve reviewer;
   docs/ER/rapor katkı kaydı; açık kalanlar backlog. Merge ekip onayıyla ileriki sprintte.

### İlk sorumluluklar

- **Sen / Üye 2:** Mevcut arama testlerini okuyup B02'nin kategori-tekilliği
  regresyonunu yaz; testin eski kodda başarısız olduğunu kanıtla. Ardından minimal arama düzeltmesi.
- **Üye 3:** B04 için aynı BookCopy.pk sözleşmesiyle üç kopya/iki üye fixture'ı
  ve PostgreSQL test ortamı hazırla; mevcut `borrow_book/return_book` yollarını birlikte gözden geçir.
- **Üye 1:** Ortak taban/kurulum ve B12 akademik şablon/kanıt toplama; güncel
  demo UI'ının Admin ve kullanıcı akışı yeterliliğini incele; staging başlatma.

## Kanıt kaydı şablonu — henüz doldurulmamış

Her senaryo için: tarih, test edilen commit/SHA, hazırlayan/inceleyen rol,
DB motor/sürüm, otomatik komut/sonuç/skip, manuel tarayıcı/rol/genişlik,
ekran bağlantısı, gözlenen sonuç, kalan açık ve ekip kabul kararı.
Boş kayıtlar başarılı kabul edilmez; TESTED → ACCEPTED ancak ekip review'uyla olur.
