<template>
  <div class="relative w-full h-full flex-1 min-h-[380px]">
    <div v-if="loading" class="absolute inset-0 z-10 flex items-center justify-center bg-slate-900/60 backdrop-blur-sm rounded-lg">
      <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-400"></div>
    </div>
    <div v-else-if="!data || data.length === 0" class="flex flex-col items-center justify-center h-full text-slate-500 border border-dashed border-slate-700/60 rounded-lg">
      <span class="text-sm font-medium">Select a Regency to View Regional Correlation Radar</span>
    </div>
    <div v-show="data && data.length > 0" ref="chartRef" class="w-full h-full"></div>
  </div>
</template>

<script>
import { markRaw } from 'vue'
import * as echarts from 'echarts'

export default {
  name: 'CrossCorrelationRadar',
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
  watch: {
    data: {
      deep: true,
      handler() {
        this.updateChart()
      }
    }
  },
  mounted() {
    this.initChart()
    window.addEventListener('resize', this.handleResize)
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.handleResize)
    if (this.chart) {
      this.chart.dispose()
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
      if (!this.chart || !this.data || this.data.length === 0) return

      const indicators = this.data.map(item => ({
        name: item.commodity_name,
        max: 1.0,
        min: -1.0
      }))

      const values = this.data.map(item => item.correlation_score)

      const option = {
        backgroundColor: 'transparent',
        tooltip: {
          trigger: 'item',
          backgroundColor: 'rgba(15, 23, 42, 0.95)',
          borderColor: 'rgba(51, 65, 85, 0.6)',
          textStyle: { color: '#e2e8f0' },
          formatter: () => {
            let html = `<div class="font-bold text-slate-200 border-b border-slate-700 pb-1 mb-1">Pearson Correlation (90D)</div>`
            this.data.forEach(d => {
              const scoreStr = d.correlation_score > 0 ? `+${d.correlation_score.toFixed(2)}` : `${d.correlation_score.toFixed(2)}`
              const colorClass = d.correlation_score >= 0.5 ? '#10b981' : d.correlation_score <= -0.2 ? '#f43f5e' : '#cbd5e1'
              html += `<div class="text-xs flex items-center justify-between gap-4 py-0.5">
                        <span>${d.commodity_name}:</span>
                        <span class="font-mono font-bold" style="color:${colorClass}">${scoreStr}</span>
                       </div>`
            })
            return html
          }
        },
        radar: {
          indicator: indicators,
          shape: 'polygon',
          center: ['50%', '55%'],
          radius: '70%',
          splitNumber: 4,
          axisName: {
            color: '#cbd5e1',
            fontSize: 12,
            fontWeight: 'bold',
            padding: [3, 5],
            formatter: (value) => {
              const words = value.split(' ');
              let res = '';
              for (let i = 0; i < words.length; i++) {
                res += words[i] + ' ';
                if ((i + 1) % 2 === 0 && i !== words.length - 1) {
                  res += '\n';
                }
              }
              return res.trim();
            }
          },
          splitLine: {
            lineStyle: {
              color: ['rgba(51, 65, 85, 0.4)', 'rgba(51, 65, 85, 0.2)', 'rgba(51, 65, 85, 0.2)', 'rgba(51, 65, 85, 0.4)']
            }
          },
          splitArea: {
            show: true,
            areaStyle: {
              color: ['rgba(30, 41, 59, 0.3)', 'rgba(15, 23, 42, 0.3)']
            }
          },
          axisLine: {
            lineStyle: {
              color: 'rgba(51, 65, 85, 0.5)'
            }
          }
        },
        series: [
          {
            name: 'Pearson Correlation',
            type: 'radar',
            data: [
              {
                value: values,
                name: 'Correlation Score'
              }
            ],
            symbol: 'circle',
            symbolSize: 6,
            itemStyle: {
              color: '#8b5cf6'
            },
            lineStyle: {
              width: 2,
              color: '#8b5cf6'
            },
            areaStyle: {
              color: 'rgba(139, 92, 246, 0.25)'
            }
          }
        ]
      }

      this.chart.setOption(option)
    }
  }
}
</script>
