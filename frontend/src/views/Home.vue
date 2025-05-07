<template>
  <div class="home">
    <section class="hero">
      <h1>Welcome to TradeSense</h1>
      <p>Leverage the power of machine learning to make smarter trading decisions</p>
      <button class="cta-button">Get Started</button>
    </section>

    <section class="features">
      <div class="feature-card">
        <div class="icon">📈</div>
        <h3>Real-time Analysis</h3>
        <p>Get instant trading recommendations based on the latest market data</p>
      </div>

      <div class="feature-card">
        <div class="icon">🤖</div>
        <h3>ML-Powered</h3>
        <p>Advanced machine learning algorithms analyze market patterns and trends</p>
      </div>

      <div class="feature-card">
        <div class="icon">📊</div>
        <h3>Market Sentiment</h3>
        <p>Understand market sentiment with our comprehensive analysis tools</p>
      </div>
    </section>
  </div>
</template>

<script setup>
// Component logic here if needed
</script>

<style scoped>
.home {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8f0 100%);
}

.hero {
  text-align: center;
  padding: 80px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
  font-weight: bold;
}

.hero p {
  font-size: 1.2rem;
  margin-bottom: 2rem;
  opacity: 0.9;
}

.cta-button {
  background: white;
  color: #764ba2;
  border: none;
  padding: 12px 30px;
  font-size: 1.1rem;
  border-radius: 25px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.cta-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.features {
  max-width: 1200px;
  margin: -50px auto 0;
  padding: 0 20px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
}

.feature-card {
  background: white;
  padding: 30px;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #333;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .hero h1 {
    font-size: 2.5rem;
  }
  
  .features {
    margin-top: -30px;
  }
}
</style> 