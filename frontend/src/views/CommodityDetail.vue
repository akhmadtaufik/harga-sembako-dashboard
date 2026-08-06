<template>
  <DashboardLayout>
    <div class="commodity-detail bg-slate-900 text-slate-50 p-6 md:p-8 lg:p-10 font-sans max-w-[1600px] mx-auto">
      
      <div class="mb-8">
        <h1 class="text-xl font-bold tracking-tight text-slate-100">Commodity Analysis</h1>
        <p class="text-sm text-slate-400 mt-1 tracking-wide">Detailed view for selected commodity tracking #{{ commodityId }}</p>
      </div>

      <!-- Split Comparative Panes (50/50 Split) -->
      <section class="mb-10">
        <div class="mb-5 border-b border-slate-800 pb-2 flex items-center justify-between relative">
          <div class="flex items-center gap-2 group relative w-max">
            <h2 class="text-xs font-bold tracking-[0.1em] text-slate-400 uppercase">Market Type Spread Analysis</h2>
            <svg class="w-4 h-4 text-slate-500 hover:text-slate-300 cursor-help transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div class="absolute left-0 top-full mt-2 w-72 p-3 bg-slate-900 border border-slate-700 rounded-md shadow-xl text-xs text-slate-300 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 pointer-events-none font-normal normal-case">
              Membandingkan tren harga rata-rata harian antara Pasar Tradisional (Baseline) dan Pasar Modern (Premium). Analisis rentang (spread) ini berguna untuk memantau disparitas harga dan mengidentifikasi margin premium yang diterapkan oleh ritel modern.
            </div>
          </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Pane 1: Traditional Markets -->
          <div class="bg-slate-800/40 border border-slate-700/50 rounded-sm h-[320px] flex flex-col overflow-hidden">
            <div class="p-4 border-b border-slate-700/50 flex justify-between items-center bg-slate-800/60">
              <h3 class="text-[11px] font-bold uppercase tracking-widest text-slate-300">Traditional Market Volume</h3>
              <span class="text-[9px] uppercase tracking-widest text-emerald-400 bg-emerald-950/50 px-2 py-1 rounded-sm border border-emerald-900/50">Baseline</span>
            </div>
            
            <div class="flex-1 relative p-4 flex flex-col">
              <!-- Skeleton -->
              <div v-if="loadingSpread" class="absolute inset-4 animate-pulse bg-slate-800/50 rounded-sm"></div>
              <!-- Empty State -->
              <div v-else-if="!traditionalSeries || traditionalSeries.length === 0" class="flex flex-col h-full w-full items-center justify-center text-slate-500 text-sm border border-dashed border-slate-700/50 rounded-sm bg-slate-800/20 p-6 text-center">
                <span class="block text-slate-400 font-medium mb-2">Informasi Tidak Lengkap</span>
                <span class="block text-xs text-slate-500">Data tidak tersedia untuk tipe pasar ini pada wilayah/waktu yang dipilih.</span>
              </div>
              <div v-else class="flex-1 w-full h-full">
                <TrendAnalyticsChart :xAxisData="traditionalXAxis" :seriesData="traditionalSeries" />
              </div>
            </div>
          </div>
          
          <!-- Pane 2: Modern Retail Markets -->
          <div class="bg-slate-800/40 border border-slate-700/50 rounded-sm h-[320px] flex flex-col overflow-hidden">
            <div class="p-4 border-b border-slate-700/50 flex justify-between items-center bg-slate-800/60">
              <h3 class="text-[11px] font-bold uppercase tracking-widest text-slate-300">Modern Retail Premium</h3>
              <span class="text-[9px] uppercase tracking-widest text-red-400 bg-red-950/50 px-2 py-1 rounded-sm border border-red-900/50">Variant</span>
            </div>
            
            <div class="flex-1 relative p-4 flex flex-col">
              <!-- Skeleton -->
              <div v-if="loadingSpread" class="absolute inset-4 animate-pulse bg-slate-800/50 rounded-sm"></div>
              <!-- Empty State -->
              <div v-else-if="!modernSeries || modernSeries.length === 0" class="flex flex-col h-full w-full items-center justify-center text-slate-500 text-sm border border-dashed border-slate-700/50 rounded-sm bg-slate-800/20 p-6 text-center">
                <span class="block text-slate-400 font-medium mb-2">Informasi Tidak Lengkap</span>
                <span class="block text-xs text-slate-500">Data tidak tersedia untuk tipe pasar ini pada wilayah/waktu yang dipilih.</span>
              </div>
              <div v-else class="flex-1 w-full h-full">
                <TrendAnalyticsChart :xAxisData="modernXAxis" :seriesData="modernSeries" />
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Asymmetric Analytics Row (Seasonality Time-Series) -->
      <section>
        <div class="mb-5 border-b border-slate-800 pb-2 flex items-center justify-between relative">
          <div class="flex items-center gap-2 group">
            <h2 class="text-xs font-bold tracking-[0.1em] text-slate-400 uppercase">Seasonality Time-Series</h2>
            <svg class="w-4 h-4 text-slate-500 hover:text-slate-300 cursor-help transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div class="absolute left-0 top-full mt-2 w-72 p-3 bg-slate-900 border border-slate-700 rounded-md shadow-xl text-xs text-slate-300 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 pointer-events-none">
              Menampilkan tren pergerakan harga rata-rata harian komoditas dari waktu ke waktu. Gunakan grafik ini untuk melihat pola musiman atau tren jangka panjang.
            </div>
          </div>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div class="lg:col-span-8 bg-slate-800/40 border border-slate-700/50 rounded-sm h-[400px] p-4 flex flex-col relative">
            <!-- Skeleton Loader -->
            <div v-if="loadingSeries" class="absolute inset-4 animate-pulse bg-slate-800/50 rounded-sm"></div>
            <!-- Empty State -->
            <div v-else-if="!seriesData" class="flex flex-col h-full w-full items-center justify-center text-slate-500 text-sm border border-dashed border-slate-700/50 rounded-sm">
              <span class="block text-slate-400 font-medium">Time-Series Empty</span>
              <span class="block text-xs mt-1">Data Unavailable for Selected Date Matrix</span>
            </div>
            <div v-else class="flex-1 w-full h-full">
              <TrendAnalyticsChart :xAxisData="seasonalityXAxis" :seriesData="seasonalitySeries" />
            </div>
          </div>
          
          <div class="lg:col-span-4 bg-slate-800/40 border border-slate-700/50 rounded-sm h-[400px] flex flex-col overflow-hidden">
             <div class="p-4 border-b border-slate-700/50 flex justify-between items-center bg-slate-800/60 sticky top-0 z-10 relative">
               <div class="flex items-center gap-2 group">
                 <h3 class="text-[11px] font-bold uppercase tracking-widest text-slate-300">Historical Anomalies</h3>
                 <svg class="w-4 h-4 text-slate-500 hover:text-slate-300 cursor-help transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                   <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                 </svg>
                 <div class="absolute left-0 top-full mt-2 w-64 p-3 bg-slate-900 border border-slate-700 rounded-md shadow-xl text-xs text-slate-300 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 pointer-events-none">
                   Mendeteksi fluktuasi harga yang tidak wajar. Anomali dicatat jika harga harian menyimpang secara signifikan (Spike/Drop) dibandingkan dengan rata-rata pergerakan harga 7 hari terakhir (7D MA).
                 </div>
               </div>
             </div>
             
             <!-- Skeleton Loader -->
             <div v-if="loadingSeries" class="p-4 space-y-4 flex-1 overflow-hidden">
               <div v-for="i in 5" :key="i" class="animate-pulse bg-slate-700/40 h-14 rounded-sm w-full"></div>
             </div>
             
             <!-- Empty State -->
             <div v-else-if="historicalAnomalies.length === 0" class="flex-1 flex flex-col items-center justify-center p-4 text-slate-500 text-sm text-center">
               <span class="block text-slate-400 font-medium">No Historical Alerts</span>
               <span class="block text-xs mt-1">Data Unavailable for Selected Date Matrix</span>
             </div>
             
             <!-- List View -->
             <div v-else class="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
               <div v-for="anomaly in historicalAnomalies" :key="anomaly.id" class="border-l-2 border-red-500/80 pl-3 py-1 bg-slate-800/30 pr-2">
                 <p class="text-[10px] text-slate-400 font-mono tracking-wider">{{ anomaly.date }}</p>
                 <p class="text-sm font-bold tracking-tight text-slate-200 mt-0.5">{{ formatCurrency(anomaly.price) }}</p>
                 <p class="text-[9px] text-red-400 mt-1 uppercase tracking-widest">{{ anomaly.reason }}</p>
               </div>
             </div>
          </div>
        </div>
      </section>

      <!-- Micro Deep-Dive Analysis (Section 6) -->
      <section class="mt-8">
        <div class="mb-5 border-b border-slate-800 pb-2 flex justify-between items-center relative">
          <div class="flex items-center gap-2 group">
            <h2 class="text-xs font-bold tracking-[0.1em] text-slate-400 uppercase">Micro Deep-Dive Analysis</h2>
            <svg class="w-4 h-4 text-slate-500 hover:text-slate-300 cursor-help transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <!-- Regency Selector for Micro Deep-Dive -->
          <div>
            <select
              v-model="selectedRegencyId"
              class="w-64 bg-slate-800 border border-slate-700 text-slate-200 text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-2 custom-select"
              @change="fetchMicroDeepDive"
            >
              <option value="" disabled selected>
                {{ loadingRegencies ? 'Loading regencies...' : '-- Select a Regency --' }}
              </option>
              <option v-for="r in regencyList" :key="r.regency_id" :value="r.regency_id">{{ r.name }}</option>
            </select>
          </div>
        </div>
        
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <!-- Predictive Price Trajectory Chart -->
          <div class="bg-slate-800/40 border border-slate-700/50 rounded-sm p-4 flex flex-col relative min-h-[420px]">
            <div class="flex items-center gap-2 group mb-2">
              <h3 class="text-[11px] font-bold uppercase tracking-widest text-slate-300">Predictive Price Trajectory (14D)</h3>
              <svg class="w-3.5 h-3.5 text-slate-500 hover:text-slate-300 cursor-help transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="absolute left-4 top-8 w-80 p-3 bg-slate-900 border border-slate-700 rounded-md shadow-xl text-xs text-slate-300 z-[60] opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 pointer-events-none">
                <strong>Deskripsi:</strong> Proyeksi estimasi harga 14 hari ke depan menggunakan algoritma Linear Regression berdasarkan tren historis dan musiman 90 hari terakhir.<br><br>
                <strong>Interpretasi:</strong> Garis solid adalah data aktual. Garis putus-putus adalah estimasi. Area berarsir (Confidence Interval) menunjukkan rentang ketidakpastian; semakin lebar area, semakin tinggi volatilitas harga.
              </div>
            </div>
            <div class="flex-1 w-full relative">
              <PredictiveTrajectoryChart 
                :data="predictiveData" 
                :loading="loadingPredictive" 
              />
            </div>
          </div>

          <!-- Cross-Commodity Correlation Radar -->
          <div class="bg-slate-800/40 border border-slate-700/50 rounded-sm p-4 flex flex-col relative min-h-[420px]">
            <div class="flex items-center gap-2 group mb-2">
              <h3 class="text-[11px] font-bold uppercase tracking-widest text-slate-300">Cross-Commodity Correlation (90D)</h3>
              <svg class="w-3.5 h-3.5 text-slate-500 hover:text-slate-300 cursor-help transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div class="absolute left-4 top-8 w-80 p-3 bg-slate-900 border border-slate-700 rounded-md shadow-xl text-xs text-slate-300 z-[60] opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 pointer-events-none">
                <strong>Deskripsi:</strong> Analisis koefisien korelasi Pearson untuk mengukur sejauh mana pergerakan harga komoditas utama mempengaruhi komoditas substitusi/komplementer di pasar lokal yang sama.<br><br>
                <strong>Interpretasi:</strong> Skala 0.0 hingga 1.0. Nilai di atas 0.70 menunjukkan hubungan yang sangat kuat (efek domino). Jika harga beras naik, komoditas dengan korelasi tinggi kemungkinan besar akan mengikuti.
              </div>
            </div>
            <div class="flex-1 w-full relative">
              <CrossCorrelationRadar 
                :data="correlationData" 
                :loading="loadingCorrelation" 
              />
            </div>
          </div>
        </div>
      </section>

    </div>
  </DashboardLayout>
