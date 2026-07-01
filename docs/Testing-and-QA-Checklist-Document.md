# 🧪 Testing and QA Checklist Document

## 1. Define Test Scenarios (Skenario Pengujian)

Skenario pengujian dibagi menjadi tiga lapisan utama: Data/Backend, Frontend/UI, dan Integrasi.

### A. Backend & Data Warehouse Testing (API Layer)

* **[ ] Akurasi Kalkulasi Agregasi:** Membandingkan *output* dari endpoint `/analytics/seasonality` dan `/analytics/disparity` dengan hasil kueri manual (*raw SQL*) di basis data untuk memastikan tidak ada kesalahan fungsi *Group By* atau *Window Function*.
* **[ ] Penanganan Data Kosong (Edge Case Hari Libur):** Menembak API pada rentang tanggal di mana skrip ETL menghasilkan `_SUCCESS` tanpa data (karena akhir pekan/hari libur). Memastikan API mengembalikan kode `200 OK` dengan *array* kosong `[]`, bukan `500 Internal Server Error`.
* **[ ] Caching Mechanism:** Mengirimkan *request* identik dua kali berturut-turut ke endpoint analitik berat. Memastikan latensi *request* kedua turun drastis (< 50ms) karena intersep dari Redis.
* **[ ] Fallback Koordinat Geospasial:** Memverifikasi endpoint `/analytics/geospatial-prices` mengembalikan koordinat titik tengah kabupaten jika suatu pasar belum sempat di-*geocode* oleh skrip Nominatim otomatis.

### B. Frontend & UI Testing (Vue.js Layer)

* **[ ] Sinkronisasi Global State (Pinia):** Memastikan saat pengguna mengganti filter "Tahun" atau "Provinsi" di navigasi utama, seluruh *widget* (Peta, *Line Chart*, Tabel) otomatis memicu proses *re-fetch* atau *re-render*.
* **[ ] Rendering Peta (Choropleth/Heatmap):** Memastikan *library* peta (seperti ECharts/Leaflet) berhasil memetakan GeoJSON Indonesia dan mewarnai area berdasarkan nilai `disparity_percentage`.
* **[ ] State Loading & Skeleton:** Memastikan saat data analitik sedang ditarik, komponen UI menampilkan *Skeleton Loader* dan layar tidak mengalami *freeze* (*Non-blocking UI*).
* **[ ] Penanganan Error (Graceful Degradation):** Mematikan koneksi internet (*offline mode*) atau mematikan *container* FastAPI. Memastikan Vue.js menampilkan *Toast Notification* (misal: "Gagal terhubung ke server") dan menampilkan *Empty State* pada *chart*, bukan layar putih kosong.

---

## 2. Plan Device Testing (Perencanaan Perangkat)

Meskipun *dashboard* analitik berfokus pada pengguna desktop (analis data), responsivitas pada perangkat portabel tetap krusial bagi pengambil kebijakan yang sedang berada di lapangan.

* **Tier 1: Desktop (Prioritas Utama - Resolusi > 1024px)**
* **Browser:** Google Chrome (versi terbaru), Mozilla Firefox, Apple Safari.
* **Fokus Uji:** Performa *rendering* kanvas grafik (WebGL/SVG) saat memuat ratusan titik *scatter/line chart*, interaksi *hover tooltip*, dan *Data Zoom slider*.


* **Tier 2: Tablet (Prioritas Menengah - Resolusi 768px - 1024px)**
* **Perangkat:** iPad (Safari), Tablet Android (Chrome).
* **Fokus Uji:** Fungsionalitas sentuhan (*touch*). Memastikan pengguna bisa melakukan *pinch-to-zoom* pada peta dan mengetuk (*tap*) titik grafik untuk memunculkan *tooltip*.


* **Tier 3: Mobile (Prioritas Rendah - Resolusi < 768px)**
* **Perangkat:** Berbagai ukuran *smartphone* iOS & Android.
* **Fokus Uji:** Penumpukan *layout* (*stacking*). Memastikan *sidebar* berubah menjadi *hamburger menu* dan kontainer grafik tidak terpotong (*overflow*).



---

## 3. Set Acceptance Criteria (Kriteria Penerimaan)

Sebuah fitur atau modul hanya dapat dianggap "Selesai" (Definisi *Done*) jika memenuhi seluruh kriteria berikut:

* **AC1 (Kinerja API):** Waktu respons seluruh endpoint kategori `/analytics` di bawah 2 detik untuk kueri awal (tanpa *cache*) dan di bawah 100ms untuk kueri dengan *cache* Redis.
* **AC2 (Integritas Data):** Tidak ada duplikasi baris data atau anomali harga pada grafik akibat *join* yang salah (*cartesian product*) antara tabel fakta dan dimensi.
* **AC3 (Visualisasi):** *Tooltip* pada grafik ECharts/Chart.js tidak terpotong layar, format mata uang menggunakan standar Rupiah (Rp XX.XXX), dan persentase menggunakan format desimal yang konsisten (misal: +12.5%).
* **AC4 (Keamanan):** Endpoint tidak dapat diakses tanpa menyertakan API Key / Token JWT yang valid (Sistem harus merespons dengan `401 Unauthorized`).
* **AC5 (Kualitas Kode):** Tidak ada *console error* atau *warning* Vue di mode produksi, dan seluruh *type hinting* Pydantic di FastAPI telah sesuai dengan skema kembalian SQL.

---

## 4. Document Bug Reporting (Standar Pelaporan Bug)

Untuk menjaga manajemen proyek tetap rapi, semua temuan *bug* selama fase pengujian (UAT/QA) harus didokumentasikan menggunakan format standar berikut pada platform *issue tracker* (seperti Jira, GitHub Issues, atau Trello).

**Format Standar Tiket Bug:**

* **[Title]:** [Modul] Ringkasan singkat masalah (Contoh: `[Geospatial Map] Peta Jawa Timur gagal di-render jika data pasar kosong`)
* **Environment:**
* OS & Browser: (Contoh: macOS Sonoma, Chrome v120)
* Device: (Contoh: Desktop 1080p)


* **Severity / Prioritas:** (Blocker / High / Medium / Low)
* **Steps to Reproduce (Langkah Reproduksi):**
1. Buka halaman Utama Dashboard.
2. Ubah *Global Filter* Provinsi ke "Jawa Timur".
3. Ubah Tanggal ke "1 Januari 2026" (Tanggal Libur).


* **Expected Result (Hasil yang Diharapkan):**
Peta tetap muncul dengan warna netral (abu-abu) atau memunculkan peringatan "Data tidak tersedia untuk tanggal ini".
* **Actual Result (Hasil Aktual):**
Peta menghilang, layar *freeze*, dan muncul *error TypeError: Cannot read properties of undefined* di konsol *browser*.
* **Attachments:** (Wajib menyertakan *Screenshot* halaman atau potongan *Response JSON* dari tab Network Inspector).