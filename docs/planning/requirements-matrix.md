# Gereksinim–kod ve kabul matrisi

Taban: `a29b535` / 7 Kasım 2026. Durum sözlüğü ve test kanıtının sınırları için
[planlama dizini](README.md). Kaynak § numaraları aksi yazılmadıkça
[docs/project-brief.md](../project-brief.md) içindir. Sorumlular kişi hesabı değil
**önerilen ekip rolüdür**. P0 temel kapsam/kabul engeli; P1 ilk sürümü tamamlayan
kalite/işlev; P2 ertelenebilir ek kapsam. TESTED yalnız listelenen alt davranışları
kanıtlar. Eksik test, kendiliğinden kod hatası demek değildir. Hiçbiri ACCEPTED değildir.

## FR-01 — Kayıt, giriş/çıkış ve oturum

| Alan | Değer |
|---|---|
| Tanım | Kayıt, giriş/çıkış ve oturum |
| Orijinal kaynak | §§2,12 Üye 3 |
| Sorumlu | Üye 3 |
| Öncelik | P0 |
| Django uygulaması / alan | accounts; Django auth |
| Kod referansı | accounts/views.py:signup; accounts/urls.py; templates/accounts/login.html |
| Mevcut durum | **TESTED** |
| Mevcut otomatik test / kanıt | accounts.tests.AccountsTests.test_public_signup_creates_only_member_even_with_tampered_role; test_invalid_password_rejected |
| Eksik doğrulama | Tarayıcıda oturum yenileme/çıkış, inaktif hesap ve süre sonu kabul kaydı |
| Kabul kriteri | Geçerli kayıt yalnız Üye olur; zayıf parola reddedilir; doğru giriş açar, çıkış POST olur; başarısız giriş yetki kazandırmaz |
| Teknik risk | Kayıt otomatik oturum açar; parola sıfırlama/e-posta doğrulama zorunlu kapsam olarak tanımlanmamış. |

## FR-02 — Rol ve veri erişimi sınırları

| Alan | Değer |
|---|---|
| Tanım | Rol ve veri erişimi sınırları |
| Orijinal kaynak | §§2,5,10,12 |
| Sorumlu | Üye 3 |
| Öncelik | P0 |
| Django uygulaması / alan | accounts; circulation; books admin |
| Kod referansı | accounts/management/commands/sync_library_roles.py:Command.handle; accounts/views.py:profile,dashboard; circulation/views.py; books/admin.py |
| Mevcut durum | **TESTED** |
| Mevcut otomatik test / kanıt | accounts.tests.AccountsTests.test_profile_and_renewal_are_scoped_to_self; test_role_permissions_and_admin_stats; books.tests.CatalogAdminTests.test_staff_without_model_permissions_cannot_manage_catalog |
| Eksik doğrulama | Tüm yazma rotalarında anonim/üye/kütüphaneci/yönetici ve inaktif hesap matrisi eksik |
| Kabul kriteri | Üye başkasının ödüncünü yenileyemez veya iade/ödeme yapamaz; yalnız yetkili personel katalog değiştirir; yönetim superuser ister |
| Teknik risk | Kütüphaneci grubu ve is_staff ayrı; servis borrow/return aktör almaz, yetkilendirme HTTP girişindedir. |

## FR-03 — Kitap, yazar, kategori CRUD ve çoktan çoğa ilişkiler

| Alan | Değer |
|---|---|
| Tanım | Kitap, yazar, kategori CRUD ve çoktan çoğa ilişkiler |
| Orijinal kaynak | §§2,6,12 Üye 2 |
| Sorumlu | Üye 2 |
| Öncelik | P0 |
| Django uygulaması / alan | books |
| Kod referansı | books/models.py:Book,Author,Category; books/admin.py:BookAdmin,AuthorAdmin,CategoryAdmin |
| Mevcut durum | **TESTED** |
| Mevcut otomatik test / kanıt | books.tests.CatalogModelTests.test_book_supports_multiple_authors_and_categories; books.tests.CatalogAdminTests.test_authorized_staff_can_create_book_and_copy; test_book_form_requires_an_author_and_valid_isbn |
| Eksik doğrulama | Yazar/kategori düzenleme-silme ve birleşik iki yazar/iki kategori/üç kopya tarayıcı senaryosunun ekip kabulü yok |
| Kabul kriteri | Yetkili görevli geçerli kitap + iki yazar + iki kategori ekler, günceller; boş yazar formu reddedilir; ilişkili geçmiş korunur |
| Teknik risk | Model.save full_clean çağırmaz; yazar zorunluluğu form katmanında, M2M DB kısıtı değildir. Kategori/yazar silinmesi kitap bağlantısını kaldırabilir. |

