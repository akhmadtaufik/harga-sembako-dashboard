import { defineStore } from 'pinia'

const today = new Date()
const yyyy = today.getFullYear()
const mm = String(today.getMonth() + 1).padStart(2, '0')
const dd = String(today.getDate()).padStart(2, '0')
const formattedToday = `${yyyy}-${mm}-${dd}`

export const useMacroStore = defineStore('macro', {
  state: () => ({
    province_id: null,
    regency_id: null,
    commodity_id: 1,
    commodity_group_id: null,
    date: formattedToday,
    basket_commodity_ids: [11, 12, 1, 3, 13, 14, 7, 21, 17, 10] // Default basket
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
    },
    setBasketCommodityIds(ids) {
      this.basket_commodity_ids = ids
    }
  }
})
