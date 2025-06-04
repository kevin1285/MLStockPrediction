<template>
    <div class="news-section" v-if="articles?.length">
        <h3>Latest News</h3>
        <div class="news-grid">
            <a v-for="article in articles" 
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
                        <span class="publisher-name">{{ article.publisher }}</span>
                        <span class="publish-date">{{ formatDate(article.published_utc) }}</span>
                    </div>
                    <h4 class="news-title">{{ article.title }}</h4>
                    <p class="news-description" v-if="article.description">{{ article.description }}</p>
                    <div class="news-footer">
                        <div class="news-meta">
                        <span v-if="article.author && article.author !== 'N/A'" class="author">By {{ article.author }}</span>
                        <span v-else class="author">By Unknown Author</span>
                        </div>
                        <span>{{ roundDecimal(article.sentiment_score, 2) }}</span>
                    </div>
                </div>
            </a>
        </div>
    </div>
</template>


<script setup>
import { formatDate, roundDecimal } from '../utils/formatting';

defineProps({
    articles: Array
})

</script>


<style scoped>
.news-section {
  grid-column: 1 / -1;
  background: white;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.news-section h3 {
  color: #2d3748;
  margin-bottom: 1.5rem;
  font-size: 1.75rem;
  font-weight: 600;
  position: relative;
  padding-bottom: 0.5rem;
}

.news-section h3::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 60px;
  height: 3px;
  background: #4299e1;
  border-radius: 2px;
}

.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 2rem;
}

.news-card {
  background: #f8fafc;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
  cursor: pointer;
  text-decoration: none;
  display: block;
  color: inherit;
  border: 1px solid #e2e8f0;
}

.news-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 20px rgba(0, 0, 0, 0.08);
  border-color: #cbd5e0;
}

.news-image {
  width: 100%;
  height: 220px;
  overflow: hidden;
  position: relative;
}

.news-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.news-card:hover .news-image img {
  transform: scale(1.05);
}

.news-content {
  padding: 1.75rem;
}

.news-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.publisher-logo {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  object-fit: cover;
  border: 1px solid #e2e8f0;
}

.publisher-name {
  font-weight: 600;
  color: #4a5568;
  font-size: 0.95rem;
}

.publish-date {
  margin-left: auto;
  font-size: 0.875rem;
  color: #718096;
  background: #edf2f7;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
}

.news-title {
  margin: 0 0 1rem;
  font-size: 1.35rem;
  line-height: 1.4;
  color: #2d3748;
  font-weight: 600;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-title:hover {
  color: #4a5568;
}

.news-description {
  color: #4a5568;
  font-size: 0.95rem;
  line-height: 1.6;
  margin-bottom: 1.25rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1.25rem;
  padding-top: 1.25rem;
  border-top: 1px solid #e2e8f0;
}

.news-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.author {
  font-size: 0.9rem;
  color: #4a5568;
  font-weight: 500;
}

@media (max-width: 768px) {
  .news-section {
    padding: 1.5rem;
  }
  
  .news-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
  
  .news-card {
    max-width: 100%;
  }
  
  .news-image {
    height: 200px;
  }
}
</style>