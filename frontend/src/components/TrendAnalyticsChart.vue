<template>
  <div class="trend-analytics-wrapper w-full h-full relative">
    <div ref="chartContainer" class="w-full h-full"></div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import * as echarts from 'echarts'

export default defineComponent({
  name: 'TrendAnalyticsChart',
  props: {
    seriesData: {
      type: Array,
      default: () => []
    },
    xAxisData: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      chartInstance: null
    }
  },
  mounted() {
    this.initChart()
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
    if (this.chartInstance) {
      this.chartInstance.dispose()
      this.chartInstance = null
    }
  },
  watch: {
    seriesData: {
      handler() {
        this.updateChart()
      },
      deep: true
    }
  },
  methods: {
    initChart() {
      this.chartInstance = echarts.init(this.$refs.chartContainer)
      this.updateChart()
    },
    formatCurrency(value) {
      if (value === null || value === undefined) return ''
      return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', maximumFractionDigits: 0 }).format(value)
    },
    updateChart() {
      if (!this.chartInstance) return

      const option = {
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'axis',
          backgroundColor: '#0f172a',
          borderColor: '#334155',
          textStyle: {
            color: '#f8fafc',
            fontFamily: 'inherit',
            fontSize: 12
          },
          valueFormatter: (value) => this.formatCurrency(value)
        },
        grid: {
          top: 30,
          right: 20,
          bottom: 30,
          left: 60,
          containLabel: false
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: this.xAxisData,
          axisLine: { lineStyle: { color: '#334155' } },
          axisLabel: { color: '#94a3b8', fontFamily: 'inherit', fontSize: 10 },
          splitLine: { show: false }
        },
        yAxis: {
          type: 'value',
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
          }
        },
        series: this.seriesData.map(series => ({
          name: series.name,
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 6,
          showSymbol: false,
          lineStyle: { width: 2, color: series.color || '#34d399' },
          itemStyle: { color: series.color || '#34d399' },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: series.color ? series.color + '40' : '#34d39940' },
              { offset: 1, color: series.color ? series.color + '00' : '#34d39900' }
            ])
          },
          data: series.data
        }))
      }

      this.chartInstance.setOption(option)
    },
    handleResize() {
      if (this.chartInstance) {
        this.chartInstance.resize()
      }
    }
  }
})
</script>
