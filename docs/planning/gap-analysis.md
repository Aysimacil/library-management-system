# Modül bazlı boşluk analizi

Sürüm `a29b535`, 7 Kasım 2026. [Matris](requirements-matrix.md) gereksinim kimliklerini,
[kanıt kaydı](README.md) test sınırlarını tanımlar. Buradaki açıklar yeni baştan
modül geliştirme talebi değildir. **Doğrulanmış işlev**, **kod farkı** ve
**eksik kabul kanıtı** ayrı değerlendirilir.

## A. Katalog ve envanter — Üye 2

### Mevcut ve korunacak davranışlar

- `books/models.py:9–68`: Author/Category/Book; iki M2M. Aynı adlı farklı yazar
  mümkün; kategori adı benzersiz. ISBN boş olabilir; dolu ISBN DB'de koşullu
  benzersizdir. `books/validators.py:validate_isbn` ISBN-10/13 kontrol basamağını
  denetler. ISBN-10/13 eşdeğerlerini birleştirme veya tire temizliği yoktur;
  bunlar açık kaynak gereksinimi olmadığı için otomatik P0 sayılmamalı.
- `books/admin.py:8–57`: yazar/kategori/kitap/kopya CRUD, arama, autocomplete,
  kategori/durum filtreleri, kitap başına toplu stok sayımı. Admin mevcut yönetim
  ekranıdır; ikinci bir katalog paneli gereksinimi henüz kanıtlanmadı.
- `BookCopy` benzersiz demirbaş, raf, iki durum, kitap FK/PROTECT taşır.
  `Book.available_copy_count` ve `books/views.py:catalog_books` bağımsız stok
  sayacı kullanmaz. Bu davranış yeniden tasarlanmamalı.
- `BookList.get_queryset:32–64`: başlık/yazar/ISBN/demirbaş araması; kategori,
  yazar, yıl aralığı, müsaitlik, başlık/yıl sıralaması. 12'li sayfalama ve detaydan
  filtreli sayfaya dönüş testli. `searchable_text` Türkçe I/İ/Ç/Ğ/Ö/Ş/Ü normalizasyonu
  yapar; başlık/yazar örnekleri testli. Bu tam Türkçe sözlük sıralaması değildir.
- Kapak raster doğrulaması, 4 MiB/12M piksel, metadata temizleme, UUID JPEG,
  güvenli kitap rotası, rollback ve ortak referans temizliği testli. Yeni bir
  upload framework'ü veya harici URL desteği gerekli değil.
- Geçmişli kopya `Loan.copy PROTECT` ile silinemez. `books.0002` trigger'ı
  kitap değişikliğini ORM/bulk SQL seviyesinde de önler. Admin geçmişli demirbaş
  ve kitap alanını readonly yapar; raf yazmasında yalnız değişen metadata kaydedilir.

### Açıklar ve kullanıcı etkisi

