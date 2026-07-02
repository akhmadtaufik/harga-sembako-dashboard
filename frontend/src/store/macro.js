import { defineStore } from 'pinia'

export const useMacroStore = defineStore('macro', {
  state: () => ({
    province_id: null,
    regency_id: null,
    commodity_id: 1,
    commodity_group_id: null,
    date: '2026-07-01'
  }),
  actions: {
    setProvinceId(id) {
      this.province_id = id
    },
    setRegencyId(id) {
      this.regency_id = id
    },
    setCommodityId(id) {
      this.commodity_id = id
    },
    setCommodityGroupId(id) {
      this.commodity_group_id = id
    },
    setDate(date) {
      this.date = date
    }
  }
})
