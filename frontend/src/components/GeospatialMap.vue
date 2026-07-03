<template>
  <div class="geospatial-map-wrapper w-full relative bg-slate-900 rounded-sm overflow-hidden">
    <!-- Pulse Skeleton Loader -->
    <div v-if="loadingGeoJson" class="absolute inset-0 z-10 bg-slate-800 flex items-center justify-center animate-pulse">
      <span class="text-slate-500 font-medium tracking-widest uppercase text-xs">Loading Geospatial Data...</span>
    </div>
    <div ref="mapContainer" id="map" class="h-[500px] w-full block z-0"></div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { mapState } from 'pinia'
import { useMacroStore } from '../store/macro'

export default defineComponent({
  name: 'GeospatialMap',
  props: {
    locations: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      map: null,
      geoJsonLayer: null,
      geoJsonData: null,
      loadingGeoJson: true,
      activeLayerInfo: null
    }
  },
  computed: {
    ...mapState(useMacroStore, ['province_id'])
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
    }
  },
  methods: {
    initMap() {
      this.map = L.map(this.$refs.mapContainer, {
        zoomControl: false,
        attributionControl: false
      }).setView([-0.789275, 113.921327], 5)

      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19
      }).addTo(this.map)
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
    renderChoropleth() {
      if (this.geoJsonLayer) {
        this.map.removeLayer(this.geoJsonLayer)
      }

      if (!this.map || !this.locations || this.locations.length === 0 || !this.geoJsonData) {
        if (this.map && (!this.province_id || this.province_id === 'all')) {
          this.map.setView([-0.789275, 113.921327], 5, { animate: true, duration: 1.0 })
        }
        return
      }

      // Zero-Fallback Composite Matching: Build Database Keys
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
          // Zero-Fallback Composite Matching: Build GeoJSON Keys
          const geoProvId = parseInt(feature.properties.province_id, 10)
          const geoReg = this.normalizeName(feature.properties.name || feature.properties.alt_name)
          
          const geoKey = `${geoProvId}_${geoReg}`
          
          // Strict Evaluation: No fuzzy fallback
          const matchedLoc = dataMap.get(geoKey)

          if (matchedLoc) {
            feature.properties.matchedData = matchedLoc
            return {
              fillColor: this.getColorForDisparity(matchedLoc.disparity), 
              weight: 1,
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
          const fallbackWarning = loc.isFallback || (!parseFloat(loc.lat))
            ? `<div class="mt-2 text-[10px] uppercase font-bold text-amber-400 flex items-center gap-1 bg-amber-900/30 px-2 py-1 rounded-sm border border-amber-500/50">
                 ⚠️ Estimated Location
               </div>`
            : ''

          const disparityColor = loc.disparity > 0 ? 'text-red-400' : 'text-emerald-400'
          const disparityText = loc.disparity !== undefined && loc.disparity !== null 
            ? `<p class="text-[11px] font-bold tracking-widest mt-1 ${disparityColor}">${loc.disparity > 0 ? '+' : ''}${loc.disparity}% DISPARITY</p>`
            : ''

          const tooltipContent = `
            <div class="font-sans bg-slate-900 text-slate-50 p-2 rounded-sm border border-slate-700 text-left">
              <h4 class="text-xs font-bold tracking-wider text-slate-300 uppercase">${loc.marketName}</h4>
              <p class="text-sm font-mono mt-1 text-slate-100">${this.formatCurrency(loc.price)}</p>
              ${disparityText}
              ${fallbackWarning}
            </div>
          `

          layer.bindTooltip(tooltipContent, {
            direction: 'top',
            sticky: true,
            className: 'custom-leaflet-tooltip bg-transparent border-none shadow-none p-0'
          })

          layer.on({
            mouseover: (e) => {
              const layer = e.target
              layer.setStyle({
                weight: 2,
                color: '#ffffff',
                fillOpacity: 0.9
              })
              layer.bringToFront()
            },
            mouseout: (e) => {
              this.geoJsonLayer.resetStyle(e.target)
            },
            click: (e) => {
              this.map.fitBounds(e.target.getBounds(), { padding: [50, 50], maxZoom: 11, animate: true, duration: 1.0 })
            }
          })
          
          matchedBounds.extend(layer.getBounds())
        }
      }).addTo(this.map)

      setTimeout(() => {
        if (this.map) {
          this.map.invalidateSize()
          // Priority: selected province bounds, then global Java+Bali bounds, then fallback to national center
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
.custom-leaflet-tooltip .leaflet-tooltip-tip {
  border-top-color: #334155;
}
</style>
