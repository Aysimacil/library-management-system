# GitHub backlog — ilk 12 anlamlı görev

7 Kasım 2026 incelemesinde GitHub issues listesinde yalnız PR #1–#4 bulundu;
ayrı Issue yoktu. Aşağıdaki B01–B12 **yerel görev kodlarıdır, GitHub Issue
numarası değildir**. İlk Issue oluşturma çağrısı 403 `Resource not accessible
by integration` döndürdü. Dolayısıyla **0 Issue oluşturuldu**; aynı başarısız
çağrı diğer 11 görev için tekrar edilmedi. Yetkili bir ekip üyesi bu metinleri
Issue olarak açabilir; önce güncel açık/kapalı Issue'ları yine kontrol etmeli.
Rastgele GitHub hesabına atama yapılmadı.

Project Board erişimi doğrulanamadı; connector repository projects ve labels
endpoint'lerini desteklemiyor. Board/label oluşturuldu iddiası yoktur.
Önerilen label seti: `P0`, `P1`, `P2`, `catalog`, `accounts`, `circulation`,
`recommendations`, `documentation`, `testing`. Label'lar var kabul edilmez.

## B01 — [P0] Gereksinimleri, kuralları ve ekip kabul yöntemini onaylayın

- **Problem:** Kod/test ile ekip kabulü birbirine karışmış; ders şablonu ve takvim doğrulanmamış.
- **Gereksinim / modül:** FR-01–18; documentation / ortak.
- **Sorumlu:** Üye 1 + Üye 2 + Üye 3. **Sprint:** 0. **Label önerisi:** P0, documentation.
- **Kabul:** Kapsam içi/dışı; 14 gün, 3 aktif, +7 tek uzatma, 5 TL ve 100 TL; takvim/hizmet saatleri; TESTED/ACCEPTED ve kişi katkısı kuralları tarihli karara bağlanır. Bilinmeyenler açık kalır.
- **Test:** Karar tablosunu brief §3 ve mevcut servis örnekleriyle karşılaştır; yeni uygulama kodu bu görevde yok.
- **Bağımlılık:** Yok. B02–B11'in uygulama kararlarını besler; ders şablonu harici kaynak.

## B02 — [P0] Kategori araması boşluğunu kapatın; katalog arama regresyonlarını tamamlayın

- **Problem:** Kategori filtresi mevcutken q alanı kategori adını aramıyor. ISBN/demirbaş arama kodunun açık kullanıcı senaryosu testi eksik.
- **Gereksinim / modül:** FR-04; books.
- **Sorumlu:** Üye 2; reviewer Üye 3. **Sprint:** 1. **Label:** P0, catalog, testing.
- **Kabul:** Yalnız kategorisi Mühendislik olan kitap q=Mühendislik ile bulunur; iki yazar/iki kategori join'i aynı kitabı çoğaltmaz; ISBN/demirbaş bulur; filtre/stock/pagination korunur.
- **Test:** Önce başarısız kategori testi; Türkçe kategori, başlık/yazar/ISBN/demirbaş, çoklu ilişki ve 13+ kitaplı sayfalama. SQLite ve PostgreSQL.
- **Bağımlılık:** B01 kapsam teyidi; mevcut BookList ve testler. İlk somut kod görevi budur.

## B03 — [P0] Çoklu yazar/kategori ve üç kopyalı Admin CRUD senaryosunu kabul edin

- **Problem:** Parça testler var; görevlinin birleşik kayıt/bakım akışı ekipçe kabul edilmedi.
- **Gereksinim / modül:** FR-03,05; books/admin.
- **Sorumlu:** Üye 2; Üye 1 kullanılabilirlik review'u. **Sprint:** 1. **Label:** P0, catalog, testing.
- **Kabul:** S1-01; iki yazar/iki kategori/üç benzersiz kopya ve rafları tam kaydolur; kitap/gerekli metadata güncellenir; boş yazar reddedilir. Bağlı yazar/kategori silme politikası ve desteklenen yazma yolları belgelenir.
- **Test:** Admin POST doğrulaması, M2M, üç kopya ve stock 3; create/update/delete izinleri; yapay verili manuel kanıt.
- **Bağımlılık:** B01; mevcut Admin korunur. Özel katalog paneli ancak ölçülen ihtiyaç varsa ayrı öneri.