## FR-04 — Katalog arama, filtre, sıralama ve detay

| Alan | Değer |
|---|---|
| Tanım | Katalog arama, filtre, sıralama ve detay |
| Orijinal kaynak | §§2 işlevsel gereksinimler,10,16; README Katalog ve arayüz |
| Sorumlu | Üye 2 |
| Öncelik | P0 |
| Django uygulaması / alan | books |
| Kod referansı | books/views.py:BookList.get_queryset,BookDetail; books/forms.py:CatalogFilterForm; books/search.py:searchable_text |
| Mevcut durum | **PARTIAL** |
| Mevcut otomatik test / kanıt | books.test_catalog.CatalogScreenTests; books.test_enhancements.CatalogEnhancementTests.test_author_year_and_stock_filters_together_and_validation |
| Eksik doğrulama | Kategori adına serbest metin araması yok (0/1 sonuçla yeniden üretildi); ISBN/demirbaş uçtan uca araması, Unicode ve ilgili kitap tekilliği için açık senaryolar gerekiyor |
| Kabul kriteri | Başlık/yazar/ISBN/demirbaş/kategori araması bekleneni bulur; kategori/yazar/yıl/müsaitlik birleşir; 12 öğe sayfalama ve detaydan geri dönüş filtreyi korur |
| Teknik risk | Türkçe başlık/yazar normalizasyonu var; demirbaş icontains kullanır. Sıralama Türkçe sözlük sırası garantisi vermez; bu ek bir öneridir. |

## FR-05 — Fiziksel kopya, demirbaş, raf, stok ve geçmiş koruması

| Alan | Değer |
|---|---|
| Tanım | Fiziksel kopya, demirbaş, raf, stok ve geçmiş koruması |
| Orijinal kaynak | §§2,3.1,6,12 Üye 2 |
| Sorumlu | Üye 2 + 3 |
| Öncelik | P0 |
| Django uygulaması / alan | books; circulation |
| Kod referansı | books/models.py:BookCopy,Book.available_copy_count; books/admin.py:BookCopyAdmin; books/migrations/0002_copy_history_guard.py |
| Mevcut durum | **TESTED** |
| Mevcut otomatik test / kanıt | books.tests.CatalogModelTests; books.tests.CatalogAdminTests; circulation.test_services.LoanTests.test_history_protected_after_return; ConcurrentLoanTests.test_stale_admin_shelf_update_and_issue |
| Eksik doğrulama | Üç kopyayla 3→2→3 ortak kabulü; geçmişli demirbaş kimliğinin ORM üzerinden değişimi politikasının kararı |
| Kabul kriteri | Demirbaş benzersiz; kopya AVAILABLE başlar; stok kopyalardan türetilir; geçmişli kopya silinemez/başka kitaba atanamaz; eşzamanlı raf ve teslim durum kaybı oluşturmaz |
| Teknik risk | book_id geçmiş koruması DB trigger; demirbaş readonly koruması Admin düzeyinde. Stok ile Loan eşitliğini doğrudan SQL/bulk update için koruyan çapraz tablo DB kısıtı yok. |

## FR-06 — Kitap talebi ve fiziksel teslimde eşleştirme

