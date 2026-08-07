<template>
  <div class="relative w-full h-full flex-1 min-h-[380px]">
    <div v-if="loading" class="absolute inset-0 z-10 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm rounded-lg">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-400"></div>
    </div>
    <div v-else-if="!data || data.length === 0" class="flex flex-col items-center justify-center h-full text-slate-500 border border-dashed border-slate-700/60 rounded-lg">
      <span class="text-sm font-medium">Select a Regency & Commodity to View Predictive Forecast</span>
    </div>
    <div v-else ref="chartRef" class="w-full min-h-[380px] min-w-0 overflow-hidden"></div>
  </div>
</template>

<script setup>
import { ref, shallowRef, watch, onMounted, onBeforeUnmount, markRaw, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const chartRef = ref(null)
const chartInstance = shallowRef(null)
let resizeObserver = null

const formatRp = (val) => {
  if (val === null || val === undefined || val === '-') return '-'
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(val)
}

const updateChart = () => {
  if (!chartInstance.value || !props.data || props.data.length === 0) return

  const dates = props.data.map(item => item.date_id)
  const actuals = props.data.map(item => item.actual_price !== null ? item.actual_price : '-')
  const forecasts = props.data.map(item => item.forecast_price !== null ? item.forecast_price : '-')
  const uppers = props.data.map(item => item.upper_bound !== null ? item.upper_bound : '-')
  const lowers = props.data.map(item => item.lower_bound !== null ? item.lower_bound : '-')

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(51, 65, 85, 0.6)',
      textStyle: { color: '#e2e8f0' },
      formatter: (params) => {
        if (!params.length) return ''
        const dateStr = params[0].axisValue
        let html = `<div class="font-bold text-slate-200 border-b border-slate-700 pb-1 mb-1">${dateStr}</div>`
        
        params.forEach(p => {
          if (p.value !== '-' && p.value !== undefined) {
            html += `<div class="text-xs flex items-center justify-between gap-4 py-0.5">
                      <span style="color:${p.color}">${p.seriesName}:</span>
                      <span class="font-mono text-white font-bold">${formatRp(p.value)}</span>
                     </div>`
          }
        })
        return html
      }
    },
    grid: { 
      top: '10%', 
      bottom: '25%', 
      left: '3%', 
      right: '5%', 
      containLabel: true 
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLine: { lineStyle: { color: 'rgba(51, 65, 85, 0.6)' } },
      axisLabel: {
        color: '#94a3b8',
        fontSize: 10,
        rotate: 30,
        interval: 'auto'
      }
    },
    yAxis: {
      type: 'value',
      splitLine: { lineStyle: { color: 'rgba(51, 65, 85, 0.3)', type: 'dashed' } },
      axisLabel: { 
        color: '#94a3b8',
        fontSize: 11,
        formatter: (v) => 'Rp ' + (v/1000).toFixed(0) + 'k'
      }
    },
    series: [
      {
        name: 'Actual Price',
        type: 'line',
        data: actuals,
        smooth: true,
        symbol: 'circle',
        symbolSize: 5,
        itemStyle: { color: '#10b981' },
        lineStyle: { width: 2.5 }
      },
      {
        name: 'Forecast Price',
        type: 'line',
        data: forecasts,
        smooth: true,
        symbol: 'circle',
        symbolSize: 5,
        itemStyle: { color: '#f59e0b' },
        lineStyle: { width: 2.5, type: 'dashed' }
      },
      {
        name: 'Upper Bound (+5%)',
        type: 'line',
        data: uppers,
        lineStyle: { opacity: 0 },
        stack: 'confidence-band',
        symbol: 'none'
      },
      {
        name: 'Confidence Band',
        type: 'line',
        data: lowers,
        lineStyle: { opacity: 0 },
        areaStyle: { color: 'rgba(245, 158, 11, 0.18)' },
        stack: 'confidence-band',
        symbol: 'none'
      }
    ]
  }

  chartInstance.value.setOption(option)
}

const initChart = () => {
  if (!chartRef.value) return
  chartInstance.value = markRaw(echarts.init(chartRef.value))
  updateChart()
  
  if (!resizeObserver) {
    resizeObserver = new ResizeObserver(() => {
      if (chartInstance.value) {
        chartInstance.value.resize()
      }
    })
    resizeObserver.observe(chartRef.value)
  }
}

watch(() => props.data, async (newData) => {
  if (newData && newData.length > 0) {
    await nextTick()
    setTimeout(() => {
      if (chartInstance.value && chartInstance.value.getDom() !== chartRef.value) {
        chartInstance.value.dispose()
        chartInstance.value = null
      }
      
      if (!chartInstance.value) {
        initChart()
      } else {
        updateChart()
      }
    }, 50)
  }
}, { deep: true })

onMounted(() => {
  initChart()
})

onBeforeUnmount(() => {
  if (resizeObserver) {
    resizeObserver.disconnect()
  }
  if (chartInstance.value) {
    chartInstance.value.dispose()
  }
})
</script>
