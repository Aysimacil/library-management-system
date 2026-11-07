# Mimari ve GitHub incelemesi

7 Kasım 2026'da `git fetch origin` ve GitHub API ile yenilendi.
Uygulama tabanı `a29b535ad12e63af7a4f94dde0259484ce022ada`;
planlama dalı `docs/sprint-0-planning`. main'in eski iskelet olması nedeniyle
analiz yalnız main'e dayandırılmadı. [Boşluk analizi](gap-analysis.md) işlev
sınırlarını ve [matris](requirements-matrix.md) kabul kriterlerini tamamlar.

## 1. Dal envanteri ve PR durumu

| Dal | Güncel uç | İçerik / ilişki |
|---|---|---|
| main | e15c918 | Django/books başlangıç iskeleti; accounts/circulation/recommendations ve yeni docs burada yok |
| feature/catalog-models | f5e848f | Model/Admin/katalog/arama/Türkçe düzeltmeleri; main'den 15 commit ileride |
| feature/secure-environment | 592a73d | Ortam/güvenlik profilleri; main'den 1 commit ileride; katalog dalından ayrı kardeş |
| feature/library-integration-mvp | ff829a5 | Katalog + secure merge + hesap/dolaşım/öneri/CI; main'e göre 26 commit |
| feature/library-ui-enhancements | 7cd630f | Entegrasyon üstüne kapak/filtre/dashboard/öneri/UI; +6 commit |
| feature/library-production-readiness | a29b535 | UI üstüne transactional medya/yedek/health/deploy; +13 commit |
| feature/project-skeleton | 1d3b46c | Tarihsel iskelet dalı; bu sprintte değiştirilmedi |
| feature/library-staging (yalnız yerel) | a29b535 + commit edilmemiş dosyalar | Yarım kalan çalışma; analiz tabanı ve bu PR dışında korunuyor |

`rev-list --left-right --count catalog...integration` = **0/11**,
`secure...integration` = **0/25**. İki çalışma integration'ın atasıdır.
`ebefa09` secure ayarlarını entegrasyona merge eder; zincirin diğer ilerlemeleri
commit geçmişinde durur. UI integration'ı, production UI'ı içerir. main..production
**45 commit** içeriyor. İki PR bağımsız değişiklik paketleri gibi görünse de
#4, #3'teki commit'leri zaten içerir.

