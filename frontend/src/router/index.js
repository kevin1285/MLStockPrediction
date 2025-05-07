import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Analysis from '../views/Analysis.vue'
import StockChart from '../views/StockChart.vue'

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