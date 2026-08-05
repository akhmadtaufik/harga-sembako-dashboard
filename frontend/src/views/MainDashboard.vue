<template>
  <DashboardLayout>
    <div class="main-dashboard bg-slate-900 text-slate-50 p-4 md:p-8 lg:p-10 font-sans max-w-[1600px] mx-auto space-y-8">
      
      <!-- Section 1: Top-Level Macro Overview & Dynamic KPI Summary Cards -->
      <section>
        <div class="flex items-center justify-between border-b border-slate-800 pb-3 mb-5">
          <div>
            <div class="flex items-center gap-2 group relative z-50 w-max">
              <h2 class="text-xs font-bold tracking-[0.15em] text-slate-400 uppercase flex items-center gap-2">
                <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                Macro Overview & Executive Indicators
              </h2>
              
              <!-- Info Icon SVG -->
              <svg class="w-4 h-4 text-slate-500 hover:text-slate-300 cursor-help transition-colors shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              
              <!-- Tooltip Box -->
              <div class="absolute left-0 top-full mt-2 w-72 p-3 bg-slate-900 border border-slate-700 rounded-md shadow-xl text-xs text-slate-300 z-[100] opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 pointer-events-none font-normal normal-case leading-relaxed">
                Ringkasan metrik eksekutif yang menampilkan rata-rata harga nasional serta wilayah dengan harga tertinggi (Peak) dan terendah (Floor). Berguna untuk pemantauan stabilitas pasar level makro secara instan.
              </div>
            </div>
            <p class="text-xs text-slate-500 mt-0.5">Real-time aggregate metric intelligence across monitored regencies</p>
          </div>
          <span class="text-[10px] text-emerald-400 font-mono font-medium bg-emerald-950/60 px-2.5 py-1 rounded-md border border-emerald-900/60 shadow-sm hidden sm:inline-block">
            Live Stream Active
          </span>
        </div>

        <!-- Skeleton Loader for KPI Grid -->
        <div v-if="loadingMap" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div v-for="i in 4" :key="i" class="animate-pulse bg-slate-800/40 backdrop-blur-md border border-slate-700/50 rounded-xl p-5 h-32 flex flex-col justify-between">
            <div class="h-4 bg-slate-700/50 rounded w-2/3"></div>
            <div class="h-8 bg-slate-700/50 rounded w-1/2"></div>
            <div class="h-3 bg-slate-700/50 rounded w-4/5"></div>
          </div>
        </div>

        <!-- KPI Cards Grid -->
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
          
          <!-- Card 1: National Average Price -->
          <div class="bg-slate-800/40 backdrop-blur-md border border-slate-700/60 rounded-xl p-5 flex flex-col justify-between hover:border-emerald-500/50 hover:bg-slate-800/60 transition-all duration-300 shadow-xl group">
            <div class="flex justify-between items-start">
              <div class="flex items-center gap-2">
                <div class="p-1.5 rounded-lg bg-emerald-950/60 border border-emerald-800/60 text-emerald-400 group-hover:scale-105 transition-transform">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                </div>
                <span class="text-xs font-bold uppercase tracking-wider text-slate-400">National Average</span>
              </div>
              <span class="text-[10px] text-emerald-400 font-mono font-medium bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-900/60">
                Baseline
              </span>
            </div>
            <div class="mt-4">
              <div class="text-2xl font-extrabold tracking-tight text-slate-100 font-mono">
                {{ formatCurrency(kpiStats.nationalAvg) }}
              </div>
              <p class="text-[11px] text-slate-400 mt-1 flex items-center gap-1">
                <span>Aggregated benchmark across network</span>
              </p>
            </div>
          </div>

          <!-- Card 2: Highest Priced Region -->
          <div class="bg-slate-800/40 backdrop-blur-md border border-slate-700/60 rounded-xl p-5 flex flex-col justify-between hover:border-red-500/50 hover:bg-slate-800/60 transition-all duration-300 shadow-xl group">
            <div class="flex justify-between items-start">
              <div class="flex items-center gap-2">
                <div class="p-1.5 rounded-lg bg-red-950/60 border border-red-800/60 text-red-400 group-hover:scale-105 transition-transform">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                  </svg>
                </div>
                <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Highest Regional Price</span>
              </div>
              <span class="text-[10px] text-red-400 font-mono font-medium bg-red-950/60 px-2 py-0.5 rounded border border-red-900/60">
                Peak
              </span>
            </div>
            <div class="mt-4">
              <div class="text-2xl font-extrabold tracking-tight text-red-300 font-mono">
                {{ kpiStats.highest ? formatCurrency(kpiStats.highest.average) : '-' }}
              </div>
              <p class="text-xs font-semibold text-slate-300 truncate mt-1" :title="kpiStats.highest ? kpiStats.highest.name : ''">
                {{ kpiStats.highest ? kpiStats.highest.name : 'N/A' }}
              </p>
            </div>
          </div>

          <!-- Card 3: Lowest Priced Region -->
          <div class="bg-slate-800/40 backdrop-blur-md border border-slate-700/60 rounded-xl p-5 flex flex-col justify-between hover:border-emerald-500/50 hover:bg-slate-800/60 transition-all duration-300 shadow-xl group">
            <div class="flex justify-between items-start">
              <div class="flex items-center gap-2">
                <div class="p-1.5 rounded-lg bg-emerald-950/60 border border-emerald-800/60 text-emerald-400 group-hover:scale-105 transition-transform">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
                  </svg>
                </div>
                <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Lowest Regional Price</span>
              </div>
              <span class="text-[10px] text-emerald-400 font-mono font-medium bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-900/60">
                Floor
              </span>
            </div>
            <div class="mt-4">
              <div class="text-2xl font-extrabold tracking-tight text-emerald-300 font-mono">
                {{ kpiStats.lowest ? formatCurrency(kpiStats.lowest.average) : '-' }}
              </div>
              <p class="text-xs font-semibold text-slate-300 truncate mt-1" :title="kpiStats.lowest ? kpiStats.lowest.name : ''">
                {{ kpiStats.lowest ? kpiStats.lowest.name : 'N/A' }}
              </p>
            </div>
          </div>

          <!-- Card 4: Active Regions Tracked -->
          <div class="bg-slate-800/40 backdrop-blur-md border border-slate-700/60 rounded-xl p-5 flex flex-col justify-between hover:border-blue-500/50 hover:bg-slate-800/60 transition-all duration-300 shadow-xl group">
            <div class="flex justify-between items-start">
              <div class="flex items-center gap-2">
                <div class="p-1.5 rounded-lg bg-blue-950/60 border border-blue-800/60 text-blue-400 group-hover:scale-105 transition-transform">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <span class="text-xs font-bold uppercase tracking-wider text-slate-400">Tracked Markets</span>
              </div>
              <span class="text-[10px] text-blue-400 font-mono font-medium bg-blue-950/60 px-2 py-0.5 rounded border border-blue-900/60">
                Coverage
              </span>
            </div>
            <div class="mt-4">
              <div class="text-2xl font-extrabold tracking-tight text-slate-100 font-mono">
                {{ kpiStats.count }}
              </div>
              <p class="text-[11px] text-slate-400 mt-1">
                Reporting regencies in active matrix
              </p>
            </div>
          </div>
        </div>
      </section>

      <!-- Section 2: Top 5 Price Anomalies Grid -->
      <!-- Section 2: Top 5 Price Anomalies & Volatility Index -->
      <section class="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <!-- Price Anomalies (Half Width) -->
        <div class="lg:col-span-6">
          <div class="flex items-center justify-between border-b border-slate-800 pb-2 mb-4">
            <div class="flex items-center gap-2 group relative z-50 w-max">
              <h2 class="text-xs font-bold tracking-[0.1em] text-slate-400 uppercase">Price Anomalies (Top 5)</h2>
              
              <!-- Info Icon SVG -->
              <svg class="w-4 h-4 text-slate-500 hover:text-slate-300 cursor-help transition-colors shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              
              <!-- Tooltip Box -->
              <div class="absolute left-0 top-full mt-2 w-72 p-3 bg-slate-900 border border-slate-700 rounded-md shadow-xl text-xs text-slate-300 z-[100] opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 pointer-events-none font-normal normal-case leading-relaxed">
                Menyoroti 5 wilayah kabupaten/kota dengan lonjakan (Spike) atau penurunan (Drop) harga paling ekstrem dibandingkan dengan rata-rata pergerakan harga 7 hari terakhir (7D MA). Fitur ini krusial untuk deteksi dini gejolak pasar lokal.
              </div>
            </div>
          </div>
          
          <!-- Skeleton Loader -->
          <div v-if="loadingAnomalies" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="i in 5" :key="i" class="animate-pulse bg-slate-800/40 rounded-lg p-4 h-24 border border-slate-700/50"></div>
          </div>

          <!-- Empty State -->
          <div v-else-if="anomalies.length === 0" class="flex flex-col items-center justify-center h-24 border border-dashed border-slate-700/60 rounded-lg text-slate-500 text-sm bg-slate-800/20">
            <span class="block text-slate-400 font-medium">No Data Available</span>
            <span class="block text-xs mt-0.5 text-slate-500">Data Unavailable for Selected Date Matrix</span>
          </div>

          <!-- Data Grid -->
          <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <div v-for="item in anomalies" :key="item.id" class="bg-slate-800/40 backdrop-blur-md rounded-lg p-4 border border-slate-700/50 flex flex-col justify-between hover:bg-slate-800/70 hover:border-slate-600 transition-all shadow-md">
              <span class="text-xs font-semibold tracking-wide text-slate-300 truncate" :title="item.name">{{ item.name }}</span>
              <div class="flex items-end justify-between mt-3">
                <span class="text-lg font-bold tracking-tight text-slate-100 font-mono">{{ formatCurrency(item.price) }}</span>
                <span :class="item.trend > 0 ? 'text-red-400 bg-red-950/60 border-red-800/50' : 'text-emerald-400 bg-emerald-950/60 border-emerald-800/50'" class="text-[11px] font-mono font-semibold tracking-tighter px-1.5 py-0.5 rounded border">
                  {{ item.trend > 0 ? '+' : '' }}{{ item.trend }}%
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Volatility Index (Half Width) -->
        <div class="lg:col-span-6">
          <div class="flex items-center justify-between border-b border-slate-800 pb-2 mb-4">
            <div class="flex items-center gap-2 group relative z-50 w-max">
              <h2 class="text-xs font-bold tracking-[0.1em] text-slate-400 uppercase">Volatility Index (30D)</h2>
              
              <!-- Info Icon SVG -->
              <svg class="w-4 h-4 text-slate-500 hover:text-slate-300 cursor-help transition-colors shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              
              <!-- Tooltip Box -->
              <div class="absolute left-0 top-full mt-2 w-72 p-3 bg-slate-900 border border-slate-700 rounded-md shadow-xl text-xs text-slate-300 z-[100] opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 pointer-events-none font-normal normal-case leading-relaxed">
                Mengukur tingkat fluktuasi harga komoditas secara nasional dalam 30 hari terakhir menggunakan Koefisien Variasi. Semakin tinggi persentase, semakin rentan rantai pasok komoditas tersebut terhadap gejolak pasar.
              </div>
            </div>
          </div>

          <div v-if="loadingVolatility" class="space-y-3">
             <div v-for="i in 5" :key="i" class="animate-pulse bg-slate-800/40 rounded-lg h-[46px] border border-slate-700/50"></div>
          </div>
          
          <div v-else-if="volatilityData.length === 0" class="flex flex-col items-center justify-center h-24 border border-dashed border-slate-700/60 rounded-lg text-slate-500 text-sm bg-slate-800/20">
            <span class="block text-slate-400 font-medium">No Data Available</span>
          </div>

          <div v-else class="space-y-3">
            <div v-for="item in volatilityData.slice(0,5)" :key="item.commodity_name" class="relative bg-slate-800/40 backdrop-blur-md rounded-lg p-3 border border-slate-700/50 hover:bg-slate-800/70 transition-all shadow-md overflow-hidden flex items-center justify-between z-10 group">
              <!-- Progress bar background -->
              <div class="absolute inset-y-0 left-0 bg-red-900/30 group-hover:bg-red-800/40 transition-all -z-10" :style="{ width: ((parseFloat(item.cv_percentage) || 0) / maxVolatilityCV) * 100 + '%' }"></div>
              
              <span class="text-xs font-semibold tracking-wide text-slate-300 truncate" :title="item.commodity_name">{{ item.commodity_name }}</span>
              <span class="text-xs font-mono font-bold text-red-400">
                {{ Number(item.cv_percentage).toFixed(2) }}%
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Section 3: Geospatial Disparity Map & Synchronized Regional Breakdown -->
      <section>
        <div class="flex items-center justify-between mb-4 border-b border-slate-800 pb-2">
          <div>
            <div class="flex items-center gap-2 group relative z-50 w-max">
              <h2 class="text-xs font-bold tracking-[0.1em] text-slate-400 uppercase">Geospatial Disparity & Regional Tracking</h2>
              
              <!-- Info Icon SVG -->
              <svg class="w-4 h-4 text-slate-500 hover:text-slate-300 cursor-help transition-colors shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              
              <!-- Tooltip Box -->
              <div class="absolute left-0 top-full mt-2 w-72 p-3 bg-slate-900 border border-slate-700 rounded-md shadow-xl text-xs text-slate-300 z-[100] opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 pointer-events-none font-normal normal-case leading-relaxed">
                Visualisasi geospasial sebaran disparitas harga. Warna kemerahan menunjukkan harga di atas rata-rata nasional (Premium/Spike), sedangkan warna hijau menunjukkan harga di bawah rata-rata (Floor/Drop). Interaksi dengan peta untuk melihat ketimpangan harga spesifik.
              </div>
            </div>
            <p class="text-[11px] text-slate-500 mt-0.5">Hover or click map polygon or regional list item for synchronized cross-highlighting & drill-down</p>
          </div>
          <span class="text-[10px] text-slate-400 font-mono bg-slate-800/60 px-2.5 py-1 rounded-md border border-slate-700/50 hidden sm:inline-block">
            Map ↔ List Synchronized
          </span>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <!-- Main Map Workspace -->
          <div class="lg:col-span-8 bg-slate-800/40 backdrop-blur-md border border-slate-700/60 rounded-xl h-[520px] relative flex flex-col overflow-hidden shadow-2xl">
             <!-- Skeleton Loader -->
             <div v-show="loadingMap" class="absolute inset-0 z-10 animate-pulse bg-slate-800/60 flex items-center justify-center">
               <span class="text-slate-400 font-mono text-xs uppercase tracking-widest">Updating Geospatial Workspace...</span>
             </div>
             <!-- Empty State -->
             <div v-show="!loadingMap && !mapData" class="absolute inset-0 z-10 flex flex-col items-center justify-center bg-slate-800/50 text-slate-500 text-sm">
                <span class="block text-slate-300 font-medium">Map Layer Unavailable</span>
                <span class="block text-xs mt-1 text-slate-500">Data Unavailable for Selected Date Matrix</span>
             </div>
             <!-- Actual GeospatialMap Component -->
             <GeospatialMap 
               ref="geoMap"
               v-show="mapData" 
               :locations="mapData || []" 
               :hoveredRegionId="hoveredRegionId"
               @region-hover="handleMapRegionHover"
               @region-select="handleRegionSelect"
               class="flex-1 w-full h-full" 
             />
          </div>

          <!-- Synchronized Data Table Matrix -->
          <div class="lg:col-span-4 bg-slate-800/40 backdrop-blur-md border border-slate-700/60 rounded-xl h-[520px] flex flex-col overflow-hidden shadow-2xl">
             <div class="p-4 border-b border-slate-700/50 bg-slate-800/80 flex items-center justify-between sticky top-0 z-10">
               <div>
                 <div class="flex items-center gap-2 group relative z-50 w-max">
                   <h3 class="text-xs font-bold uppercase tracking-widest text-slate-200">Regional Breakdown</h3>
                   
                   <!-- Info Icon SVG -->
                   <svg class="w-4 h-4 text-slate-500 hover:text-slate-300 cursor-help transition-colors shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                     <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                   </svg>
                   
                   <!-- Tooltip Box -->
                   <div class="absolute left-0 top-full mt-2 w-72 p-3 bg-slate-900 border border-slate-700 rounded-md shadow-xl text-xs text-slate-300 z-[100] opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 pointer-events-none font-normal normal-case leading-relaxed">
                     Daftar perbandingan harga antar kabupaten/kota yang tersinkronisasi dengan peta. Klik pada baris wilayah untuk memusatkan titik peta dan memunculkan opsi menuju analisis mendalam (Micro Deep-Dive).
                   </div>
                 </div>
                 <p class="text-[10px] text-slate-400">Click row to center map & open drill-down</p>
               </div>
               <span class="text-[10px] text-emerald-400 font-mono bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-900/60 font-semibold">
                 {{ regions.length }} Regencies
               </span>
             </div>
             
             <!-- Skeleton Loader -->
             <div v-if="loadingMap" class="p-4 space-y-3 flex-1">
               <div v-for="i in 7" :key="i" class="animate-pulse bg-slate-700/40 h-9 rounded-md w-full"></div>
             </div>
             
             <!-- Empty State -->
             <div v-else-if="regions.length === 0" class="flex-1 flex flex-col items-center justify-center p-4 text-slate-500 text-sm text-center">
                <span class="block text-slate-400 font-medium">No Breakdown Available</span>
                <span class="block text-xs mt-1 text-slate-500">Data Unavailable for Selected Date Matrix</span>
             </div>
             
             <!-- Data Matrix with Bidirectional Cross-Highlighting -->
             <div v-else class="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-1">
               <div
                 v-for="region in regions" 
                 :key="region.id" 
                 :ref="el => { if (el) regionRefs[region.id] = el }"
                 @mouseenter="hoveredRegionId = region.id" 
                 @mouseleave="hoveredRegionId = null"
                 @click="handleRegionClick(region)"
                 :class="hoveredRegionId === region.id ? 'bg-emerald-950/50 border-l-4 border-emerald-400 text-emerald-100 shadow-md translate-x-1 font-semibold' : 'border-b border-slate-700/30 hover:bg-slate-700/30 text-slate-300'"
                 class="transition-all duration-200 cursor-pointer rounded-r-md px-3 py-2.5 flex items-center justify-between text-xs group"
               >
                 <div class="flex items-center gap-2 truncate pr-2">
                   <span :class="hoveredRegionId === region.id ? 'bg-emerald-400' : 'bg-slate-600 group-hover:bg-slate-400'" class="w-1.5 h-1.5 rounded-full transition-colors shrink-0"></span>
                   <span class="truncate group-hover:text-white transition-colors" :title="region.name">{{ region.name }}</span>
                 </div>
                 
                 <div class="flex items-center gap-2 font-mono shrink-0">
                   <span class="text-xs font-bold" :class="hoveredRegionId === region.id ? 'text-emerald-300' : 'text-slate-200'">
                     {{ formatCurrency(region.average) }}
                   </span>
                   <span :class="hoveredRegionId === region.id ? 'opacity-100 translate-x-0' : 'opacity-0 -translate-x-1'" class="text-emerald-400 transition-all font-sans font-bold">
                     &rarr;
                   </span>
                 </div>
               </div>
             </div>
          </div>
        </div>
      </section>
      
      <!-- Section 4: Tabbed Technical Regional Averages Spreadsheet Matrix -->
      <section>
         <div class="flex items-center justify-between border-b border-slate-800 pb-2 mb-4">
           <div class="flex items-center gap-2 group relative z-50 w-max">
             <h2 class="text-xs font-bold tracking-[0.1em] text-slate-400 uppercase">Regional Averages Matrix (Provincial Aggregates)</h2>
             
             <!-- Info Icon SVG -->
             <svg class="w-4 h-4 text-slate-500 hover:text-slate-300 cursor-help transition-colors shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
               <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
             </svg>
             
             <!-- Tooltip Box -->
             <div class="absolute left-0 top-full mt-2 w-72 p-3 bg-slate-900 border border-slate-700 rounded-md shadow-xl text-xs text-slate-300 z-[100] opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 pointer-events-none font-normal normal-case leading-relaxed">
               Tabel agregasi yang merangkum rata-rata harga komoditas pada tingkat provinsi secara makro. Kolom 'Data Records Count' menunjukkan volume data mentah yang berhasil dihimpun dari API pada tanggal matriks yang dipilih untuk memastikan akurasi sampel.
             </div>
           </div>
         </div>
         <div class="bg-slate-800/40 backdrop-blur-md border border-slate-700/60 rounded-xl flex flex-col overflow-hidden shadow-xl">
           <!-- Skeleton Loader -->
           <div v-if="loadingMatrix" class="p-4 space-y-2">
             <div v-for="i in 4" :key="i" class="animate-pulse bg-slate-700/40 h-10 rounded-md w-full"></div>
           </div>
           <!-- Empty State -->
           <div v-else-if="matrixData.length === 0" class="p-10 flex flex-col items-center justify-center text-slate-500 text-sm">
             <span class="block text-slate-400 font-medium">Matrix Unavailable</span>
             <span class="block text-xs mt-1 text-slate-500">Data Unavailable for Selected Date Matrix</span>
           </div>
           <!-- Spreadsheet view -->
           <div v-else class="overflow-x-auto h-[320px] overflow-y-auto custom-scrollbar">
             <table class="w-full text-sm text-slate-300 whitespace-nowrap">
               <thead class="bg-slate-900/80 text-slate-400 text-xs tracking-wider border-b border-slate-700/60 sticky top-0 backdrop-blur-md z-10">
                 <tr>
                   <th class="py-3 px-5 font-bold text-left">Province Name</th>
                   <th class="py-3 px-5 font-bold text-right">Avg Price (IDR)</th>
                   <th class="py-3 px-5 font-bold text-right">Data Records Count</th>
                 </tr>
               </thead>
               <tbody class="divide-y divide-slate-700/30">
                 <tr v-for="row in matrixData" :key="row.province_id" class="hover:bg-slate-700/30 transition-colors">
                   <td class="py-3 px-5 text-xs font-bold text-slate-200">{{ row.province_name }}</td>
                   <td class="py-3 px-5 text-right font-mono text-xs font-semibold text-emerald-400">{{ formatCurrencySafe(row.average_price) }}</td>
                   <td class="py-3 px-5 text-right font-mono text-xs text-slate-400">{{ row.record_count > 0 ? row.record_count : '-' }}</td>
                 </tr>
               </tbody>
             </table>
           </div>
         </div>
      </section>

      <!-- Section 4: MoM Inflation Heatmap -->
      <section>
        <div class="flex items-center justify-between border-b border-slate-800 pb-2 mb-4">
          <div class="flex items-center gap-2 group relative z-50 w-max">
            <h2 class="text-xs font-bold tracking-[0.1em] text-slate-400 uppercase">MoM Inflation Heatmap</h2>
            
            <svg class="w-4 h-4 text-slate-500 hover:text-slate-300 cursor-help transition-colors shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            
            <div class="absolute left-0 top-full mt-2 w-72 p-3 bg-slate-900 border border-slate-700 rounded-md shadow-xl text-xs text-slate-300 z-[100] opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 pointer-events-none font-normal normal-case leading-relaxed">
              Matriks inflasi Month-over-Month (MoM) yang membandingkan rata-rata harga bulan ini dengan bulan sebelumnya. Warna merah pekat menunjukkan inflasi ekstrem, sedangkan hijau menunjukkan deflasi atau penurunan harga.
            </div>
          </div>
        </div>
        
        <div v-if="loadingHeatmap" class="w-full h-64 animate-pulse bg-slate-800/40 rounded-lg border border-slate-700/50"></div>

        <div v-else-if="heatmapMatrix.commodities.length === 0" class="flex flex-col items-center justify-center h-48 border border-dashed border-slate-700/60 rounded-lg text-slate-500 text-sm bg-slate-800/20">
          <span class="block text-slate-400 font-medium">No Data Available</span>
        </div>

        <div v-else class="w-full overflow-x-auto custom-scrollbar border border-slate-700/60 rounded-lg shadow-xl">
          <table class="w-full text-left border-collapse text-xs">
            <thead>
              <tr class="bg-slate-900 border-b border-slate-700/80">
                <th class="p-3 font-semibold text-slate-300 uppercase tracking-widest bg-slate-900 sticky left-0 z-20 border-r border-slate-700/80 shadow-[2px_0_5px_-2px_rgba(0,0,0,0.5)] min-w-[150px]">
                  Province
                </th>
                <th v-for="c in heatmapMatrix.commodities" :key="c" class="p-3 font-medium text-slate-400 whitespace-nowrap border-r border-slate-800/50 last:border-r-0">
                  {{ c }}
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-800/60 bg-slate-800/30">
              <tr v-for="row in heatmapMatrix.matrix" :key="row.province" class="hover:bg-slate-800/50 transition-colors">
                <td class="p-3 font-medium text-slate-300 whitespace-nowrap bg-slate-900/90 sticky left-0 z-10 border-r border-slate-700/80 shadow-[2px_0_5px_-2px_rgba(0,0,0,0.5)]">
                  {{ row.province }}
                </td>
                <td v-for="c in heatmapMatrix.commodities" :key="c" 
                    :class="[
                      'p-3 font-mono font-medium text-right border-r border-slate-800/50 last:border-r-0',
                      row[c] !== null && row[c] > 5 ? 'bg-red-500/20 text-red-300' :
                      row[c] !== null && row[c] > 0 ? 'bg-red-500/10 text-red-200' :
                      row[c] !== null && row[c] < 0 ? 'bg-emerald-500/20 text-emerald-300' :
                      row[c] !== null && row[c] === 0 ? 'bg-slate-800/50 text-slate-400' :
                      'text-slate-600'
                    ]">
                  {{ row[c] !== null ? (row[c] > 0 ? '+' : '') + Number(row[c]).toFixed(2) + '%' : '-' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
      
    </div>
  </DashboardLayout>
</template>

<script>
import { defineComponent } from 'vue'
import { mapState, mapActions } from 'pinia'
import { useMacroStore } from '../store/macro'
import DashboardLayout from '../components/DashboardLayout.vue'
import GeospatialMap from '../components/GeospatialMap.vue'
import apiClient from '../plugins/axios'

export default defineComponent({
  name: 'MainDashboard',
  components: {
    DashboardLayout,
    GeospatialMap
  },
  data() {
    return {
      loadingAnomalies: true,
      loadingMap: true,
      loadingMatrix: true,
      loadingVolatility: true,
      loadingHeatmap: true,
      anomalies: [],
      regions: [],
      mapData: null,
      matrixData: [],
      volatilityData: [],
      heatmapData: [],
      nationalBaselinePrice: 0,
      hoveredRegionId: null,
      regionRefs: {},
      abortController: null
    }
  },
  computed: {
    ...mapState(useMacroStore, ['province_id', 'date', 'commodity_id']),
    kpiStats() {
      if (!this.regions || this.regions.length === 0) {
        return {
          nationalAvg: 0,
          highest: null,
          lowest: null,
          count: 0
        }
      }
      let highest = this.regions[0]
      let lowest = this.regions[0]
      let sum = 0

      this.regions.forEach(r => {
        const val = parseFloat(r.average) || 0
        sum += val
        if (val > (parseFloat(highest.average) || 0)) highest = r
        if (val < (parseFloat(lowest.average) || Number.MAX_VALUE)) lowest = r
      })

      const nationalAvg = this.nationalBaselinePrice || (this.regions.length ? sum / this.regions.length : 0)

      return {
        nationalAvg,
        highest,
        lowest,
        count: this.regions.length
      }
    },
    maxVolatilityCV() {
      if (!this.volatilityData || this.volatilityData.length === 0) return 1
      return Math.max(...this.volatilityData.map(d => parseFloat(d.cv_percentage) || 0)) || 1
    },
    heatmapMatrix() {
      if (!this.heatmapData || this.heatmapData.length === 0) return { commodities: [], matrix: [] }
      const provinces = [...new Set(this.heatmapData.map(d => d.province_name))].sort()
      const commodities = [...new Set(this.heatmapData.map(d => d.commodity_name))].sort()
      
      const matrix = provinces.map(p => {
        const row = { province: p }
        commodities.forEach(c => {
          const match = this.heatmapData.find(d => d.province_name === p && d.commodity_name === c)
          row[c] = match ? Number(match.mom_percentage) : null
        })
        return row
      })
      
      return { commodities, matrix }
    }
  },
  watch: {
    province_id: 'fetchData',
    date: 'fetchData',
    commodity_id: 'fetchData'
  },
  mounted() {
    this.fetchData()
  },
  beforeUnmount() {
    if (this.abortController) {
      this.abortController.abort()
    }
  },
  methods: {
    ...mapActions(useMacroStore, ['setProvinceId']),
    handleMapRegionHover(regionId) {
      this.hoveredRegionId = regionId
      if (regionId && this.regionRefs[regionId]) {
        const el = this.regionRefs[regionId]
        if (el && el.scrollIntoView) {
          el.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
        }
      }
    },
    handleRegionClick(region) {
      if (region.province_id) {
        this.setProvinceId(region.province_id)
      }
      if (this.$refs.geoMap && region.id) {
        this.$refs.geoMap.selectRegionById(region.id)
      } else {
        const targetCommodityId = this.commodity_id || 1
        this.$router.push({ name: 'CommodityDetail', params: { id: targetCommodityId } })
      }
    },
    handleRegionSelect(location) {
      if (location && location.province_id) {
        this.setProvinceId(location.province_id)
      }
    },
    async fetchData() {
      // Clear components data to reset reactivity
      this.anomalies = []
      this.regions = []
      this.mapData = null
      this.matrixData = []
      this.volatilityData = []
      this.heatmapData = []
      this.regionRefs = {}

      this.loadingAnomalies = true
      this.loadingMap = true
      this.loadingMatrix = true
      this.loadingVolatility = true
      this.loadingHeatmap = true
      
      // Cancel pending requests
      if (this.abortController) {
        this.abortController.abort()
      }
      this.abortController = new AbortController()
      const signal = this.abortController.signal
      
      const payloadParams = { date_id: this.date }
      if (this.province_id !== null && this.province_id !== 'all') {
        payloadParams.province_id = this.province_id
      }
      
      try {
        // Fetch Anomalies
        const anomaliesRes = await apiClient.get('/analytics/macro-anomalies', {
          params: { ...payloadParams, commodity_id: this.commodity_id },
          signal
        })
        
        if (anomaliesRes.data.success && anomaliesRes.data.data) {
          this.anomalies = anomaliesRes.data.data.map(item => ({
            id: item.regency_id,
            name: item.regency_name,
            price: item.current_price,
            trend: Number(item.percentage_difference).toFixed(2)
          }))
        } else {
          this.anomalies = []
        }
      } catch (err) {
        if (err.name !== 'CanceledError' && err.message !== 'canceled') {
          console.error('Failed to fetch anomalies:', err)
        }
        this.anomalies = []
      } finally {
        this.loadingAnomalies = false
      }

      try {
        // Fetch Geospatial Disparity
        const disparityRes = await apiClient.get('/analytics/disparity', {
          params: { ...payloadParams, commodity_id: this.commodity_id },
          signal
        })
        
        if (disparityRes.data.success && disparityRes.data.data) {
          if (disparityRes.data.data.length > 0 && disparityRes.data.data[0].national_avg) {
            this.nationalBaselinePrice = parseFloat(disparityRes.data.data[0].national_avg)
          }

          const mapLocations = disparityRes.data.data.map(item => ({
            id: item.regency_id,
            lat: item.latitude,
            lng: item.longitude,
            marketName: item.regency_name,
            regency_name: item.regency_name,
            provinceName: item.province_name,
            province_id: item.province_id,
            price: item.regency_avg,
            disparity: item.disparity_percentage,
            isAnomaly: item.disparity_percentage > 0,
            isFallback: false
          }))
          
          this.mapData = mapLocations.length > 0 ? mapLocations : null
          
          this.regions = disparityRes.data.data.map(item => ({
            id: item.regency_id,
            name: item.regency_name,
            average: item.regency_avg,
            province_id: item.province_id
          }))
        } else {
          this.regions = []
          this.mapData = null
        }
      } catch (err) {
        if (err.name !== 'CanceledError' && err.message !== 'canceled') {
          console.error('Failed to fetch disparity:', err)
        }
        this.regions = []
        this.mapData = null
      } finally {
        this.loadingMap = false
      }

      try {
        const matrixRes = await apiClient.get('/analytics/regional-matrix', {
          params: { date_id: this.date, commodity_id: this.commodity_id },
          signal
        })
        
        if (matrixRes.data.success && matrixRes.data.data) {
          this.matrixData = matrixRes.data.data
        } else {
          this.matrixData = []
        }
      } catch (err) {
        if (err.name !== 'CanceledError' && err.message !== 'canceled') {
          console.error('Failed to fetch regional matrix:', err)
        }
        this.matrixData = []
      } finally {
        this.loadingMatrix = false
      }

      try {
        const volRes = await apiClient.get('/analytics/volatility', {
          params: { ...payloadParams },
          signal
        })
        if (volRes.data.success && volRes.data.data) {
          this.volatilityData = volRes.data.data
        } else {
          this.volatilityData = []
        }
      } catch (err) {
        if (err.name !== 'CanceledError' && err.message !== 'canceled') console.error('Failed to fetch volatility:', err)
        this.volatilityData = []
      } finally {
        this.loadingVolatility = false
      }

      try {
        const heatRes = await apiClient.get('/analytics/inflation-heatmap', {
          params: { date_id: this.date },
          signal
        })
        if (heatRes.data.success && heatRes.data.data) {
          this.heatmapData = heatRes.data.data
        } else {
          this.heatmapData = []
        }
      } catch (err) {
        if (err.name !== 'CanceledError' && err.message !== 'canceled') console.error('Failed to fetch heatmap:', err)
        this.heatmapData = []
      } finally {
        this.loadingHeatmap = false
      }
    },
    formatCurrency(value) {
      if (!value) return 'Rp 0'
      return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(value)
    },
    formatCurrencySafe(value) {
      if (value === null || value === undefined || value === 0 || value === '0') return '-'
      return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(value)
    }
  }
})
</script>

<style scoped>
/* Custom scrollbar styling */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(71, 85, 105, 0.5) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(71, 85, 105, 0.5);
  border-radius: 9999px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(100, 116, 139, 0.8);
}
</style>
