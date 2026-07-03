<template>
  <DashboardLayout>
    <div class="main-dashboard bg-slate-900 text-slate-50 p-6 md:p-8 lg:p-10 font-sans max-w-[1600px] mx-auto">
      
      <!-- Top 5 Price Anomalies Grid Component (Metric Summary Grid) -->
      <section class="mb-10">
        <h2 class="text-xs font-bold tracking-[0.1em] text-slate-400 mb-5 uppercase border-b border-slate-800 pb-2">Price Anomalies (Top 5)</h2>
        
        <!-- Skeleton Loader -->
        <div v-if="loadingAnomalies" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4">
          <div v-for="i in 5" :key="i" class="animate-pulse bg-slate-800/50 rounded-sm p-4 h-28 border border-slate-700/50"></div>
        </div>

        <!-- Empty State -->
        <div v-else-if="anomalies.length === 0" class="flex flex-col items-center justify-center h-28 border border-dashed border-slate-700/50 rounded-sm text-slate-500 text-sm">
          <span class="block text-slate-400 font-medium">No Data Available</span>
          <span class="block text-xs mt-1">Data Unavailable for Selected Date Matrix</span>
        </div>

        <!-- Data Grid -->
        <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4">
          <div v-for="item in anomalies" :key="item.id" class="bg-slate-800/40 rounded-sm p-4 border border-slate-700/50 flex flex-col justify-between hover:bg-slate-800/60 transition-colors">
            <span class="text-xs font-semibold tracking-wide text-slate-400 truncate">{{ item.name }}</span>
            <div class="flex items-end justify-between mt-4">
              <span class="text-xl font-bold tracking-tight text-slate-100">{{ formatCurrency(item.price) }}</span>
              <span :class="item.trend > 0 ? 'text-red-400' : 'text-emerald-400'" class="text-xs font-mono font-medium tracking-tighter bg-slate-900/50 px-1.5 py-0.5 rounded-sm">
                {{ item.trend > 0 ? '+' : '' }}{{ item.trend }}%
              </span>
            </div>
          </div>
        </div>
      </section>

      <!-- Geospatial Disparity Map Container (Asymmetric Analytics Row) -->
      <section class="mb-10">
        <h2 class="text-xs font-bold tracking-[0.1em] text-slate-400 mb-5 uppercase border-b border-slate-800 pb-2">Geospatial Disparity & Regional Tracking</h2>
        
        <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <!-- Main Chart Workspace -->
          <div class="lg:col-span-8 bg-slate-800/40 border border-slate-700/50 rounded-sm h-[400px] relative flex flex-col overflow-hidden">
             <!-- Skeleton Loader -->
             <div v-show="loadingMap" class="absolute inset-0 z-10 animate-pulse bg-slate-800/30"></div>
             <!-- Empty State -->
             <div v-show="!loadingMap && !mapData" class="absolute inset-0 z-10 flex flex-col items-center justify-center bg-slate-800/40 text-slate-500 text-sm">
                <span class="block text-slate-400 font-medium">Map Unavailable</span>
                <span class="block text-xs mt-1">Data Unavailable for Selected Date Matrix</span>
             </div>
             <!-- Actual Map Component -->
             <GeospatialMap v-show="mapData" :locations="mapData || []" class="flex-1 w-full h-full" />
          </div>

          <!-- Scroll-locked Data Table Matrix -->
          <div class="lg:col-span-4 bg-slate-800/40 border border-slate-700/50 rounded-sm h-[400px] flex flex-col overflow-hidden">
             <div class="p-4 border-b border-slate-700/50 bg-slate-800/60 flex items-center justify-between">
               <h3 class="text-[11px] font-bold uppercase tracking-widest text-slate-300">Regional Breakdown</h3>
             </div>
             <!-- Skeleton Loader -->
             <div v-if="loadingMap" class="p-4 space-y-3 flex-1">
               <div v-for="i in 6" :key="i" class="animate-pulse bg-slate-700/40 h-8 rounded-sm w-full"></div>
             </div>
             <!-- Empty State -->
             <div v-else-if="regions.length === 0" class="flex-1 flex flex-col items-center justify-center p-4 text-slate-500 text-sm text-center">
                <span class="block text-slate-400 font-medium">No Breakdown</span>
                <span class="block text-xs mt-1">Data Unavailable for Selected Date Matrix</span>
             </div>
             <!-- Data Matrix -->
             <div v-else class="flex-1 overflow-y-auto">
               <table class="w-full text-left text-sm text-slate-300">
                 <tbody>
                   <tr v-for="region in regions" :key="region.id" class="border-b border-slate-700/30 hover:bg-slate-700/30 transition-colors">
                     <td class="py-3 px-4 text-xs font-medium">{{ region.name }}</td>
                     <td class="py-3 px-4 font-mono text-[13px] text-right">{{ formatCurrency(region.average) }}</td>
                   </tr>
                 </tbody>
               </table>
             </div>
          </div>
        </div>
      </section>
      
      <!-- Tabbed Technical Matrices (Full-width spreadsheet) -->
      <section>
         <h2 class="text-xs font-bold tracking-[0.1em] text-slate-400 mb-5 uppercase border-b border-slate-800 pb-2">Regional Averages Matrix</h2>
         <div class="bg-slate-800/40 border border-slate-700/50 rounded-sm flex flex-col overflow-hidden">
           <!-- Skeleton Loader -->
           <div v-if="loadingMatrix" class="p-4 space-y-2">
             <div v-for="i in 4" :key="i" class="animate-pulse bg-slate-700/40 h-10 rounded-sm w-full"></div>
           </div>
           <!-- Empty State -->
           <div v-else-if="matrixData.length === 0" class="p-10 flex flex-col items-center justify-center text-slate-500 text-sm">
             <span class="block text-slate-400 font-medium">Matrix Unavailable</span>
             <span class="block text-xs mt-1">Data Unavailable for Selected Date Matrix</span>
           </div>
           <!-- Spreadsheet view -->
           <div v-else class="overflow-x-auto h-[300px] overflow-y-auto">
             <table class="w-full text-sm text-slate-300 whitespace-nowrap">
               <thead class="bg-slate-900/50 text-slate-400 text-xs tracking-wider border-b border-slate-700/50 sticky top-0">
                 <tr>
                   <th class="py-3 px-4 font-semibold text-left">Province</th>
                   <th class="py-3 px-4 font-semibold text-right">Avg Price</th>
                   <th class="py-3 px-4 font-semibold text-right">Data Points</th>
                 </tr>
               </thead>
               <tbody class="divide-y divide-slate-700/30">
                 <tr v-for="row in matrixData" :key="row.province_id" class="hover:bg-slate-700/20 transition-colors">
                   <td class="py-3 px-4 text-xs font-bold text-slate-200">{{ row.province_name }}</td>
                   <td class="py-3 px-4 text-right font-mono text-[13px]">{{ formatCurrencySafe(row.average_price) }}</td>
                   <td class="py-3 px-4 text-right font-mono text-[13px]">{{ row.record_count > 0 ? row.record_count : '-' }}</td>
                 </tr>
               </tbody>
             </table>
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
      anomalies: [],
      regions: [],
      mapData: null,
      matrixData: [],
      abortController: null
    }
  },
  computed: {
    ...mapState(useMacroStore, ['province_id', 'date', 'commodity_id'])
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
    async fetchData() {
      // Re-paint guard: Clear component data instantly to trigger Vue reactivity
      this.anomalies = []
      this.regions = []
      this.mapData = null
      this.matrixData = []

      this.loadingAnomalies = true
      this.loadingMap = true
      this.loadingMatrix = true
      
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
        const anomaliesRes = await apiClient.get('/analytics/anomalies', {
          params: payloadParams,
          signal
        })
        
        // Map backend response shape to frontend layout format
        if (anomaliesRes.data.success && anomaliesRes.data.data) {
          this.anomalies = anomaliesRes.data.data.map(item => ({
            id: item.commodity_id,
            name: item.commodity_name,
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
        // Using the globally selected commodity_id from the store
        const disparityRes = await apiClient.get('/analytics/disparity', {
          params: { ...payloadParams, commodity_id: this.commodity_id },
          signal
        })
        
        if (disparityRes.data.success && disparityRes.data.data) {
          const mapLocations = disparityRes.data.data.map(item => ({
            lat: item.latitude,
            lng: item.longitude,
            marketName: item.regency_name,
            regency_name: item.regency_name,
            provinceName: item.province_name,
            province_id: item.province_id,
            price: item.regency_avg,
            disparity: item.disparity_percentage,
            isAnomaly: item.disparity_percentage > 0, // Any positive spike is an anomaly (crimson), negative is editorial green
            isFallback: false // Mocking fallback check logic
          }))
          console.log("MAPPED LOCATIONS", mapLocations.slice(0, 2))
          
          this.mapData = mapLocations.length > 0 ? mapLocations : null
          
          this.regions = disparityRes.data.data.map(item => ({
            id: item.regency_id,
            name: item.regency_name,
            average: item.regency_avg
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
