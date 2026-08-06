<template>
  <div class="relative w-full h-[400px]">
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-slate-900/50 z-10 rounded">
      <div class="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
    </div>
    <div ref="chartRef" class="w-full h-full"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, TitleComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { markRaw } from 'vue'

echarts.use([BarChart, GridComponent, TooltipComponent, TitleComponent, CanvasRenderer])

export default {
  name: 'SupplyChainWaterfall',
  props: {
    data: {
      type: Object,
      default: null
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      chart: null
    }
  },
  mounted() {
    this.initChart()
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    if (this.chart) this.chart.dispose()
    window.removeEventListener('resize', this.handleResize)
  },
  watch: {
    data: {
      deep: true,
      handler() {
        this.updateChart()
      }
    }
  },
  methods: {
    initChart() {
      if (!this.$refs.chartRef) return
      this.chart = markRaw(echarts.init(this.$refs.chartRef))
      this.updateChart()
    },
    handleResize() {
      if (this.chart) this.chart.resize()
    },
    updateChart() {
      if (!this.chart || !this.data) return

      const d = this.data

      // Step 1: Parse and round data
      const prodPrice = Math.round(Number(d.producer_price) || 0)
      const wholesalePrice = Math.round(Number(d.wholesale_price) || 0)
      const marginWholesale = Math.round(Number(d.margin_wholesale) || 0)
      const tradPrice = Math.round(Number(d.traditional_retail_price) || 0)
      const marginTrad = Math.round(Number(d.margin_traditional) || 0)
      const modernPrice = Math.round(Number(d.modern_retail_price) || 0)
      const marginModern = Math.round(Number(d.margin_modern) || 0)

      // Step 2: Build dynamic steps
      const steps = []
      
      // If producer price > 0, Produsen is the base.
      if (prodPrice > 0) {
        steps.push({ name: 'Produsen', price: prodPrice, margin: prodPrice, isBase: true })
      }
      
      // Grosir
      steps.push({ 
        name: 'Grosir', 
        price: wholesalePrice, 
        margin: steps.length === 0 ? wholesalePrice : marginWholesale, 
        isBase: steps.length === 0 
      })
      
      // Tradisional
      steps.push({ 
        name: 'Tradisional', 
        price: tradPrice, 
        margin: marginTrad, 
        isBase: false 
      })
      
      // Modern
      steps.push({ 
        name: 'Modern', 
        price: modernPrice, 
        margin: marginModern, 
        isBase: false 
      })

      // Step 3: Map to ECharts arrays
      const categories = steps.map(s => s.name)
      
      const baseData = []
      const marginData = []
      
      steps.forEach((s) => {
        if (s.isBase) {
          baseData.push(0)
          marginData.push(s.margin)
        } else {
          // If it's a leaf node (Tradisional, Modern), the base is Grosir's price.
          // If it's Grosir (and Produsen existed), the base is Produsen's price.
          if (s.name === 'Grosir') {
            baseData.push(prodPrice)
          } else {
            baseData.push(wholesalePrice)
          }
          marginData.push(s.margin)
        }
      })

      // Formatter function
      const formatRp = (val) => new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(val)

      // Step 4: Apply to ECharts option
      const option = {
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          borderColor: 'rgba(51, 65, 85, 0.5)',
          textStyle: { color: '#e2e8f0' },
          formatter: (params) => {
            const tar = params[1] // The visible bar
            const total = params[0].value + params[1].value
            
            const fmtVal = formatRp(tar.value)
            const fmtTotal = formatRp(total)
            
            // Check if the current node is the base node using the dynamic steps array
            const isNodeBase = steps.find(s => s.name === tar.name)?.isBase
            let label = isNodeBase ? 'Base Price' : '+ Margin'
            
            return `<div class="font-bold">${tar.name}</div>
                    <div class="text-slate-400 text-xs mt-1">${label}: <span class="text-white font-mono">${fmtVal}</span></div>
                    <div class="text-slate-400 text-xs">Total: <span class="text-white font-mono">${fmtTotal}</span></div>`
          }
        },
        grid: {
          top: 40,
          right: 20,
          bottom: 20,
          left: 60,
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: categories,
          axisLine: { lineStyle: { color: 'rgba(51, 65, 85, 0.5)' } },
          axisTick: { show: false },
          axisLabel: { 
            color: '#cbd5e1', 
            fontWeight: 'bold',
            interval: 0,
            overflow: 'break',
            width: 80
          }
        },
        yAxis: {
          type: 'value',
          splitLine: { lineStyle: { color: 'rgba(51, 65, 85, 0.3)', type: 'dashed' } },
          axisLabel: { color: '#94a3b8' }
        },
        series: [
          {
            name: 'Placeholder',
            type: 'bar',
            stack: 'Total',
            itemStyle: { borderColor: 'transparent', color: 'transparent' },
            emphasis: { itemStyle: { borderColor: 'transparent', color: 'transparent' } },
            data: baseData
          },
          {
            name: 'Value',
            type: 'bar',
            stack: 'Total',
            label: { 
              show: true, 
              position: 'top', 
              color: '#fff', 
              formatter: (p) => formatRp(p.value)
            },
            itemStyle: {
              color: (params) => {
                const isNodeBase = steps.find(s => s.name === params.name)?.isBase
                if (isNodeBase) return '#3b82f6' // Blue for the base (whether Produsen or Grosir)
                if (params.name === 'Grosir') return '#f59e0b' // Amber
                if (params.name === 'Tradisional') return '#10b981' // Emerald
                return '#8b5cf6' // Violet
              },
              borderRadius: [4, 4, 0, 0]
            },
            data: marginData
          }
        ]
      }
      this.chart.setOption(option)
    }
  }
}
</script>
