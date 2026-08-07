<template>
  <div class="market-cluster-wrapper relative w-full h-full flex-1 min-h-[380px]">
    <div v-if="loading" class="absolute inset-0 flex items-center justify-center bg-slate-800/50 z-10 rounded-sm">
      <div class="animate-pulse flex space-x-2">
        <div class="h-2 w-2 bg-emerald-500 rounded-full"></div>
        <div class="h-2 w-2 bg-emerald-500 rounded-full"></div>
        <div class="h-2 w-2 bg-emerald-500 rounded-full"></div>
      </div>
    </div>
    
    <div v-else-if="!data || data.length === 0" class="flex flex-col h-full w-full items-center justify-center text-slate-500 text-sm border border-dashed border-slate-700/50 rounded-sm bg-slate-800/20 p-6 text-center">
      <span class="block text-slate-400 font-medium mb-2">Insufficient Data</span>
      <span class="block text-xs text-slate-500">Not enough data to calculate market clusters.</span>
    </div>

    <div v-else ref="chartContainer" class="w-full min-h-[380px] min-w-0 overflow-hidden"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount, markRaw, shallowRef, nextTick } from 'vue'
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

const chartContainer = ref(null)
const chartInstance = shallowRef(null)
let resizeObserver = null

const formatCurrency = (value) => {
  if (value === null || value === undefined) return ''
  return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(value)
}

const formatNumber = (value) => {
  if (value === null || value === undefined) return ''
  return new Intl.NumberFormat('id-ID', { maximumFractionDigits: 2 }).format(value)
}

const initChart = () => {
  if (!chartContainer.value) return
  chartInstance.value = markRaw(echarts.init(chartContainer.value))
  updateChart()
  
  if (!resizeObserver) {
    resizeObserver = new ResizeObserver(() => {
      if (chartInstance.value) {
        chartInstance.value.resize()
      }
    })
    resizeObserver.observe(chartContainer.value)
  }
}

const updateChart = () => {
  if (!chartInstance.value || !props.data || props.data.length === 0) return

  const clusters = {}
  props.data.forEach(item => {
    if (!clusters[item.cluster_label]) {
      clusters[item.cluster_label] = []
    }
    clusters[item.cluster_label].push(item)
  })

  // Define colors for clusters
  const clusterColors = {
    'Premium': '#f59e0b', // amber-500
    'Baseline': '#3b82f6', // blue-500
    'Budget': '#34d399', // emerald-400
    'Outlier': '#ef4444' // red-500
  }

  const series = Object.keys(clusters).map((label, index) => {
    return {
      name: label,
      type: 'scatter',
      symbolSize: function (data) {
        // Base size 10 + 5 per anomaly
        return Math.max(10, Math.min(50, 10 + data[2] * 5))
      },
      itemStyle: {
        color: clusterColors[label] || clusterColors['Baseline'],
        opacity: 0.8,
        borderColor: '#0f172a',
        borderWidth: 1
      },
      data: clusters[label].map(item => [
        Number(item.average_price),
        Number(item.volatility),
        Number(item.anomaly_count),
        item.market_name
      ])
    }
  })

  const option = {
    backgroundColor: 'transparent',
    tooltip: {
      backgroundColor: 'rgba(15, 23, 42, 0.95)',
      borderColor: 'rgba(51, 65, 85, 0.5)',
      textStyle: { color: '#e2e8f0' },
      formatter: function (param) {
        return `
          <div class="font-bold text-gray-100">${param.data[3]}</div>
          <div class="text-sm text-gray-400 mt-1">Cluster: <span class="font-semibold" style="color: ${param.color}">${param.seriesName}</span></div>
          <div class="text-sm text-gray-300 mt-1">Avg Price: Rp ${param.data[0].toLocaleString('id-ID')}</div>
          <div class="text-sm text-gray-300">Volatility: ${param.data[1].toFixed(2)}</div>
        `
      }
    },
    legend: {
      bottom: 0,
      textStyle: {
        color: '#94a3b8',
        fontSize: 10
      },
      icon: 'circle'
    },
    grid: {
      top: 20,
      right: 20,
      bottom: 40,
      left: 60,
      containLabel: true
    },
    xAxis: {
      type: 'value',
      name: 'Avg Price (X)',
      nameLocation: 'middle',
      nameGap: 25,
      nameTextStyle: {
        color: '#64748b',
        fontSize: 10
      },
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { 
        color: '#94a3b8', 
        fontFamily: 'inherit', 
        fontSize: 10,
        formatter: (value) => {
          if (value >= 1000000) return (value / 1000000) + 'M'
          if (value >= 1000) return (value / 1000) + 'K'
          return value
        }
      },
      splitLine: { 
        show: true,
        lineStyle: {
          color: '#1e293b',
          type: 'dashed'
        }
      },
      scale: true
    },
    yAxis: {
      type: 'value',
      name: 'Volatility (Y)',
      nameLocation: 'middle',
      nameGap: 40,
      nameTextStyle: {
        color: '#64748b',
        fontSize: 10
      },
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { 
        color: '#94a3b8', 
        fontFamily: 'inherit', 
        fontSize: 10
      },
      splitLine: { 
        show: true,
        lineStyle: {
          color: '#1e293b',
          type: 'dashed'
        }
      },
      scale: true
    },
    series: series
  }

  chartInstance.value.setOption(option, true)
}

watch(() => props.data, async (newData) => {
  if (newData && newData.length > 0) {
    await nextTick()
    // Delay initialization to ensure the browser has calculated the CSS layout
    setTimeout(() => {
      if (chartInstance.value && chartInstance.value.getDom() !== chartContainer.value) {
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
  // Delay initialization slightly to ensure container is fully rendered
  setTimeout(() => {
    initChart()
  }, 100)
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
