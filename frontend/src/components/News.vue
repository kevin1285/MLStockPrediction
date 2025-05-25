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

@media (max-width: 768px) {
  .news-grid {
    grid-template-columns: 1fr;
  }
  
  .news-card {
    max-width: 100%;
  }
}
</style>