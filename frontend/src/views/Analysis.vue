<template>
  <div class="analysis">
    <section class="analysis-header">
      <h1>Stock Analysis</h1>
      <p>Enter a ticker to get started with our ML-powered analysis</p>
    </section>

    <section class="analysis-content">
      <div class="search-section">
        <div class="search-box">
          <input 
            type="text" 
            v-model="ticker" 
            placeholder="Enter ticker"
            @keyup.enter="analyzeStock"
          >
          <button @click="analyzeStock" class="analyze-btn">Analyze</button>
        </div>
      </div>

      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Analyzing stock data...</p>
      </div>

      <div v-if="analysisData" class="analysis-results">
        <div class="result-card">
          <h3>Prediction</h3>
          <div class="prediction-value">{{ analysisData.prediction }}</div>
        </div>

        <div class="result-card">
          <h3>Market Sentiment</h3>
          <div class="sentiment-score" :class="getSentimentClass(analysisData.sentiment)">
            {{ analysisData.sentiment.toFixed(2) }}
          </div>
        </div>

        <div class="result-card">
          <h3>Risk Assessment</h3>
          <div class="risk-level" :class="analysisData.riskLevel">
            {{ analysisData.riskLevel }}
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const ticker = ref('')
const loading = ref(false)
const analysisData = ref(null)

const getSentimentClass = (sentiment) => {
  if (sentiment > 0.6) return 'very-positive'
  if (sentiment > 0.2) return 'positive'
  if (sentiment > 0.05) return 'slightly-positive'
  if (sentiment >= -0.05) return 'neutral'
  if (sentiment > -0.2) return 'slightly-negative'
  if (sentiment > -0.6) return 'negative'
  return 'very-negative'
}


/*
const analyzeStock = async () => {
  if (!ticker.value) return
  
  loading.value = true
  // Simulated API call - replace with actual API integration
  setTimeout(() => {
    analysisData.value = {
      prediction: 'buy',
      sentiment: 75,
      riskLevel: 'Moderate'
    }
    loading.value = false
  }, 2000)
}*/

const analyzeStock = async () => {
  if (!ticker.value) return
  
  loading.value = true
  try {
    const response = await fetch(`http://localhost:8000/api/analysis/${ticker.value}`)
    if (!response.ok) {
      throw new Error('Failed to fetch analysis')
    }
    const analysis = await response.json()
    analysisData.value = {
      prediction: 'buy',
      sentiment: analysis.sentiment,
      riskLevel: 'Moderate'
    }
  } catch (error) {
    console.error('Error analyzing stock:', error)
    // You might want to show an error message to the user here
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.analysis {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
  padding: 2rem;
}

.analysis-header {
  text-align: center;
  margin-bottom: 3rem;
}

.analysis-header h1 {
  font-size: 2.5rem;
  color: #2d3748;
  margin-bottom: 1rem;
}

.analysis-header p {
  color: #4a5568;
  font-size: 1.1rem;
}

.analysis-content {
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

.analyze-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: transform 0.2s;
}

.analyze-btn:hover {
  transform: translateY(-2px);
}

.loading {
  text-align: center;
  padding: 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  margin: 0 auto 1rem;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.analysis-results {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 2rem;
}

.result-card {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.result-card h3 {
  color: #2d3748;
  margin-bottom: 1rem;
  font-size: 1.2rem;
}

.prediction-value {
  font-size: 2rem;
  font-weight: bold;
  color: #2d3748;
  text-transform: capitalize;
}

.sentiment-score {
  font-size: 2rem;
  font-weight: bold;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  transition: all 0.3s ease;
}

.sentiment-score.very-positive {
  background: #dcfce7;
  color: #166534;
}

.sentiment-score.positive {
  background: #bbf7d0;
  color: #166534;
}

.sentiment-score.slightly-positive {
  background: #f0fdf4;
  color: #166534;
}

.sentiment-score.neutral {
  background: #fef3c7;
  color: #92400e;
}

.sentiment-score.slightly-negative {
  background: #fef2f2;
  color: #991b1b;
}

.sentiment-score.negative {
  background: #fee2e2;
  color: #991b1b;
}

.sentiment-score.very-negative {
  background: #fecaca;
  color: #991b1b;
}

.risk-level {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 500;
}

.risk-level.Moderate {
  background: #fefcbf;
  color: #975a16;
}

@media (max-width: 768px) {
  .analysis {
    padding: 1rem;
  }

  .analysis-header h1 {
    font-size: 2rem;
  }

  .search-box {
    flex-direction: column;
  }

  .analyze-btn {
    width: 100%;
  }
}
</style> 