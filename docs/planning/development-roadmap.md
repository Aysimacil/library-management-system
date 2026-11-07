# Geliştirme yol haritası — Sprint 0–6

Bu plan **mevcut kodu kabul edilebilir ürüne dönüştürme** planıdır; modüllerin
baştan yazılması planı değildir. Başlangıç kanıtı a29b535, durumlar [matriste](requirements-matrix.md).
Dersin gerçek ara/final teslim tarihleri doğrulanmadı. Aşağıdaki süreler teslim
tarihi değil, üç kişilik öğrenci ekibi için **tahmini kişi-saat** ve önerilen
çalışma pencereleridir. İlk gözden geçirmede gerçek kapasiteyle yeniden hesaplanmalı.
Görev kodları [backlog](github-backlog.md) içindir.

## Sprint 0 — Gereksinim ve proje analizi

- **Hedef:** Ortak kapsam, kaynak–kod–test zinciri, kabul yöntemi ve ilk işler.
- **Önkoşul:** Güncel dal/PR/CI erişimi, orijinal proje özeti.
- **Görevler:** Bu planlama paketi; B01 kapsam/sayısal kararlar; B12 akademik envanter.
- **Sorumlu:** Üye 1 derleme; Üye 2 katalog/ER; Üye 3 hesap/dolaşım. Kararlar ortak.
- **Bağımlılık:** Yok; ders takvimi/şablonu harici karar gerektirir.
- **Yük / pencere:** 8–12 kişi-saat, 2–3 çalışma günü önerisi; ekip inceleme süresi ayrıca.
- **Risk:** Kod varlığının kabul sayılması, author bilgisinin rol sanılması, özgün ders şablonunun eksikliği.
- **Kabul testi:** Matris her temel gereksinimi kod/test/eksik/kriterle bağlar; kategori arama farkı yeniden üretilebilir; protected dallar değişmez.
- **Tamamlanma:** Belgeler repoya gönderilmiş, kaynak/ref kontrolü yapılmış; ekip B01 kararlarını kayıt altına almış. Bu otomasyon belge hazırlığını bitirebilir; ekip onayı henüz alınmış sayılmaz.
- **Teslimatlar:** Yedi planlama belgesi, 12 görev metni, dal/CI kanıtı, Draft PR veya compare.
- **Gözden geçirme:** Her üye kendi alanındaki eksikleri doğrular; Sprint 1 kapsamını ve saat tahminlerini günceller.

## Sprint 1 — Katalog ve envanter

- **Hedef:** Üye 2'nin mevcut katalog akışını gerçek senaryolarla doğrulamak; yalnız eksik P0'ları kapatmak.
- **Önkoşul:** Sprint 0 matrisi, B01 kapsam ve desteklenen katalog yazma yolunun kararı; izole test DB.
- **Görevler:** B02 kategori/ISBN/demirbaş araması; B03 çoklu ilişki ve CRUD kabulü; B04 stok/raf yarışı; B05 kimlik politikası incelemesi.
- **Sorumlu:** Üye 2 uygular; Üye 3 stok/yarış birlikte; Üye 1 UI/kurulum incelemesi.
- **Bağımlılık:** Mevcut circulation servisleri test fixture olarak kullanılır; yeni dolaşım modülü yazılması beklenmez. Sprint 3'te daha geniş iş kuralı kabulü yapılır.
- **Yük / pencere:** 12–18 kişi-saat, 3–5 çalışma günü önerisi.
- **Risk:** Çoklu join stok/sayfalama regresyonu, SQLite yarışın yanlış kanıt sayılması, geçmişli kopyaya müdahale.
- **Kabul testleri:** [S1-01…S1-05](sprint-1-catalog.md): iki yazar/iki kategori/üç kopya; arama; 3→2→3; geçersiz/yetkisiz işlemler; eşzamanlı raf/teslim.
- **Tamamlanma:** P0 senaryoları otomatik+manuel kanıtlı, mevcut testler geçer; Üye 3 kod incelemesi ve Üye 2 kabul kanıtı kayıtlı. P1 kimlik politikası kararı ayrı iş olabilir.
- **Teslimatlar:** Önce kırmızı sonra yeşil kategori testi ve minimal düzeltme; katalog kabul/test/gerçek ekran kayıtları; gerekirse ileri migration ayrı inceleme (şu sprintte planlanmaz).
- **Gözden geçirme:** Admin yeterliliği ve eksik arama/kimlik bulgularını kapat veya gerekçeli ertele; Sprint 2/3 tahminlerini güncelle.

## Sprint 2 — Kullanıcı hesapları ve roller