| Bulgu | Kanıt / durum | Etki | Öncelik ve işlem |
|---|---|---|---|
| Kategori adı serbest aramada yok | `BookList.get_queryset:41–49` title/author/isbn/code içerir; geçici DB'de kategori sorgusu 0, kategori filtresi 1 sonuç | Kullanıcı mevcut kategorideki kitabı aramayla bulamaz; brief §§2,16 kategori aramasını kapsıyor | P0, B02: önce kırmızı regresyon testi, sonra minimal sorgu düzeltmesi; filtre/Count davranışı korunmalı |
| Birleşik personel senaryosu kabul edilmemiş | Mevcut `CatalogModelTests` ilişkileri, `CatalogAdminTests` eklemeyi ayrı testler; iki yazar+iki kategori+üç kopya tek yolculuk değil | Yönetici demo sırasında tutarsız form adımlarına rastlayabilir | P0 B03/B04; S1-01 ve S1-04 kabul testi; CRUD'u yeniden yazma |
| ISBN/demirbaş araması için belirgin bağımsız regresyon örneği eksik | Kodda ikisi var; `CatalogScreenTests` çoğunlukla başlık/yazar/filtre; `test_search_and_category_filter_keep_counts_correct` Admin yazar sorgusu kullanır | Özellikle demirbaşla fiziksel kitabı bulma değişikliklerde fark edilmeden bozulabilir | P0 B02; mevcut kodu koruyup test ekle |
| Geçmişli demirbaş kimliği koruması katmanlar arasında farklı | `BookCopyAdmin.get_readonly_fields` korur; `books.0002` yalnız book_id korur | ORM ile kod değişirse insanın eski demirbaş etiketiyle geçmişi eşleştirmesi zorlaşır; Loan.copy PK geçmişi yine korunur | P1 B05: önce kimlik değişikliği politikasını kararlaştır; kanıtsız veri kaybı iddiası yok |
| Yazar zorunluluğu form düzeyinde | Model.save full_clean çağırmaz; M2M doğrudan ORM'de boş bırakılabilir | İçe aktarılan/demo kitaplarda yazar görünmeyebilir | P1 B03: desteklenen yazma yollarını belgeleyip testle; DB M2M yeniden tasarımını otomatik önerme |
| Kategori/yazar silme davranışı kararı eksik | M2M bağları silinebilir; kopyası olan kitap PROTECT | Kitap kalırken keşif metadatası kaybolabilir | P1 B03: boş ve bağlı kayıt silmeyi ekipçe kabul et; gerekiyorsa sonra form uyarısı |
| Güncel mobil/Admin kullanım kabulü yok | Eski tarayıcı notları var; a29b535 için imzalı senaryo/ekran dosyaları yok | Personel çok adımlı kayıt işinde veya dar ekranda zorlanabilir | P1 B11; Admin yeterlilik ölçümü sonrası özel ekran önerisi değerlendir |

Arama ve stok sorgularında `Count(distinct=True)` ve gruplama kullanılıyor;
`distinct()` kelimesi görünmüyor diye otomatik yinelenen kitap hatası ilan edilmedi.
`related_books` çoklu kategori kesişimi ve stok sayımları için de regresyon
senaryosu önerilir. Büyük katalog performansı ölçülmedi; arama motoru eklemek yerine
ilk aşamada örnek veri hacmiyle sorgu sayısı/yanıt süresi ölçülmeli (öneri/P2).

## B. Hesap ve roller — Üye 3

`accounts/views.py:signup` UserCreationForm ve atomic kayıtla yalnız Üye grubunu
atar; istemciden staff/superuser alanı alınmaz. Login/Logout Django auth view'ları;
çıkış POST. `profile` queryset'leri request.user ile sınırlı. `member_renew` aynı
üyeye ait Loan arar. Dashboard superuser ister. `sync_library_roles` personel
izinlerini kurar; Admin için ayrıca is_staff gerekir.

Mevcut kanıt: `AccountsTests` kayıt rol manipülasyonu, parola, profil/yenileme
sahipliği, personel izinleri ve demo idempotansını testler. Katalog Admin tests
staff olmanın tek başına yeterli olmadığını doğrular.

P0 **B06**: bütün yazma rotaları için anonim/Üye/Kütüphaneci/Yönetici matrisi,
başkasının talebini iptal, fine ödeme ve inaktif kullanıcı davranışı için mevcut
kapsamı genişlet. Kullanıcı etkisi yetkisiz işlem veya çalışması gereken işlemde
403 olabilir; açık test olmaması kanıtlanmış bir açık değildir. Şifre sıfırlama,
e-posta doğrulama, sosyal giriş ve MFA brief'te ilk sürüm zorunluluğu değildir;
başlangıç backlog'una yeni modül olarak alınmadı.

## C. Ödünç, iade ve ceza — Üye 3

