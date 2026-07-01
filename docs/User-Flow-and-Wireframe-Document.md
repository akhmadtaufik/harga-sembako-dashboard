# 🗺️ User Flow & Wireframe Document

## 1. Sketch User Journey (Alur Pengguna)

Alur ini memetakan perjalanan pengguna sejak pertama kali membuka aplikasi hingga menemukan *insight* analitik.

* **Langkah 1: Entry Point (Global Overview)**
* Pengguna *login* dan diarahkan ke **Main Dashboard**.
* Sistem memuat *Global Filter* (Tahun, Provinsi Default) dari `dim_provinces` dan merender widget "Top 5 Price Anomalies".


* **Langkah 2: Macro Analysis (Geospatial Discovery)**
* Pengguna melihat *Choropleth Map*. Jika ada area berwarna merah pekat (Disparitas Tinggi), pengguna mengklik area (Provinsi/Kabupaten) tersebut.
* Peta melakukan *zoom-in*, memuat data *Geospatial Prices* dari `dim_markets` untuk menampilkan titik-titik pasar yang mengalami lonjakan.


* **Langkah 3: Micro Investigation (Trend & Spread)**
* Pengguna memilih satu komoditas spesifik (misal: Cabai Rawit) dari *dropdown*.
* Sistem merender *Line Chart* (Seasonality) dan *Multi-series Chart* (Market Type Spread) untuk melihat apakah lonjakan terjadi di rantai Produsen atau murni fluktuasi Pasar Tradisional.


* **Langkah 4: Correlation & Action**
* Pengguna melihat *Correlation Heatmap* untuk mengecek apakah komoditas substitusi juga naik.
* Pengguna mengunduh grafik atau tabel (*Export to CSV/PDF*) untuk bahan laporan kebijakan.



---

## 2. Identify Edge Cases (Skenario Pinggiran)

Mengingat sifat data ETL harian yang bergantung pada API eksternal, desain antarmuka harus siap menangani kondisi ketidaksempurnaan data:

* **API BI Kosong (Akhir Pekan/Hari Libur):** Karena pasar sering tidak melaporkan data di akhir pekan, grafik tren *time-series* mungkin memiliki *gap* (tanggal bolong).
* *UX Handling:* *Chart library* (seperti ECharts) harus dikonfigurasi dengan properti `connectNulls: true` agar garis grafik tidak terputus, atau berikan penanda abu-abu (arsir) pada area akhir pekan menggunakan data `is_weekend` dari tabel `dim_dates`.


* **Titik Koordinat Pasar Tidak Ditemukan:** Beberapa pasar mungkin menggunakan koordinat *fallback* (titik tengah kabupaten).
* *UX Handling:* Pada *tooltip* peta, tambahkan *badge* peringatan kecil (misal: ⚠️ *Estimated Location*) jika titik tersebut adalah *fallback* kabupaten, bukan lokasi pasar eksak.


* **Long-Running Aggregation Queries:** Meskipun ada Redis, saat pengguna mengubah filter tahun ke rentang yang sangat lebar (misal 5 tahun ke belakang), kueri PostgreSQL mungkin memakan waktu >1 detik.
* *UX Handling:* Jangan membekukan layar (*UI Freeze*). Gunakan *Skeleton Loader* pada komponen *chart* yang terdampak saja, biarkan komponen lain tetap interaktif.


* **Data Kosong untuk Filter Kombinasi:** Pengguna memilih komoditas spesifik di provinsi tertentu yang ternyata tidak memperdagangkan komoditas tersebut di tanggal terpilih.
* *UX Handling:* Tampilkan *Empty State Illustration* ("Data tidak tersedia untuk kombinasi ini") alih-alih grafik kosong atau pesan *error* teknis.



---

## 3. Low-Fi Wireframes (Struktur Layout)

Tata letak (*layout*) dirancang responsif menggunakan konsep *Grid System* (misal dengan Tailwind CSS).

### Screen 1: Main Dashboard (Macro View)