| Alan | Değer |
|---|---|
| Tanım | Kitap talebi ve fiziksel teslimde eşleştirme |
| Orijinal kaynak | §§2,3.1 |
| Sorumlu | Üye 3 |
| Öncelik | P0 |
| Django uygulaması / alan | circulation |
| Kod referansı | circulation/models.py:CheckoutRequest; circulation/views.py:request_book,cancel_request; circulation/services.py:borrow_book |
| Mevcut durum | **TESTED** |
| Mevcut otomatik test / kanıt | circulation.test_views.DeskTests.test_request_checkout_and_return_at_staff_desk |
| Eksik doğrulama | İptal, başka üyenin talebini iptal reddi ve talepten sonra son kopyanın kaybı senaryoları |
| Kabul kriteri | Talep stok ayırmaz; tekrarlı talep tek PENDING kayıttır; personel teslimi Loan ve FULFILLED eşleşmesini atomik kaydeder |
| Teknik risk | Bu rezervasyon kuyruğu değildir; talepler arasında öncelik veya teslim garantisi yok. |

## FR-07 — Atomik teslim/iade, eşzamanlılık ve idempotans

| Alan | Değer |
|---|---|
| Tanım | Atomik teslim/iade, eşzamanlılık ve idempotans |
| Orijinal kaynak | §§3.1–3.2,5,10 |
| Sorumlu | Üye 3; 2 ortak kabul |
| Öncelik | P0 |
| Django uygulaması / alan | circulation; books |
| Kod referansı | circulation/services.py:borrow_book,locked_loan,return_book; circulation/models.py:Loan.Meta |
| Mevcut durum | **TESTED** |
| Mevcut otomatik test / kanıt | circulation.test_services.LoanTests.test_stock_and_repeated_return; test_rollback_if_copy_write_fails; ConcurrentLoanTests.test_double_issue |
| Eksik doğrulama | Servis yarışı CI PostgreSQL ile kanıtlı; tam HTTP eşzamanlı test ve ekip kabul kaydı yok |
| Kabul kriteri | 2 müsait→teslim→1→iade→2; aynı kopyaya iki teslimden biri reddedilir; eski iade tekrarı yeni ödüncü/stoku değiştirmez |
| Teknik risk | SQLite select_for_update satır kilidi sağlamaz; PostgreSQL yarışı zorunlu kanıttır. Servislerin atlanması tutarsızlık riski taşır. |

## FR-08 — 14 takvim günü, kapalı günde vade düzeltme, yerel tarih

| Alan | Değer |
|---|---|
| Tanım | 14 takvim günü, kapalı günde vade düzeltme, yerel tarih |
| Orijinal kaynak | §3,3.1 |
| Sorumlu | Üye 3 |
| Öncelik | P0 |
| Django uygulaması / alan | circulation; library_system |
| Kod referansı | circulation/services.py:open_day,borrow_book; library_system/settings.py:TIME_ZONE,LIBRARY_CLOSED_DATES |
| Mevcut durum | **PARTIAL** |
| Mevcut otomatik test / kanıt | circulation.test_services.LoanTests.test_stock_and_repeated_return; test_calendar_and_renewal |
| Eksik doğrulama | Temel vade testinin bekleneni yine open_day ile hesaplaması; bağımsız sabit tarih ve İstanbul gece sınırı; fiziksel hizmet saatleri arayüzde yok |
| Kabul kriteri | 19.10.2026 teslim→02.11.2026 vade; hafta sonu+ardışık tatil ilk açık güne ötelenir; kullanıcı saati belirleyici olmaz; kararlaştırılan hizmet saatleri gösterilir |
| Teknik risk | Hafta sonu sabit kodlanmış, tatiller ortamdan. Gerçek kurum saat/tatil takvimi bilinmiyor. |

## FR-09 — Üye başına üç aktif ödünç sınırı

| Alan | Değer |
|---|---|
| Tanım | Üye başına üç aktif ödünç sınırı |
| Orijinal kaynak | §3,3.1 |
| Sorumlu | Üye 3 |
| Öncelik | P0 |
| Django uygulaması / alan | circulation |
| Kod referansı | circulation/services.py:borrow_book,check_account |
| Mevcut durum | **TESTED** |
| Mevcut otomatik test / kanıt | circulation.test_services.LoanTests.test_limit_and_missing_copy; ConcurrentLoanTests.test_member_limit_across_different_copies |
| Eksik doğrulama | İade sonrası yeniden hak ve arayüz hata mesajı kabul kaydı |
| Kabul kriteri | Üç aktif kaydı olan üyenin dördüncü teslimi reddedilir; iki yarışan teslim limiti aşamaz; iade hak açar |
| Teknik risk | Limit servis içinde 3, talep view içinde tekrar 3 olarak geçiyor; merkezi tek tanım gereksinimi ayrı ele alınmalı. |