## B04 — [P0] Katalog–dolaşım stok ve raf yarışını birlikte doğrulayın

- **Problem:** 2→1→2 ve servis yarışları testli; üç kopyalı ortak demo ve tam Admin akışı kabul edilmedi.
- **Gereksinim / modül:** FR-05,07; books + circulation.
- **Sorumlu:** Üye 2 + Üye 3; Üye 1 kanıt incelemesi. **Sprint:** 1. **Label:** P0, catalog, circulation, testing.
- **Kabul:** S1-03/05; 3→2→3; aynı kopyaya iki teslimden yalnız biri; raf değişimi ON_LOAN durumunu ezmez; başarısız işlem stock/Loan bırakmaz.
- **Test:** PostgreSQL ayrı bağlantılar/Barrier; mevcut ConcurrentLoanTests korunur; Admin POST kilit/form katmanı da prova edilir. SQLite skip'i başarı kanıtı sayılmaz.
- **Bağımlılık:** B03 test verisi, mevcut atomik servisler. Sprint 3 modülünün yeniden yazılmasını beklemez.

## B05 — [P1] Geçmişli demirbaş kimliği ve desteklenen yazma yollarını netleştirin

- **Problem:** book_id değişimi DB trigger ile, inventory_code Admin readonly ile korunuyor; ORM/SQL politikasının sınırı belirsiz.
- **Gereksinim / modül:** FR-05,13; books/circulation.
- **Sorumlu:** Üye 2 + Üye 3. **Sprint:** 1 inceleme; gerekirse sonraki dar düzeltme. **Label:** P1, catalog.
- **Kabul:** Geçmişli demirbaş değişikliği yasak mı yoksa kontrollü etiket düzeltmesi mi, yazılı karar; Loan.copy PK korunur; desteklenmeyen bulk yazma açık. Gerekli koruma yalnız karardan sonra uygulanır.
- **Test:** History sonrası silme/book reassign reddi mevcut testlerini koru; yeni inventory kararı için Admin ve ORM örnekleri; migration gerekiyorsa ileri migration incelemesi.
- **Bağımlılık:** B01, B04; bu Issue DB'de kanıtlanmış veri kaybı var demiyor.

## B06 — [P0] Bütün yazma uçları için rol ve sahiplik matrisini tamamlayın

- **Problem:** Temel erişim testli; her rol/rota ve talep/ceza sahipliği kombinasyonu ayrı kanıtlanmadı.
- **Gereksinim / modül:** FR-01,02,06,13; accounts/circulation/books admin.
- **Sorumlu:** Üye 3; Üye 2 reviewer. **Sprint:** 2. **Label:** P0, accounts, testing.
- **Kabul:** Anonim/üye/kütüphaneci/yönetici/inaktif davranışı açık; üye başkasının talebini iptal/Loan yenileme/Fine ödeme yapamaz; staff tek başına yetmez; logout POST/CSRF ve doğru oturum çalışır.
- **Test:** Parametrik HTTP rota matrisi, gerçek login POST, CSRF zorlamalı Client; izin ve sahiplik hatasında veri değişmediği assert edilir.
- **Bağımlılık:** B01 roller, mevcut sync_library_roles ve katalog fixture. Parola sıfırlama yeni zorunlu modül değil.

## B07 — [P0] Tarih, ceza ve idempotans kabul sınırlarını bağımsız örneklerle test edin

