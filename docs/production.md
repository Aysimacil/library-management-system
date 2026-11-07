# Üretime hazırlık ve işletim

Bu sürüm uygulama, test ve dağıtım dosyalarını hazırlar. Canlı sunucuya dağıtım,
alan adı/TLS, gerçek SMTP teslimi ve Gemini hesabı ayrı ortamlarda doğrulanmalıdır.
Entegrasyon ve UI dalları korunur. Üretime geçiş ekip onayından sonra yapılır.

## Ortam ve kalıcı dizinler

Üretim örneği `deploy/production.env.example` içindedir. Gizli değerleri sunucunun
sır yönetiminden veya root tarafından yönetilen `/etc/library/environment`
dosyasından verin. Gerçek ortam dosyasını repoya eklemeyin.

Linux örneğinde uygulama kullanıcısı `library`, Nginx grubu `www-data` ve
değiştirilebilir release bağlantısı `/srv/library/current` olarak seçilmiştir.
Dağıtım alan adını ve bu yolları hedef sunucuya göre uyarlayın.

```bash
install -d -o library -g www-data -m 0750 /srv/library/media /srv/library/tmp
install -d -o library -g www-data -m 0750 /srv/library/static
# Only after verifying the intended persistent volume is mounted:
printf '%s' library-covers > /srv/library/media/.library-volume
chown library:www-data /srv/library/media/.library-volume
chmod 0640 /srv/library/media/.library-volume
```

- `MEDIA_ROOT` üretimde zorunlu, mutlak ve release dizininin dışında olmalıdır.
  Bir sunucuda kalıcı yerel disk, çok uygulama sunucusunda tüm süreçlerin aynı
  veriyi gördüğü kalıcı ortak dosya sistemi kullanın. Geçici container diski uygun değildir.
- `MEDIA_VOLUME_ID` üretimde zorunludur. Kalıcı kökteki `.library-volume`
  işaretçisi bu değeri taşımalıdır. Eksik/yanlış volume'de yazma, silme, yedek
  ve readiness durur; commit edilmiş yeni içerik yeniden deneme kuyruğunda kalır.
  İşaretçiyi her yeniden başlatmada oluşturmayın; yalnız doğru diski ilk
  hazırlarken veya doğrulanmış restore'dan sonra koyun.
- Statik kök `STATIC_ROOT`, medya köküyle kesişemez. Kapaklar Django'nun
  kitap-ID rotasından sunulur; Nginx'in `/media/` rotası dosyaları doğrudan açmaz.
- `FILE_UPLOAD_TEMP_DIR` yalnız uygulamanın yazabildiği geçici yükleme alanıdır.
- PostgreSQL istemcisinin `pg_dump` ve `pg_restore` sürümleri sunucuyla uyumlu
  olmalıdır. Gerekirse `PG_DUMP_PATH` ve `PG_RESTORE_PATH` tam yollarını verin.
- Üretim DB kullanıcısını uygulamanın veritabanıyla sınırlandırın.
  `DB_SSLMODE=verify-full` ve `DB_SSLROOTCERT` güvenilir CA dosyasıyla sunucu
  kimliğini doğrulayın. Test DB oluşturma yetkisi yalnız test kullanıcısına gerekir.
- SMTP için `SMTP_SECURITY=starttls` (genellikle 587) veya `ssl` (genellikle 465)
  seçin. `SMTP_HOST`, `SMTP_PORT`, yetkilendirme bilgileri ve
  `DEFAULT_FROM_EMAIL` değerini sağlayıcının izin verdiği göndericiyle doldurun.

## Transaction ile dosya tutarlılığı

Yeni JPEG içeriği ve rastgele dosya adı, Book kaydıyla aynı DB transaction'ında
`CoverOperation` kuyruğuna yazılır. Fiziksel yazma yalnız commit sonrasında,
geçici dosya + fsync + atomik replace ile yapılır. Outer transaction rollback
olursa yeni dosya yazılmaz ve eski kapak korunur.