## FR-10 — Tek seferlik mevcut vadeden yedi günlük uzatma

| Alan | Değer |
|---|---|
| Tanım | Tek seferlik mevcut vadeden yedi günlük uzatma |
| Orijinal kaynak | §3,3.1 |
| Sorumlu | Üye 3 |
| Öncelik | P0 |
| Django uygulaması / alan | circulation |
| Kod referansı | circulation/services.py:renew_loan; circulation/views.py:member_renew,extend |
| Mevcut durum | **TESTED** |
| Mevcut otomatik test / kanıt | circulation.test_services.LoanTests.test_calendar_and_renewal; test_fine_boundaries_repeated_payment_and_account_blocks; accounts.tests.AccountsTests.test_profile_and_renewal_are_scoped_to_self |
| Eksik doğrulama | Son vade günü, erken uzatma, başka gecikmiş ödünç ve iade edilmiş kayıt için ayrı bağımsız testler |
| Kabul kriteri | Bir kez +7 gün/kapalı gün düzeltmesi; önceki vade, zaman ve sayaç korunur; ikinci, gecikmiş veya yetkisiz uzatma reddedilir |
| Teknik risk | Kurallar doğru servise yönlenmeli; arayüzde düğmenin gizlenmesi yetki kontrolü yerine geçmez. |

## FR-11 — Ceza 5 TL/gün, ödünç başına 100 TL; tek demo ödeme

| Alan | Değer |
|---|---|
| Tanım | Ceza 5 TL/gün, ödünç başına 100 TL; tek demo ödeme |
| Orijinal kaynak | §3.2 |
| Sorumlu | Üye 3 |
| Öncelik | P0 |
| Django uygulaması / alan | circulation |
| Kod referansı | circulation/models.py:Loan.daily_rate,fine_cap,Fine; circulation/services.py:calculate_fine,return_book,pay_fine |
| Mevcut durum | **TESTED** |
| Mevcut otomatik test / kanıt | circulation.test_services.LoanTests.test_fine_boundaries_repeated_payment_and_account_blocks |
| Eksik doğrulama | 3/20 gün, üç ayrı 100 TL cezanın toplamı, gece sınırı, tarife değişse de eski kaydın korunması ve ilk ödeme aktörü için açık testler |
| Kabul kriteri | 0/1/3/19/20/25 gün→0/5/15/95/100/100 TL; iadede tutar sabit; tek Fine; tekrar ödeme ilk görevli/zamanı korur |
| Teknik risk | Decimal ve kayıtlı tarife mevcut; sayısal politikalar farklı dosyalarda. Gerçek/kısmi ödeme kapsam dışı. |

## FR-12 — Borç veya aktif gecikmede teslim/uzatma engeli; iade serbest

| Alan | Değer |
|---|---|
| Tanım | Borç veya aktif gecikmede teslim/uzatma engeli; iade serbest |
| Orijinal kaynak | §3.1–3.2 |
| Sorumlu | Üye 3 |
| Öncelik | P0 |
| Django uygulaması / alan | circulation |
| Kod referansı | circulation/services.py:check_account,borrow_book,renew_loan,return_book |
| Mevcut durum | **TESTED** |
| Mevcut otomatik test / kanıt | circulation.test_services.LoanTests.test_fine_boundaries_repeated_payment_and_account_blocks |
| Eksik doğrulama | Ödenmemiş borçla uzatma, başka gecikmiş kayıt ve borçlunun katalog/profil erişimi için açık testler |
| Kabul kriteri | Borç veya gecikme yeni teslim ve uzatmayı engeller; iade/katalog/kendi hesap erişimi devam eder; ödeme ve gecikme giderilince teslim açılır |
| Teknik risk | Ödeme yapmak aktif gecikmiş ödüncü ortadan kaldırmaz; ceza tavanı da iade sayılmaz. |