- **Hedef:** Mevcut auth/rol sınırlarını ve kişiye özel görünümü kabul etmek.
- **Önkoşul:** B01 rol sözleşmesi, katalog fixture ve sync_library_roles.
- **Görevler:** B06 tüm HTTP yazma rotaları için rol/sahiplik matrisi; staff-grup ayrımı, oturum, giriş/çıkış ve inaktif hesap davranışı.
- **Sorumlu:** Üye 3; Üye 1 ekran/oturum; Üye 2 katalog izinlerinin reviewer'ı.
- **Bağımlılık:** Katalog verisi; Sprint 1 devam ederken rol testleri hazırlanabilir. Demo dışı kişisel veri gerekmez.
- **Yük / pencere:** 8–12 kişi-saat, 2–3 çalışma günü önerisi.
- **Risk:** Permission kontrolünün düğme görünürlüğüne indirgenmesi, yanlış rol atama, testte force_login ile gerçek oturum akışının karıştırılması.
- **Kabul testleri:** Anonim yönlendirme, üye başka Loan/talep/Fine işlemine erişemez; personel kendi izinleriyle çalışır ve kullanıcı rolü yönetemez; yönetici yönetir; logout POST/CSRF.
- **Tamamlanma:** Rol matrisi otomatik geçer; yapay hesaplarla manuel giriş/çıkış kanıtı; ikinci üye review'u.
- **Teslimatlar:** Gerekli eksik testler, varsa dar yetki düzeltmesi, profil/izin kabul kaydı.
- **Gözden geçirme:** Reddin beklenen HTTP/message davranışını ekip kararıyla sabitle; Sprint 3'te kullanılacak hesap fixture'larını güncelle.

## Sprint 3 — Ödünç, iade ve ceza

- **Hedef:** Mevcut dolaşım servislerinin sayısal kurallarla ve stok sözleşmesiyle tam kabulü.
- **Önkoşul:** Sprint 1 stok ve Sprint 2 rol senaryoları; B01 tarife/takvim kararı; PostgreSQL test DB.
- **Görevler:** B07 bağımsız tarih/ceza/idempotans örnekleri; B08 merkezi politika; B09 hizmet takvimi ve UI bilgisi.
- **Sorumlu:** Üye 3; Üye 2 kopya/stock/history; Üye 1 ortak arayüz.
- **Bağımlılık:** Rol kabulü olmadan personel işlemleri ACCEPTED olmaz; test tasarımı Sprint 1/2 ile paralel yapılabilir.
- **Yük / pencere:** 14–20 kişi-saat, 3–5 çalışma günü önerisi.
- **Risk:** Tarih/saat sınırı, eski Loan tarife snapshot'ının bozulması, tekrar iadede yeni ödüncün etkilenmesi.
- **Kabul testleri:** 14 gün; kapalı gün zinciri; üç aktif limit; bir kez +7; 0/1/3/19/20/25 gün ve 300 TL toplam; borç/gecikme engeli fakat iade serbest; yarış/rollback/tekrar ödeme.
- **Tamamlanma:** PostgreSQL yarışları dahil testler, bağımsız beklenen değerler, personel/üye demo akışı ve ekip review'u; gerçek ödeme kapsam dışı açık.
- **Teslimatlar:** Gereken sınırlı servis/politika düzeltmeleri, genişletilmiş iş kuralı testleri, tarih/ceza kabul tablosu.
- **Gözden geçirme:** Sayısal kuralları brief ve raporla karşılaştır; Sprint 4/5 entegrasyon hata listesi güncellenir.

## Sprint 4 — Gemini önerileri

- **Hedef:** Mevcut öneri akışını, gizlilik/katalog bağını ve Türkçe öneri kalitesini değerlendirmek.
- **Önkoşul:** B01 LLM kapsamı; yeterli açıklamalı yapay katalog; kalite rubriği. Mock için API anahtarı gerekmez.
- **Görevler:** B10 10 örnek sorgu, beklenen adaylar/uygunluk/özet dayanağı; kota geçişi/hatalı payload; açık opt-in varsa smoke.
- **Sorumlu:** Üye 1; Üye 2 katalog verisi/beklenen aday; Üye 3 kişisel veri/erişim review'u.
- **Bağımlılık:** Aday seçimi için Sprint 1 kabulü. Mock/kalite veri hazırlığı Sprint 2/3'e paralel olabilir; canlı hesap erişimi harici bağımlılık.
- **Yük / pencere:** 10–16 kişi-saat, 2–4 çalışma günü önerisi; hesap erişim gecikmesi hariç.
- **Risk:** Model erişimi/maliyet, açıklamadan taşan özet, prompt injection; sonuçları fazla genelleme.
- **Kabul testleri:** 10 aday/3 sonuç sınırı, aday dışı ID yok; payload kişisel/ham metin içermez; kota/timeout/anahtarsız davranış; temel katalog bağımsız çalışır.
- **Tamamlanma:** Mock güvenlik kanıtları ve rubrik sonuçları var. Gerçek çağrı yoksa canlı kalite **UNVERIFIED** kalır; ders demosunda fallback gösterilir. Akademik hedef canlı doğrulama isterse ekip bu kısıtı çözmeden kabul etmez.
- **Teslimatlar:** Sorgu veri seti ve değerlendirme tablosu, gereken dar adapter/aday düzeltmeleri, canlı veya SKIPPED kanıtı.
- **Gözden geçirme:** Gerçek çağrı ile mock ayrımını ve eksik model erişimini rapora geçir; Sprint 5 kullanıcı mesajlarını güncelle.