- **Problem:** Testler temel kuralları kapsıyor; bazı beklenenler aynı yardımcı fonksiyonu kullanıyor ve kritik sınır örnekleri eksik.
- **Gereksinim / modül:** FR-07–13; circulation.
- **Sorumlu:** Üye 3; Üye 2 stock/history reviewer. **Sprint:** 3. **Label:** P0, circulation, testing.
- **Kabul:** 19.10→02.11 vade; tatil zinciri; İstanbul gün sınırı; son gün/erken/ikinci/gecikmiş uzatma; 0/1/3/19/20/25 gün ceza; üç ödünç toplam 300; eski iade tekrarı yeni ödüncü etkilemez; farklı görevli ödeme tekrarı ilk aktörü korur.
- **Test:** Sabit tarih ve Decimal beklenenleri; borç+uzatma, başka gecikme, iade serbest, rollback ve yarış testleri; eski tarife snapshot testi.
- **Bağımlılık:** B01 kural kararı, B04 stock ve B06 yetki senaryoları.

## B08 — [P1] Sayısal politikaları merkezileştirin; eski Loan koşullarını koruyun

- **Problem:** Brief tek merkez isterken limit servis/view, süre servis, tarife model default'larında dağılmış; ileride ayrışabilir.
- **Gereksinim / modül:** FR-08–12; circulation + request view.
- **Sorumlu:** Üye 3; Üye 1 yapılandırma review'u. **Sprint:** 3. **Label:** P1, circulation.
- **Kabul:** 3/14/7 ve yeni Loan tarifesi için ortak isimli politika; mevcut kayıtlı vade/daily_rate/fine_cap sessizce değişmez. Yeni tarife yönetim paneli gerekmez.
- **Test:** Talep ve teslim aynı limiti uygular; politika değişimi eski Loan cezasını etkilemez; mevcut iş kuralı testleri geçer.
- **Bağımlılık:** B01 ve B07 bağımsız beklenen testler. Migration gerekirse eski dosyalar değiştirilmez.

## B09 — [P1] Hizmet takvimini ve fiziksel teslim saatleri bilgisini netleştirin

- **Problem:** Vade kapalı güne göre düzeliyor; brief §3.1'de istenen saat bilgisi ekranda yok ve gerçek saatler bilinmiyor.
- **Gereksinim / modül:** FR-08,16; circulation/settings/templates.
- **Sorumlu:** Üye 3 kural + Üye 1 UI. **Sprint:** 3. **Label:** P1, circulation, documentation.
- **Kabul:** Ekipten doğrulanmış çalışma gün/saatleri ve tatil kaynağı; kullanıcıya görünür bilgi. Saat bilinmiyorsa “görevliyle teyit edin” gibi dürüst açıklama; uydurma mesai ve yeni otomatik teslim yasağı yok.
- **Test:** Kapalı gün zinciri ve görünür bilgi; kaynak değişince tarih örnekleri tutarlı.
- **Bağımlılık:** B01 kurum/ders kararı; B07 takvim testi.

## B10 — [P1] Gemini için Türkçe kalite, gizlilik ve hata değerlendirme paketi hazırlayın

- **Problem:** Mock adapter testleri var; gerçek hesap/model erişimi ve öneri/özet kalitesi doğrulanmış değil.
- **Gereksinim / modül:** FR-14,15; recommendations.
- **Sorumlu:** Üye 1; Üye 2 aday katalog; Üye 3 gizlilik review'u. **Sprint:** 4. **Label:** P1, recommendations, testing.
- **Kabul:** 10 kişisel bilgi içermeyen örnek sorgu ve beklenen aday/uygunluk/açıklama dayanağı rubriği; aday dışı ID yok; metadata/prompt benzeri içerik ve boş açıklama davranışı kayıtlı; canlı çağrı yalnız ayrıca --live izniyle. Anahtarsız SKIPPED başarı sayılmaz.
- **Test:** Mevcut mock testleri + kota gün/dakika geçişi/eşzamanlılık + bozuk payload tablosu; model çağrısı yoksa kalite UNVERIFIED.
- **Bağımlılık:** B01 LLM kapsamı ve B02/03 açıklamalı katalog. Gerçek hesap erişimi harici bağımlılık, tüm projeyi bloke etmez.

