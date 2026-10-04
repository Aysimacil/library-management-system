# Library Management System
 
Kitap arama, ödünç alma ve iade süreçlerinin yönetildiği; geciken iadeler için otomatik ceza hesaplayan, stok takibi yapan ve LLM (Büyük Dil Modeli) desteğiyle kullanıcıya kişiselleştirilmiş kitap önerileri ve özetler sunan web tabanlı kütüphane yönetim sistemi.
 
> **Ders:** CEN317 Engineering Design, Çukurova Üniversitesi Bilgisayar Mühendisliği Bölümü
 
---
 
## İçindekiler
 
- [Özellikler](#özellikler)
- [Sistem Mimarisi](#sistem-mimarisi)
- [Teknolojiler](#teknolojiler)
- [Veritabanı Tasarımı](#veritabanı-tasarımı)
- [Proje Yapısı](#proje-yapısı)
- [Kurulum](#kurulum)
- [Ortam Değişkenleri](#ortam-değişkenleri)
- [Testler](#testler)
- [Geliştirme Akışı](#geliştirme-akışı)
- [Ekip ve Görev Dağılımı](#ekip-ve-görev-dağılımı)
---
 
## Özellikler
 
- **Kullanıcı ve yetki yönetimi:** Üye, kütüphaneci ve admin rolleri.
- **Katalog ve arama:** Kitap, yazar ve kategori yönetimi; başlık, yazar ve kategoriye göre arama ve filtreleme.
- **Ödünç alma ve iade:** Stok kontrollü ödünç kaydı ve iade işlemleri.
- **Ceza motoru:** Geciken iadeler için otomatik ceza hesaplama, ödenmemiş cezası olan kullanıcının yeni ödünç almasının engellenmesi, ceza geçmişi.
- **Stok takibi:** Toplam ve mevcut kopya sayısı, düşük stok uyarısı.
- **LLM entegrasyonu:** Kullanıcının okuma geçmişine göre kitap önerisi, kitap özeti ve analiz.
## Sistem Mimarisi
 
Sistem, sunucu tarafında HTML üreten katmanlı bir Django mimarisine sahiptir.
 
```
┌────────────────────────────────────────────────────────────┐
│ Frontend                                                   │
│ Django Templates + HTML + CSS + Bootstrap                  │
│ Kullanıcı ve yönetici panelleri, arama, ödünç/iade ekranları│
└──────────────────────────┬─────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────┐
│ Backend                                                    │
│ Python + Django                                            │
│ İş mantığı, kullanıcı yönetimi, ödünç işlemleri,           │
│ ceza hesaplama ve LLM bağlantısı                           │
└───────────────┬────────────────────────────┬───────────────┘
                │                            │
     ┌──────────▼──────────┐      ┌──────────▼──────────┐
     │ PostgreSQL          │      │ LLM API             │
     │ İlişkisel veritabanı│      │ Akıllı kitap önerileri│
     └─────────────────────┘      └─────────────────────┘
```
 
İş mantığı (ceza hesaplama, LLM çağrıları) view'lerden ayrı olarak her uygulamanın `services.py` dosyasında tutulur. Bu sayede bu bileşenler bağımsız olarak test edilebilir.
 
## Teknolojiler
 
| Katman | Teknoloji |
|---|---|
| Backend | Python, Django |
| Frontend | Django Templates, HTML, CSS, Bootstrap 5 |
| Veritabanı | PostgreSQL |
| LLM | LLM API (Claude / OpenAI, `.env` ile yapılandırılır) |
| Test | Django TestCase / pytest |
| Sürüm kontrolü | Git, GitHub |
 
## Veritabanı Tasarımı
 
Ana tablolar:
 
| Tablo | Açıklama |
|---|---|
| `users` | Kullanıcılar ve rolleri |
| `books` | Kitap bilgileri |
| `authors` | Yazarlar |
| `categories` | Kategoriler |
| `book_authors` | Kitap ↔ Yazar (**Many-to-Many**) |
| `book_categories` | Kitap ↔ Kategori (**Many-to-Many**) |
| `book_copies` | Fiziksel kopyalar ve stok durumu |
| `loans` | Ödünç kayıtları (alış tarihi, son tarih, iade tarihi) |
| `fines` | Cezalar (ilgili ödünç, tutar, ödendi mi) |
 
> ER diyagramı: `docs/er-diagram.png` (eklenecek)
 
## Proje Yapısı
 
```
library-management-system/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── config/                  # Django proje ayarları
│   ├── settings.py
│   └── urls.py
├── accounts/                # Kimlik doğrulama, roller
├── catalog/                 # Kitap, yazar, kategori, arama, stok
├── circulation/             # Ödünç/iade, ceza motoru
│   └── services.py          # Ceza hesaplama mantığı
├── recommendations/         # LLM entegrasyonu
│   └── services.py          # LLM istemcisi, prompt, önbellek, fallback
├── templates/               # Ortak ve uygulamaya özel şablonlar
├── static/                  # CSS, görseller
└── docs/                    # ER diyagramı, raporlar
```
 
## Kurulum
 
### Gereksinimler
 
- Python 3.11+
- PostgreSQL 14+
- Git
### Adımlar
 
```bash
# 1. Repoyu klonla
git clone https://github.com/<kullanici-adi>/library-management-system.git
cd library-management-system
 
# 2. Sanal ortam oluştur ve etkinleştir
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
 
# 3. Bağımlılıkları yükle
pip install -r requirements.txt
 
# 4. Ortam değişkenlerini ayarla
cp .env.example .env            # Windows: copy .env.example .env
# .env dosyasını kendi değerlerinle düzenle
 
# 5. Veritabanını oluştur (PostgreSQL içinde)
#    CREATE DATABASE library_db;
 
# 6. Migration'ları uygula
python manage.py migrate
 
# 7. Yönetici hesabı oluştur
python manage.py createsuperuser
 
# 8. Sunucuyu başlat
python manage.py runserver
```
 
Uygulama `http://127.0.0.1:8000/` adresinde, yönetim paneli `http://127.0.0.1:8000/admin/` adresinde çalışır.
 
## Ortam Değişkenleri
 
`.env.example` dosyasını `.env` olarak kopyalayıp doldur. **`.env` dosyası asla commit edilmemelidir.**
 
```env
SECRET_KEY=your-django-secret-key
DEBUG=True
 
DB_NAME=library_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
 
LLM_API_KEY=your-llm-api-key
LLM_MODEL=model-name
```
 
## Testler
 
```bash
python manage.py test
```
 
Ceza hesaplama motoru ve LLM servisi için ayrı birim testleri yazılır.
 
## Geliştirme Akışı
 
- `main` branch'ine doğrudan push yapılmaz.
- Her geliştirici kendi branch'inde çalışır:
  - `feature/catalog`
  - `feature/circulation`
  - `feature/accounts-llm`
- İş bitince **Pull Request** açılır, en az bir ekip arkadaşı kodu inceledikten sonra `main`'e birleştirilir.
- Commit mesajları kısa ve açıklayıcı olmalıdır (ör. `Add fine calculation service`).
## Ekip ve Görev Dağılımı
 
| Üye | Sorumluluk | Django uygulaması |
|---|---|---|
| **Üye A** (ad soyad, öğrenci no) | Katalog, arama, stok takibi, istatistik paneli | `catalog` |
| **Üye B** (ad soyad, öğrenci no) | Ödünç/iade akışı, ceza motoru, birim testler | `circulation` |
| **Üye C** (ad soyad, öğrenci no) | Kimlik doğrulama, roller, LLM entegrasyonu, ortak şablon düzeni | `accounts`, `recommendations` |
 
Her üye, sorumlu olduğu modülün veritabanı modellerini, iş mantığını ve arayüz ekranlarını birlikte geliştirir.