```text
+-----------------------------------------------------------------------+
|  [Logo] Sembako Analytics     [Search Market/Commodity...]   [User]   |
+--------+--------------------------------------------------------------+
|        | GLOBAL FILTERS: [Date Picker] [Province Dropdown]            |
| SIDE   +--------------------------------------------------------------+
| BAR    | +-------------------+ +------------------------------------+ |
|        | | 🚨 ANOMALIES      | | 🗺️ GEOSPATIAL DISPARITY MAP      | |
| - Home | | 1. Cabai (▲35%)   | |                                    | |
| - Trend| | 2. Bawang (▲12%)  | |    [ Map rendering dots /        | |
| - Map  | | 3. Daging (▲5%)   | |      chloropleth based on        | |
| - Corr.| |                   | |      avg_price vs national_avg]  | |
|        | +-------------------+ +------------------------------------+ |
|        | +----------------------------------------------------------+ |
|        | | 📈 SEASONALITY TREND (Yearly)                            | |
|        | | [ Line Chart showing aggregated prices by month ]        | |
|        | +----------------------------------------------------------+ |
+--------+--------------------------------------------------------------+

```

### Screen 2: Commodity Deep-Dive (Micro View)

```text
+-----------------------------------------------------------------------+
|  [ < Back to Home ]   Detail Komoditas: [Dropdown: Cabai Rawit Merah] |
+--------+--------------------------------------------------------------+
|        | LOCAL FILTERS: [Date Range] [Regency Dropdown]               |
| SIDE   +--------------------------------------------------------------+
| BAR    | +----------------------------------------------------------+ |
|        | | 📊 MARKET TYPE SPREAD (Integrasi Pasar)                  | |
| - Home | | [ Multi-line chart: Tradisional vs Modern vs Produsen]   | |
| - Trend| |                                                          | |
| - Map  | +----------------------------------------------------------+ |
| - Corr.| +-------------------------+ +------------------------------+ |
|        | | 🔗 CORRELATION MATRIX   | | 📋 REGIONAL AVERAGE TABLE    | |
|        | | [ Heatmap chart ]       | | Reg | Price | Disparity    | |
|        | |                         | | SBY | 95k   | +18%         | |
|        | |                         | | MLG | 70k   | -12%         | |
|        | +-------------------------+ +------------------------------+ |
+--------+--------------------------------------------------------------+

```

---

## 4. Document Interaction Patterns (Pola Interaksi)

Konsistensi interaksi (*behavior*) di Vue.js sangat penting untuk menjaga pengguna tetap fokus pada analisis data.

### A. Pola Manajemen State (Pinia)

* **Global vs Local State:** Data *dropdown* (Provinsi, Komoditas) dimuat satu kali saat *app mounting* dan disimpan di Pinia (*Global State*). Namun, data seperti *Date Range* atau *Selected Commodity* untuk analisis spesifik harus dikelola di komponen lokal atau dibagikan antar komponen melalui *URL Query Parameters* (misal: `/dashboard?commodity=15&date=20260420`). Ini memungkinkan analis membagikan *link URL* hasil temuannya ke rekan kerja dengan posisi filter yang sama persis.

### B. Pola Interaksi Chart (ECharts / Chart.js)

* **Hover Tooltips:** Saat pengguna mengarahkan kursor (*hover*) ke titik di *Line Chart*, *tooltip* tidak hanya menampilkan harga, tetapi juga metadata relevan (nama hari, apakah itu *weekend*, nama pasar).
* **Data Zoom & Brush:** Pada grafik *Time-Series* (Seasonality/Spread), sediakan fitur *Data Zoom* (slider di bawah grafik) agar pengguna dapat memperbesar rentang waktu tertentu tanpa harus mengubah konfigurasi *Global Date Picker*.

### C. Pola Pemuatan Data (Loading Mechanisms)

* **Graceful Degradation:** Ketika *dashboard* dimuat, jangan berikan layar putih dengan satu *spinner* raksasa di tengah. Muat struktur halaman (*sidebar, navbar, grid container*) secara instan, lalu gunakan *Pulse Skeleton Loader* pada setiap kotak grafik (widget) yang sedang menunggu respons dari API FastAPI. Ini memberikan impresi performa sistem yang sangat cepat (*perceived performance*).

### D. Pola Penanganan Error (Error Handling)

* **Toast Notifications (Non-blocking):** Jika terjadi `500 Internal Server Error` (misalnya karena kueri gagal) atau `429 Too Many Requests`, munculkan *Toast Notification* kecil di sudut kanan atas (menggunakan library seperti `vue-toastification`). Jangan merusak tampilan grafik, cukup biarkan grafik dalam *Empty State* dengan tombol "Coba Lagi" (*Retry Button*) di tengah kontainer grafik tersebut.