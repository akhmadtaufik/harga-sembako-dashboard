# 📄 Product Requirements Document (PRD)

## 1. Define the Problem

Data harga pangan harian dari API Bank Indonesia memiliki struktur yang kompleks (JSON bersarang) dan sering kali mencampuradukkan tingkat granularitas data (nasional, provinsi, hingga level pasar). Meskipun data mentah tersedia, analis, pengambil kebijakan, maupun masyarakat kesulitan untuk melihat tren historis jangka panjang, membandingkan margin harga antar jenis pasar, atau mendeteksi anomali lonjakan harga secara *real-time*. Dibutuhkan sebuah *dashboard* analitik terpusat yang menyajikan metrik harga sembako secara visual, cepat, dan berbasis geospasial.

## 2. Set Success Metrics

Keberhasilan proyek ini akan diukur melalui metrik teknis dan bisnis berikut:

* **Performa API (Latency):** Waktu respons *endpoint* analitik (P95) berada di bawah 200ms pada beban puncak, berkat pemanfaatan *caching* Redis.
* **Reliabilitas Sistem:** *Uptime dashboard* 99.9%, dengan *zero downtime* saat proses ETL harian berjalan di latar belakang.
* **Akurasi Data:** 100% kesesuaian antara angka agregasi di *dashboard* dengan data mentah tingkat pasar (Level 3) dari Bank Indonesia.
* **Adopsi Fitur:** Peningkatan penggunaan filter geospasial dan deteksi anomali harga oleh pengguna aktif.

## 3. List Core Features

* **Geospatial Price Disparity Map:** Peta interaktif (*Choropleth/Heatmap*) yang menunjukkan perbandingan harga rata-rata komoditas antar kabupaten terhadap rata-rata nasional.
* **Time-Series Price Trend:** Grafik garis historis interaktif yang dapat difilter berdasarkan rentang waktu, provinsi, dan komoditas.
* **Price Anomaly Detection:** Peringatan dini (*early warning*) berupa daftar "Top 5" komoditas yang mengalami lonjakan harga ekstrem di atas rata-rata pergerakan (*Moving Average*) 7 hari terakhir.
* **Market Type Spread:** Visualisasi margin harga antara Produsen, Pedagang Besar, Pasar Tradisional, dan Pasar Modern.
* **Master Data Management:** *Dropdown* interaktif untuk filter dimensi wilayah (Provinsi/Kabupaten) dan komoditas (Grup/Spesifik) yang tersinkronisasi.

## 4. Identify Stakeholders

* **Data Engineer / Backend Developer:** Bertanggung jawab atas stabilitas *pipeline* ETL (Luigi/Cron) dan performa integrasi API.
* **Frontend Developer:** Bertanggung jawab mengonversi *endpoint* analitik menjadi visualisasi data UI/UX di Vue.js.
* **Data Analyst / Economist:** Pengguna utama *dashboard* untuk memantau pergerakan inflasi pangan.
* **Pemerintah / Pengambil Kebijakan:** Menggunakan wawasan anomali harga untuk operasi pasar atau intervensi rantai pasok.

---