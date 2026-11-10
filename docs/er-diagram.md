
## Görsel ER Diyagramı

![Kütüphane Yönetim Sistemi ER Diyagramı](er-diagram.png)

*Görsel, sistemin temel varlıklarını ve ilişkilerini özetler. Ayrıntılı teknik veri modeli aşağıdadır.*

# Uygulamanın veri modeli

```mermaid
erDiagram
    USER }o--o{ GROUP : membership
    GROUP }o--o{ PERMISSION : grants
    USER }o--o{ PERMISSION : direct_grants
    BOOK }o--o{ AUTHOR : authors
    BOOK }o--o{ CATEGORY : categories
    BOOK ||--o{ BOOK_COPY : copies
    USER ||--o{ LOAN : borrows
    BOOK_COPY ||--o{ LOAN : history
    LOAN ||--o| FINE : final_charge
    USER o|--o{ FINE : records_payment
    USER ||--o{ CHECKOUT_REQUEST : asks
    BOOK ||--o{ CHECKOUT_REQUEST : requested_title
    LOAN o|--o| CHECKOUT_REQUEST : fulfilled_by
    BOOK_COPY {
        bigint id PK
        bigint book_id FK
        string inventory_code UK
        string shelf_location
        string status
    }
    LOAN {
        bigint id PK
        bigint copy_id FK
        bigint member_id FK
        datetime issued_at
        date due_date
        datetime returned_at
        int renewal_count
        decimal daily_rate
        decimal fine_cap
    }
    FINE {
        bigint loan_id FK
        decimal amount
        datetime paid_at
        bigint paid_by_id FK
    }
    COVER_OPERATION {
        bigint id PK
        string name
        string kind
        binary content
        datetime created_at
    }
    MEDIA_LOCK {
        bigint id PK
        bigint version
    }
    USAGE_WINDOW {
        string scope PK
        string window
        int used
    }
```

`UsageWindow` üye/dakika, üye/gün ve uygulama/gün sayaçlarını tutar. Katalog kitabı ile model önerisi arasında kalıcı ilişki kurulmaz. Diyagram uygulamanın alan ilişkilerini gösterir; Django'nun oturum ve admin günlük tabloları ayrıca standart migration'larla oluşturulur.

Kapak işlem kuyruğunun `name` alanı dosya adını taşır. İlişki Book.cover değeri üzerinden uygulamada yönetilir. MediaLock yayın, silme ve yedekleme sırasında ortak kilit sağlar.
