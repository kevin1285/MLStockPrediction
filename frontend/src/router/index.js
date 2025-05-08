import { createRouter, createWebHistory } from 'vue-router'
import Home from '../pages/Home.vue'
import Analysis from '../pages/Analysis.vue'
import StockChart from '../pages/StockChart.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/analysis',
    name: 'Analysis',
    component: Analysis
  },
  {
    path: '/chart',
    name: 'StockChart',
    component: StockChart
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router 