- [PR #3](https://github.com/Aysimacil/library-management-system/pull/3): açık,
  draft değil, head catalog f5e848f → main; 15 commit / 18 dosya. İnceleme,
  satır yorumu ve issue yorumu yok.
- [PR #4](https://github.com/Aysimacil/library-management-system/pull/4): açık,
  draft değil, head integration ff829a5 → main; 26 commit / 69 dosya. İnceleme ve
  yorum yok. Açıklaması kapsamı doğrulamaya yeterli ayrıntı içermiyor.
- API kontrolünde ikisi `mergeable=true / clean`; bu **kabul veya merge izni değildir**.
- `issues?state=all&per_page=100` dört kayıt döndürüyor; #1–#4'ün tamamı PR.
  Ayrı açık/kapalı Issue bulunmadı; görev kopyası oluşturulmadı.
- Project Board varlığı/yetkisi doğrulanamadı: connector projects endpoint'ini
  desteklemiyor. “Pano yok” sonucu çıkarılmadı. Label listeleme de desteklenmiyor.
- Issue create denemesi 403 `Resource not accessible by integration` döndürdü;
  Issue açılmış sayılmadı. [Backlog](github-backlog.md) içeriği hazırlandı.

## 2. Django sınırları ve bağımlılıklar

| Alan | Gerçek sorumluluk | Bağımlılık ve dikkat |
|---|---|---|
| library_system | settings/URL/health/güvenli log; ortak proje | books şemasını health'te kontrol eder; Üye 1 |
| books | bibliyografya, M2M, fiziksel kopya, katalog, kapak | Üye 2; kapak altyapısı Üye 1'le ortak; history trigger circulation tablosuna bağlı |
| accounts | Django User/Group auth, kayıt/profil/dashboard, rol kurma/demo | circulation geçmiş/borç, books/stok; Üye 3, ortak UI Üye 1 |
| circulation | Loan/Fine/CheckoutRequest, formlar ve atomik servisler | User ve BookCopy; Üye 3; status geçişlerinin tek desteklenen sahibi |
| recommendations | aday sorgusu, DB kota, HTTP adapter, yanıt doğrulama | books salt okunur; auth kullanıcı kimliği yalnız yerel kota; Üye 1 |
| templates/static | HTML sunumu, navigasyon, mesaj/ortak görsel parçaları | Sunucu izinleri view/admin'de kalır; frontend gizleme güvenlik sınırı değildir |

Brief'teki `config/catalog` hedef adları gerçekte `library_system/books`.
Bu bir yeniden adlandırma görevi değildir; var olan mimari korunmalı.

## 3. ER ve veri sözleşmesi

Book–Author ve Book–Category M2M; Book 1→N BookCopy. Loan üyeyi ve **BookCopy.pk**
üzerinden fiziksel kopyayı bağlar. `inventory_code` kullanıcı etiketi/arama anahtarıdır;
FK olarak kullanılmaz. Fine her Loan için en fazla bir kesinleşmiş tutar ve isteğe
bağlı ödeme görevlisi/zamanı tutar. CheckoutRequest kitabı hedefler; fiziksel stok
ayırmaz, teslimde tek Loan'a eşleşir. User/Group/Permission Django standartlarıdır.

`docs/er-diagram.md` bu ilişkileri gösterir; Fine.loan alanı ayrıca OneToOne/unique
olarak raporda açıklanmalı. CoverOperation ve MediaLock teknik tutarlılık tabloları;
UsageWindow kota sayacıdır. Bunlar kullanıcı alanının yeni ana modülleri değildir.

| Alan / işlem | Sahip | Atomik sözleşme |
|---|---|---|
| Book/Author/Category; BookCopy book/demirbaş/raf | Üye 2 | Admin/form doğrulaması; geçmişli kitap/kimlik kısıtları; metadata save status yazmaz |
| AVAILABLE→ON_LOAN | Üye 3 borrow_book | Üye kilidi → kopya kilidi; borç/limit; Loan create + status save + ilgili PENDING eşleşmesi tek transaction |
| ON_LOAN→AVAILABLE | Üye 3 return_book | Üye → kopya → Loan; returned_at + gerekiyorsa tek Fine + status aynı transaction |
| Uzatma | Üye 3 renew_loan | Önceki/yeni vade + sayaç + zaman aynı transaction; status değişmez |
| Demo ödeme | Üye 3 pay_fine | Fine kilidi; paid_at ve paid_by birlikte; ilk kayıt tekrarda korunur |
| Stok görünümü | Üye 2 | Kopyalardan hesaplanır; servis harici bağımsız sayaç veya manuel status yok |

Kopya silme Loan FK PROTECT; geçmişli başka kitaba atama SQLite/PostgreSQL trigger.
Admin kopya POST queryset'i select_for_update ile kilitlenir; save_model yalnız
book/inventory_code/shelf_location içindeki değişen alanları yazar. Böylece
eski formun AVAILABLE durumuyla yeni teslimi ezmesi önlenir. Demirbaş değişimi
DB trigger'ında değil Admin'de korunur; desteklenen ORM politikası karar bekler.

## 4. Transaction, servis ve yetki değerlendirmesi

`circulation/services.py` önemli değişiklikleri transaction.atomic içinde toplar;
Loan koşullu unique aynı kopyada iki aktif ödüncü DB'de reddeder. Kayıtlı tarife
ve vade eski işlemleri korur. İade ve ödeme idempotandır. Kilit sırası kullanıcı →
kopya → loan; farklı üye/same copy ve same user/different copy yarışları PostgreSQL
CI'da testli. SQLite sonucu eşzamanlılık kanıtı değildir.

View'lar kimlik/permission, HTTP metodu, form ve geri bildirimi yönetir; servisler
kuralları yürütür. İstisna: request_book hesap/limit/pending mantığını view'da taşır;
3 limiti tekrarlanır. Küçük bir servis/politika düzenlemesi B08 kapsamında
önerilir; tüm projeyi yeniden katmanlamak gerekmez. borrow/return/renew aktör
parametresi almaz: yeni bir API/komut eklenirse yetki giriş katmanında açıkça
kontrol edilmeli. pay_fine ayrıca aktör iznini içeride kontrol eder.

ORM/SQL ile doğrudan Loan/status yazmak servis bütünlüğünü atlar. Tarife, ISBN
formatı veya zorunlu yazar gibi bazı kurallar form/model validasyonundadır;
her biri DB kısıtı değildir. Admin LedgerAdmin geçmişi salt okunur yapar.
Bu sınırları ekip anlamadan yeni yönetim/ithal ekranı açılmamalı.

## 5. Gemini bağlantısı

Yerel kategori/başlık/yazar/açıklama aday puanlaması → en çok 10 aday → yerel
kota rezervasyonu → tek HTTPS çağrı → aday kimliği ve şekil doğrulaması →
en çok 3 kitap ve güncel DB bilgisi. Kimlik/hesap/ham soru sağlayıcı payload'ında
yok. Servis yokken normal katalog/dolaşım bağımsız çalışır. Mock testler entegrasyon
şeklini kanıtlar; kalite, model erişimi veya canlı şartları kanıtlamaz. B10 rubriği
ve açık opt-in gerçek deneme bu boşluğu kapatır; anahtarsız SKIPPED korunur.

## 6. Migration tutarlılığı

Gerçek bağımlılıklar:

1. books.0001 ve Django auth → circulation.0001 (Loan/Fine).
2. books.0002, books.0001 + circulation.0001 sonrası history trigger kurar.
3. circulation.0002 (CheckoutRequest) books.0002 ve circulation.0001'e bağlı.
4. books.0003 (cover) books.0002 → books.0004 (MediaLock/CoverOperation) → books.0005 (içerik/kind kısıtı).
5. recommendations.0001 bağımsız kota tablosu; standart admin/session/auth migration'ları ayrıca var.

Uygulama importları çift yönlü görünse de migration grafiğinde dependency cycle
bulunmadı. Son CI iki motorda temiz migrate ve makemigrations --check --dry-run
başarılı. Bu, gerçek bir kurumun dolu DB yükseltmesini doğrulamaz. Eski migration
silme/squash/yeniden numaralandırma yapılmamalı; gerekirse yalnız ileri migration.
Brief/ER'deki hedef isimleri migration yeniden adlandırma gerekçesi değildir.

## 7. Gereken temel yapı ve ertelenebilir karmaşıklık

| Bileşen | İlk akademik sürüm | Bakım yükü / karar |
|---|---|---|
| Django/Templates/auth/ORM; atomik dolaşım | Gerekli | İş kuralları/izinler ve deterministik testler öncelikli |
| PostgreSQL yarış doğrulaması | Gerekli kanıt | SQLite kolay kurulum alternatifi, eşzamanlılık kanıtı değil |
| Pillow güvenli kapak | Mevcut ek özellik; korunur | Format/limit ve lifecycle testlerini koru; ek depolama sistemi şart değil |
| Medya kuyruğu/lock | Üretim hazırlığında eklenmiş; artık Book.save yolunda | DB binary büyümesi, global kilit, callback/worker ve pending-image karmaşıklığı; testli kodu gerekçesiz sökme |
| Backup/restore, volume marker, probes | Gelecek işletim için korunur/dondurulur | Marker/worker/PG istemci sürümü ve gizli arşiv yönetimi öğrenilmeli; Sprint 1 hedefi değil |
| Gunicorn/Nginx/systemd/HSTS/SMTP | Yerel ders demosu için zorunlu değil | Gerçek TLS/SMTP/live deployment teyidi yok; dosyalar var diye dağıtıldı denmez |
| Docker staging | Bitmemiş yerel çalışma, kapsam dışı | Bu sprintte başlatma/commit/entegrasyon yok |

Kodun anlaşılabilirliği: servis fonksiyonları kısa ve alanlar belirgin; bazı
şablonlar tek satırlı, Book.save dosya yaşam döngüsüyle yoğun, politikalar
servis/view/model arasında dağılmış. Teknik borcu belgelerle görünür kıl;
yeni framework, mikroservis veya arayüz yeniden yazımı önermek gerekmiyor.

## 8. Güvenli entegrasyon önerisi — bu sprintte uygulanmaz

1. Önce B01 kapsam/kabul ve ortak taban kararı; mevcut branch SHA'larını not al.
   PR #3/#4'e bu sprintte yorum/retarget/merge yapılmaz.
2. Gelecek incelemede PR #3'ü Üye 2 dışındaki biri katalog senaryolarıyla inceler;
   ardından ekip izin verirse normal merge commit ile main'e alır. Squash/rebase
   varsayılan yapılmaz; mevcut commit kimlikleri korunur.
3. #4 katalog commit'lerini zaten içeriyor. #3 merge edilince ortak atalar Git
   tarafından korunur; #4'ün farkı daralır. Merge öncesi güncel main + #4 ayrı
   geçici entegrasyon dalında denenir. Çatışma olursa eski dalı rewrite etmek
   yerine ayrı çözüm dalı/PR önerilir; karar ekipte.
4. #4'ün kalanını hesap/izin, dolaşım/ceza, öneri ve ortak UI/test dosya gruplarıyla
   incele; her gruba sahip ve kanıt checklist'i ver. Geniş PR'ı körlemesine onaylama.
   Gerekirse review-only dar diff bağlantıları üret; aynı commit'leri cherry-pick
   ederek ikinci kopya tarihçe oluşturma.
5. UI ve production zincirini birbirine eklenen **stacked** farklarla incele:
   integration→UI ve UI→production. İnceleme tabanı seçmek merge izni değildir.
   Akademik MVP kabulünde üretim altyapısı ayrı P2 paket olarak kalabilir; hangi
   düğümün ortak taban olacağı ekip kararıdır, testli güvenlik kodu otomatik silinmez.
6. Sonraki işler kabul edilen ortak tabandan kısa feature branch; tek backlog
   görevi/PR; başka üye review; SQLite+PostgreSQL kanıtı; migration/ER/rapor etkisi.
   Korunan eski dallara force push yok. Üye rollerini commit author'dan çıkarmayın.

## 9. CI ve bu sprintin doğrulaması

[42373569757](https://github.com/Aysimacil/library-management-system/actions/runs/42373569757)
`a29b535` için SQLite 89 geçti/4 skip, PostgreSQL 93 geçti ve Nginx yapılandırma
başarısını kanıtlar. Gunicorn config, temiz migrate, çift seed, collectstatic ve
anahtarsız smoke de bu işlerde başarılı. Gerçek Gemini çağrısı ve SMTP teslimi yok.

Mevcut workflow push'ta yalnız integration/UI/production/main; PR'da yalnız main
hedefini dinler. Dolayısıyla docs/sprint-0-planning → production hedefli Draft PR
**yeni CI çalışması tetiklemeyebilir**. Bu sprintte yalnız docs/planning sınırı
nedeniyle workflow değiştirilmedi. Yerel tüm testler aynı tabanda tekrar geçti;
doküman link/kod/test referansları ayrıca kontrol edildi. Yeni kod PR'ları için
CI hedef kapsamı B11'de düzeltilmeli; bu belge dalına yeşil CI uydurulmamalı.