## FR-13 — Üye geçmişi, personel işlemleri ve korunan kayıtlar

| Alan | Değer |
|---|---|
| Tanım | Üye geçmişi, personel işlemleri ve korunan kayıtlar |
| Orijinal kaynak | §§2,3.2,12 Üye 3 |
| Sorumlu | Üye 3 |
| Öncelik | P0 |
| Django uygulaması / alan | accounts; circulation |
| Kod referansı | accounts/views.py:profile; circulation/views.py:desk; circulation/admin.py:LedgerAdmin; circulation/models.py PROTECT ilişkileri |
| Mevcut durum | **TESTED** |
| Mevcut otomatik test / kanıt | accounts.tests.AccountsTests.test_profile_and_renewal_are_scoped_to_self; circulation.test_views.DeskTests; circulation.test_services.LoanTests.test_history_protected_after_return |
| Eksik doğrulama | Personel sonuç limitleri, geçmiş/ceza görünümü ve farklı rol kombinasyonlarının manuel kabulü |
| Kabul kriteri | Üye yalnız kendi aktif/geçmiş/cezasını görür; görevli yetkili işlemleri yapar; geçmişli User/BookCopy/Loan silinemez |
| Teknik risk | Masa [:100]/[:25] kesimleri sayfalama sağlamaz. Tam audit trail (teslim/iade aktörü dahil) kaynakta açık zorunluluk değildir: öneri. |

## FR-14 — Katalogla doğrulanan Gemini önerisi ve açıklamaya bağlı kısa özet

| Alan | Değer |
|---|---|
| Tanım | Katalogla doğrulanan Gemini önerisi ve açıklamaya bağlı kısa özet |
| Orijinal kaynak | §3.3,12 Üye 1 |
| Sorumlu | Üye 1 |
| Öncelik | P1 |
| Django uygulaması / alan | recommendations |
| Kod referansı | recommendations/services.py:candidate_books,fetch_suggestions,recommend; recommendations/views.py:index |
| Mevcut durum | **IMPLEMENTED / UNVERIFIED** |
| Mevcut otomatik test / kanıt | recommendations.tests.RecommendationTests.test_only_catalog_payload_and_existing_candidates; test_safe_topics_and_preferences_guide_provider; test_ranking_exclusions_and_stock_happen_before_provider |
| Eksik doğrulama | Gerçek hesap/model erişimi ve Türkçe kalite değerlendirmesi yok; açıklama olunca model metninin gerçekliğini kod semantik olarak doğrulamaz |
| Kabul kriteri | En çok 10 aday/3 geçerli katalog kimliği; başlık/stok DB’den; açıklama yoksa özet boş; açıklamaya dayalı uygunluk ekip rubriğinde doğrulanır |
| Teknik risk | Mock API canlı başarı değildir. Modelin muhakeme/özet doğruluğu kimlik doğrulamasıyla garanti edilmez. |

## FR-15 — LLM gizliliği, kota, hata/anahtar yokluğunda normal akış

| Alan | Değer |
|---|---|
| Tanım | LLM gizliliği, kota, hata/anahtar yokluğunda normal akış |
| Orijinal kaynak | §3.3,10 |
| Sorumlu | Üye 1 |
| Öncelik | P0 |
| Django uygulaması / alan | recommendations |
| Kod referansı | recommendations/services.py:CONTACT,reserve_call,fetch_suggestions,recommend; recommendations/management/commands/smoke_gemini.py |
| Mevcut durum | **TESTED** |
| Mevcut otomatik test / kanıt | recommendations.tests.RecommendationTests.test_contact_and_length_rejected_before_external_call; test_minute_day_and_global_quota; test_timeout_and_bad_payload_do_not_leak_provider_details; test_missing_key_degrades_without_breaking_catalog; recommendations.test_smoke.GeminiSmokeTests |
| Eksik doğrulama | Eşzamanlı kota sınırı, gün/dakika değişimi ve istek/yanıt kötü amaçlı içerik tablosu genişletilmeli |
| Kabul kriteri | 500 karakter; 5/dk,20/gün/üye,100/gün uygulama; 10 sn/tek çağrı; kişisel hesap/ham soru gönderilmez; hata katalog ve dolaşımı bozmaz; canlı için ayrıca --live |
| Teknik risk | Kalıp filtresi tam anonimleştirme değildir; katalog açıklamasına kişisel bilgi girilmemeli. Sağlayıcı şartları/hesap erişimi bu sprintte doğrulanmadı. |

