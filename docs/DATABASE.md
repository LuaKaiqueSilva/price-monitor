# Database

Price Monitor stores its data in a local SQLite database at `data/price_monitor.db`, relative to the directory from which the app is started. The `data/` directory is created automatically and local database files are excluded from Git.

The schema is initialized when the application opens a connection. Both tables are created with `IF NOT EXISTS`, so opening an existing database preserves its records.

## Tables

### `products`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | integer | Primary key, generated automatically |
| `name` | text | Product title from the store page |
| `url` | text | Product URL; unique to prevent duplicate tracking |
| `current_price` | text | Decimal amount stored as text to preserve precision |
| `currency` | text | Currency code, currently `BRL` |
| `store` | text | Store display name |
| `created_at` | text | ISO-formatted local date and time |
| `last_updated` | text | ISO-formatted local date and time, nullable |

### `price_history`

| Column | Type | Notes |
| --- | --- | --- |
| `id` | integer | Primary key, generated automatically |
| `product_id` | integer | References `products.id` |
| `price` | text | Decimal amount stored as text |
| `recorded_at` | text | ISO-formatted local date and time |

Foreign-key enforcement is enabled for each connection. Removing a product cascades to its history records. A record is created when a product is registered and whenever its price changes.
