<template>
  <div class="candlestick-chart-container">
    <canvas ref="chartCanvas"></canvas>
    <div v-if="!props.data || props.data.length === 0" class="no-data">
      No chart data available
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue';
import {
  Chart,
  CategoryScale,
  LinearScale,
  TimeScale,
  Tooltip,
  Legend,
  LineElement,
  PointElement
} from 'chart.js';

// Import the financial chart controllers
import {
  CandlestickController,
  OhlcController,
  CandlestickElement,
  OhlcElement
} from 'chartjs-chart-financial';

import 'chartjs-adapter-date-fns';

// Register Chart.js components and financial chart types
Chart.register(
  CategoryScale,
  LinearScale,
  TimeScale,
  Tooltip,
  Legend,
  LineElement,
  PointElement,
  CandlestickController,
  CandlestickElement,
  OhlcController,
  OhlcElement
);

const props = defineProps({
  data: {
    type: Array,
    required: true
  },
  pattern: {
    type: String,
    required: true
  }
});

const chartCanvas = ref(null);
let chartInstance = null;

const createChart = () => {
  if (!chartCanvas.value || !props.data || props.data.length === 0) {
    return;
  }

  // Destroy existing chart if it exists
  if (chartInstance) {
    chartInstance.destroy();
    chartInstance = null;
  }

  const ctx = chartCanvas.value.getContext('2d');
  
  // Transform data for Chart.js financial format
  const chartData = props.data.map(item => ({
    x: new Date(item.timestamp).getTime(), // Use timestamp for better compatibility
    o: parseFloat(item.open),
    h: parseFloat(item.high),
    l: parseFloat(item.low),
    c: parseFloat(item.close)
  }));

  try {
    // Try candlestick chart first
    chartInstance = new Chart(ctx, {
      type: 'candlestick',
      data: {
        datasets: [{
          label: `${props.pattern} Pattern`,
          data: chartData,
          color: {
            up: '#00C851',    // Green for bullish candles
            down: '#ff4444',  // Red for bearish candles
            unchanged: '#999' // Gray for unchanged
          },
          borderColor: {
            up: '#00C851',
            down: '#ff4444',
            unchanged: '#999'
          }
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            type: 'time',
            time: {
              unit: 'minute',
              displayFormats: {
                minute: 'HH:mm'
              }
            },
            title: {
              display: true,
              text: 'Time'
            }
          },
          y: {
            title: {
              display: true,
              text: 'Price ($)'
            }
          }
        },
        plugins: {
          legend: {
            display: false
          },
          tooltip: {
            mode: 'index',
            intersect: false,
            callbacks: {
              label: function(context) {
                const point = context.parsed;
                if (point && typeof point === 'object' && 'o' in point) {
                  return [
                    `Open: $${point.o.toFixed(2)}`,
                    `High: $${point.h.toFixed(2)}`,
                    `Low: $${point.l.toFixed(2)}`,
                    `Close: $${point.c.toFixed(2)}`
                  ];
                }
                return 'Invalid data';
              }
            }
          }
        }
      }
    });
  } catch (error) {
    // Fallback to line chart using close prices
    try {
      const lineData = props.data.map(item => ({
        x: new Date(item.timestamp).getTime(),
        y: parseFloat(item.close)
      }));

      chartInstance = new Chart(ctx, {
        type: 'line',
        data: {
          datasets: [{
            label: `${props.pattern} Pattern (Close Prices)`,
            data: lineData,
            borderColor: '#764ba2',
            backgroundColor: 'rgba(118, 75, 162, 0.1)',
            tension: 0.1,
            fill: true
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            x: {
              type: 'time',
              time: {
                unit: 'minute',
                displayFormats: {
                  minute: 'HH:mm'
                }
              },
              title: {
                display: true,
                text: 'Time'
              }
            },
            y: {
              title: {
                display: true,
                text: 'Price ($)'
              }
            }
          },
          plugins: {
            legend: {
              display: false
            },
            tooltip: {
              mode: 'index',
              intersect: false,
              callbacks: {
                label: function(context) {
                  return `Close: $${context.parsed.y.toFixed(2)}`;
                }
              }
            }
          }
        }
      });
    } catch (fallbackError) {
      console.error('Chart creation failed:', fallbackError);
    }
  }
};

onMounted(() => {
  nextTick(() => {
    createChart();
  });
});

watch(() => props.data, (newData) => {
  createChart();
}, { deep: true });

watch(() => props.pattern, (newPattern) => {
  createChart();
});
</script>

<style scoped>
.candlestick-chart-container {
  width: 400px;
  height: 300px;
  background: white;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  position: relative;
}

.candlestick-chart-container canvas {
  width: 100% !important;
  height: 100% !important;
}

.no-data {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #666;
  font-style: italic;
}
</style> 