Disk hatası veya süreç kapanmasıyla callback tamamlanamazsa kuyruk DB'de kalır.
Kapak rotası kuyruğun doğrulanmış JPEG içeriğini sunabilir. Sonraki worker veya
`process_cover_operations` işlemi yeniden dener. Eski kapak silme işi de commit
sonrasında çalışır; başka kitap aynı dosyayı kullanıyorsa dosya tutulur.
Desteklenen model/admin yazmaları, temizleme ve yedek aynı medya kilidini kullanır.

```bash
python manage.py process_cover_operations --limit 1000
python manage.py reconcile_covers
# Dry-run sonucunu inceleyip gerekiyorsa:
python manage.py reconcile_covers --apply --older-than-hours 24
```

Reconciliation yalnız covers/ altında uygulamaya ait UUID-JPEG adlarını, yaş
eşiğini geçen ve hiçbir kitap/kuyruk tarafından referanslanmayan dosyaları siler.
Bilinmeyen dosya adları ve symlink'ler temizlenmez. Kapakları admin/model save
akışından değiştirin; cover alanında doğrudan SQL veya QuerySet.update bu
yaşam döngüsünü atlar. `deploy/library-media.timer` kuyruk işini dakikada bir çalıştırır.

## Veritabanı ve medya yedeği

```bash
python manage.py backup_library --output /srv/backups/library-2026-11-07.zip
python manage.py restore_library_backup \
  --archive /srv/backups/library-2026-11-07.zip \
  --target /srv/restore/library-2026-11-07
```

Yedek komutu SQLite snapshot veya PostgreSQL custom dump ile yönetilen kapakları
aynı arşivde toplar. Medya referans değişiklikleri ve dosya yayınlamaları boyunca
kilit tutulduğu için DB ile fiziksel dosya görünümü tutarlıdır. Commit edilmiş
bekleyen içerik de veritabanı yedeğinde bulunur. İlk migration'ı veya uygulama
deployment'ını yedekleme ile aynı anda çalıştırmayın.

Arşivde SHA-256 kontrol toplamları, motor ve migration bilgileri bulunur.
Çıktı dosyası 0600 izinle oluşturulur; mevcut arşiv üzerine yazılmaz.
Yedek adı mutlak olmalı ve release/medya dizinlerinin dışında bulunmalıdır.
Yedek kullanıcı, parola hash'i ve işlem verisi içerir. Dosyayı erişimi sınırlı,
şifreli ve ayrı konumdaki yedek depolamaya taşıyın. Saklama süresi kurumca
belirlenmelidir. SHA-256 kazara bozulmayı bulur; arşivin güvenilir kaynaktan
geldiğinin kontrolünün yerine geçmez. Komut arşiv şifrelemesi yapmaz.

Geri yükleme komutu yalnız yeni bir offline dizine açar. Dosya adlarını,
boyut sınırını, symlink'leri ve tüm kontrol toplamlarını doğrular. Çalışan
veritabanına veya mevcut medya dizinine dokunmaz. Varsayılan açılmış boyut
sınırı 2 GiB; daha büyük güvenilir yedekte `--max-bytes` açıkça verilebilir.

Doğrulamadan sonra ayrı bir geri dönüş provası yapın:

1. SQLite için restore dizinindeki `database.sqlite3` dosyasını ve `media` kökünü
   ayrı deneme ortamına bağlayın.
2. PostgreSQL için yeni boş bir prova DB oluşturun ve örneğin
   `pg_restore --no-owner --no-acl --dbname library_restore database.dump`
   çalıştırın. Bağlantı sırlarını PGPASSFILE veya sır yönetiminden verin.
3. Restore medya köküne doğru volume işaretçisini kurun. Aynı uygulama sürümüyle `migrate --plan`, sağlık ve katalog testlerini çalıştırın.
   `process_cover_operations` ile bekleyen dosyaları tekrar yayınlayın.
