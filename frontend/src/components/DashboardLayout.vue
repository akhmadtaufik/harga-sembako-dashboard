<template>
  <div class="min-h-screen bg-slate-900 flex text-slate-50">
    <!-- Persistent Analytical Sidebar -->
    <aside class="w-64 border-r border-slate-800 bg-slate-900/80 flex flex-col flex-shrink-0 z-20">
      <div class="h-16 flex items-center px-6 border-b border-slate-800">
        <h1 class="text-sm font-bold tracking-widest uppercase text-slate-100">Sembako<span class="text-slate-500 font-light">Analytics</span></h1>
      </div>
      <nav class="flex-1 py-6 px-4 space-y-2">
        <router-link to="/" class="block px-3 py-2 text-sm rounded transition-colors hover:bg-slate-800 text-slate-300 hover:text-white">
          Macro Analysis
        </router-link>
        <router-link to="/commodity/1" class="block px-3 py-2 text-sm rounded transition-colors hover:bg-slate-800 text-slate-300 hover:text-white">
          Micro Deep-Dive
        </router-link>
      </nav>
      <div class="p-4 border-t border-slate-800">
        <div class="text-xs text-slate-500 font-mono">System Secure</div>
      </div>
    </aside>

    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Navigation Bar / Reactive Global Filter Inputs -->
      <header class="h-16 border-b border-slate-800 bg-slate-900/80 flex items-center justify-between px-6 flex-shrink-0 z-10 sticky top-0">
        <div class="flex items-center space-x-6">
          <div class="flex flex-col">
            <label class="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Province</label>
            <select v-model="localProvince" @change="updateProvince" class="bg-slate-800 border border-slate-700 rounded text-sm text-slate-300 focus:ring-1 focus:ring-emerald-500 outline-none px-2 py-1 cursor-pointer">
              <option value="all">All Provinces</option>
              <option v-for="prov in provinces" :key="prov.province_id" :value="prov.province_id">{{ prov.name }}</option>
            </select>
          </div>
          <div class="h-8 w-px bg-slate-800"></div>
          <div class="flex flex-col">
            <label class="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Date Matrix</label>
            <input type="date" v-model="localDate" @change="updateDate" class="bg-slate-800 border border-slate-700 rounded text-sm text-slate-300 focus:ring-1 focus:ring-emerald-500 outline-none px-2 py-1" />
          </div>
          <div class="h-8 w-px bg-slate-800"></div>
          <div class="flex flex-col">
            <label class="text-[10px] uppercase tracking-wider text-slate-500 font-semibold mb-1">Commodity</label>
            <select v-model="localCommodity" @change="updateCommodity" class="bg-slate-800 border border-slate-700 rounded text-sm text-slate-300 focus:ring-1 focus:ring-emerald-500 outline-none px-2 py-1 cursor-pointer">
              <option v-for="com in commodities" :key="com.commodity_id" :value="com.commodity_id">{{ com.name }}</option>
            </select>
          </div>
        </div>
        
        <div class="flex items-center">
           <span class="w-2 h-2 rounded-full bg-emerald-500 mr-2 animate-pulse"></span>
           <span class="text-xs font-mono text-slate-400">Live Connection</span>
        </div>
      </header>

      <!-- Dynamic Context Banner -->
      <div v-if="activeCommodity" class="bg-slate-900 border-b border-slate-800/60 px-6 py-2.5 flex items-center flex-shrink-0">
        <div class="text-sm text-slate-400 font-medium tracking-wide border-l-2 border-emerald-500 pl-3 py-0.5 my-2">
          Active Matrix: <span class="text-slate-200 font-semibold">{{ activeCommodity.name }}</span> (Price metrics are strictly normalized per {{ activeCommodity.unit || 'Kg' }})
        </div>
      </div>

      <!-- Main Content Area -->
      <main class="flex-1 overflow-y-auto relative">
        <slot />
      </main>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { mapState, mapActions } from 'pinia'
import { useMacroStore } from '../store/macro'
import apiClient from '../plugins/axios'

export default defineComponent({
  name: 'DashboardLayout',
  data() {
    return {
      localProvince: 'all',
      localDate: '2026-07-01',
      localCommodity: 1,
      provinces: [],
      commodities: []
    }
  },
  computed: {
    ...mapState(useMacroStore, ['province_id', 'date', 'commodity_id']),
    activeCommodity() {
      if (!this.commodities.length) return null
      return this.commodities.find(c => c.commodity_id === parseInt(this.localCommodity, 10)) || this.commodities[0]
    }
  },
  async mounted() {
    this.localProvince = this.province_id || 'all'
    this.localDate = this.date || '2026-07-01'
    this.localCommodity = this.commodity_id || 1
    
    try {
      const res = await apiClient.get('/locations/provinces')
      if (res.data && res.data.success) {
        this.provinces = res.data.data
      }
    } catch (e) {
      console.error('Failed to load provinces', e)
    }

    try {
      const res = await apiClient.get('/commodities/items')
      if (res.data && res.data.success) {
        this.commodities = res.data.data
        // Make sure localCommodity is valid, otherwise set to the first commodity's id
        if (this.commodities.length > 0 && !this.commodities.find(c => c.commodity_id === parseInt(this.localCommodity, 10))) {
          this.localCommodity = this.commodities[0].commodity_id
          this.setCommodityId(this.localCommodity)
        }
      }
    } catch (e) {
      console.error('Failed to load commodities', e)
    }
  },
  methods: {
    ...mapActions(useMacroStore, ['setProvinceId', 'setDate', 'setCommodityId']),
    updateProvince() {
      // Strictly coerce to integer for FastAPI Pydantic schemas, or null if all
      const payload = this.localProvince === 'all' ? null : parseInt(this.localProvince, 10)
      this.setProvinceId(payload)
    },
    updateDate() {
      // Date naturally binds as YYYY-MM-DD string, matching FastAPI's date parser
      this.setDate(this.localDate)
    },
    updateCommodity() {
      this.setCommodityId(parseInt(this.localCommodity, 10))
    }
  }
})
</script>