| Kural | Kod ve mevcut test | Kalan doğrulama / etki |
|---|---|---|
| 14 gün; kapalı gün ileri ötelenir | `borrow_book:47`, `open_day:15–18`; `test_stock_and_repeated_return`, `test_calendar_and_renewal` | Bağımsız beklenen sabit tarihler ve İstanbul gece sınırı; yanlış vade kullanıcıya hatalı borç gösterebilir |
| En çok 3 aktif ödünç | Üye satır kilidi; `borrow_book:43`; `test_limit_and_missing_copy`, PostgreSQL `test_member_limit_across_different_copies` | İade sonrası yeniden hak ve anlaşılır HTTP hata kabulü |
| Bir kez mevcut vadeden +7 | `renew_loan:79–88`, önceki vade/sayaç/zaman; aynı calendar testi | Son gün, erken uzatma, iade edilmiş kaydın reddi ve başka gecikmiş ödünç testlerini açıklaştır |
| 5 TL/gün, 100 TL/ödünç | Loan Decimal snapshot; `calculate_fine`; Fine OneToOne; `test_fine_boundaries_repeated_payment_and_account_blocks` 0/1/19/25 günü kapsar | Brief'teki 3/20 gün ve toplam 300 TL, gece sınırı ve eski tarifenin korunması açık test değil |
| Borç/gecikme engeli, iade serbest | `check_account`, borrow/renew çağırır; return çağırmaz; aynı fine testi | Ödenmemiş borç+uzatma, başka gecikmiş kayıt ve katalog/profil erişimi için ayrı örnekler |
| Stok dönüşü ve atomiklik | `borrow_book`, `return_book`; `test_stock_and_repeated_return` 2→1→2; rollback testi | Sprint 1 üç kopya 3→2→3 kabulü ve güncel UI kanıtı |
| Tek kopyaya yarış | DB koşullu unique; PostgreSQL `ConcurrentLoanTests.test_double_issue` | HTTP üzerinden iki operatör ve ekip kabul kaydı; SQLite kanıt sayılmaz |
| Raf değişimi sırasında teslim | `BookCopyAdmin.save_model` yalnız metadata yazar; PostgreSQL `test_stale_admin_shelf_update_and_issue` | Gerçek Admin POST/izin/form katmanıyla prova |
| Tekrar iade/ödeme | `return_book:66` erken dönüş; pay_fine kilidi ve ilk aktör/zaman; mevcut servis testleri | Eski iade tekrarı sonrası yeni ödünç ve farklı görevliyle ödeme tekrarında ilk aktör için açık assertion |
| Geçmiş korunur | Loan/Fine FK PROTECT, readonly LedgerAdmin, books.0002 trigger; history testi | Desteklenen yönetim akışları dışındaki ORM/SQL yazmalarının sınırı belgelenmeli |

P0 B07 sayısal tarih/ceza ve idempotans kanıtlarını genişletir. **P1 B08**:
brief §3 tek merkezde politika ister; 3 limiti servis+view'da, süreler serviste,
tarife model default'larında dağılmış. Şu an aynı sayılardalar; bu mevcut yanlış
ceza kanıtı değil, sonraki değişiklikte ayrışma riskidir. Merkezi isimli politika
ve eski Loan tarife/vade snapshot'ını koruyan testler yeterlidir; yeni tarife
paneli gerekmez. **P1 B09**: hizmet saatleri belirlenip ekranda gösterilmeli;
saatler bilinmediği için hayalî saat yazılmamalı ve otomatik mesai engeli eklenmemeli.

## D. Gemini önerileri — Üye 1

`candidate_books` başlık/yazar/kategori/açıklamaya 8/5/4/1 yerel puan verir;
Max ile en yüksek satır puanını alır, en çok 10 aday seçer. Kategori hariç tutma,
müsaitlik ve okuma düzeyi mevcut. Bu yöntem semantik arama veya öğrenilmiş
kişiselleştirme değildir; eşleşmeyen sorgu boş sonuç verir.

`recommend:104–148` kişisel iletişim kalıplarını/500 karakteri sınırlar; serbest
isteği göndermek yerine katalogdan doğrulanan kavramları iletir. Sağlayıcı yalnız
katalog kimlikleri/metadata/tercihleri alır. HTTP timeout 10 saniye; yanıt 64 KiB
ile sınırlı; aday dışı kimlikler atılır; en çok 3 sonuç; güncel kitap DB'den
okunur. Açıklama boşsa özet boş bırakılır. Quota DB sayaçlarında 5/20/100;
anahtar/hata halinde normal katalog çalışır. `UsageWindow` hesap kimliğini
**yerel** scope içinde tutar; dış modele yollanmaz.

Mock testler payload, gizlilik, kota ve hataları doğruluyor; canlı Gemini
başarısını doğrulamıyor. **P1 B10**: uydurma katalogla Türkçe 10 sorguluk rubrik,
beklenen adaylar ve özetin açıklamaya dayalılığı; açık opt-in varsa gerçek API.
Anahtar yoksa SKIPPED; başarı diye yazılmamalı. Gerçek model adı/hesap erişimi,
kota ve sağlayıcı koşulları henüz teyit edilmedi; bu sprintte dış belge doğruluğu
iddia edilmiyor. Tarihsel brief bağlantıları güncel erişim kanıtı değildir.

