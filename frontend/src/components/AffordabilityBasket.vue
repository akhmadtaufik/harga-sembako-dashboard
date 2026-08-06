<template>
  <div class="relative w-full h-[400px]">
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-slate-900/50 z-10 rounded">
      <div class="w-8 h-8 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
    </div>
    <div ref="chartRef" class="w-full h-full"></div>
  </div>
</template>

<script>
import * as echarts from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, TitleComponent, DataZoomComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { markRaw } from 'vue'

echarts.use([BarChart, GridComponent, TooltipComponent, TitleComponent, DataZoomComponent, CanvasRenderer])

export default {
  name: 'AffordabilityBasket',
  props: {
    data: {
      type: Array,
      default: () => []
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

      // Sort data ascending for better visualization (Echarts bar paints bottom-up)
      const sortedData = [...this.data].sort((a, b) => a.total_cost - b.total_cost)
      
      const provinces = sortedData.map(d => d.province_name)
      const costs = sortedData.map(d => Number(d.total_cost))

      const option = {
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          axisPointer: { type: 'shadow' },
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          borderColor: 'rgba(51, 65, 85, 0.5)',
          textStyle: { color: '#e2e8f0' },
          formatter: (params) => {
            const val = params[0]
            const formatted = new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(val.value)
            return `<div class="font-bold">${val.name}</div>
                    <div class="text-emerald-400 font-mono mt-1">${formatted}</div>`
          }
        },
        grid: {
          top: 10,
          right: 20,
          bottom: 20,
          left: 10,
          containLabel: true
        },
        xAxis: {
          type: 'value',
          splitLine: { lineStyle: { color: 'rgba(51, 65, 85, 0.3)', type: 'dashed' } },
          axisLabel: { color: '#94a3b8' }
        },
        yAxis: {
          type: 'category',
          data: provinces,
          axisLine: { show: false },
          axisTick: { show: false },
          axisLabel: { color: '#cbd5e1', fontSize: 10, width: 100, overflow: 'truncate' }
        },
        dataZoom: [
          {
            type: 'inside',
            yAxisIndex: 0,
            startValue: Math.max(0, provinces.length - 15), // Show top 15 by default
            endValue: provinces.length - 1
          }
        ],
        series: [
          {
            name: 'Total Cost',
            type: 'bar',
            data: costs,
            itemStyle: {
              color: new echarts.graphic.LinearGradient(1, 0, 0, 0, [
                { offset: 0, color: '#10b981' },
                { offset: 1, color: '#047857' }
              ]),
              borderRadius: [0, 4, 4, 0]
            }
          }
        ]
      }
      this.chart.setOption(option)
    }
  }
}
</script>