## FR-16 — Ortak gezinme, anlaşılır hata ve mobil kullanıcı akışları

| Alan | Değer |
|---|---|
| Tanım | Ortak gezinme, anlaşılır hata ve mobil kullanıcı akışları |
| Orijinal kaynak | §§4–5,12 Üye 1,16 |
| Sorumlu | Üye 1; herkes kendi ekranı |
| Öncelik | P1 |
| Django uygulaması / alan | templates; static; tüm uygulamalar |
| Kod referansı | templates/base.html; templates/403.html,404.html,500.html; static/css/catalog.css; templates/circulation/desk.html |
| Mevcut durum | **IMPLEMENTED / UNVERIFIED** |
| Mevcut otomatik test / kanıt | books.test_catalog.CatalogScreenTests.test_return_from_detail_keeps_filtered_page; accounts.test_statistics.StatisticsTests; docs/development.md tarihsel tarayıcı kaydı |
| Eksik doğrulama | Güncel a29b535 için rol bazlı klavye/320px/tarayıcı kabul matrisi ve gerçek ekran görüntüleri eksik |
| Kabul kriteri | Üye talep→teslim→uzatma→iade geçmişini izler; hatada anlaşılır geri dönüş; dar ekranda taşma yok; klavye odağı görünür (erişilebilirlik önerisi) |
| Teknik risk | Brief Bootstrap 5 hedefliyor; aktif base kendi CSS’ini kullanıyor. Yeniden framework ekleme yerine mevcut tasarımı ekipçe karara bağla. |

## FR-17 — Tekrarlanabilir kurulum, migration, otomatik test ve entegrasyon kanıtı

| Alan | Değer |
|---|---|
| Tanım | Tekrarlanabilir kurulum, migration, otomatik test ve entegrasyon kanıtı |
| Orijinal kaynak | §§8–10,16 |
| Sorumlu | Üye 1 + 2 + 3 |
| Öncelik | P0 |
| Django uygulaması / alan | tüm uygulamalar; CI |
| Kod referansı | requirements.txt; .github/workflows/tests.yml; books/migrations/; circulation/migrations/; recommendations/migrations/; README.md |
| Mevcut durum | **TESTED** |
| Mevcut otomatik test / kanıt | CI 42373569757: PostgreSQL 93, SQLite 89+4 skip, Nginx başarılı; Sprint 0 yerel SQLite aynı sonuç |
| Eksik doğrulama | Yeni doküman dalı/hedef base mevcut workflow tetikleyicileri dışında; kaynak kod kabulü ve main tabanından yükseltme provası henüz ekipçe kabul edilmedi |
| Kabul kriteri | Temiz DB migrate; model farkı yok; seed iki kez tekrarlanabilir; her kısa feature PR SQLite+PostgreSQL kanıtı taşır |
| Teknik risk | Test sayısı kapsam değildir; migration zincirinin doğruluğu mevcut ortam dışında DB yükseltme verisine de bağlıdır. CI kapsam düzeltmesi gelecek görev. |

## FR-18 — Ara/final rapor, literatür, APA 7, ER, ekran ve kişi katkıları

