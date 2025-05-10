<template>
  <div class="analysis">
    <section class="analysis-header">
      <h1>Stock Analysis</h1>
      <p>Enter a ticker to get started with our ML-powered analysis</p>
    </section>

    <section class="analysis-content">
      <div class="search-section">
        <div class="search-box">
          <button @click="showSettings = true" class="settings-btn">
            <span class="settings-icon">⚙️</span>
          </button>
          <input 
            type="text" 
            v-model="ticker" 
            placeholder="Enter ticker"
            @keyup.enter="analyzeStock"
          >
          <button @click="analyzeStock" class="analyze-btn">Analyze</button>
        </div>
      </div>

      <!-- Settings Modal -->
      <div v-if="showSettings" class="modal-overlay">
        <div class="modal-content" @click.stop>
          <h2>Risk Settings</h2>
          <div class="settings-form">
            <div class="setting-item">
              <label>Risk/Reward Ratio</label>
              <input 
                type="number" 
                v-model="rrRatio" 
                min="0.5" 
                max="10" 
                step="0.1"
                @change="validateSettings"
              >
              <p class="setting-description">How much reward per unit of risk (default: {{ DEFAULT_RR_RATIO }})</p>
            </div>
            <div class="setting-item">
              <label>ATR Stop Loss Multiplier</label>
              <input 
                type="number" 
                v-model="atrSlMultiplier" 
                min="1" 
                max="5" 
                step="0.1"
                @change="validateSettings"
              >
              <p class="setting-description">How many ATR units to use for stop loss (default: {{ DEFAULT_ATR_SL_MULTIPLIER }})</p>
            </div>
            <div class="modal-actions">
              <button @click="showSettings = false" class="cancel-btn">Cancel</button>
              <button @click="showSettings = false" class="save-btn">Save</button>
            </div>
          </div>
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
          <h3>Price Targets</h3>
          <div class="price-targets">
            <div class="target-item">
              <span class="target-label">Take Profit</span>
              <span class="target-value">${{ roundDecimal(analysisData.takeProfit, 2) }}</span>
            </div>
            <div class="target-item">
              <span class="target-label">Stop Loss</span>
              <span class="target-value">${{ roundDecimal(analysisData.stopLoss, 2) }}</span>
            </div>
          </div>
        </div>
        
        <div class="result-card">
          <h3>Market Sentiment</h3>
          <div class="sentiment-score" :class="getSentimentClass(analysisData.sentiment)">
            {{ roundDecimal(analysisData.sentiment, 2) }}
          </div>
        </div>

        <div class="news-section">
          <h3>Latest News</h3>
          <div class="news-grid">
            <a v-for="article in analysisData.articles" 
               :key="article.url" 
               :href="article.url" 
               target="_blank" 
               rel="noopener" 
               class="news-card">
              <div class="news-image" v-if="article.image_url">
                <img :src="article.image_url" :alt="article.title">
              </div>
              <div class="news-content">
                <div class="news-header">
                  <img v-if="article.publisher.logo_url" :src="article.publisher.logo_url" :alt="article.publisher.name" class="publisher-logo">
                  <span class="publisher-name">{{ article.publisher.name }}</span>
                  <span class="publish-date">{{ formatDate(article.published_utc) }}</span>
                </div>
                <h4 class="news-title">{{ article.title }}</h4>
                <p class="news-description" v-if="article.description">{{ article.description }}</p>
                <div class="news-footer">
                  <div class="news-meta">
                    <span v-if="article.author && article.author !== 'N/A'" class="author">By {{ article.author }}</span>
                    <span v-else class="author">By Unknown Author</span>
                    <div class="keywords" v-if="article.keywords && article.keywords.length">
                      <span v-for="keyword in article.keywords.slice(0, 3)" :key="keyword" class="keyword-tag">
                        {{ keyword }}
                      </span>
                    </div>
                  </div>
                  <div class="sentiment-indicator" :class="getSentimentClass(article.sentiment_score)">
                    {{ roundDecimal(article.sentiment_score, 2) }}
                  </div>
                </div>
              </div>
            </a>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useToast } from 'vue-toastification'

const toast = useToast();

const ticker = ref('')
const loading = ref(false)
const analysisData = ref(null)
const showSettings = ref(false)

const DEFAULT_RR_RATIO = 1.5;
const DEFAULT_ATR_SL_MULTIPLIER = 1.5;

const rrRatio = ref(DEFAULT_RR_RATIO)
const atrSlMultiplier = ref(DEFAULT_ATR_SL_MULTIPLIER)

const validateSettings = () => {
  if (rrRatio.value < 0.5 || rrRatio.value > 10) {
    toast.error("Risk/Reward ratio must be between 0.5 and 10.");
    rrRatio.value = DEFAULT_RR_RATIO;
  }

  if (atrSlMultiplier.value < 1 || atrSlMultiplier.value > 5) {
    toast.error("Stop-loss multiplier must be between 1.0 and 5.0.");
    atrSlMultiplier.value = DEFAULT_ATR_SL_MULTIPLIER;
  }
}

