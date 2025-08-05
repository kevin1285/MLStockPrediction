<template>
    <h3 class="heading">Prediction</h3>
    <div class="trade-signal">{{ tradeSignal }}</div>
    <div v-if="papPattern && papPattern !== 'N/A' && papPattern !== ''" class="pap-pattern-container">
        <div 
            class="pap-pattern"
            @mouseenter="showTooltip"
            @mouseleave="hideTooltip"
        >
            Pattern: {{ papPattern }}
            <span class="hover-indicator">🔍</span>
        </div>
        
        <!-- Tooltip with candlestick chart -->
        <div 
            v-if="isTooltipVisible" 
            class="chart-tooltip"
            :style="tooltipStyle"
        >
            <div v-if="!candlestickData || candlestickData.length === 0" class="no-chart-data">
                No chart data available
            </div>
            <CandlestickChart 
                v-else
                :data="candlestickData" 
                :pattern="papPattern"
            />
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import CandlestickChart from './CandlestickChart.vue';

const props = defineProps({
    tradeSignal: String,
    papPattern: String,
    candlestickData: Array
});

const isTooltipVisible = ref(false);
const tooltipStyle = ref({});

const showTooltip = (event) => {
    isTooltipVisible.value = true;
    
    // Position tooltip relative to the hovered element
    const rect = event.target.getBoundingClientRect();
    tooltipStyle.value = {
        top: `${rect.bottom + 10}px`,
        left: `${Math.max(10, rect.left - 200)}px`, // Prevent going off left edge
        position: 'fixed',
        zIndex: 1000
    };
};

const hideTooltip = () => {
    isTooltipVisible.value = false;
};
</script>

<style scoped>
.heading {
    margin-bottom: 1rem;
}

.trade-signal {
    font-size: 2rem;
    font-weight: bold;
    color: #2d3748;
    text-transform: capitalize;
    margin-bottom: 1rem;
}

.pap-pattern-container {
    position: relative;
}

.pap-pattern {
    font-size: 1.2rem;
    color: #764ba2;
    font-weight: 500;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    transition: background-color 0.2s ease;
}

.pap-pattern:hover {
    background-color: rgba(118, 75, 162, 0.1);
}

.hover-indicator {
    font-size: 0.8rem;
    opacity: 0.6;
    margin-left: 4px;
}

.chart-tooltip {
    position: fixed;
    background: white;
    border-radius: 8px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    z-index: 1000;
    max-width: 450px;
    border: 1px solid #e2e8f0;
}

.no-chart-data {
    padding: 20px;
    text-align: center;
    color: #666;
    font-style: italic;
}

/* Add a subtle animation for tooltip appearance */
.chart-tooltip {
    animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>