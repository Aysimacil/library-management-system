# Sprint 0 — doğrulanmış planlama paketi

İnceleme tarihi: **7 Kasım 2026**. Ders: CEN317 Engineering Design,
Çukurova Üniversitesi Bilgisayar Mühendisliği. Proje geliştirme aşamasındadır.
Kodun çokluğu, testlerin geçmesi veya bir dalın adı ekip kabulü değildir.

## Okuma sırası

1. [Gereksinim–kod matrisi](requirements-matrix.md): kapsam, durum ve kabul kriterleri.
2. [Boşluk analizi](gap-analysis.md): kullanıcı etkisi ve doğrulama eksikleri.
3. [Mimari/GitHub incelemesi](architecture-review.md): analiz edilen sürüm, dal ilişkileri, CI ve entegrasyon.
4. [Geliştirme yol haritası](development-roadmap.md): Sprint 0–6, bağımlılık ve teslimatlar.
5. [GitHub backlog](github-backlog.md): 12 uygulanabilir görev ve pano taslağı.
6. [Sprint 1 katalog planı](sprint-1-catalog.md): Üye 2 için beş kabul senaryosu ve uygulama sırası.

## Kapsam ve kanıt disiplini

Asıl kaynak [proje özeti](../project-brief.md) §§1–3,12–16'dır; bu belge de
19 Ekim tarihli iş kuralı setini **öneri / ekip incelemesine açık** olarak tanımlar.
Dersin özgün rapor şablonları ve gerçek teslim tarihleri depoda bulunamadı.
Bunların doğruluğu ders yürütücüsü ve ekip tarafından teyit edilmelidir.

Analiz edilen uygulama: `feature/library-production-readiness` →
`a29b535ad12e63af7a4f94dde0259484ce022ada`.
Planlama dalı: `docs/sprint-0-planning`, bu commit'ten oluşturuldu.
Yalnız `docs/planning/` değiştirildi. Uygulama ve migration değişikliği yoktur.
Önceki çalışma alanındaki tamamlanmamış `feature/library-staging` dosyaları
ayrı bırakıldı; analiz tabanına dahil edilmedi. Docker/staging başlatılmadı,
canlı veri veya sunucu kullanılmadı. Hiçbir PR birleştirilmedi.

## Durum sözlüğü

- **NOT IMPLEMENTED:** İlgili kod/teslimat bulunamadı.
- **PARTIAL:** Gereksinimin yalnız bir bölümü uygulanmış.
- **IMPLEMENTED / UNVERIFIED:** Kod var; belirtilen kabul doğrulaması eksik.
- **TESTED:** İlgili otomatik test kanıtı var; kapsam sınırı ayrıca belirtilir.
- **ACCEPTED:** Ekip incelemesi, kabul senaryosu ve kayıtlı onay var.

Bu pakette hiçbir gereksinim ACCEPTED olarak işaretlenmedi. Bir testte birçok
assertion bulunması tüm olası sınırların doğrulandığı anlamına gelmez.

## Yeniden doğrulanan kanıt

- `git fetch origin`, dal uçları ve PR #3/#4 API kayıtları incelendi.
- [Taban commit CI](https://github.com/Aysimacil/library-management-system/actions/runs/42373569757): PostgreSQL **93/93**; SQLite **89 geçti / 4 atlandı**; Nginx yapılandırma işi başarılı. Atlananlar üç satır kilidi yarışı ve PostgreSQL yedek dönüş testidir.
- Bu sprintte ayrı worktree'de, mevcut Python 3.12 sanal ortamıyla, gerçek Gemini anahtarı olmadan `manage.py test --verbosity 1`: **93 test keşfedildi, 89 geçti, 4 atlandı, 0 hata**. SQLite test DB'si Django tarafından oluşturulup kaldırıldı. PostgreSQL bu sprintte yeniden başlatılmadı; kanıt yukarıdaki CI'dır.
- Geçici SQLite test DB'sinde `Deneme Başlığı` kitabına `Mühendislik` kategorisi bağlandı: `GET /?q=Mühendislik` **0 sonuç**, `GET /?category=<id>` **1 sonuç**. Kategori filtresi var; kategori adına serbest metin araması yok. Bu keşif kalıcı regresyon testi değildir; Sprint 1 görevine alındı.
- Gemini kanıtı mock testlerdir. CI smoke çıktısı `SKIPPED: LLM_API_KEY is absent. No API call made.`; canlı API veya Türkçe kalite başarısı ileri sürülmez.
- Eski `docs/development.md` içindeki 59 ve katalog notlarındaki 30 test, ilgili eski sürümlerin tarihsel kayıtlarıdır; güncel sayıyla karıştırılmamalı.

## Ekip kararı bekleyenler

İş kuralları/takvim, katalog yönetimi için Admin'in yeterliliği, rol–kişi eşlemesi,
rapor şablonları ve teslim tarihleri, kaynakça/lisans, Gemini erişimi ve kalite
ölçütleri, ortak kabul tabanı ve entegrasyon sırası. Başarı ölçütü yeni modül
sayısı değil, kanıtlanmış kapsam ve ekipçe yürütülebilen görevlerdir.