| Alan | Değer |
|---|---|
| Tanım | Ara/final rapor, literatür, APA 7, ER, ekran ve kişi katkıları |
| Orijinal kaynak | §§12–16 |
| Sorumlu | Üye 1 + 2 + 3 |
| Öncelik | P0 |
| Django uygulaması / alan | docs; akademik teslim |
| Kod referansı | docs/project-brief.md §§13–15; docs/er-diagram.md; docs/development.md; Git commit geçmişi |
| Mevcut durum | **PARTIAL** |
| Mevcut otomatik test / kanıt | Rapor için otomatik içerik kabul testi yok; şema/test kanıtı teknik destek sağlar |
| Eksik doğrulama | Ara/final rapor dosyaları, karşılaştırmalı literatür, APA 7 kaynakça, gerçek ekran varlıkları ve kişi bazlı onaylı katkı kayıtları bulunamadı |
| Kabul kriteri | Ders şablonuna göre gerçek/planlanan ayrımı; modelle uyumlu ER; okunmuş kaynak künyeleri; commit/test/ekran ile katkı beyanı; her üye başka PR inceler |
| Teknik risk | Commit author tek başına üç kişinin fiilî katkısını göstermez. Ders tarihleri ve özgün şablonlar bilinmiyor. |

## FR-19 — Kapak yükleme ve dosya bütünlüğü — mevcut ek özellik

| Alan | Değer |
|---|---|
| Tanım | Kapak yükleme ve dosya bütünlüğü — mevcut ek özellik |
| Orijinal kaynak | ÖNERİ / UI ve üretime hazırlık kapsamı; brief §12 katalog ekranlarıyla ilişkili, zorunlu kapak maddesi yok |
| Sorumlu | Üye 2; depolama 1 |
| Öncelik | P2 |
| Django uygulaması / alan | books |
| Kod referansı | books/covers.py:prepare_cover; books/models.py:Book.save,CoverOperation,MediaLock; books/media_lifecycle.py; books/signals.py |
| Mevcut durum | **TESTED** |
| Mevcut otomatik test / kanıt | books.test_enhancements.CatalogEnhancementTests; books.test_media_lifecycle.MediaLifecycleTests |
| Eksik doğrulama | Ortak kullanıcı kabulü ve işletim sahipliği; gereksiz yeni medya özelliği eklenmemeli |
| Kabul kriteri | Mevcut kapak güvenliği gerilemez; 4 MiB/12M piksel, metadata’sız JPEG; rollback/ortak referans/disk arızasında tutarlılık |
| Teknik risk | Global medya kilidi ve DB’de binary kuyruk bakım yükü yaratır; QuerySet.update/bulk yazmaları yaşam döngüsünü atlayabilir. |

## FR-20 — Yedek, health, HTTPS ve canlı işletim — ertelenebilir altyapı

| Alan | Değer |
|---|---|
| Tanım | Yedek, health, HTTPS ve canlı işletim — ertelenebilir altyapı |
| Orijinal kaynak | ÖNERİ / docs/production.md; brief §1 üretimde ölçeklendirmeyi zorunlu tutmaz |
| Sorumlu | Üye 1 |
| Öncelik | P2 |
| Django uygulaması / alan | books; library_system; deploy |
| Kod referansı | books/backup.py:create_backup,restore_backup; library_system/health.py; deploy/; library_system/settings.py |
| Mevcut durum | **IMPLEMENTED / UNVERIFIED** |
| Mevcut otomatik test / kanıt | books.test_backups; library_system.test_production; library_system.test_settings; CI Nginx config |
| Eksik doğrulama | Hedef sunucu, gerçek TLS/SMTP ve canlı yedekleme politikası yok; staging tamamlanmadı |
| Kabul kriteri | İlk akademik demo için yerel kurulum yeterli; altyapı silinmeden dondurulur; canlıya geçiş ayrı onay ve hedef ortam kanıtı gerektirir |
| Teknik risk | ZIP bütünlük kontrolü şifreleme değildir. Bu Sprint 0 kapsamında servis açılmaz; Docker/live deployment yeni zorunluluk yapılmaz. |

## Kapsam dışında

Gerçek/kısmi ödeme, RFID, çok şube, e-kitap, gelişmiş rezervasyon kuyruğu,
ham okuma geçmişiyle kişiselleştirme, canlı deployment ve otomatik bildirim
bu sprintlerin zorunlu tamamlanma kapıları değildir. Yeni talep ayrıca gerekçelendirilir.
