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

        <div class="news-section">
          <h3>Latest News</h3>
          <div class="news-grid">
            <div v-for="article in analysisData.articles" :key="article.url" class="news-card">
              <div class="news-image" v-if="article.image_url">
                <img :src="article.image_url" :alt="article.title">
              </div>
              <div class="news-content">
                <div class="news-header">
                  <img v-if="article.publisher.logo_url" :src="article.publisher.logo_url" :alt="article.publisher.name" class="publisher-logo">
                  <span class="publisher-name">{{ article.publisher.name }}</span>
                  <span class="publish-date">{{ formatDate(article.published_utc) }}</span>
                </div>
                <h4 class="news-title">
                  <a :href="article.url" target="_blank" rel="noopener">{{ article.title }}</a>
                </h4>
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
                    {{ article.sentiment_score.toFixed(2) }}
                  </div>
                </div>
              </div>
            </div>
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

const analyzeStock = async () => {
  loading.value = true
  try {
    const response = await fetch(`http://localhost:8000/api/analysis/${ticker.value}`)
    if (response.status === 404) {
      toast.error("Invalid ticker symbol. Please try again.");
      console.log("404 error reachhhhheddddd");
      //alert("404 reached");
      return;
    }
    if (!response.ok) {
      console.log("got some other error");
      return
    }
    const analysis = await response.json();
    console.log(analysis);
    analysisData.value = {
      prediction: analysis.signal,
      sentiment: analysis.sentiment_score,
      riskLevel: 'Moderate',
      articles: analysis.articles
    };
  } catch (error) {
    console.error('Error analyzing stock:', error)
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
}

.news-title a {
  color: #2d3748;
  text-decoration: none;
}

.news-title a:hover {
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

  .news-grid {
    grid-template-columns: 1fr;
  }
  
  .news-card {
    max-width: 100%;
  }
}
</style> 