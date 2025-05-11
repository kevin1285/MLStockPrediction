<!-- SentimentGauge.vue -->
<template>
  <div class="sentiment-gauge">
    <div class="sentiment-value">{{ roundDecimal(sentiment, 2) }}</div>

    <svg viewBox="0 0 200 110" class="gauge">
      <!-- colour band -->
      <defs>
        <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%"   stop-color="#ef4444"/>
          <stop offset="25%"  stop-color="#f97316"/>
          <stop offset="50%"  stop-color="#facc15"/>
          <stop offset="75%"  stop-color="#4ade80"/>
          <stop offset="100%" stop-color="#22c55e"/>
        </linearGradient>
      </defs>

      <!-- flat-ended semicircle -->
      <path
        d="M10 100 A90 90 0 0 1 190 100"
        fill="none"
        stroke="url(#gaugeGradient)"
        stroke-width="20"
        stroke-linecap="butt"   
      />

      <!-- Ring at the base -->
      <circle cx="100" cy="100" r="5" class="hub-ring"/>
      <!-- Needle -->
      <g :transform="`rotate(${needleAngle} 100 100)`" class="needle-group">
        <polygon points="104,104.5 96,104.5 100,30" class="needle-body"/>
      </g>
      <!-- White center cap (drawn last, so always on top) -->
      <circle cx="100" cy="100" r="3.5" fill="#fff"/>
    </svg>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({ sentiment: Number });

const needleAngle = computed(() => props.sentiment * 90);

const roundDecimal = (n, dp) => {
  const s = n.toFixed(dp);
  return Number(s) === 0 ? (0).toFixed(dp) : s;
};
</script>

<style scoped>
.sentiment-gauge{
  display:flex;
  flex-direction:column;
  align-items:center;
}

.sentiment-value{
  font-weight:600;
  margin-bottom:.25rem;
}

/* --- SVG sizing ---------------------------------------------------------- */
.gauge{ width:200px; height:110px; }

/* --- needle & hub styling ------------------------------------------------ */
.needle-group{
  transition:transform .4s cubic-bezier(.4,0,.2,1);
}

/* dark slate needle with a faint lift */
.needle-body{
  fill: #444;
  filter: drop-shadow(0 1px 1px rgba(0,0,0,.25));
}

/* dark inner cap */
.hub-cap{ fill:#1f2937; }

.hub-ring {
  fill: none;
  stroke: #444;
  stroke-width: 4;
}
</style>