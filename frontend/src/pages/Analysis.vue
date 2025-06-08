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
              <button 
                @click="settingsValid ? showSettings = false : null" 
                class="save-btn"
                :class="{ 'save-btn-disabled': !settingsValid }"
                :disabled="!settingsValid"
              >Save</button>
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
          <Prediction :tradeSignal="analysisData.tradeSignal" :papPattern="analysisData.papPattern"/>
        </div>

        <div class="result-card">
          <PriceTargets :takeProfit="analysisData.takeProfit" :stopLoss="analysisData.stopLoss" />
        </div>
        
        <div class="result-card">
          <Sentiment :sentiment="analysisData.sentiment" />
        </div>
        
        <News :articles="analysisData.articles"/>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useToast } from 'vue-toastification';
import Prediction from '../components/Prediction.vue';
import PriceTargets from '../components/PriceTargets.vue';
import Sentiment from '../components/Sentiment.vue';
import News from '../components/News.vue';

const api_root_url = import.meta.env.VITE_ENVIRONMENT === "PROD" ? "" : "http://localhost:8000";

const toast = useToast();

const ticker = ref('');
const loading = ref(false);
const analysisData = ref(null);
const showSettings = ref(false);
const settingsValid = ref(true);

const DEFAULT_RR_RATIO = 1.5;
const DEFAULT_ATR_SL_MULTIPLIER = 1.5;

const rrRatio = ref(DEFAULT_RR_RATIO);
const atrSlMultiplier = ref(DEFAULT_ATR_SL_MULTIPLIER);

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
  loading.value = true;
  try {
    const res = await fetch(`${api_root_url}/api/analysis/${ticker.value}?rr_ratio=${rrRatio.value}&atr_sl_multiplier=${atrSlMultiplier.value}`)
    const data = await res.json();

    if (!res.ok) {
      toast.error(data.detail || "Unexpected error occurred.");
      return;
    }
    
    analysisData.value = {
      tradeSignal: data.signal,
      sentiment: data.sentiment_score,
      takeProfit: data.take_profit,
      stopLoss: data.stop_loss,
      articles: data.articles,
      papPattern: data.pap_pattern
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

const validateSettings = () => {
  settingsValid.value = true;
  if (rrRatio.value < 0.5 || rrRatio.value > 10) {
    toast.error("Risk/Reward ratio must be between 0.5 and 10.");
    rrRatio.value = DEFAULT_RR_RATIO;
    settingsValid.value = false;
    return false;
  }

  if (atrSlMultiplier.value < 1 || atrSlMultiplier.value > 5) {
    toast.error("Stop-loss multiplier must be between 1.0 and 5.0.");
    atrSlMultiplier.value = DEFAULT_ATR_SL_MULTIPLIER;
    settingsValid.value = false;
    return false;
  }
  return true;
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

.save-btn-disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.save-btn-disabled:hover {
  transform: none !important;
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

.risk-level {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-weight: 500;
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
}
</style> 