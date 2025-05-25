<template>
    <h3 class="heading">Prediction</h3>
    <div class="trade-signal">{{ tradeSignal }}</div>
    <div v-if="papPattern && papPattern !== 'N/A'" class="pap-pattern">Pattern: {{ papPattern }}</div>
</template>

<script setup>
defineProps({
    tradeSignal: String,
    papPattern: String
});
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

.pap-pattern {
    font-size: 1.2rem;
    color: #764ba2;
    font-weight: 500;
}
</style>