const roundDecimal = (num, decimalPlaces) => {
  const roundedStr = num.toFixed(decimalPlaces)
  return Number(roundedStr) === 0 ? (0).toFixed(decimalPlaces) : roundedStr;
}

const getSentimentClass = (sentiment) => {
  if (sentiment > 0.6) return 'very-positive'
  if (sentiment > 0.2) return 'positive'
  if (sentiment > 0.05) return 'slightly-positive'
  if (sentiment >= -0.05) return 'neutral'
  if (sentiment > -0.2) return 'slightly-negative'
  if (sentiment > -0.6) return 'negative'
  return 'very-negative'
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return new Intl.DateTimeFormat('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date)
}

const isMarketOpen = () => {
  return true;
  const curEST = new Date(new Date().toLocaleString('en-US', { timeZone: 'America/New_York' }));
  const day = curEST.getDay(); // 0 = Sunday, 6 = Saturday
  const curMin = 60*curEST.getHours() + curEST.getMinutes();
  const openMin = 60*9 + 30, closeMin = 60*16;
  return day >= 1 && day <= 5 && curMin >= openMin && curMin <= closeMin;
}
const analyzeStock = async () => {
  if (!isMarketOpen()) {
    toast.error("Market is closed");
    return;
  }
  loading.value = true
  try {
    const res = await fetch(`http://localhost:8000/api/analysis/${ticker.value}?rr_ratio=${rrRatio.value}&atr_sl_multiplier=${atrSlMultiplier.value}`)
    if (res.status === 404) {
      toast.error("Invalid ticker symbol. Please try again.");
      return;
    }
    if (!res.ok) {
      toast.error("Unexpected error occurred.");
      return
    }
    const analysis = await res.json();
    analysisData.value = {
      prediction: analysis.signal,
      sentiment: analysis.sentiment_score,
      takeProfit: analysis.take_profit,
      stopLoss: analysis.stop_loss,
      articles: analysis.articles
    };
  } catch (error) {
    if (error instanceof TypeError && error.message.includes("Failed to fetch")) {
      toast.error("Unable to reach the analysis server.");
    } else {
      toast.error("An unexpected error occurred.");
    }
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

.price-targets {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.target-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8fafc;
  border-radius: 8px;
}

.target-label {
  color: #4a5568;
  font-weight: 500;
}

.target-value {
  font-size: 1.25rem;
  font-weight: bold;
  color: #2d3748;
}

.news-section {
  grid-column: 1 / -1;
  background: white;
  padding: 2rem;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.news-section h3 {
  color: #2d3748;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.news-card {
  background: #f8fafc;
  border-radius: 8px;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  cursor: pointer;
  text-decoration: none;
  display: block;
  color: inherit;
}

.news-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
}

.news-image {
  width: 100%;
  height: 200px;
  overflow: hidden;
}

.news-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.news-content {
  padding: 1.5rem;
}

.news-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.publisher-logo {
  width: 24px;
  height: 24px;
  border-radius: 4px;
}

.publisher-name {
  font-weight: 500;
  color: #4a5568;
}

.publish-date {
  margin-left: auto;
  font-size: 0.875rem;
  color: #718096;
}

.news-title {
  margin: 0 0 0.75rem;
  font-size: 1.25rem;
  line-height: 1.4;
  color: #2d3748;
}

.news-title:hover {
  color: #4a5568;
}

.news-description {
  color: #4a5568;
  font-size: 0.875rem;
  line-height: 1.5;
  margin-bottom: 1rem;
}

.news-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.news-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.author {
  font-size: 0.875rem;
  color: #4a5568;
}

.keywords {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.keyword-tag {
  background: #edf2f7;
  color: #4a5568;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
}

.sentiment-indicator {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.settings-btn {
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.settings-btn:hover {
  background: #e2e8f0;
}

.settings-icon {
  font-size: 1.2rem;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 2rem;
  border-radius: 10px;
  width: 90%;
  max-width: 500px;
}

.modal-content h2 {
  color: #2d3748;
  margin-bottom: 1.5rem;
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.setting-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.setting-item label {
  font-weight: 500;
  color: #4a5568;
}

.setting-item input {
  padding: 0.5rem;
  border: 2px solid #e2e8f0;
  border-radius: 6px;
  font-size: 1rem;
}

.setting-description {
  font-size: 0.875rem;
  color: #718096;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}

.cancel-btn, .save-btn {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background: #f8fafc;
  border: 2px solid #e2e8f0;
  color: #4a5568;
}

.save-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
}

.cancel-btn:hover {
  background: #e2e8f0;
}

.save-btn:hover {
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .analysis {
    padding: 1rem;
  }

  .analysis-header h1 {
    font-size: 2rem;
  }

  .search-box {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .search-box input {
    flex: 1;
    min-width: 200px;
  }

  .analyze-btn, .settings-btn {
    flex: 0 0 auto;
  }

  .news-grid {
    grid-template-columns: 1fr;
  }
  
  .news-card {
    max-width: 100%;
  }
}
</style> 