## Sprint 5 — Modüllerin entegrasyonu ve UX

- **Hedef:** Kabul edilmiş modülleri tek kullanıcı yolculuğunda ve incelemesi yapılmış ortak tabanda birleştirmek.
- **Önkoşul:** Sprint 1–4 temel senaryoları; ekipçe seçilmiş entegrasyon tabanı/merge sırası.
- **Görevler:** B11 entegrasyon/CI dal kapsamı, responsive/klavye ve hata mesajları; PR inceleme paketleri; gereksiz template/HTML farklarını yalnız kanıtlı ihtiyaçla düzelt.
- **Sorumlu:** Üye 1 koordinasyon; Üye 2 katalog; Üye 3 hesap/dolaşım. Her merge ayrı ekip onayı ister.
- **Bağımlılık:** #3/#4 iç içe tarihçesi; ortak taban kararı. Üretim/staging gerekli bağımlılık değildir.
- **Yük / pencere:** 12–18 kişi-saat, 3–5 çalışma günü önerisi.
- **Risk:** Büyük PR inceleme yükü, eski dalı rewrite etme, workflow'un yanlış dal hedefi yüzünden test çalışmaması.
- **Kabul testleri:** Kayıt→arama→talep→teslim→uzatma→iade→geçmiş; gecikme→ceza→demo ödeme; LLM hata akışı; 320px/masaüstü ve klavye; tüm izin/stock assert'leri.
- **Tamamlanma:** Güncel ortak commit'te SQLite+PostgreSQL yeşil; PR review kayıtları, gerçek ekranlar ve kabul kontrol listesi; kabul edilmeyen paketler ayrı.
- **Teslimatlar:** Dar entegrasyon/UX değişiklikleri, CI kanıtları, güncel kurulum/şema/katkı kaydı.
- **Gözden geçirme:** Açık P0/P1 ve kapsam dışı istekleri yeniden sırala; Sprint 6 demo sürümünü seç.

## Sprint 6 — Kapsamlı test, rapor ve final demo

- **Hedef:** Akademik gereksinimleri gerçek uygulama/kanıtlarla tamamlamak.
- **Önkoşul:** Kabul edilebilir ortak sürüm; dersin doğrulanmış rapor şablonu ve teslim takvimi.
- **Görevler:** B12 ara raporu güncelle/final rapor, literatür karşılaştırması/APA7, ER ve ekranlar, gerçek kişi katkıları; temiz kurulum ve final prova.
- **Sorumlu:** Ortak; Üye 1 mimari/LLM, Üye 2 veri/katalog/ER, Üye 3 hesap/dolaşım/ceza. Tek kişi raporu sahiplenmez.
- **Bağımlılık:** B01/12 planı Sprint 0'dan başlar; final yazımı sona bırakılmaz. Ara raporun gerçek tarihi gelirse ilgili çıktı daha erken teslim edilir.
- **Yük / pencere:** 18–26 kişi-saat, 4–6 çalışma günü önerisi.
- **Risk:** Gerçekte olmayan canlı test/ekran/kabul iddiası; eksik katkı beyanı; teslim tarihinin geç öğrenilmesi.
- **Kabul testleri:** Yeni yerel ortam kurulum/migration/seed; tüm testlerde 0 beklenmeyen hata; demo kuru provası; rapor iddiaları commit/test/ekran kaynaklarına bağlanır; APA7 ve gerçek/planlanan ayrımı kontrol edilir.
- **Tamamlanma:** Ekip teslim checklist'i ve üç kişinin katkı incelemesi; rapor/ekler/demonun aynı kabul sürümünü anlatması. Açık sınırlılıklar dürüstçe belirtilir.
- **Teslimatlar:** Ara/final raporlar, kaynakça, ER çıktısı, yapay verili gerçek ekranlar, katkı kayıtları, demo senaryo notları.
- **Gözden geçirme:** Ders geribildirimi ve kalan işleri kayıt altına al; gelecekte canlı işletim istenirse ayrı kapsam/tehdit/dağıtım planı aç.

## Paralel çalışma ve kalite kapısı

Sprint sırası kabul kapılarını gösterir, üç kişinin sırayla boş beklemesini gerektirmez.
Üye 2 Sprint 1'i yürütürken Üye 3 B06/B07 test tablolarını, Üye 1 B10 kalite
rubriğini ve B12 rapor iskeletini hazırlayabilir. Ortak model/izin/sözleşme
kararları B01 sonrası uygulanır. B12 literatür/katkı kanıtı her sprint boyunca sürer.

Toplam tahmin **82–122 kişi-saat**; gerçek süre kapasite, ders şablonu, API erişimi
ve gözden geçirme sonuçlarına bağlıdır. Hiçbir takvim aralığı kesin ders tarihi
olarak kullanılmamalı. Her sprint kapanışında bir başka üyenin review'u, test
kanıtı, açık risk listesi ve sonraki backlog güncellemesi zorunlu kabul adımıdır.