## B11 — [P1] Ortak kullanıcı yolculuğu, UX ve PR/CI inceleme kapısını tamamlayın

- **Problem:** Güncel sürüm için tam rol/tarayıcı kabulü yok; workflow bazı feature/PR hedeflerinde çalışmıyor; #3/#4 kapsamları iç içe.
- **Gereksinim / modül:** FR-16,17; ortak UI/CI/entegrasyon.
- **Sorumlu:** Üye 1 koordinasyon; Üye 2/3 kendi ekranları. **Sprint:** 5 (CI kapsamı yeni kod PR'ından önce yapılabilir). **Label:** P1, testing, documentation.
- **Kabul:** Architecture-review entegrasyon sırası ekipçe kararlaştırılır; yeni kod PR'ları hedeflenen tabanda SQLite+PostgreSQL CI alır; kayıt→talep→teslim→uzatma→iade ve ceza/demo ödeme akışı; 320px/masaüstü/klavye, HTML kapanışları ve hata mesajları kontrol edilir.
- **Test:** Otomatik HTTP yolculuğu, PostgreSQL yarışları ve gerçek tarayıcı kanıtları; başarılı Actions URL/SHA; merge izni ayrı tutulur.
- **Bağımlılık:** B02/04/06/07; B10 sağlayıcı hata akışı. Bu Sprint 0 PR #3/#4'ü değiştirmez veya merge etmez.

## B12 — [P0] Akademik rapor, literatür ve gerçek katkı kanıtlarını hazırlayın

- **Problem:** Plan/checklist ve ER var; yazılmış ara/final rapor, karşılaştırmalı literatür, APA7 ve kişi katkı/ekran varlıkları yok.
- **Gereksinim / modül:** FR-18; documentation / ortak.
- **Sorumlu:** Üye 1 mimari/LLM; Üye 2 ER/katalog; Üye 3 hesap/dolaşım/ceza. **Sprint:** 0'dan 6'ya devam. **Label:** P0, documentation.
- **Kabul:** Gerçek ders şablonu/takvim teyidi; brief §§13–15 bölümleri; her üyenin okuduğu kaynak analizi ve APA7; ER gerçek modele uyumlu; gerçek yapay-verili ekranlar/commit/test bağlantıları; kişi katkıları fiilî çalışmayla doğrulanır. Ekip her iddiayı inceleyip kabul eder.
- **Test:** Belge/atıf/link kontrolü; test sayısı ve sürüm tutarlılığı; demo provası; planlanan/uygulanan/tested/accepted ayrımı. Sahte katkı veya ekran yok.
- **Bağımlılık:** B01 ders kaynağı; kanıt toplama her görevle paralel. Final metni B11 ortak kabul sürümüne bağlanır.

## Project Board taslağı ve geçiş kuralları

**Backlog → Ready → In Progress → In Review → Verified → Done**

| Sütun | Giriş / çıkış koşulu |
|---|---|
| Backlog | Problem ve FR bağlantısı var, kapsam kararı veya bağımlılık bekliyor |
| Ready | Kabul kriteri/test/sorumlu rolü ve bağımlılıkları net; alınabilir |
| In Progress | Rol/kişi işi aldı, kısa feature branch ve iş referansı var |
| In Review | PR veya belge paketi hazır; test kanıtı ve başka üye review'u bekleniyor |
| Verified | Teknik testler ve senaryo kanıtı var; ekip kabulü hâlâ bekleyebilir |
| Done | Ekip senaryoyu kabul etmiş, review ve belgeler tamam, kararlaştırılan tabana entegrasyon durumu açık |

Sprint 0 belge paketinin hazırlanması B01 kararlarını kendiliğinden Done yapmaz.
İlk Ready adayları B01 ve B12 kaynak/şablon toplama; B02–04 test tasarımı paralel
başlayabilir, gereksinim değiştiren uygulama kararı B01'i bekler. Öneri: kişi başına
bir aktif uygulama işi; blocked işlerde nedeni/bağımlılığı açıklamaya yazın.
