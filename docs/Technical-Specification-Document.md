# 🛠️ Technical Specification Document

## 1. Choose Tech Stack

* **Database / Data Warehouse:** PostgreSQL 15 (menyimpan *Star Schema*).
* **Backend (API Layer):** Python 3.12, FastAPI (Asynchronous), SQLAlchemy (ORM/Asyncpg), Pydantic (Skema Validasi).
* **Caching Layer:** Redis (In-memory data store) dipadukan dengan library `fastapi-cache2` untuk menyimpan hasil kueri analitik berat.
* **Frontend (UI/UX Layer):** Vue.js 3 (Composition API), Pinia (State Management), TailwindCSS (Styling), ECharts atau Leaflet.js (Visualisasi Peta & Bagan).
* **Orchestration / Infrastructure:** Docker & Docker Compose untuk orkestrasi *container*, Nginx (Opsional, sebagai *Reverse Proxy* frontend).

## 2. Define API Contract

API dirancang menggunakan arsitektur RESTful dengan pemisahan tegas antara data dimensi (ringan) dan data analitik (berat):

* **Dimensi (Metadata):**
* `GET /api/v1/locations/provinces`
* `GET /api/v1/locations/regencies?province_id={id}`
* `GET /api/v1/commodities/groups`
* `GET /api/v1/markets`


* **Analitik (Terintegrasi dengan Redis Cache):**
* `GET /api/v1/analytics/seasonality?group_id={id}&year={yyyy}`
* `GET /api/v1/analytics/disparity?date_id={id}&commodity_id={id}`
* `GET /api/v1/analytics/anomalies?date_id={id}`
* `GET /api/v1/analytics/spread/market-types?start_date={id}&end_date={id}`



*(Semua response menggunakan standar Pydantic Schema dengan root key `{"success": true, "data": [...]}`).*

## 3. Map System Architecture

Sistem beroperasi dalam arsitektur layanan mikro terbungkus Docker Compose:

1. **Ingestion & ETL (Cron):** Skrip *Python/Luigi* menarik data dari API BI, mentransformasi, dan memuatnya secara *batch* ke PostgreSQL (Idempoten via *UPSERT*).
2. **Request Flow:** Vue.js meminta data analitik -> FastAPI menerima *request*.
3. **Cache Interception:** FastAPI memeriksa Redis. Jika ada *cache* (Hit), langsung dikembalikan (<50ms). Jika tidak ada (Miss), lanjut ke DB.
4. **Database Execution:** FastAPI (melalui `asyncpg`) mengeksekusi kueri agregasi SQL kompleks ke PostgreSQL.
5. **Response & Cache Set:** Hasil diagregasi dikembalikan ke Vue.js, sekaligus disimpan di Redis dengan TTL (misalnya 12 jam) hingga jadwal ETL berikutnya selesai.

## 4. Plan Data Models

Data model memanfaatkan desain *Star Schema* yang telah ada di dalam *Data Warehouse* untuk menekan latensi *join* analitik:

* **Fact Table:**
* `fact_daily_prices`: Menyimpan transaksi (date_id, market_id, commodity_id, price).


* **Dimension Tables:**
* `dim_dates`: Untuk agregasi berdasarkan tahun, bulan, nama hari, dan *weekend*.
* `dim_provinces` & `dim_regencies`: Menyimpan nama wilayah serta koordinat (`latitude`, `longitude`) untuk *rendering* peta geospasial.
* `dim_markets` & `dim_market_types`: Mengkategorikan pasar (Tradisional, Modern, Produsen) beserta titik koordinat pasar spesifik.
* `dim_commodities` & `dim_commodity_groups`: Mengelompokkan jenis sembako untuk filter komparasi.
