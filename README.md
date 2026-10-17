# Library Management System

Django ve PostgreSQL kullanılarak geliştirilecek web tabanlı bir Kütüphane Yönetim Sistemi. Proje; kitap kataloğu ve arama, kitap kopyalarının stok takibi, ödünç alma ve iade işlemleri, gecikme cezası hesaplama ve Büyük Dil Modeli (LLM) destekli kitap özeti/kişiselleştirilmiş öneri özelliklerini tek bir uygulamada birleştirmeyi amaçlar.

> **Ders:** CEN317 – Engineering Design  
> **Bölüm:** Bilgisayar Mühendisliği, Çukurova Üniversitesi  
> **Proje durumu:** Geliştirme aşamasında. Bu README’deki özellikler hedeflenen kapsamı anlatır; tamamlandığı doğrulanmamış işlevler tamamlanmış kabul edilmemelidir.

---

## İçindekiler

- [1. Amaç ve kapsam](#1-amaç-ve-kapsam)
- [2. Kullanıcı rolleri ve işlevsel gereksinimler](#2-kullanıcı-rolleri-ve-işlevsel-gereksinimler)
- [3. İş kuralları ve karar bekleyen noktalar](#3-iş-kuralları-ve-karar-bekleyen-noktalar)
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
6. **LLM destekli öneriler:** Kitap özeti/analizi ve kullanıcı tercihleri ya da okuma geçmişine dayalı öneriler.

### Kapsam dışı veya ayrıca kararlaştırılacak konular

Çevrim içi ödeme, barkod/RFID donanımı, e-kitap dağıtımı, çok şubeli kütüphane yönetimi, gerçek zamanlı bildirimler ve üretim ortamında ölçeklendirme ilk sürümün zorunlu kapsamı değildir. Ekip ve ders gereksinimleri doğrultusunda eklenmeleri ayrıca kararlaştırılmalıdır.

---

## 2. Kullanıcı rolleri ve işlevsel gereksinimler

Roller ve izinler uygulama geliştirilirken kesinleştirilecektir. Önerilen başlangıç modeli şöyledir:

| Rol | Temel yetkiler |
|---|---|
| **Üye** | Kataloğu görüntüleme ve arama, kendi ödünç kayıtlarını ve cezalarını görüntüleme, uygun kitap için ödünç talebinde bulunma/ödünç alma, LLM önerilerinden yararlanma |
| **Kütüphaneci** | Katalog kayıtlarını ve kopyaları yönetme, ödünç/iade işlemlerini yönetme, gerekli kayıtları görüntüleme |
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

## 3. İş kuralları ve karar bekleyen noktalar

Aşağıdaki maddeler geliştirmeye başlamadan önce ekipçe karara bağlanmalı, README’deki bu bölüm ve ilgili raporlar buna göre güncellenmelidir.

| Konu | Karar / uygulanacak yaklaşım |
|---|---|
| Ödünç süresi | **Ekip kararı bekleniyor.** Örneğin belirli sayıda gün olarak tanımlanabilir. |
| Günlük gecikme ücreti | **Ekip kararı bekleniyor.** Para birimi ve hesaplama yöntemi belirlenmeli. |
| Azami ceza | **Ekip kararı bekleniyor.** Üst sınır olup olmayacağı belirlenmeli. |
| Hafta sonu/resmî tatil | **Ekip kararı bekleniyor.** Takvim günleri mi iş günleri mi sayılacağı belirlenmeli. |
| Ödenmemiş ceza kısıtı | Hedeflenen kural: ödenmemiş cezası bulunan üyenin yeni ödünç almasının engellenmesi. Eşik veya istisna varsa tanımlanmalı. |
| Aynı anda alınabilecek kitap sayısı | **Ekip kararı bekleniyor.** |
| Yenileme/uzatma | İlk sürüme dahil edilip edilmeyeceği belirlenmeli. |
| Kopya durumu | En azından ödünç alınabilir/ödünçte durumları tanımlanmalı; kayıp veya hasarlı durumları kapsam kararıyla eklenebilir. |
| LLM sağlayıcısı/modeli | API ve model `.env` üzerinden yapılandırılmalı; sağlayıcı seçimi ekipçe yapılmalı. |
| Kullanıcı verisi | LLM’ye yalnızca özellik için gerekli asgari veri gönderilmeli; gizli veya gereksiz kişisel bilgi gönderilmemeli. |

### Ceza hesaplaması için önerilen tanım

Ekip farklı bir kural seçmezse, hesaplama aşağıdaki genel mantıkla uygulanabilir:

`gecikme_günü = max(0, iade_tarihi veya bugün - son_teslim_tarihi)`

`ceza = gecikme_günü × günlük_ceza`

Bu formül yalnızca başlangıç önerisidir. Gün sayımının başlangıç/bitiş noktası, günün hangi saatinde iade yapıldığı, azami ceza ve hafta sonu politikası netleştirilmeden nihai kabul edilmemelidir. Ceza tutarı `float` yerine para hesabına uygun `Decimal` türüyle hesaplanmalıdır.

---

## 4. Teknoloji yığını

| Katman / amaç | Seçilen veya önerilen teknoloji |
|---|---|
| Programlama dili | Python |
| Web çatısı | Django |
| Arayüz | Django Templates, HTML, CSS, Bootstrap 5 |
| İlişkisel veritabanı | PostgreSQL |
| LLM | Bir LLM sağlayıcısının API’si; sağlayıcı/model yapılandırılabilir tutulacak |
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
| `BookCopy` | Fiziksel kopya kimliği/etiketi, bağlı kitap ve kopyanın durumu |
| `Loan` | Üye, kopya, ödünç tarihi, son teslim tarihi, iade tarihi ve durum |
| `Fine` | İlgili ödünç/üye, tutar, oluşturulma tarihi ve ödeme durumu/tarihi (ödeme işlevi kapsama alınırsa) |
| LLM kullanım kaydı (isteğe bağlı) | Hata ayıklama/ölçüm için gerekli en az bilgi; hassas prompt ve kişisel veriler varsayılan olarak kaydedilmemeli |

### İlişki ve bütünlük notları

- `Book`–`Author` ve `Book`–`Category` ilişkileri Django ORM üzerinden `ManyToManyField` ile modellenebilir. Django ara tabloları otomatik oluşturabilir; özel ilişki alanları gerekiyorsa `through` modeli kullanılabilir.
- `BookCopy`, kitap başlığını fiziksel kopyalardan ayırır. Stok, yalnızca kitap kaydındaki serbest bir sayıdan değil, kopyaların tutarlı durumlarından türetilebilir veya kontrollü bir özet alanla yönetilebilir.
- `Loan`, bir kullanıcı ile bir fiziksel kopyayı ilişkilendirmelidir. Aynı kopyanın aynı anda birden fazla aktif ödünç kaydına bağlanması engellenmelidir.
- `Fine` ile `Loan` arasındaki ilişki ve bir ödünç için birden fazla ceza oluşup oluşamayacağı açıkça kararlaştırılmalıdır.
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

# LLM (kullanılacak sağlayıcıya göre adlar değişebilir)
LLM_PROVIDER=replace-with-provider
LLM_API_KEY=
LLM_MODEL=replace-with-model
```

Güvenlik kuralları:

- Gerçek `.env` dosyası `.gitignore` içinde olmalı ve GitHub’a gönderilmemelidir.
- `.env.example` içinde gerçek anahtar, parola veya kişisel bilgi bulunmamalıdır.
- `SECRET_KEY`, veritabanı parolası ve LLM API anahtarı kod içinde sabit yazılmamalıdır.
- API anahtarı eksik/geçersizse LLM özelliği anlaşılır bir hata veya güvenli fallback göstermeli; tüm uygulamayı çökertmemelidir.
- Kullanıcı girdileri LLM’ye gönderilmeden önce sınırlandırılmalı; kullanıcıya ait gereksiz hassas veriler prompt’a eklenmemelidir.
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
- İade edilmemiş/aktif ödünç için “bugüne kadar” hesaplama yaklaşımı (ekip kararıyla).
- Azami ceza ve hafta sonu kuralları kararlaştırılmışsa bunların test edilmesi.
- Para hesaplamasında `Decimal` kullanılması.
- Ödenmemiş ceza kuralının yeni ödünç işlemine doğru uygulanması.

**Hesap ve yetkilendirme**
- Giriş yapmamış kullanıcının korumalı sayfalara erişememesi.
- Üyenin başka bir kullanıcının ödünç/ceza kayıtlarını görememesi.
- Katalog ve dolaşım işlemlerinde rol izinlerinin sunucu tarafında kontrol edilmesi.

**LLM entegrasyonu**
- API yanıtının başarıyla işlenmesi.
- API hatası, zaman aşımı, boş veya beklenmeyen yanıt durumlarının yönetilmesi.
- Anahtar yokken uygulamanın temel işlevlerinin çalışmaya devam etmesi.
- LLM’nin önerdiği kitapların katalog kayıtlarıyla eşleştirilmesi veya katalogda olmadığı açıkça belirtilmesi.
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
- LLM özelliği için sağlayıcı seçeneklerini, API maliyeti/gizlilik risklerini ve katalog verisiyle eşleştirme yaklaşımını araştırmak.
- LLM servisinin sınırlarını ve önerilen prompt/yanıt işleme akışını tasarlamak; henüz uygulanmadıysa raporda bunu “planlanan çalışma” olarak belirtmek.
- Ara rapor için mimari, teknoloji seçimi, araçlar ve kendi katkılarını belgelemek; ilgili literatür/benzer çalışmalar araştırmasına katkı vermek.

**Final raporuna kadar**
- `recommendations` modülünü geliştirmek: kitap özeti/analizi ve kullanıcı tercihi/okuma geçmişi temelli öneri akışını uygulamak.
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
- Ödünç süresi, günlük gecikme ücreti, azami ceza, hafta sonu hesabı ve ödenmemiş ceza kısıtı gibi karar bekleyen iş kurallarını ekip gündemine getirmek.
- Ödünç ve iade senaryolarını, hata durumlarını ve kabul ölçütlerini yazmak.
- Üye 1 ve Üye 2 ile modellerin ve stok güncelleme akışının entegrasyonunu planlamak.
- Ara rapor için kullanıcı rolleri, ödünç/iade ve ceza yaklaşımı ile ilgili literatür/benzer sistemler konusunda katkı sağlamak.

**Final raporuna kadar**
- `accounts` uygulamasında gerekli kimlik doğrulama, rol ve erişim kontrollerini geliştirmek; Django’nun yerleşik kimlik doğrulama sistemini uygun şekilde kullanmak.
- `circulation` uygulamasında ödünç alma ve iade akışlarını uygulamak.
- Ödünç sırasında kopya uygunluğunu doğrulamak; işlem başarısız olursa stok/ödünç durumunun tutarsız kalmasını önlemek.
- Ceza hesaplama mantığını ayrı bir servis fonksiyonunda geliştirmek; kararlaştırılan kuralları merkezi olarak uygulamak.
- Ödenmemiş ceza nedeniyle ödünç kısıtı kararlaştırıldığı şekilde uygulanacaksa bu kontrolü sunucu tarafında yapmak.
- Üyenin kendi ödünç geçmişi/cezalarını görmesini sağlamak; başka kullanıcılara ait kayıtları yetkisiz erişime kapatmak.
- Kimlik doğrulama, yetkilendirme, ödünç/iade ve ceza kuralları için testler yazmak.
- Final raporu için iş kurallarını, ekranları, test sonuçlarını ve bilinen sınırlılıkları belgelemek.

**Beklenen çıktılar**
- Hesap/rol ve izin kontrolleri.
- Ödünç/iade akışları ve kayıtları.
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
