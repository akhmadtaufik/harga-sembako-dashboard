<template>
  <DashboardLayout>
    <div class="commodity-detail bg-slate-900 text-slate-50 p-6 md:p-8 lg:p-10 font-sans max-w-[1600px] mx-auto">
      
      <div class="mb-8">
        <h1 class="text-xl font-bold tracking-tight text-slate-100">Commodity Analysis</h1>
        <p class="text-sm text-slate-400 mt-1 tracking-wide">Detailed view for selected commodity tracking #{{ commodityId }}</p>
      </div>

      <!-- Split Comparative Panes (50/50 Split) -->
      <section class="mb-10">
        <h2 class="text-xs font-bold tracking-[0.1em] text-slate-400 mb-5 uppercase border-b border-slate-800 pb-2">Market Type Spread Analysis</h2>
        
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
              <div v-else-if="!traditionalData" class="flex flex-col h-full w-full items-center justify-center text-slate-500 text-sm border border-dashed border-slate-700/50 rounded-sm">
                <span class="block text-slate-400 font-medium">Missing Spread Data</span>
                <span class="block text-xs mt-1">Data Unavailable for Selected Date Matrix</span>
              </div>
              <div v-else id="chart-traditional" class="flex-1 w-full h-full"></div>
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
              <div v-else-if="!modernData" class="flex flex-col h-full w-full items-center justify-center text-slate-500 text-sm border border-dashed border-slate-700/50 rounded-sm">
                <span class="block text-slate-400 font-medium">Missing Spread Data</span>
                <span class="block text-xs mt-1">Data Unavailable for Selected Date Matrix</span>
              </div>
              <div v-else id="chart-modern" class="flex-1 w-full h-full"></div>
            </div>
          </div>
        </div>
      </section>

      <!-- Asymmetric Analytics Row (Seasonality Time-Series) -->
      <section>
        <h2 class="text-xs font-bold tracking-[0.1em] text-slate-400 mb-5 uppercase border-b border-slate-800 pb-2">Seasonality Time-Series</h2>
        
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div class="lg:col-span-8 bg-slate-800/40 border border-slate-700/50 rounded-sm h-[400px] p-4 flex flex-col relative">
            <!-- Skeleton Loader -->
            <div v-if="loadingSeries" class="absolute inset-4 animate-pulse bg-slate-800/50 rounded-sm"></div>
            <!-- Empty State -->
            <div v-else-if="!seriesData" class="flex flex-col h-full w-full items-center justify-center text-slate-500 text-sm border border-dashed border-slate-700/50 rounded-sm">
              <span class="block text-slate-400 font-medium">Time-Series Empty</span>
              <span class="block text-xs mt-1">Data Unavailable for Selected Date Matrix</span>
            </div>
            <!-- ECharts Placeholder -->
            <div v-else id="seasonality-chart" class="flex-1 w-full h-full"></div>
          </div>
          
          <div class="lg:col-span-4 bg-slate-800/40 border border-slate-700/50 rounded-sm h-[400px] flex flex-col overflow-hidden">
             <div class="p-4 border-b border-slate-700/50 bg-slate-800/60 sticky top-0 z-10">
               <h3 class="text-[11px] font-bold uppercase tracking-widest text-slate-300">Historical Anomalies</h3>
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
             <div v-else class="flex-1 overflow-y-auto p-4 space-y-4">
               <div v-for="anomaly in historicalAnomalies" :key="anomaly.id" class="border-l-2 border-red-500/80 pl-3 py-1 bg-slate-800/30 pr-2">
                 <p class="text-[10px] text-slate-400 font-mono tracking-wider">{{ anomaly.date }}</p>
                 <p class="text-sm font-bold tracking-tight text-slate-200 mt-0.5">{{ formatCurrency(anomaly.price) }}</p>
                 <p class="text-[9px] text-red-400 mt-1 uppercase tracking-widest">{{ anomaly.reason }}</p>
               </div>
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
import apiClient from '../plugins/axios'

export default defineComponent({
  name: 'CommodityDetail',
  components: {
    DashboardLayout
  },
  data() {
    return {
      commodityId: null,
      loadingSpread: true,
      loadingSeries: true,
      traditionalData: null,
      modernData: null,
      seriesData: null,
      historicalAnomalies: [],
      abortController: null
    }
  },
  computed: {
    ...mapState(useMacroStore, ['province_id', 'date'])
  },
  watch: {
    date: 'fetchDetailData'
  },
  mounted() {
    this.commodityId = this.$route.params.id || 'N/A'
    this.fetchDetailData()
  },
  beforeUnmount() {
    if (this.abortController) {
      this.abortController.abort()
    }
  },
  methods: {
    async fetchDetailData() {
      this.traditionalData = null
      this.modernData = null
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
            commodity_id: parseInt(this.commodityId, 10),
            ...payloadParams
          },
          signal
        })
        
        if (spreadRes.data.success && spreadRes.data.data && spreadRes.data.data.length > 0) {
          // In a real scenario, map this data into the chart instances.
          // Since the chart instances are just placeholders currently, we populate the raw state.
          this.traditionalData = spreadRes.data.data.filter(d => d.market_type_name === 'Traditional')
          this.modernData = spreadRes.data.data.filter(d => d.market_type_name === 'Modern Retail')
          
          // Safeguard if filters yield empty arrays
          if (this.traditionalData.length === 0) this.traditionalData = null
          if (this.modernData.length === 0) this.modernData = null
        } else {
          this.traditionalData = null
          this.modernData = null
        }
      } catch (err) {
        if (err.name !== 'CanceledError' && err.message !== 'canceled') {
          console.error('Failed to fetch spread data:', err)
        }
        this.traditionalData = null
        this.modernData = null
      } finally {
        this.loadingSpread = false
      }
      
      try {
        // Fetch Seasonality Time-Series (Seasonality API is currently aggregated by commodity, 
        // if we add province filtering it would go here. For now it is national.)
        const seriesRes = await apiClient.get('/analytics/seasonality', {
          params: { commodity_id: parseInt(this.commodityId, 10), year: new Date(this.date).getFullYear() },
          signal
        })
        
        if (seriesRes.data.success && seriesRes.data.data && seriesRes.data.data.length > 0) {
          this.seriesData = seriesRes.data.data
        } else {
          this.seriesData = null
        }
      } catch (err) {
        if (err.name !== 'CanceledError' && err.message !== 'canceled') {
          console.error('Failed to fetch seasonality:', err)
        }
        this.seriesData = null
      } finally {
        this.loadingSeries = false
      }
    },
    formatCurrency(value) {
      if (!value) return 'Rp 0'
      return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(value)
    }
  }
})
</script>
