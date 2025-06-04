<template>
    <h3 class="heading">Price Targets</h3>
    <div class="price-targets">
        <div class="target-item">
            <span class="target-label">Take Profit</span>
            <span class="target-value">
            {{ takeProfit === 'N/A' 
                ? 'N/A' 
                : `${roundDecimal(takeProfit, 2)}` 
            }}
            </span>
        </div>
        <div class="target-item">
            <span class="target-label">Stop Loss</span>
            <span class="target-value">
            {{ stopLoss === 'N/A'
                ? 'N/A'
                : `${roundDecimal(stopLoss, 2)}` 
            }}
            </span>
        </div>
    </div>
</template>

<script setup>
import { roundDecimal } from '../utils/formatting';

defineProps({
    takeProfit: [Number, String],
    stopLoss: [Number, String]
});
</script>

<style scoped>
.heading {
    margin-bottom: 1rem;
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
</style>