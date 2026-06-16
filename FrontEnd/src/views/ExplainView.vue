<template>
  <div class="card-container wide">
    <div class="page-header flex-header">
      <div>
        <h1>GradCAM Explanations: {{ patientId }}</h1>
        <p>Interpretability heatmaps for AI predictions</p>
      </div>
      <button @click="goBack" class="action-btn btn-grey">
        <i class="fa fa-arrow-left"></i> Back to Results
      </button>
    </div>

    <div class="scan-grid">
      <div class="grid-col-header">Original Slice (Unhighlighted)</div>
      <div class="grid-col-header">GradCAM Result (Highlighted)</div>

      <div class="scan-box"><p>Slice 42 Original</p></div>
      <div class="scan-box highlight-box"><p>Slice 42 Heatmap</p></div>

      <div class="scan-box"><p>Slice 45 Original</p></div>
      <div class="scan-box highlight-box"><p>Slice 45 Heatmap</p></div>

      <div class="scan-box"><p>Slice 48 Original</p></div>
      <div class="scan-box highlight-box"><p>Slice 48 Heatmap</p></div>
    </div>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
const router = useRouter()
const route = useRoute()
const patientId = route.params.id

const goBack = () => {
  router.push(`/results/${patientId}`)
}
</script>

<style scoped>
.card-container { background: #ffffff; border-radius: 12px; padding: 30px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); width: 100%; }
.card-container.wide { max-width: 1000px; }
.flex-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; border-bottom: 2px solid #f0f2f5; padding-bottom: 15px; }
.page-header h1 { color: #2c3e50; font-size: 28px; margin-bottom: 5px; }
.page-header p { color: #7f8c8d; font-size: 15px; }
.scan-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; align-items: center; }
.grid-col-header { font-weight: 700; color: #2c3e50; text-align: center; padding-bottom: 10px; border-bottom: 2px solid #e9ecef; }
.scan-box { background: #1a1a1a; height: 250px; border-radius: 8px; display: flex; align-items: center; justify-content: center; color: #7f8c8d; border: 1px solid #dcdde1; }
.highlight-box { border: 2px solid #0aa159; box-shadow: 0 0 15px rgba(10, 161, 89, 0.1); }
</style>