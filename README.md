# Library Management System

Django ve PostgreSQL kullanılarak geliştirilecek web tabanlı bir Kütüphane Yönetim Sistemi. Proje; kitap kataloğu ve arama, kitap kopyalarının stok takibi, ödünç alma ve iade işlemleri, gecikme cezası hesaplama ve Büyük Dil Modeli (LLM) destekli kitap özeti/kişiselleştirilmiş öneri özelliklerini tek bir uygulamada birleştirmeyi amaçlar.

> **Ders:** CEN317 – Engineering Design  
> **Bölüm:** Bilgisayar Mühendisliği, Çukurova Üniversitesi  
> **Proje durumu:** Geliştirme aşamasında. Bu README’deki özellikler hedeflenen kapsamı anlatır; tamamlandığı doğrulanmamış işlevler tamamlanmış kabul edilmemelidir.

---

## İçindekiler

- [1. Amaç ve kapsam](#1-amaç-ve-kapsam)
- [2. Kullanıcı rolleri ve işlevsel gereksinimler](#2-kullanıcı-rolleri-ve-işlevsel-gereksinimler)
- [3. İş kuralları ve uygulama kararları](#is-kurallari)
- [4. Teknoloji yığını](#4-teknoloji-yığını)
- [5. Mimari ve tasarım ilkeleri](#5-mimari-ve-tasarım-ilkeleri)
- [6. Veritabanı tasarımı](#6-veritabanı-tasarımı)
- [7. Önerilen proje dizin yapısı](#7-önerilen-proje-dizin-yapısı)
- [8. Kurulum ve yerel geliştirme](#8-kurulum-ve-yerel-geliştirme)
- [9. Ortam değişkenleri ve gizli bilgiler](#9-ortam-değişkenleri-ve-gizli-bilgiler)
- [10. Test stratejisi ve kalite kontrolleri](#10-test-stratejisi-ve-kalite-kontrolleri)
- [11. Git ve ekip çalışma akışı](#11-git-ve-ekip-çalışma-akışı)
- [12. Görev dağılımı ve teslimatlar](#12-görev-dağılımı-ve-teslimatlar)
- [13. Ara rapor için çalışma planı](#13-ara-rapor-için-çalışma-planı)
- [14. Final raporu için çalışma planı](#14-final-raporu-için-çalışma-planı)
- [15. Raporlama ve katkıların belgelenmesi](#15-raporlama-ve-katkıların-belgelenmesi)
- [16. Tamamlanma ölçütleri](#16-tamamlanma-ölçütleri)
- [17. Riskler ve önlemler](#17-riskler-ve-önlemler)
- [18. Geliştirme yol haritası](#18-geliştirme-yol-haritası)
- [19. Lisans ve akademik kullanım](#19-lisans-ve-akademik-kullanım)

---

## 1. Amaç ve kapsam

Projenin amacı, temel kütüphane süreçlerini dijital ortamda yönetebilen, kuralları açıkça tanımlanmış ve test edilebilir bir web uygulaması geliştirmektir. LLM entegrasyonu, katalog ve ödünç alma işlevlerinin yerine geçmez; mevcut kitap bilgilerini ve kullanıcı tercihlerini kullanarak ek bir keşif/öneri deneyimi sunar.

### Kapsam içindeki ana modüller

1. **Hesap ve yetkilendirme:** Giriş/çıkış, kullanıcı profili ve rol bazlı erişim.
2. **Katalog:** Kitap, yazar ve kategori kayıtları; arama ve filtreleme.
3. **Kopya ve stok yönetimi:** Her kitabın fiziksel kopyalarının ve kullanılabilirlik durumunun takibi.
4. **Ödünç alma ve iade:** Ödünç kaydı, son teslim tarihi, iade tarihi ve aktif ödünçlerin takibi.
5. **Gecikme cezası:** Belirlenen kurallara göre cezanın hesaplanması ve ceza geçmişinin gösterilmesi.
6. **LLM destekli öneriler:** Katalog açıklamasına dayalı kısa özet/analiz ve mevcut kullanıcı isteği/tercihlerine göre öneriler. Okuma geçmişine dayalı gelişmiş kişiselleştirme sonraki aşamadır.

### Kapsam dışı veya ayrıca kararlaştırılacak konular

Çevrim içi ödeme, kısmi ödeme, rezervasyon kuyruğu, kayıp/hasar ve tazminat süreçleri, okuma geçmişine dayalı gelişmiş kişiselleştirme, barkod/RFID donanımı, e-kitap dağıtımı, çok şubeli kütüphane yönetimi, gerçek zamanlı bildirimler ve üretim ortamında ölçeklendirme ilk sürümün zorunlu kapsamı değildir. Ekip ve ders gereksinimleri doğrultusunda eklenmeleri ayrıca kararlaştırılmalıdır.

---

## 2. Kullanıcı rolleri ve işlevsel gereksinimler

Roller ve izinler uygulama geliştirilirken kesinleştirilecektir. Önerilen başlangıç modeli şöyledir:

| Rol | Temel yetkiler |
|---|---|
| **Üye** | Kataloğu görüntüleme ve arama, kendi ödünç kayıtlarını ve cezalarını görüntüleme, uygun kitap için ödünç talebinde bulunma, koşullar sağlandığında uzatma isteme, LLM önerilerinden yararlanma |
| **Kütüphaneci** | Katalog kayıtlarını ve kopyaları yönetme, fiziksel teslim/iade işlemlerini onaylama, uzatma kurallarını uygulama, kesinleşmiş cezalar için demo ödeme kaydı oluşturma, gerekli kayıtları görüntüleme |
| **Yönetici** | Kullanıcı ve rol yönetimi ile uygulamanın yönetim işlevleri; gerektiğinde Django Admin üzerinden veri yönetimi |

### İşlevsel gereksinimler

- Kitaplar başlık, yazar ve kategori bilgilerine göre aranabilmeli ve filtrelenebilmelidir.
- Bir kitap birden fazla yazara ve kategoriye bağlanabilmelidir.
- Kitabın bibliyografik kaydı ile fiziksel kopyaları birbirinden ayrılmalıdır.
- Ödünç işlemi yalnızca uygun durumda bulunan bir kopya için oluşturulmalıdır.
- Ödünç kaydında alış tarihi, son teslim tarihi ve varsa iade tarihi tutulmalıdır.
- İade işlemi kopyanın durumunu ve stok/uygunluk bilgisini güncellemelidir.
- Gecikme cezası belirlenmiş kurallara göre hesaplanmalıdır.
- Yetkili kullanıcılar katalog, kopya ve dolaşım kayıtlarını yönetebilmelidir.
- Kullanıcılar kendi ödünç geçmişlerini ve ceza bilgilerini görebilmelidir.
- LLM özelliği, mevcut katalogda bulunmayan bir kitabı gerçek katalog kaydıymış gibi sunmamalıdır. Önerilerin katalogdaki kitaplarla eşleştirilmesi hedeflenir.
- LLM servisi erişilemez olduğunda temel katalog, ödünç ve iade işlevleri çalışmaya devam etmelidir.

---

<a name="is-kurallari"></a>

## 3. İş kuralları ve uygulama kararları

**19 Ekim 2026 — İlk sürüm için önerilen karar seti.** Bu bölüm geliştirmede uygulanacak kuralları somutlaştırır; ekip incelemesine açıktır. Kuralların burada yazılması, ilgili özelliklerin uygulanıp test edildiği anlamına gelmez. Dersin yazılı gereksinimleriyle çelişen bir madde varsa geliştirmeden önce düzeltilmelidir.

| Konu | Karar / uygulanacak yaklaşım |
|---|---|
| Ödünç süresi | Kütüphanecinin fiziksel teslimi onayladığı tarihten itibaren **14 takvim günü**. Son iade günü kapalıysa ilk açık güne ötelenir. |
| Günlük gecikme ücreti | Her fiziksel kopyanın her ödünç işlemi için **günlük 5,00 TL**. Son iade gününde ceza yoktur; ertesi gün başlar. |
| Azami ceza | Tek ödünç kaydı için **en fazla 100,00 TL gecikme cezası**. Bu sınır üyenin toplam hesabına uygulanmaz. |
| Hafta sonu/resmî tatil | Ödünç süresi takvim günüyle sayılır. Son gün kapalıysa vade ötelenir; düzeltilmiş vadeden sonraki gecikme hesabına hafta sonları ve tatiller de dahildir. |
| Ödenmemiş ceza kısıtı | Kesinleşmiş ödenmemiş borcu **0 TL'den fazla olan** veya **gecikmiş aktif ödüncü bulunan** üye yeni kitap alamaz ve uzatma yapamaz. İade, katalog ve kendi hesabına erişim engellenmez. |
| Aynı anda alınabilecek kitap sayısı | Üye başına **en fazla 3 aktif fiziksel kopya**. İade edilen kopya bu sayıdan düşer. |
| Yenileme/uzatma | İlk sürüme dahil: her ödünç için **en fazla 1 kez, mevcut vadeden itibaren 7 gün**. Ödünç gecikmemiş olmalı; üyede ödenmemiş borç veya başka gecikmiş ödünç bulunmamalıdır. |
| Kopya durumu | İlk sürümde **AVAILABLE (ödünç verilebilir)** ve **ON_LOAN (ödünçte)**. Kayıp/hasar bildirimi, değerlendirmesi ve tazminat süreçleri sonraki sürüme bırakılır. |
| LLM sağlayıcısı/modeli | Başlangıç tercihi **Google Gemini API / `gemini-3.5-flash-lite`**. `LLM_PROVIDER`, `LLM_MODEL` ve `LLM_API_KEY` sunucu ortam değişkenlerinden okunur; model değiştirilebilir tutulur. |
| Kullanıcı verisi | LLM'ye yalnızca **kişisel bilgi içermeyen kitap isteği ve gerekli katalog bilgileri** gönderilir. Hesap bilgileri, parola, ham ödünç geçmişi ve borç/ödeme bilgileri gönderilmez. |

Sayısal değerler ders projesi için önerilmiştir; gerçek bir kurumun resmî tarifesi değildir. Süre, ücret, üst sınır, aktif ödünç limiti ve uzatma kuralları sunucuda tek yerde tanımlanmalıdır. Aktif ödüncün vadesi ve ücret koşulları kayıtta korunmalı; yapılandırma değişikliği eski işlemleri sessizce değiştirmemelidir.

### 3.1 Ödünç, takvim ve uzatma

- Ödünç kaydı bir **üyeyi bir fiziksel kopyaya** bağlar. Üç kitap tesliminde üç ayrı ödünç kaydı oluşturulur.
- Süre, talep düğmesine basılınca değil, kütüphanecinin teslimi onaylamasıyla başlar. İlk sürümde ayrıca bir rezervasyon/bekleme kuyruğu yoktur.
- Tarihler **Europe/Istanbul** saat dilimindeki sunucu tarihine göre değerlendirilir; kullanıcının cihaz saati kullanılmaz. İşlem zamanları UTC saklanabilir; son iade tarihi ayrı bir tarih alanı olmalıdır.
- Ödünç başlangıcına 14 gün eklenir. Örneğin 19 Ekim 2026'da teslim edilen kitabın ham son iade tarihi 2 Kasım 2026'dır.
- İlk takvim varsayımı: teslim/iade hizmeti pazartesi-cuma açık; cumartesi, pazar ve yapılandırılmış tatil günleri kapalıdır. Kurumun farklı hizmet takvimi varsa bu ayar değiştirilir. Fiziksel teslim için geçerli hizmet saatleri arayüzde gösterilmelidir.
- Kapalı tarihler yıl bilgisiyle birlikte yapılandırmada tutulur; ilk sürümde dış tatil API'sine ihtiyaç yoktur. Vade, art arda kapalı günler varsa ilk açık güne kadar ötelenir.
- Son iade tarihinin gün sonuna kadar gecikme cezası oluşmaz. Ertesi gün 00.00 itibarıyla bir günlük gecikme oluşur.
- Uzatma, talep tarihinden değil **mevcut son iade tarihinden** hesaplanır. 7 gün eklenir ve yeni tarih kapalıysa yine ilk açık güne ötelenir. Erken uzatma kullanıcının kalan günlerini azaltmaz.
- Son iade günü ilk uzatma yapılabilir. İkinci uzatma, gecikmiş ödünç için uzatma ve başka üyenin kaydına yetkisiz uzatma reddedilir.
- Uzatma yeni bir ödünç oluşturmaz; aynı kayıtta uzatma sayısı, önceki/yeni vade ve işlem zamanı tutulur.
- Kopya ve üye limiti kontrolleri ödünç kaydıyla aynı atomik işlemde yapılır. Eşzamanlı istekler aynı kopyayı iki üyeye verememeli veya bir üyenin 3 kopya sınırını aşamamalıdır.

### 3.2 Ceza hesaplaması

```text
hesap_tarihi = iade edilmişse iade anının yerel tarihi, değilse bugünün yerel tarihi
gecikme_gunu = max(0, hesap_tarihi - son_iade_tarihi)
ceza = min(gecikme_gunu × Decimal("5.00"), Decimal("100.00"))
```

Tarih farkı takvim günü olarak alınır; geçen saatlerin 24'e bölünmesiyle hesaplanmaz. Son iade tarihi, kapalı gün düzenlemesi ve varsa uzatma sonrasındaki kayıtlı tarihtir. Para hesabında `float` yerine Python `Decimal` ve Django `DecimalField` kullanılır; sayısal sabitler metinden oluşturulur.

| Gecikme | Tek ödüncün cezası |
|---|---|
| 0 gün | 0,00 TL |
| 1 gün | 5,00 TL |
| 3 gün | 15,00 TL |
| 19 gün | 95,00 TL |
| 20 gün | 100,00 TL |
| 25 gün | 100,00 TL |

- Aktif ödünçte ceza güncel tahmin olarak gösterilir; her gün yeni `Fine` kaydı oluşturulmaz.
- İadede nihai tutar kesinleştirilir ve gerekiyorsa ilgili ödünç için tek `Fine` kaydı oluşturulur. İadeden sonra ceza büyümez.
- Üç ayrı ödüncün her biri 100 TL cezaya ulaşmışsa toplam borç 300 TL olabilir.
- 100 TL sınırına ulaşmak kitabı iade edilmiş saydırmaz. Gecikmiş aktif ödünç bulunduğu sürece yeni ödünç ve uzatma engeli devam eder.
- Üye borçlu olsa da kitabını iade edebilir. İade kabulü ödeme şartına bağlanmaz.
- İlk sürümde gerçek ödeme altyapısı ve kısmi ödeme yoktur. Kütüphaneci, kesinleşmiş cezanın tamamı için demo ödeme kaydı oluşturup borcu ödendi olarak işaretler; üye kendi borcunu silemez veya ödendi yapamaz.
- Ödeme kaydı görevli ve işlem zamanını içermelidir. İade/ödeme isteğinin tekrarlanması ikinci bir ceza veya ödeme oluşturmamalıdır.

### 3.3 LLM kapsamı, sınırları ve kullanıcı verisi

- İlk sürüm, kişisel bilgi içermeyen mevcut isteğe/tercihlere göre kitap önerir; kısa özet/analiz yalnızca sağlanan katalog açıklamasına dayanır. Açıklama yetersizse kitap hakkında doğrulanmamış içerik üretmek yerine bu durum belirtilir.
- Sunucu katalogdan ön aramayla en fazla 10 aday seçer; modele bu kitapların kimliği, başlığı, yazarı, kategorileri ve kısa açıklaması verilir. Model en fazla 3 katalog kitabı önerir.
- Modelin döndürdüğü kitap kimlikleri sunucuda doğrulanır. Aday listesi dışında kalan öneriler gösterilmez; başlık ve güncel müsaitlik bilgisi veritabanından alınır.
- Ceza hesabı, ödünç uygunluğu ve veri değişikliği LLM'ye bırakılmaz. Modele serbest SQL veya veri değiştiren araç yetkisi verilmez.
- Okuma geçmişine dayalı gelişmiş kişiselleştirme sonraki aşamadır; ham ödünç geçmişini dış API'ye göndermek ilk sürüm kapsamında değildir.
- Ad-soyad, e-posta, telefon, öğrenci numarası, hesap kimliği, parola, oturum bilgisi, API anahtarı ve ceza/ödeme kayıtları prompt'a eklenmez. Kullanıcıya arama alanına kişisel bilgi yazmaması söylenir. Açık e-posta/telefon kalıpları içeren istekler sağlayıcıya gönderilmeden reddedilir; bu filtre tam anonimleştirme garantisi değildir.
- Demo yalnızca uydurma kullanıcılarla ve kişisel bilgi içermeyen isteklerle yürütülür. LLM işlevi 18 yaş ve üzerindeki üniversite öğrencilerine yönelik ders demosu kapsamında değerlendirilmiştir.
- Başlangıç uygulama sınırları: üye başına dakikada 5, günde 20; uygulama genelinde günde 100 model çağrısı. Bunlar sağlayıcının kotası değil uygulamanın kendi limitleridir. İstek en fazla 500 karakterdir; bir istek için tek model çağrısı ve 10 saniye zaman aşımı uygulanır. Başarısız çağrılar otomatik döngüyle tekrarlanmaz.
- Anahtar yoksa, kota dolarsa veya çağrı başarısız olursa normal arama devam eder; LLM özelliğinin geçici olarak kullanılamadığı açıkça belirtilir. Ham sorular/yanıtlar varsayılan olarak kalıcı günlüğe yazılmaz.

**Sağlayıcı seçiminin dayanağı:** 19 Ekim 2026'da kontrol edilen [resmî model belgesi](https://ai.google.dev/gemini-api/docs/models/gemini-3.5-flash-lite), `gemini-3.5-flash-lite` modelini kararlı sürüm olarak listeler. [Fiyatlandırma belgesinde](https://ai.google.dev/gemini-api/docs/pricing) ücretsiz katman bulunur; hesap erişimi ve kota geliştirme sırasında ve teslim öncesinde doğrulanmalıdır. [Hizmet koşulları](https://ai.google.dev/gemini-api/terms) ücretsiz girdilerin ürün geliştirmede kullanılabileceğini belirtir. Bu nedenle kişisel bilgi gönderilmez; modelin Türkçe öneri kalitesi örnek sorgularla değerlendirilir.

---

## 4. Teknoloji yığını

| Katman / amaç | Seçilen veya önerilen teknoloji |
|---|---|
| Programlama dili | Python |
| Web çatısı | Django |
| Arayüz | Django Templates, HTML, CSS, Bootstrap 5 |
| İlişkisel veritabanı | PostgreSQL |
| LLM | Google Gemini API; başlangıç modeli `gemini-3.5-flash-lite`, sağlayıcı/model sunucu ortam değişkenlerinden yapılandırılacak |
| Test | Django `TestCase`; ihtiyaç duyulursa `pytest` |
| Sürüm kontrolü | Git ve GitHub |
| Dokümantasyon | README, ara/final rapor, ER diyagramı ve gerekli teknik belgeler |

**Sürüm politikası:** Geliştirme ortamında kullanılan Python, Django, PostgreSQL ve bağımlılık sürümleri ekipçe sabitlenmeli; `requirements.txt` içine gerçek kurulumda kullanılan sürümler yazılmalıdır. Bu dosya hazırlanıp doğrulanmadan yukarıdaki liste belirli bir sürümün kurulduğu anlamına gelmez.

---

## 5. Mimari ve tasarım ilkeleri

Uygulama, Django’nun sunucu tarafında HTML üreten yapısını kullanacaktır.

```text
Kullanıcı / Tarayıcı
        |
        v
Django Templates + HTML/CSS/Bootstrap
        |
        v
Django URL'leri ve View'lar
        |
        +--------------------+
        |                    |
        v                    v
Uygulama servisleri      Django ORM
        |                    |
        |                    v
        |                PostgreSQL
        |
        +----> LLM API (yalnızca öneri/özet işlevleri)
```

### Katmanların sorumlulukları

- **Templates:** Verinin kullanıcıya sunulması ve form/ekran bileşenleri.
- **Views:** HTTP isteklerini doğrulama, uygun servis/model çağrılarını yapma ve yanıtı döndürme.
- **Models:** Veri yapıları, ilişkiler ve veritabanı kısıtları.
- **Services:** Ceza hesaplama, ödünç/iade gibi iş kuralları ve LLM çağrısı gibi test edilebilir iş mantığı.
- **Tests:** İş kurallarının ve temel kullanıcı akışlarının beklenen sonucu verdiğini doğrulama.

### Tasarım ilkeleri

1. İş kuralları mümkün olduğunca doğrudan view içine gömülmemeli; uygun servis fonksiyonlarında tutulmalıdır.
2. İstemciden gelen verilere güvenilmemeli; sunucu tarafında doğrulanmalıdır.
3. Yetki kontrolü yalnızca arayüzde değil, view/işlem düzeyinde de uygulanmalıdır.
4. Ödünç alma ve iade sırasında stok/kopya durumu tutarlı kalmalıdır. Eşzamanlı isteklerde aynı kopyanın iki kez ödünç verilmesini önleyecek veritabanı işlemleri ve gerekli kilitleme/kısıtlar değerlendirilmelidir.
5. LLM yanıtları doğrulanmamış içerik olarak ele alınmalı; kullanıcıya açıkça sunulmalı ve sistemin katalog/veritabanı gerçeklerinin yerine geçirilmemelidir.
6. API anahtarları kaynak koduna yazılmamalıdır.
7. Modüller birbirlerinin iç uygulama ayrıntılarına gereksiz yere bağımlı olmamalıdır.

---

## 6. Veritabanı tasarımı

Aşağıdaki varlıklar başlangıç tasarımıdır. Kesin alanlar ve ilişkiler ER diyagramında ekipçe belirlenmelidir.

| Varlık / tablo | Amaç ve temel alanlar (öneri) |
|---|---|
| `User` | Django kullanıcı modeli veya özel kullanıcı modeli; kimlik, e-posta/kullanıcı adı ve rol/izinler |
| `Book` | Başlık, ISBN (varsa), yayın yılı, açıklama ve diğer bibliyografik bilgiler |
| `Author` | Yazar adı ve gerekiyorsa ek bilgiler |
| `Category` | Kategori adı ve açıklama |
| `Book` ↔ `Author` | Bir kitabın birden fazla yazarı, bir yazarın birden fazla kitabı olabilir (**Many-to-Many**) |
| `Book` ↔ `Category` | Bir kitap birden fazla kategoriye, kategori birden fazla kitaba bağlanabilir (**Many-to-Many**) |
| `BookCopy` | Benzersiz fiziksel kopya kimliği/etiketi, bağlı kitap; ilk sürümde `AVAILABLE` / `ON_LOAN` durumu |
| `Loan` | Üye, kopya, ödünç zamanı, kayıtlı son iade tarihi, iade zamanı, durum, uzatma sayısı/zamanı ve ödünçte sabitlenen günlük ücret/ceza üst sınırı |
| `Fine` | Tek bir ödünce bağlı kesinleşmiş gecikme tutarı; oluşturulma zamanı, ödenme durumu/zamanı ve ödemeyi kaydeden görevli |
| LLM kullanım kaydı (isteğe bağlı) | Hata ayıklama/ölçüm için gerekli en az bilgi; hassas prompt ve kişisel veriler varsayılan olarak kaydedilmemeli |

### İlişki ve bütünlük notları

- `Book`–`Author` ve `Book`–`Category` ilişkileri Django ORM üzerinden `ManyToManyField` ile modellenebilir. Django ara tabloları otomatik oluşturabilir; özel ilişki alanları gerekiyorsa `through` modeli kullanılabilir.
- `BookCopy`, kitap başlığını fiziksel kopyalardan ayırır. İlk sürümde kullanılabilir stok, `AVAILABLE` kopyaların sayısından türetilir; bağımsız elle düzenlenen stok sayacı tutulmaz.
- `Loan`, bir kullanıcı ile bir fiziksel kopyayı ilişkilendirmelidir. Aynı kopyanın aynı anda birden fazla aktif ödünç kaydına bağlanması engellenmelidir.
- Bir `Loan` için en fazla bir kesinleşmiş `Fine` bulunur; ilişki `OneToOneField` ile korunabilir. Ceza 0 TL ise `Fine` oluşturmak gerekmez. Aktif ödüncün güncel tahmini cezası ayrı borç kayıtları üretmeden hesaplanır.
- İadede ödünç kaydı, kopya durumu ve varsa kesinleşmiş ceza aynı atomik işlemde güncellenir. Üye limiti için eşzamanlı istekler de kontrol edilir.
- Gerekli alanlarda `NOT NULL`, `UNIQUE`, `CHECK` ve foreign key kısıtları değerlendirilmelidir. Örneğin ISBN varsa benzersizliği, ceza tutarının negatif olmaması ve son teslim tarihinin ödünç tarihinden önce olmaması kontrol edilmelidir.
- Para alanları `DecimalField` ile temsil edilmelidir.
- Silme davranışları (`CASCADE`, `PROTECT` vb.) geçmiş ödünç/ceza kayıtlarını yanlışlıkla yok etmeyecek şekilde seçilmelidir.

> **ER diyagramı:** `docs/er-diagram.png` (diyagram oluşturulduğunda eklenecek). Diyagram, ara rapor ve final raporunda kullanılan gerçek modelle tutarlı olmalıdır.

---

## 7. Önerilen proje dizin yapısı

Aşağıdaki yapı hedeflenen düzeni gösterir; henüz oluşturulmamış dosyalar ve uygulamalar mevcut kabul edilmemelidir.

```text
library-management-system/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── config/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── accounts/                 # Kimlik doğrulama ve rol/izinler
├── catalog/                  # Kitap, yazar, kategori, arama ve kopyalar
├── circulation/              # Ödünç/iade ve ceza kuralları
│   ├── services.py            # İş kuralları için servisler
│   └── tests.py
├── recommendations/          # LLM destekli özet ve öneriler
│   ├── services.py            # Sağlayıcı istemcisi/prompt/yanıt işleme
│   └── tests.py
├── templates/
│   ├── base.html
│   └── ...
├── static/
│   ├── css/
│   └── images/
├── docs/
│   ├── er-diagram.png
│   ├── architecture.md
│   └── ...
└── ...
```

Uygulama isimleri ve dizinler ilk ortak Django iskeleti oluşturulurken kesinleştirilmeli, sonrasında ekip üyeleri aynı isimlendirmeyi kullanmalıdır.

---

## 8. Kurulum ve yerel geliştirme

### Gereksinimler

- Git
- Projede kararlaştırılıp `requirements.txt` içinde sabitlenen Python sürümü
- PostgreSQL sunucusu
- Bir sanal ortam aracı (`venv`)
- LLM özelliğini çalıştırmak için seçilen sağlayıcıya ait API anahtarı (temel uygulama LLM anahtarı olmadan da çalışabilecek şekilde tasarlanmalıdır)

### 8.1 Repoyu klonlama

GitHub deposu oluşturulduktan sonra aşağıdaki komuttaki URL gerçek depo adresiyle değiştirilmelidir:

```bash
git clone <repository-url>
cd library-management-system
```

### 8.2 Sanal ortam oluşturma

**Windows PowerShell:**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**

```bat
python -m venv .venv
.venv\Scripts\activate.bat
```

**Linux/macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 8.3 Bağımlılıkları yükleme

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

`requirements.txt` henüz oluşturulmadıysa önce ekipçe Django ve PostgreSQL bağlantısı için seçilen paketler belirlenip dosyaya eklenmelidir. PostgreSQL sürücüsü ve ortam değişkenlerini okumak için kullanılacak paket gerçek uygulama tercihine göre seçilmelidir.

### 8.4 PostgreSQL veritabanı oluşturma

PostgreSQL üzerinde bir veritabanı ve bu veritabanına erişim yetkisi olan kullanıcı oluşturulmalıdır. Örnek SQL (kullanıcı/parola değerleri yerel ortama göre değiştirilmelidir):

```sql
CREATE DATABASE library_db;
```

Veritabanı kullanıcısının yetkileri, yerel PostgreSQL kurulumuna uygun biçimde ayrıca ayarlanmalıdır. Geliştirme ortamındaki gerçek parola README’ye yazılmamalıdır.

### 8.5 Ortam değişkenlerini ayarlama

`.env.example` dosyası varsa kopyalayın:

```bash
# Linux/macOS
cp .env.example .env
```

```powershell
# Windows PowerShell
Copy-Item .env.example .env
```

Ardından `.env` içindeki değerleri kendi yerel ortamınıza göre doldurun. Proje henüz ortam değişkeni yükleme paketini/ayarlarını içermiyorsa bu mekanizma uygulama iskeleti kurulurken eklenmelidir.

### 8.6 Migration ve yönetici hesabı

```bash
python manage.py check
python manage.py migrate
python manage.py createsuperuser
```

Model değişiklikleri yapıldığında ilgili migration dosyalarını oluşturun ve değişiklikleri Git’e ekleyin:

```bash
python manage.py makemigrations
python manage.py migrate
```

Migration dosyaları sürüm kontrolüne eklenmelidir; yerel veritabanı dosyaları ve parolalar eklenmemelidir.

### 8.7 Geliştirme sunucusu

```bash
python manage.py runserver
```

Varsayılan yerel adresler:

- Uygulama: `http://127.0.0.1:8000/`
- Django yönetim paneli: `http://127.0.0.1:8000/admin/`

Bu adreslerin açılması, henüz geliştirilmemiş bütün ekranların hazır olduğu anlamına gelmez.

---

## 9. Ortam değişkenleri ve gizli bilgiler

Örnek `.env.example` dosyası aşağıdaki değişkenleri içerebilir. İsimler, Django ayarlarıyla birebir uyumlu olacak şekilde uygulanırken kesinleştirilmelidir.

```env
# Django
SECRET_KEY=replace-with-a-local-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

# PostgreSQL
DB_NAME=library_db
DB_USER=library_user
DB_PASSWORD=replace-with-local-password
DB_HOST=localhost
DB_PORT=5432

# LLM (yalnızca sunucuda; anahtar sunucudaki sağlayıcı SDK istemcisine aktarılır)
LLM_PROVIDER=gemini
LLM_API_KEY=
LLM_MODEL=gemini-3.5-flash-lite
```

Güvenlik kuralları:

- Gerçek `.env` dosyası `.gitignore` içinde olmalı ve GitHub’a gönderilmemelidir.
- `.env.example` içinde gerçek anahtar, parola veya kişisel bilgi bulunmamalıdır.
- `SECRET_KEY`, veritabanı parolası ve LLM API anahtarı kod içinde sabit yazılmamalıdır.
- API anahtarı eksik/geçersizse LLM özelliği anlaşılır bir hata veya güvenli fallback göstermeli; tüm uygulamayı çökertmemelidir.
- LLM istekleri Bölüm 3.3 sınırlarına uymalı; hesap bilgileri, ham ödünç geçmişi ve borç kayıtları prompt'a eklenmemelidir. API anahtarı tarayıcıya gönderilmemelidir.
- LLM çıktısı HTML olarak doğrudan güvenilerek render edilmemeli; uygun şekilde metin olarak gösterilmeli veya güvenli biçimde temizlenmelidir.
- Hata kayıtlarında API anahtarı, parola veya hassas kullanıcı verileri yer almamalıdır.

---

## 10. Test stratejisi ve kalite kontrolleri

Testler yalnızca “sayfa açılıyor mu?” kontrolüyle sınırlı kalmamalıdır. Öncelik, iş kurallarının doğru çalıştığını ve kullanıcı/rol sınırlarının korunduğunu doğrulamaktır.

### Önerilen test kapsamı

**Katalog ve stok**
- Kitap, yazar ve kategori kayıtlarının oluşturulması ve görüntülenmesi.
- Birden fazla yazar ve kategorinin aynı kitapla ilişkilendirilmesi.
- Başlık/yazar/kategori arama ve filtrelerinin beklenen sonuçları vermesi.
- Uygun olmayan veya ödünçteki kopyanın yeniden ödünç verilememesi.
- Kopya durum değişikliklerinin stok/uygunluk görünümüne yansıması.

**Ödünç ve iade**
- Uygun kopya için ödünç kaydı oluşturulması.
- Kopya yokken ödünç işleminin reddedilmesi.
- İadenin yalnızca geçerli aktif ödünç için yapılması.
- İade tarihinin ve kopya durumunun doğru güncellenmesi.
- Aynı kopyanın eşzamanlı veya tekrarlı isteklerle birden fazla aktif ödünç kaydı almamasının kontrol edilmesi.

**Ceza motoru**
- Zamanında iade için sıfır gecikme cezası.
- Bir günlük ve birden çok günlük gecikme hesapları.
- Aktif ödünç için bugüne kadar tahmini cezanın hesaplanması; iadede tutarın sabitlenmesi.
- 19 gün için 95 TL; 20 ve 25 gün için 100 TL üst sınırının doğrulanması.
- Kapalı güne denk gelen vadenin ilk açık güne ötelenmesi; bundan sonraki gecikmenin takvim günü sayılması.
- Para hesaplamasında `Decimal` kullanılması.
- Ödenmemiş borcun veya gecikmiş aktif ödüncün yeni ödünç/uzatmayı engellemesi; iadeyi engellememesi.
- Üyenin 3 aktif kopya sınırının eşzamanlı isteklerde de aşılmaması.
- İlk uzatmanın mevcut vadeye 7 gün eklemesi; ikinci veya gecikmiş uzatmanın reddedilmesi.
- Tekrarlı iade/ödeme isteklerinin ikinci bir ceza/ödeme oluşturmaması.
- Ücret ayarı değiştiğinde eski ödüncün kaydedilmiş ücret koşullarının korunması.

**Hesap ve yetkilendirme**
- Giriş yapmamış kullanıcının korumalı sayfalara erişememesi.
- Üyenin başka bir kullanıcının ödünç/ceza kayıtlarını görememesi.
- Katalog ve dolaşım işlemlerinde rol izinlerinin sunucu tarafında kontrol edilmesi.

**LLM entegrasyonu**
- API yanıtının başarıyla işlenmesi.
- API hatası, zaman aşımı, boş veya beklenmeyen yanıt durumlarının yönetilmesi.
- Anahtar yokken uygulamanın temel işlevlerinin çalışmaya devam etmesi.
- LLM önerilerinin verilen katalog adaylarıyla eşleştirilmesi; adaylar dışındaki kimliklerin gösterilmemesi.
- Kişisel hesap/ödünç/ceza bilgilerinin model isteğine dahil edilmemesi; açık e-posta/telefon içeren isteğin gönderilmeden reddedilmesi.
- Uygulama istek limitleri ve zaman aşımı sonrasında normal aramanın çalışması.
- Testlerde gerçek API çağrısı yerine mock/fake yanıt kullanılması; testlerin ücretli dış servise bağımlı olmaması.

### Test komutları

Django testleri için:

```bash
python manage.py test
```

`pytest` seçilirse ekip, `pytest` yapılandırmasını ve gerekli paketleri `requirements.txt` içinde tanımlamalıdır. İki test aracını gerekçesiz biçimde birlikte kullanmak zorunlu değildir.

### Kod inceleme kontrol listesi

- İlgili testler çalıştırıldı mı?
- Migration değişikliği varsa dosyalar eklendi mi?
- Yetki ve veri doğrulama kontrolleri sunucu tarafında mı?
- Gizli bilgi veya gerçek kullanıcı verisi eklendi mi?
- İsimlendirme ve kod biçimi anlaşılır mı?
- README/rapor/ER diyagramı değişiklikten etkilendiyse güncellendi mi?

---

## 11. Git ve ekip çalışma akışı

### Temel kurallar

1. `main` branch'ine doğrudan push yapılmamalıdır.
2. Her iş için kısa ömürlü bir feature branch açılmalıdır.
3. İşlevsel değişiklikler Pull Request üzerinden birleştirilmelidir.
4. Bir ekip arkadaşı değişikliği gözden geçirmeden PR birleştirilmemesi hedeflenir.
5. Her geliştirici kendi kodunun testini, açıklamasını ve ilgili rapor katkısını sağlamalıdır.
6. Migration dosyaları, `.env.example` ve README güncellemeleri ilgili değişikliklerle birlikte değerlendirilmelidir.
7. `.env`, sanal ortam klasörü, cache dosyaları, kişisel IDE ayarları ve yerel veritabanı dökümleri repoya eklenmemelidir.

### Branch isimleri

```text
main
feature/project-setup
feature/accounts-permissions
feature/catalog-search
feature/copy-inventory
feature/borrowing-return
feature/fine-calculation
feature/llm-recommendations
feature/shared-ui
test/integration-tests
docs/interim-report
docs/final-report
```

İsimler örnektir; branch’ler ekipteki kişilere değil, yapılan işe göre açılabilir.

### Commit mesajları

Kısa ve yapılan işi anlatan mesajlar kullanın:

```text
Add book search filters
Create loan model and migrations
Implement overdue fine calculation
Add recommendation service tests
Document PostgreSQL setup
```

### Düzenli ekip kontrolü

Her toplantıda şu dört soru yanıtlanmalıdır:

- Önceki toplantıdan beri ne tamamlandı?
- Şu anda ne üzerinde çalışılıyor?
- Hangi engel veya karar ihtiyacı var?
- Bir sonraki toplantıya kadar hangi somut çıktı teslim edilecek?

---

## 12. Görev dağılımı ve teslimatlar

Bu dağılım **Üye 1, Üye 2 ve Üye 3** olarak hazırlanmıştır. Kişi adları ve öğrenci numaraları ekipte anlaşma sağlandıktan sonra eklenebilir. Görevler önerilen sorumluluk alanlarıdır; ortak entegrasyon ve raporlama tüm ekip üyelerinin sorumluluğudur.

### Üye 1 — Ortak mimari, proje iskeleti, arayüz bütünlüğü ve LLM

**Ana sorumluluk:** Ortak Django proje iskeletinin kurulması, modüllerin birlikte çalışacağı yapının ve ortak arayüzün düzenlenmesi, LLM destekli öneri/özet modülünün geliştirilmesi.

**Ara rapora kadar**
- Ortak Django projesini ve temel ayarları oluşturmak; `config`, URL yönlendirmeleri ve ortak şablon yaklaşımını belirlemek.
- GitHub deposunun temel çalışma düzenini, branch/PR akışını ve başlangıç dokümantasyonunu hazırlamak.
- PostgreSQL bağlantısının proje ayarlarına entegre edilmesi için Üye 2 ve Üye 3 ile birlikte çalışmak; tek başına veritabanı tasarımını sahiplenmek yerine ortak yapının çalışmasını doğrulamak.
- Ortak `base.html`, gezinme menüsü ve temel sayfa düzeninin başlangıç sürümünü hazırlamak.
- Bölüm 3.3'te önerilen Gemini API/model seçimini hesap erişimi, kota, Türkçe yanıt kalitesi ve gizlilik sınırları açısından doğrulamak; katalog verisiyle eşleştirme yaklaşımını tasarlamak.
- LLM servisinin sınırlarını ve önerilen prompt/yanıt işleme akışını tasarlamak; henüz uygulanmadıysa raporda bunu “planlanan çalışma” olarak belirtmek.
- Ara rapor için mimari, teknoloji seçimi, araçlar ve kendi katkılarını belgelemek; ilgili literatür/benzer çalışmalar araştırmasına katkı vermek.

**Final raporuna kadar**
- `recommendations` modülünü geliştirmek: katalog açıklamasına dayalı kısa özet/analiz ve mevcut kullanıcı isteği/tercihlerine dayalı öneri akışını Bölüm 3.3'e uygun uygulamak; okuma geçmişine dayalı gelişmiş kişiselleştirmeyi sonraki aşama olarak belgelemek.
- LLM istemcisini servis katmanında tutmak; zaman aşımı, API hatası, eksik anahtar ve beklenmeyen yanıt durumlarını yönetmek.
- Önerileri katalogdaki kitaplarla ilişkilendirmek; katalogda bulunmayan önerileri gerçek stok kaydı gibi göstermemek.
- Ortak şablonların modüllerle tutarlı kullanılmasını ve sayfalar arasında gezinmenin bütünlüğünü sağlamak.
- Üye 2 ve Üye 3’ün modüllerini ortak projeye entegre etmek; entegrasyon hatalarını ilgili kişiyle birlikte gidermek.
- LLM servisi ve temel ortak akışlar için testler yazmak; entegrasyon testlerine katkı sağlamak.
- Mimari, arayüz, LLM yaklaşımı, test sonuçları ve sınırlılıklarla ilgili final raporu bölümlerini hazırlamak.

**Beklenen çıktılar**
- Çalışır ortak Django iskeleti ve proje ayarları.
- Ortak temel şablon ve gezinme düzeni.
- `recommendations` modülü ve servis/testleri.
- Mimari açıklaması, LLM tasarım notları ve katkı kayıtları.

### Üye 2 — Veritabanı/ER tasarımı, katalog, arama ve stok

**Ana sorumluluk:** Kütüphane katalog verisinin modellenmesi; kitap, yazar, kategori ve fiziksel kopya ilişkileri; katalog arama/filtreleme ve stok/uygunluk görünümü.

**Ara rapora kadar**
- Gereksinimleri varlık ve ilişkilere dönüştürmek; ilk ER diyagramını hazırlamak.
- `Book`, `Author`, `Category` ve `BookCopy` modelleri için alan ve ilişki önerilerini hazırlamak.
- Kitap–yazar ve kitap–kategori Many-to-Many ilişkilerini tasarlamak.
- ISBN benzersizliği, zorunlu alanlar, kopya durumu ve silme davranışları gibi bütünlük kurallarını değerlendirmek.
- PostgreSQL şemasının Django ORM ile nasıl uygulanacağını Üye 1 ve Üye 3 ile koordine etmek.
- Ara rapor için veri modeli, ER diyagramı, katalog gereksinimleri ve ilgili literatür/benzer sistemler hakkında katkı sağlamak.

**Final raporuna kadar**
- `catalog` uygulamasındaki modelleri, migration’ları, form/validasyonları ve gerekli yönetim ekranlarını geliştirmek.
- Kitap, yazar ve kategori için ekleme/görüntüleme/güncelleme/silme işlevlerini yetki tasarımına uygun şekilde uygulamak.
- Başlık, yazar ve kategoriye göre arama/filtreleme işlevlerini geliştirmek.
- Fiziksel kopya kayıtlarını ve uygunluk/stok görünümünü oluşturmak.
- Ödünç/iade modülünün kopya durumunu doğru güncelleyebilmesi için gerekli servis/API arayüzünü Üye 3 ile netleştirmek.
- Katalog ve stok kuralları için birim testleri yazmak; entegrasyon testlerine katılmak.
- Final raporu için gerçek veri modelini, katalog ekranlarını, test sonuçlarını ve sınırlılıkları belgelemek.

**Beklenen çıktılar**
- Güncel ER diyagramı ve Django modelleri/migration’ları.
- Katalog yönetimi ve arama/filtreleme ekranları.
- Kopya/stok/uygunluk takibi.
- İlgili testler, ekran görüntüleri ve rapor katkısı.

### Üye 3 — Hesap/rol yönetimi, ödünç-iade ve ceza motoru

**Ana sorumluluk:** Kullanıcı erişimi ve izinler ile ödünç alma, iade, gecikme cezası ve ödünç geçmişi iş kurallarının uygulanması.

**Ara rapora kadar**
- Üye, kütüphaneci ve yönetici rollerinin ihtiyaçlarını ve izin sınırlarını tanımlamak.
- `Loan` ve `Fine` modelleri için gerekli alanları, durumları ve ilişkileri tasarlamak.
- Bölüm 3'teki 14 gün, 5 TL/gün, 100 TL üst sınır, 3 aktif kopya, tek 7 günlük uzatma, kapalı gün ve borç/gecikme kurallarını ekipçe gözden geçirmek; tarih örnekleri ve kabul ölçütlerini belgelemek.
- Ödünç ve iade senaryolarını, hata durumlarını ve kabul ölçütlerini yazmak.
- Üye 1 ve Üye 2 ile modellerin ve stok güncelleme akışının entegrasyonunu planlamak.
- Ara rapor için kullanıcı rolleri, ödünç/iade ve ceza yaklaşımı ile ilgili literatür/benzer sistemler konusunda katkı sağlamak.

**Final raporuna kadar**
- `accounts` uygulamasında gerekli kimlik doğrulama, rol ve erişim kontrollerini geliştirmek; Django’nun yerleşik kimlik doğrulama sistemini uygun şekilde kullanmak.
- `circulation` uygulamasında ödünç alma, iade, tek uzatma ve görevlinin demo ödeme kaydı akışlarını uygulamak.
- Ödünç sırasında kopya uygunluğunu doğrulamak; işlem başarısız olursa stok/ödünç durumunun tutarsız kalmasını önlemek.
- Ceza hesaplama mantığını ayrı bir servis fonksiyonunda geliştirmek; kararlaştırılan kuralları merkezi olarak uygulamak.
- Ödenmemiş borç ve gecikmiş aktif ödünç nedeniyle yeni ödünç/uzatma kısıtlarını sunucu tarafında uygulamak; iadeye izin vermek.
- Üyenin kendi ödünç geçmişi/cezalarını görmesini sağlamak; başka kullanıcılara ait kayıtları yetkisiz erişime kapatmak.
- Kimlik doğrulama, yetkilendirme, ödünç/iade ve ceza kuralları için testler yazmak.
- Final raporu için iş kurallarını, ekranları, test sonuçlarını ve bilinen sınırlılıkları belgelemek.

**Beklenen çıktılar**
- Hesap/rol ve izin kontrolleri.
- Ödünç/iade/uzatma akışları ve demo ödeme kayıtları.
- Ceza hesaplama servisi ve ceza geçmişi.
- İlgili testler, ekran görüntüleri ve rapor katkısı.

### Ortak sorumluluklar

Her ekip üyesi:

- Kendi modülündeki model, iş mantığı ve arayüzü birlikte geliştirmeye katkı verir; yalnızca kod yazıp entegrasyonu diğer üyelere bırakmaz.
- Kendi değişiklikleri için test yazar ve sonuçları kaydeder.
- En az bir başka ekip üyesinin Pull Request’ini inceler.
- Kendi teknik kararlarını ve literatür katkısını rapora yansıtır.
- Ara rapor ve final raporu için kendisine ait metin, kaynakça girdileri, ekran görüntüleri ve katkı beyanını zamanında teslim eder.
- Entegrasyon ve sunum öncesi ortak hata ayıklama çalışmalarına katılır.
- Görev kapsamı değişirse değişikliği ekipçe kararlaştırır ve README’yi günceller.

> **Önemli:** Görev dağılımı bir modülün tek kişide tamamen izole kalması anlamına gelmez. Özellikle veritabanı, kopya durumu, ödünç akışı ve LLM önerileri arasında ortak arayüzler belirlenmeli ve entegrasyon birlikte test edilmelidir.

---

## 13. Ara rapor için çalışma planı

Ara rapor şablonundaki bölümler esas alınarak aşağıdaki çıktılar hazırlanmalıdır. Ara rapor, henüz tamamlanmamış özellikleri bitmiş gibi göstermemeli; mevcut ilerlemeyi kanıtlarıyla açıklamalıdır.

| Ara rapor bölümü | Hazırlanacak içerik | Ana katkı |
|---|---|---|
| **Abstract / Özet** | Problem, amaç, yaklaşım, mevcut ilerleme ve bir sonraki aşamanın kısa özeti | Üç üyenin ortak kontrolü |
| **Introduction / Giriş** | Problem bağlamı, mevcut durum, projenin amacı/kapsamı, hedefler ve rapor yapısı | Üye 1 taslak; tüm ekip gözden geçirir |
| **Literature Review / İlgili çalışmalar** | Benzer kütüphane sistemleri, katalog/ödünç yönetimi, veri modelleme ve LLM tabanlı öneriler üzerine karşılaştırmalı inceleme | Her üye kendi alanına kaynak ve analiz sağlar |
| **Materials / Proje materyalleri** | Python, Django, PostgreSQL, Bootstrap, Git/GitHub, test araçları ve LLM API seçeneğinin gerekçesi | Üye 1 derler; diğer üyeler teknik ayrıntıları sağlar |
| **Current State / Mevcut durum** | Gerçekte tamamlanan işler, çalışan iskelet/bağlantılar, ilk ER diyagramı, örnek ekranlar ve test sonuçları | Her üye kendi ilerlemesini kanıtlar |
| **Future Improvements / Gelecek çalışmalar** | Final aşamasında yapılacak katalog, ödünç/ceza, yetkilendirme, LLM, test ve entegrasyon işleri | Üç üye birlikte |
| **Acknowledgements / Teşekkür** | Varsa katkı sağlayan kişi/kurumlar | Ekip |
| **References / Kaynakça** | Kullanılan kaynakların APA 7 biçiminde listesi | Her üye kendi kaynaklarını sağlar; ekip kontrol eder |
| **Author Contributions / Yazar katkıları** | Her üyenin gerçek katkılarının açık ve doğru beyanı | Üç üye birlikte |
| **Appendices / Ekler** | ER diyagramı, ekran görüntüleri, gerekli teknik kanıtlar ve ek tablolar | Her üye kendi kanıtlarını sağlar |

### Ara rapor teslim kontrolü

- [ ] Gereksinimler ve kapsam açıkça tanımlandı.
- [ ] İlk ER diyagramı ile metindeki veri modeli tutarlı.
- [ ] Teknoloji seçimlerinin gerekçeleri yazıldı.
- [ ] Literatür bölümü yalnızca kaynak sıralamıyor; ilgili çalışmaları karşılaştırıyor.
- [ ] Mevcut durum yalnızca gerçekten tamamlanan işler üzerinden yazıldı.
- [ ] Ekran görüntüleri ve test çıktıları gerçek uygulamadan alındı.
- [ ] APA 7 kaynakça ve metin içi atıflar kontrol edildi.
- [ ] Yazar katkıları fiilî çalışmayla uyumlu.
- [ ] Final aşamasında yapılacaklar, mevcut ilerlemeden ayrı belirtildi.

---

## 14. Final raporu için çalışma planı

Final raporunda ara raporun içeriği güncellenmeli ve proje uygulamasının nasıl çalıştığı, hangi sonuçların elde edildiği ve hangi sınırlılıkların kaldığı somut kanıtlarla açıklanmalıdır.

| Final raporu bölümü | Hazırlanacak içerik | Ana katkı |
|---|---|---|
| **Abstract / Özet** | Amaç, yöntem, uygulanan sistem, test/sonuç özeti ve ana çıkarımlar | Üç üyenin ortak kontrolü |
| **Introduction / Giriş** | Problem, amaç, kapsam, hedefler ve rapor yapısı | Üye 1 taslak; ekip kontrolü |
| **Literature Review / İlgili çalışmalar** | Ara rapor kaynaklarının güncellenmiş karşılaştırması ve projenin bu çalışmalarla ilişkisi | Her üye kendi alanı |
| **Materials / Proje materyalleri** | Gerçekte kullanılan teknolojiler, araçlar, ortamlar ve API’ler | Üye 1 derler; ekip doğrular |
| **The Project / Proje** | Mimari, veri modeli, modüller, ekranlar, iş akışları, önemli tasarım kararları, test yaklaşımı ve elde edilen sonuçlar | Her üye kendi modülü; ekip entegrasyonu |
| **Conclusions / Sonuçlar** | Hedeflere ne ölçüde ulaşıldığı, testlerden çıkan sonuçlar, sınırlılıklar ve gelecekteki iyileştirmeler | Üç üye birlikte |
| **Acknowledgements / Teşekkür** | Varsa katkı sağlayan kişi/kurumlar | Ekip |
| **References / Kaynakça** | APA 7 biçiminde tüm kullanılan kaynaklar | Her üye kaynaklarını sağlar; ekip kontrol eder |
| **Author Contributions / Yazar katkıları** | Gerçek katkıların kişi bazında açıklanması | Üç üye birlikte |
| **Appendices / Ekler** | ER diyagramı, ekran görüntüleri, test kanıtları, gerekli ek teknik materyaller | Her üye kendi kanıtlarını sağlar |

### Final raporu ve demo için kontrol listesi

- [ ] Kurulum talimatları yeni bir ortamda denenebiliyor.
- [ ] Veritabanı migration’ları temiz bir veritabanında uygulanabiliyor.
- [ ] Üye, kütüphaneci ve yönetici izinleri test edildi.
- [ ] Kitap arama ve filtreleme doğru sonuç veriyor.
- [ ] Kopya/uygunluk ve ödünç/iade durumları tutarlı.
- [ ] Ceza kuralları ekip kararlarıyla uyumlu ve testlerle doğrulanmış.
- [ ] LLM hataları temel kütüphane işlevlerini durdurmuyor.
- [ ] Testler çalıştırıldı; başarısız veya kapsam dışı testler dürüstçe raporlandı.
- [ ] Ekran görüntüleri ve sonuçlar gerçek uygulamadan alındı.
- [ ] Bilinen sınırlılıklar ve gelecek geliştirmeler açıklandı.
- [ ] APA 7 atıfları, kaynakça ve yazar katkıları gözden geçirildi.
- [ ] Sunum/demoda kullanılacak örnek veriler kişisel veya gizli bilgi içermiyor.

---

## 15. Raporlama ve katkıların belgelenmesi

Raporlarda yapılmış işler ile planlanan işler açıkça ayrılmalıdır. Bir özellik yalnızca tasarlanmışsa “tasarlanmıştır/planlanmıştır”; uygulaması ve testi tamamlanmışsa elde edilen kanıtla birlikte “uygulanmıştır/test edilmiştir” şeklinde yazılmalıdır.

Her üye kendi çalışması için aşağıdaki kayıtları tutmalıdır:

- Tarih ve yapılan işin kısa açıklaması.
- İlgili branch/commit/PR bağlantısı.
- Eklenen veya değiştirilen modeller, servisler, ekranlar ve testler.
- Test komutu ve sonucu.
- Rapor için kullanılabilecek ekran görüntüsü veya diyagram.
- Karşılaşılan sorunlar, alınan kararlar ve kalan işler.

Literatür araştırmasında kaynağın tam künyesi, bağlantısı/DOI bilgisi, araştırma sorusu, yöntemi, önemli sonucu ve bu projeyle ilişkisi not edilmelidir. Kaynaklar okunmadan yalnızca başlıklarına dayanarak sonuç aktarılmamalıdır.

---

## 16. Tamamlanma ölçütleri

Bir özellik, yalnızca kodu yazıldığı için tamamlanmış sayılmamalıdır. Mümkün olduğunda aşağıdaki koşullar birlikte sağlanmalıdır:

1. İlgili gereksinim ve kabul ölçütü belirlenmiştir.
2. Kod ortak branch'e gözden geçirilerek birleştirilmiştir.
3. Normal durum ve önemli hata durumları test edilmiştir.
4. İlgili model/migration ve izin kontrolleri tutarlıdır.
5. Arayüzde kullanıcıya anlaşılır sonuç veya hata mesajı gösterilir.
6. Kurulum veya kullanım değiştiyse README güncellenmiştir.
7. Ara/final raporunda kullanılacak kanıt ve katkı kaydı tutulmuştur.

### Örnek kabul ölçütleri

- **Arama:** Başlık/yazar/kategori araması beklenen kitapları döndürür; sonuç bulunmadığında uygun mesaj gösterilir.
- **Stok:** Ödünçteki veya uygun olmayan kopya tekrar ödünç verilemez; iade sonrası uygunluk doğru güncellenir.
- **Ceza:** Belirlenen örnek tarih ve ücretler için hesap sonucu beklenen değerle aynıdır.
- **Yetki:** Üye başka bir üyenin özel ödünç/ceza kayıtlarına erişemez.
- **LLM:** Geçerli yanıt gösterilir; API hatası veya anahtar eksikliğinde anlaşılır geri bildirim verilir ve temel katalog işlemleri çalışmayı sürdürür.

---

## 17. Riskler ve önlemler

| Risk | Olası etki | Önlem |
|---|---|---|
| ER diyagramı ve Django modellerinin farklılaşması | Migration ve entegrasyon sorunları | Model değişikliklerini ortak incelemek; diyagramı güncel tutmak |
| Görev sınırlarının belirsiz olması | İşlerin tekrarlanması veya bazı işlerin sahipsiz kalması | Modül arayüzlerini ve sorumlulukları erken kararlaştırmak; düzenli kontrol |
| PostgreSQL bağlantı/ortam farkları | Ekip üyelerinde farklı hatalar | Ortak kurulum talimatı, `.env.example` ve aynı migration akışı |
| Ödünç alma sırasında stok tutarsızlığı | Aynı kopyanın birden fazla kişiye verilmesi | İşlemleri atomik yapmak; veritabanı kısıtları ve testler eklemek |
| Ceza kurallarının geç belirlenmesi | Tekrar kodlama ve rapor uyuşmazlığı | Kuralları kodlamadan önce yazılı olarak kararlaştırmak |
| LLM API maliyeti, hız sınırı veya erişim sorunu | Öneri özelliğinin çalışmaması | Mock testler, zaman aşımı, hata yönetimi ve isteğe bağlı fallback |
| LLM’nin yanlış/uydurma öneri üretmesi | Kullanıcıda yanıltıcı bilgi | Önerileri katalog verisiyle eşleştirmek; sınırları açık belirtmek |
| API anahtarı veya kişisel verinin repoya girmesi | Güvenlik ve gizlilik sorunu | `.env` kullanmak, `.gitignore`, PR kontrolü ve asgari veri ilkesi |
| Raporun uygulamadan önce tamamlanmış gibi yazılması | Akademik doğruluk sorunu | Planlanan/gerçekleşen işleri ayırmak; gerçek ekran ve test kanıtı kullanmak |
| Entegrasyonun son haftaya kalması | Final tesliminde kritik hatalar | Modülleri erken birleştirmek ve her PR sonrası temel testleri çalıştırmak |

---

## 18. Geliştirme yol haritası

Tarihler ders takvimine göre ekipçe eklenmelidir. Sıralama, teknik bağımlılıklara göre önerilmiştir.

1. **Gereksinimlerin netleştirilmesi:** Kullanıcı rolleri, ödünç/ceza kuralları, kapsam ve kabul ölçütleri.
2. **Tasarım:** İlk ER diyagramı, uygulama sınırları, ortak model/servis arayüzleri.
3. **Ortak iskelet:** Django ayarları, PostgreSQL bağlantısı, ortak şablon, `.env.example`, Git akışı.
4. **Temel modüller:** Katalog/kopyalar, hesap/izinler, ödünç/iade/ceza ve öneri modülünün geliştirilmesi.
5. **Ara rapor:** Gerçek ilerleme, literatür, materyaller, diyagramlar ve gelecek çalışma planı.
6. **Entegrasyon:** Modüller arası akışlar, migration kontrolü ve uçtan uca senaryolar.
7. **Test ve hata düzeltme:** Birim, entegrasyon, yetkilendirme ve hata senaryoları.
8. **Son arayüz ve dokümantasyon:** Ekran tutarlılığı, kurulum adımları, bilinen sınırlılıklar.
9. **Final raporu ve demo:** Sonuçlar, test kanıtları, katkı beyanları ve sunum.

---

## 19. Lisans ve akademik kullanım

Proje akademik ders kapsamında geliştirilmektedir. Açık bir lisans seçilmediyse bu README belirli bir açık kaynak lisansı ilan etmez. Kodun lisanslanması, üçüncü taraf paketlerin lisans koşulları ve kullanılan veri/kaynakların atıf gereklilikleri ekip ve ders gereksinimleri doğrultusunda ayrıca belirlenmelidir.