4. Kopya, ödünç, ceza ve kapakları karşılaştırın. Canlı cutover için yazmaları
   durdurun, son yedeği alın ve doğrulanmış DB/medya çiftini birlikte etkinleştirin.
   Eski çift ve release, rollback kararı için korunmalıdır.

İlk defa bu sürüme geçerken eski sürümde yeni backup komutu bulunmaz. Geçiş
öncesi yazmalar durdurulmuşken altyapının native DB dump/snapshot ve medya
kopyasını alın; yeni migration'ları bundan sonra uygulayın.

## Dağıtım sırası

1. Yeni release'e Python 3.12 sanal ortamı ve requirements kurulumu yapın.
2. Üretim ortamını yükleyip `python manage.py check --deploy` çalıştırın.
3. Mevcut sürümün yedeğini alın. Ayrı provada migration'ı deneyin.
4. Bakım penceresinde `migrate --noinput`, `sync_library_roles` ve
   `collectstatic --noinput` çalıştırın. Üretimde demo seed çalıştırmayın.
5. `deploy/library.service`, `library-media.service` ve `library-media.timer`
   dosyalarını hedef yollarla systemd'ye kurun.
6. Gerçek alan adı ve sertifikayla `deploy/nginx.conf` içeriğini Nginx http
   kapsamına dahil edin. `nginx -t` ile doğrulayın. Gunicorn yalnız Unix socket
   üzerinden erişilir. Proxy gelen X-Forwarded-Proto değerini kendisi yazar.
7. Servis ve timer'ı başlatıp HTTPS üzerinden sağlık rotalarını ve kapakları deneyin.
8. Gerçek TLS doğrulandıktan sonra HSTS'yi önce kısa süreyle açın.
   Tüm alt alanlar hazır olmadan preload/alt alan seçeneğini açmayın.

Başlangıç üretim profilinde HSTS sıfırdır; Django W004 uyarısı beklenir.
TLS'i doğrulanmış, tüm alt alanları uygun bir test profili için
`HSTS_SECONDS=31536000 HSTS_INCLUDE_SUBDOMAINS=true HSTS_PRELOAD=true`
değerleriyle `check --deploy --fail-level WARNING` kullanılabilir.

## Sağlık ve günlükler

- `/health/live/` süreç yanıtını ölçer.
- `/health/ready/` DB bağlantısı ve gerekli tabloları, medya yazma/okuma
  işlemini ve statik CSS dosyasının bulunmasını kontrol eder. Sorunda 503 döner.
  Yanıtta yol, hata ayrıntısı veya sır bulunmaz; cache no-store kullanılır.
- Probe SMTP/Gemini çağrısı yapmaz. Dış sağlayıcı teslimi ayrı test edilir.
- JSON günlükleri seviye, logger, hata türü, kod konumu ve eşleşen rota içerir.
  Serbest hata mesajı, HTTP body/query ve kimlik doğrulama bilgileri yazılmaz.
- `cover_publish_retry_required` olayını ve media worker başarısızlığını izleyin.
  Kalıcı kuyruk artışı disk/izin sorununun araştırılmasını gerektirir.

## İsteğe bağlı Gemini canlı doğrulaması

```bash
# Güvenli varsayılan; API anahtarı yoksa SKIPPED:
python manage.py smoke_gemini
# Açıkça gerçek çağrı izni; sır ortamda, kullanıcı gerçek ve etkin olmalı:
python manage.py smoke_gemini --live --user-id 123 --query bilim
```

Anahtar tek başına çağrı izni sayılmaz. Komut --live olmadan çağrı yapmaz.
Canlı deneme normal kotaları tüketir ve ücret doğurabilir. Katalogda aramayla
eşleşen aday olmalı; sağlayıcının döndürdüğü en az bir geçerli katalog kimliği
kabul edilmeden LIVE VERIFIED sonucu yazılmaz. Kişisel bilgi kullanmayın.
Taklit yanıt testleri ve SKIPPED çıktısı canlı API başarısı değildir.
