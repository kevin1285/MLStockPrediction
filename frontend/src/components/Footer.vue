<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-section">
        <h3>TradeSense</h3>
        <p>Making investment decisions smarter with machine learning</p>
      </div>
      
      <div class="footer-section">
        <h4>Quick Links</h4>
        <a href="#">Home</a>
        <a href="#">Analysis</a>
        <a href="#">Charts</a>
      </div>
      
      <div class="footer-section">
        <h4>Contact</h4>
        <p>Email: info@mltrading.com</p>
        <p>Phone: (555) 123-4567</p>
      </div>
    </div>
    
    <div class="footer-bottom">
      <p>&copy; 2025 TradeSense. All rights reserved.</p>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background: #2d3748;
  color: white;
  padding: 4rem 0 0;
  margin-top: 4rem;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 2rem;
}

.footer-section h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.footer-section h4 {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  color: #a0aec0;
}

.footer-section p {
  color: #cbd5e0;
  line-height: 1.6;
  margin-bottom: 0.5rem;
}

.footer-section a {
  display: block;
  color: #cbd5e0;
  text-decoration: none;
  margin-bottom: 0.5rem;
  transition: color 0.2s;
}

.footer-section a:hover {
  color: #667eea;
}

.footer-bottom {
  margin-top: 3rem;
  padding: 1.5rem 0;
  text-align: center;
  border-top: 1px solid #4a5568;
}

.footer-bottom p {
  color: #a0aec0;
}

@media (max-width: 768px) {
  .footer {
    padding: 3rem 0 0;
  }
  
  .footer-content {
    padding: 0 1rem;
  }
}
</style> 