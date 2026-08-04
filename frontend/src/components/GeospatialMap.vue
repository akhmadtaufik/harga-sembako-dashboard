<template>
  <div class="geospatial-map-wrapper w-full relative bg-slate-900 rounded-lg overflow-hidden flex flex-col h-full border border-slate-800 shadow-2xl">
    <!-- Pulse Skeleton Loader -->
    <div v-if="loadingGeoJson" class="absolute inset-0 z-20 bg-slate-900/90 backdrop-blur-sm flex flex-col items-center justify-center animate-pulse gap-3">
      <div class="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
      <span class="text-slate-400 font-mono tracking-widest uppercase text-xs">Loading Geospatial Layer...</span>
    </div>
    <div ref="mapContainer" id="map" class="h-full w-full block z-0 flex-1"></div>

    <!-- Floating Choropleth Legend -->
    <div class="absolute bottom-4 right-4 z-[400] bg-slate-900/80 backdrop-blur-md border border-slate-700/70 rounded-lg p-3.5 shadow-2xl text-xs text-slate-300 pointer-events-auto max-w-[210px] transition-all duration-300 hover:border-slate-600">
      <div class="font-bold uppercase tracking-wider text-[10px] text-slate-400 mb-2 border-b border-slate-700/50 pb-1 flex items-center justify-between">
        <span>Price Disparity Scale</span>
        <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
      </div>
      <div class="space-y-2 font-mono text-[11px]">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-xs inline-block bg-[#991b1b] shadow-sm shadow-red-900/50"></span>
            <span class="text-red-300 font-medium">> +15%</span>
          </div>
          <span class="text-[9px] text-slate-400 font-sans">High Spike</span>
        </div>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-xs inline-block bg-[#f87171] shadow-sm shadow-red-400/50"></span>
            <span class="text-red-400 font-medium">0% to +15%</span>
          </div>
          <span class="text-[9px] text-slate-400 font-sans">Mild Spike</span>
        </div>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-xs inline-block bg-[#475569] shadow-sm"></span>
            <span class="text-slate-400 font-medium">0%</span>
          </div>
          <span class="text-[9px] text-slate-400 font-sans">Baseline</span>
        </div>
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="w-3 h-3 rounded-xs inline-block bg-[#10b981] shadow-sm shadow-emerald-500/50"></span>
            <span class="text-emerald-400 font-medium">< 0%</span>
          </div>
          <span class="text-[9px] text-slate-400 font-sans">Below Avg</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { mapState, mapActions } from 'pinia'
import { useMacroStore } from '../store/macro'

export default defineComponent({
  name: 'GeospatialMap',
  props: {
    locations: {
      type: Array,
      default: () => []
    },
    hoveredRegionId: {
      type: [Number, String],
      default: null
    }
  },
  emits: ['region-hover', 'region-select'],
  data() {
    return {
      map: null,
      geoJsonLayer: null,
      geoJsonData: null,
      loadingGeoJson: true,
      layerMap: new Map() // maps regency_id -> layer
    }
  },
  computed: {
    ...mapState(useMacroStore, ['province_id', 'commodity_id'])
  },
  async mounted() {
    this.initMap()
    await this.fetchGeoJson()
    if (this.locations.length && this.geoJsonData) {
      this.renderChoropleth()
    }
  },
  beforeUnmount() {
    if (this.map) {
      this.map.remove()
      this.map = null
    }
  },
  watch: {
    locations: {
      handler() {
        if (this.geoJsonData) {
          this.renderChoropleth()
        }
      },
      deep: true
    },
    hoveredRegionId(newId, oldId) {
      if (oldId !== newId) {
        this.highlightLayerById(oldId, false)
        this.highlightLayerById(newId, true)
      }
    }
  },
  methods: {
    ...mapActions(useMacroStore, ['setProvinceId']),
    initMap() {
      this.map = L.map(this.$refs.mapContainer, {
        zoomControl: false,
        attributionControl: false
      }).setView([-0.789275, 113.921327], 5)

      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19
      }).addTo(this.map)

      // Listen for popup button clicks via delegation
      this.map.on('popupopen', () => {
        const btn = document.getElementById('map-drilldown-btn')
        if (btn) {
          btn.onclick = () => {
            const provId = btn.getAttribute('data-province-id')
            if (provId) {
              this.setProvinceId(parseInt(provId, 10))
            }
            const targetCommodityId = this.commodity_id || 1
            this.$router.push({ name: 'CommodityDetail', params: { id: targetCommodityId } })
          }
        }
      })
    },
    async fetchGeoJson() {
      this.loadingGeoJson = true
      try {
        const response = await fetch('/indonesia-regencies.geojson')
        if (!response.ok) throw new Error('Failed to load GeoJSON')
        const rawData = await response.json()
        const allowedProvinces = ['31', '32', '33', '34', '35', '36', '51']
        this.geoJsonData = {
          ...rawData,
          features: rawData.features.filter(f => allowedProvinces.includes(f.properties.province_id))
        }
      } catch (err) {
        console.error('GeoJSON Load Error:', err)
      } finally {
        this.loadingGeoJson = false
      }
    },
    formatCurrency(value) {
      if (!value) return 'Rp 0'
      return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(value)
    },
    getColorForDisparity(disparity) {
      if (disparity === undefined || disparity === null) return 'transparent'
      if (disparity > 15) return '#991b1b' // Deep Crimson (High positive spike)
      if (disparity > 0) return '#f87171'  // Soft Coral (Mild spike)
      if (disparity === 0) return '#475569' // Neutral Slate Gray (Baseline stable)
      return '#10b981' // Emerald Green (Below average)
    },
    normalizeName(name) {
      if (!name) return ''
      return name.toLowerCase()
        .replace(/kabupaten/g, '')
        .replace(/kab\./g, '')
        .replace(/kota/g, '')
        .replace(/provinsi/g, '')
        .replace(/prov\./g, '')
        .replace(/daerah istimewa/g, '')
        .replace(/di /g, '')
        .replace(/dki /g, '')
        .replace(/\s+/g, '')
        .replace(/[^a-z0-9]/g, '')
    },
    highlightLayerById(id, isHighlight) {
      if (!id || !this.layerMap.has(id)) return
      const layer = this.layerMap.get(id)
      if (isHighlight) {
        layer.setStyle({
          weight: 3,
          color: '#34d399', // Emerald glow stroke
          fillOpacity: 0.95
        })
        if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
          layer.bringToFront()
        }
      } else {
        if (this.geoJsonLayer) {
          this.geoJsonLayer.resetStyle(layer)
        }
      }
    },
    selectRegionById(id) {
      if (!id || !this.layerMap.has(id)) return
      const layer = this.layerMap.get(id)
      if (layer) {
        if (layer.getBounds && layer.getBounds().isValid()) {
          this.map.fitBounds(layer.getBounds(), { padding: [50, 50], maxZoom: 11, animate: true, duration: 0.8 })
        }
        layer.openPopup()
        this.highlightLayerById(id, true)
      }
    },
    renderChoropleth() {
      if (this.geoJsonLayer) {
        this.map.removeLayer(this.geoJsonLayer)
      }
      this.layerMap.clear()

      if (!this.map || !this.locations || this.locations.length === 0 || !this.geoJsonData) {
        if (this.map && (!this.province_id || this.province_id === 'all')) {
          this.map.setView([-0.789275, 113.921327], 5, { animate: true, duration: 1.0 })
        }
        return
      }

      const dataMap = new Map()
      this.locations.forEach(loc => {
        const provId = loc.province_id
        const regName = loc.regency_name || loc.marketName
        if (!provId || !regName) return
        const dbKey = `${provId}_${this.normalizeName(regName)}`
        dataMap.set(dbKey, loc)
      })

      const matchedBounds = L.latLngBounds()
      const globalBounds = L.latLngBounds()
      const provinceBounds = L.latLngBounds()
      
      const isProvinceFiltered = this.province_id && this.province_id !== 'all'

      this.geoJsonLayer = L.geoJSON(this.geoJsonData, {
        style: (feature) => {
          const geoProvId = parseInt(feature.properties.province_id, 10)
          const geoReg = this.normalizeName(feature.properties.name || feature.properties.alt_name)
          
          const geoKey = `${geoProvId}_${geoReg}`
          const matchedLoc = dataMap.get(geoKey)

          if (matchedLoc) {
            feature.properties.matchedData = matchedLoc
            return {
              fillColor: this.getColorForDisparity(matchedLoc.disparity), 
              weight: 1.5,
              opacity: 1,
              color: '#334155',
              fillOpacity: 0.8
            }
          }

          return {
            fillColor: 'transparent',
            weight: 1,
            opacity: 0.2,
            color: '#1e293b',
            fillOpacity: 0.1
          }
        },
        onEachFeature: (feature, layer) => {
          globalBounds.extend(layer.getBounds())
          
          if (isProvinceFiltered && parseInt(feature.properties.province_id, 10) === parseInt(this.province_id, 10)) {
            provinceBounds.extend(layer.getBounds())
          }
          
          if (!feature.properties.matchedData) return

          const loc = feature.properties.matchedData
          if (loc.id) {
            this.layerMap.set(loc.id, layer)
          }

          const fallbackWarning = loc.isFallback || (!parseFloat(loc.lat))
            ? `<div class="mt-2 text-[10px] font-medium text-amber-400 flex items-center gap-1 bg-amber-950/60 px-2 py-1 rounded border border-amber-500/40">
                 ⚠️ Estimated Coordinates
               </div>`
            : ''

          const disparityColor = loc.disparity > 0 ? 'text-red-400 bg-red-950/50 border-red-800/50' : 'text-emerald-400 bg-emerald-950/50 border-emerald-800/50'
          const disparityText = loc.disparity !== undefined && loc.disparity !== null 
            ? `<div class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-mono font-bold border ${disparityColor} mt-2">
                ${loc.disparity > 0 ? '+' : ''}${loc.disparity}% DISPARITY
               </div>`
            : ''

          const popupContent = `
            <div class="font-sans bg-slate-900/95 backdrop-blur-md text-slate-100 p-4 rounded-xl border border-slate-700/80 shadow-2xl text-left min-w-[220px]">
              <div class="border-b border-slate-800 pb-2 mb-2">
                <span class="text-[10px] uppercase font-bold tracking-widest text-slate-400 block">${loc.provinceName || 'Region'}</span>
                <h4 class="text-sm font-bold text-white leading-snug">${loc.marketName}</h4>
              </div>
              <div class="my-2">
                <span class="text-[10px] text-slate-400 uppercase font-semibold">Average Price</span>
                <p class="text-lg font-mono font-bold text-emerald-400 leading-tight">${this.formatCurrency(loc.price)}</p>
                ${disparityText}
              </div>
              ${fallbackWarning}
              <button 
                id="map-drilldown-btn" 
                data-province-id="${loc.province_id || ''}" 
                class="mt-3 w-full bg-emerald-600 hover:bg-emerald-500 active:bg-emerald-700 text-white font-semibold text-xs py-2 px-3 rounded-lg transition-all flex items-center justify-center gap-1.5 shadow-lg shadow-emerald-900/30 group cursor-pointer">
                <span>View Detailed Analytics</span>
                <span class="group-hover:translate-x-1 transition-transform">&rarr;</span>
              </button>
            </div>
          `

          layer.bindPopup(popupContent, {
            className: 'custom-leaflet-popup'
          })

          layer.on({
            mouseover: (e) => {
              const ly = e.target
              ly.setStyle({
                weight: 2.5,
                color: '#34d399',
                fillOpacity: 0.95
              })
              if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
                ly.bringToFront()
              }
              if (loc.id) {
                this.$emit('region-hover', loc.id)
              }
            },
            mouseout: (e) => {
              if (this.hoveredRegionId !== loc.id) {
                this.geoJsonLayer.resetStyle(e.target)
              }
              this.$emit('region-hover', null)
            },
            click: (e) => {
              this.map.fitBounds(e.target.getBounds(), { padding: [50, 50], maxZoom: 11, animate: true, duration: 0.8 })
              this.$emit('region-select', loc)
            }
          })
          
          matchedBounds.extend(layer.getBounds())
        }
      }).addTo(this.map)

      setTimeout(() => {
        if (this.map) {
          this.map.invalidateSize()
          if (isProvinceFiltered && provinceBounds.isValid()) {
            this.map.fitBounds(provinceBounds, { padding: [20, 20], animate: true, duration: 1.0 })
          } else if (!isProvinceFiltered && globalBounds.isValid()) {
            this.map.fitBounds(globalBounds, { padding: [20, 20], animate: true, duration: 1.0 })
          } else if (matchedBounds.isValid()) {
            this.map.fitBounds(matchedBounds, { padding: [20, 20], animate: true, duration: 1.0 })
          } else {
            this.map.setView([-0.789275, 113.921327], 5, { animate: true, duration: 1.0 })
          }
        }
      }, 300)
    }
  }
})
</script>

<style>
.custom-leaflet-popup .leaflet-popup-content-wrapper {
  background: transparent !important;
  padding: 0 !important;
  box-shadow: none !important;
  border: none !important;
}
.custom-leaflet-popup .leaflet-popup-content {
  margin: 0 !important;
}
.custom-leaflet-popup .leaflet-popup-tip-container {
  margin-top: -1px;
}
.custom-leaflet-popup .leaflet-popup-tip {
  background: #0f172a !important;
  border: 1px solid #334155 !important;
}
</style>
