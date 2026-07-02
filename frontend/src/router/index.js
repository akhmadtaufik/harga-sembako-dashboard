import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'MainDashboard',
    component: () => import('../views/MainDashboard.vue')
  },
  {
    path: '/commodity/:id',
    name: 'CommodityDetail',
    component: () => import('../views/CommodityDetail.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue') // Lazy-loaded Placeholder
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env?.BASE_URL || '/'),
  routes
})

// Hardened Vue Router Navigation Guard
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('API_KEY') || localStorage.getItem('JWT_TOKEN')
  
  // Enforce rigid authentication boundary
  if (to.name !== 'Login' && !token) {
    // Short-circuit execution and force redirection to a clean state
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router