Riskler: açıklama mevcutken modelin summary metninin doğruluğu semantik olarak
kontrol edilmiyor; katalog verisi de talimat benzeri metin içerebilir. Şablon
autoescape yardımcıdır, önerinin doğruluğunu garanti etmez. Kota penceresi
geçişi/eşzamanlılık ve sıra dışı payload örnekleri eklenmeli. Tam anonimleştirme
vaat edilmemeli; gelişmiş okuma geçmişi kişiselleştirmesi kapsam dışı kalmalı.

## E. Ortak mimari ve arayüz — Üye 1

Tek Django projesi, sunucu tarafında Templates ve yerel CSS/JS kullanılıyor.
Aktif `base.html` Bootstrap yüklemiyor; brief hedef teknoloji tablosu ile fark
var. Karar kaydında kendi CSS yaklaşımı gerekçelendirilebilir; Bootstrap'e geçiş
kendiliğinden zorunlu görev değildir. `catalog_base.html` base'i genişletir;
kart ve kapak partial'ları ortak. Eski `book_form.html`/`borrow_form.html`
dosyalarının varlığı aktif özel CRUD ekranı demek değildir; mevcut URL'ler
kataloğu salt okunur, yazmaları Admin/personel servislerine yönlendiriyor.

Navigasyon izinlere göre görünür, hata sayfaları ve messages var. Güncel tüm
rol akışları için erişilebilirlik ve mobil kabul raporu yok: **B11**.
`templates/circulation/desk.html:9–18` koşula bağlı `</section>` ve ek kapatma
şüpheli; HTML validator/tarayıcı DOM ile doğrulanmalı, görsel bozulma kanıtlanmış
sayılmamalı. Desk listeleri sabit 100/25 sınırında; veri büyürse erişilemeyen
sonuç olabilir (P1 ölçüm/karar). HTML tek satırlı yoğun şablonlar bakım/inceleme
yükü yaratır; hedefli formatlama önerisi, toptan UI yeniden yazımı değil.

## F. Akademik teslimatlar — ortak

| Teslimat | Gerçek durum | Sonraki iş |
|---|---|---|
| Orijinal kapsam ve görev dağılımı | project-brief §§12–16 var; bunlar plan/checklist | B01 ile ekip kararı ve ders şablonu/takvimini doğrula |
| Ara rapor | Yazılmış ara rapor dosyası bulunamadı | B12: §§13 bölüm iskeleti, mevcut kanıt ve ayrı gelecek çalışmalar |
| Final raporu | Final rapor dosyası bulunamadı | B12/Sprint 6: §14 kapsam/sonuç/sınırlılıklar |
| Literatür karşılaştırması | Ayrı okunmuş çalışma analizi yok | Her üye alanıyla ilgili kaynak künyesi, yöntem, bulgu, projeyle farklar; sayı ekipçe belirlenecek |
| APA 7 kaynakça | Düzenlenmiş akademik kaynakça bulunamadı | Gerçekte okunan kaynaklar ve metin içi atıfların eşleşmesi |
| ER | docs/er-diagram.md Mermaid var; temel ilişkiler uyumlu | Ara/final raporda okunur çıktı; Fine.loan OneToOne/unique, M2M ve teknik tabloları metinle tamamla |
| Gerçek ekran görüntüleri | Tarihsel tarayıcı anlatımları var; depoda PNG/JPEG ekran kanıtları bulunamadı | Yapay veriyle kabul edilen sürümde ekran+rol+senaryo+commit kaydı |
| Kişi bazlı katkı | Commit geçmişi var; incelenen geliştirme commit'leri aynı author adıyla görünüyor | Commit yazarını rol/persona sanma; herkes fiilî katkısını ve incelediği PR'ı doğrulasın |

P0 burada kanıtlı bir uygulama açığı anlamından çok **akademik teslim/kabul engeli**
anlamındadır. Kullanıcıyı “proje bitti” sanısına sürüklememek için rapor,
TESTED ve ACCEPTED ayrımını korumalıdır. Kanıt uydurulmaz ve hazır olmayan
şablon/tarih doldurulmaz.
