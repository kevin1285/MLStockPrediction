<template>
  <div class="stock-chart">
    <section class="chart-header">
      <h1>Live Market Charts</h1>
      <p>Professional-grade charts powered by TradingView</p>
    </section>

    <section class="chart-content">
      <div class="search-section">
        <div class="search-box">
          <input 
            type="text" 
            v-model="ticker" 
            placeholder="Enter ticker"
            @keyup.enter="updateChart"
          >
          <button @click="updateChart" class="update-btn">Update Chart</button>
        </div>
      </div>

      <div class="tradingview-widget-container">
        <div id="tradingview_chart"></div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'

const ticker = ref('AAPL') // Default ticker

const initTradingViewWidget = () => {
  const script = document.createElement('script')
  script.src = 'https://s3.tradingview.com/tv.js'
  script.async = true
  script.onload = () => {
    new TradingView.widget({
      "width": "100%",
      "height": 600,
      "symbol": ticker.value,
      "interval": "D",
      "timezone": "Etc/UTC",
      "theme": "light",
      "style": "1",
      "locale": "en",
      "toolbar_bg": "#f1f3f6",
      "enable_publishing": false,
      "allow_symbol_change": true,
      "container_id": "tradingview_chart",
      "studies": [
        "RSI@tv-basicstudies",
        "MASimple@tv-basicstudies"
      ]
    })
  }
  document.head.appendChild(script)
}

const updateChart = () => {
  if (!ticker.value) return
  const container = document.getElementById('tradingview_chart')
  if (container) {
    container.innerHTML = ''
    initTradingViewWidget()
  }
}

onMounted(() => {
  initTradingViewWidget()
})

watch(ticker, () => {
  if (ticker.value) {
    updateChart()
  }
})
</script>

<style scoped>
.stock-chart {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
  padding: 2rem;
}

.chart-header {
  text-align: center;
  margin-bottom: 3rem;
}

.chart-header h1 {
  font-size: 2.5rem;
  color: #2d3748;
  margin-bottom: 1rem;
}

.chart-header p {
  color: #4a5568;
  font-size: 1.1rem;
}

.chart-content {
  max-width: 1200px;
  margin: 0 auto;
}

.search-section {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.search-box {
  display: flex;
  gap: 1rem;
  max-width: 600px;
  margin: 0 auto;
}

.search-box input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.search-box input:focus {
  outline: none;
  border-color: #667eea;
}

.update-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: transform 0.2s;
}

.update-btn:hover {
  transform: translateY(-2px);
}

.tradingview-widget-container {
  background: white;
  padding: 1rem;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

@media (max-width: 768px) {
  .stock-chart {
    padding: 1rem;
  }

  .chart-header h1 {
    font-size: 2rem;
  }

  .search-box {
    flex-direction: column;
  }

  .update-btn {
    width: 100%;
  }
}
</style> 