</template>

<script>
import { defineComponent } from 'vue'
import { mapState } from 'pinia'
import { useMacroStore } from '../store/macro'
import DashboardLayout from '../components/DashboardLayout.vue'
import TrendAnalyticsChart from '../components/TrendAnalyticsChart.vue'
import PredictiveTrajectoryChart from '../components/PredictiveTrajectoryChart.vue'
import CrossCorrelationRadar from '../components/CrossCorrelationRadar.vue'
import apiClient from '../plugins/axios'

export default defineComponent({
  name: 'CommodityDetail',
  components: {
    DashboardLayout,
    TrendAnalyticsChart,
    PredictiveTrajectoryChart,
    CrossCorrelationRadar
  },
  data() {
    return {
      commodityId: null,
      loadingSpread: true,
      loadingSeries: true,
      traditionalXAxis: [],
      traditionalSeries: [],
      modernXAxis: [],
      modernSeries: [],
      seasonalityXAxis: [],
      seasonalitySeries: [],
      seriesData: null,
      historicalAnomalies: [],
      abortController: null,
      
      // Micro Deep-Dive State
      regencyList: [],
      selectedRegencyId: "",
      predictiveData: [],
      correlationData: [],
      loadingPredictive: false,
      loadingCorrelation: false,
      loadingRegencies: false
    }
  },
  computed: {
    ...mapState(useMacroStore, ['province_id', 'date', 'commodity_id'])
  },
  watch: {
    date: 'fetchDetailData',
    province_id() {
      this.fetchDetailData()
      this.fetchRegencies()
    },
    commodity_id() {
      this.fetchDetailData()
      this.fetchMicroDeepDive()
    }
  },
  mounted() {
    this.fetchDetailData()
    this.fetchRegencies()
  },
  beforeUnmount() {
    if (this.abortController) {
      this.abortController.abort()
    }
  },
  methods: {
    async fetchDetailData() {
      this.traditionalXAxis = []
      this.traditionalSeries = []
      this.modernXAxis = []
      this.modernSeries = []
      this.seasonalityXAxis = []
      this.seasonalitySeries = []
      this.seriesData = null
      this.historicalAnomalies = []
      
      this.loadingSpread = true
      this.loadingSeries = true
      
      if (this.abortController) {
        this.abortController.abort()
      }
      this.abortController = new AbortController()
      const signal = this.abortController.signal
      
      const payloadParams = {}
      if (this.province_id !== null && this.province_id !== 'all') {
        payloadParams.province_id = this.province_id
      }
      
      try {
        // Fetch Market Type Spread
        // We set a 30-day window based on the selected date for spread analysis
        const endDate = new Date(this.date)
        const startDate = new Date(endDate)
        startDate.setDate(startDate.getDate() - 30)
        
        const spreadRes = await apiClient.get('/analytics/spread/market-types', {
          params: { 
            start_date: startDate.toISOString().split('T')[0], 
            end_date: this.date,
            commodity_id: parseInt(this.commodity_id, 10),
            ...payloadParams
          },
          signal
        })
        
        if (spreadRes.data.success && spreadRes.data.data && spreadRes.data.data.length > 0) {
          const tradData = spreadRes.data.data.filter(d => d.market_type_name === 'Pasar Tradisional')
          const modData = spreadRes.data.data.filter(d => d.market_type_name === 'Pasar Modern')
          
          if (tradData.length > 0) {
            this.traditionalXAxis = tradData.map(d => {
              const dt = new Date(d.date_id)
              return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
            })
            this.traditionalSeries = [{
              name: 'Average Price',
              data: tradData.map(d => parseFloat(d.avg_price)),
              color: '#34d399'
            }]
          } else {
            this.traditionalSeries = []
          }
          
          if (modData.length > 0) {
            this.modernXAxis = modData.map(d => {
              const dt = new Date(d.date_id)
              return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
            })
            this.modernSeries = [{
              name: 'Average Price',
              data: modData.map(d => parseFloat(d.avg_price)),
              color: '#f87171'
            }]
          } else {
            this.modernSeries = []
          }
        } else {
          this.traditionalSeries = []
          this.modernSeries = []
        }
      } catch (err) {
        if (err.name !== 'CanceledError' && err.message !== 'canceled') {
          console.error('Failed to fetch spread data:', err)
        }
        this.traditionalSeries = []
        this.modernSeries = []
      } finally {
        this.loadingSpread = false
      }
      
      try {
        // Fetch Seasonality Time-Series (Seasonality API is currently aggregated by commodity, 
        // if we add province filtering it would go here. For now it is national.)
        const seriesRes = await apiClient.get('/analytics/seasonality', {
          params: { commodity_id: parseInt(this.commodity_id, 10), year: new Date(this.date).getFullYear() },
          signal
        })
        
        if (seriesRes.data.success && seriesRes.data.data && seriesRes.data.data.length > 0) {
          const rawData = seriesRes.data.data
          this.seasonalityXAxis = rawData.map(d => {
            const dt = new Date(d.date_id)
            return dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
          })
          this.seasonalitySeries = [{
            name: 'Historical Trend',
            data: rawData.map(d => parseFloat(d.avg_price)),
            color: '#60a5fa'
          }]
          this.seriesData = true // Keeps UI out of empty state
        } else {
          this.seriesData = null
          this.seasonalitySeries = []
        }
      } catch (err) {
        if (err.name !== 'CanceledError' && err.message !== 'canceled') {
          console.error('Failed to fetch seasonality:', err)
        }
        this.seriesData = null
        this.seasonalitySeries = []
      } finally {
        this.loadingSeries = false
      }

      try {
        // Fetch Historical Anomalies for current date matrix
        const anomalyRes = await apiClient.get('/analytics/anomalies', {
          params: { date_id: this.date, commodity_id: parseInt(this.commodity_id, 10), ...payloadParams },
          signal
        })
        if (anomalyRes.data.success && anomalyRes.data.data) {
          this.historicalAnomalies = anomalyRes.data.data.map((item, idx) => {
            // Parse YYYYMMDD integer back to a readable date
            const dateStr = String(item.date_id);
            const formattedDate = dateStr.length === 8 
                ? new Date(dateStr.slice(0,4), dateStr.slice(4,6)-1, dateStr.slice(6,8)).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
                : item.date_id;

            return {
                id: idx,
                date: formattedDate, // Properly mapped date
                price: item.current_price,
                reason: `${item.anomaly_type || 'Deviated'} (${item.percentage_difference > 0 ? '+' : ''}${parseFloat(item.percentage_difference).toFixed(2)}% vs 7D MA)`
            };
          })
        } else {
          this.historicalAnomalies = []
        }
      } catch (err) {
        if (err.name !== 'CanceledError' && err.message !== 'canceled') {
          console.error('Failed to fetch historical anomalies:', err)
        }
        this.historicalAnomalies = []
      }
    },
    async fetchRegencies() {
      try {
        this.loadingRegencies = true
        const payload = {}
        if (this.province_id && this.province_id !== 'all') {
          payload.province_id = this.province_id
        }
        
        const res = await apiClient.get('/locations/regencies', { params: payload })
        if (res.data.success) {
          this.regencyList = res.data.data
          // Reset selection if the current one is no longer in the list
          if (this.selectedRegencyId && !this.regencyList.find(r => r.regency_id === this.selectedRegencyId)) {
            this.selectedRegencyId = ""
            this.predictiveData = []
            this.correlationData = []
          }
        }
      } catch (err) {
        console.error('Failed to fetch regencies:', err)
      } finally {
        this.loadingRegencies = false
      }
    },
    async fetchMicroDeepDive() {
      if (!this.selectedRegencyId || !this.commodity_id) return
      
      this.loadingPredictive = true
      this.loadingCorrelation = true
      
      try {
        // Fetch Predictive Trajectory
        const predRes = await apiClient.get('/analytics/predictive-trajectory', {
          params: {
            commodity_id: this.commodity_id,
            regency_id: this.selectedRegencyId
          }
        })
        if (predRes.data.success) {
          this.predictiveData = predRes.data.data
        }
      } catch (err) {
        console.error('Failed to fetch predictive trajectory:', err)
        this.predictiveData = []
      } finally {
        this.loadingPredictive = false
      }
      
      try {
        // Fetch Cross Correlation
        const corrRes = await apiClient.get('/analytics/correlation', {
          params: {
            commodity_id: this.commodity_id,
            regency_id: this.selectedRegencyId
          }
        })
        if (corrRes.data.success) {
          this.correlationData = corrRes.data.data
        }
      } catch (err) {
        console.error('Failed to fetch cross correlation:', err)
        this.correlationData = []
      } finally {
        this.loadingCorrelation = false
      }
    },
    formatCurrency(value) {
      if (!value) return 'Rp 0'
      return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(value)
    }
  }
})
</script>

<style scoped>
/* Firefox */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(71, 85, 105, 0.5) transparent; /* slate-600/50 */
}

/* Webkit (Chrome, Edge, Safari) */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(71, 85, 105, 0.5); /* slate-600 with opacity */
  border-radius: 10px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(100, 116, 139, 0.8); /* slate-500 on hover */
}
</style>
