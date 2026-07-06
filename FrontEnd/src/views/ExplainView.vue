<template>
  <div class="card-container wide">
    <div class="page-header flex-header">
      <div>
        <h1>GradCAM Explanations: {{ patientId }}</h1>
        <p>Paired original and highlighted slices returned by the analysis</p>
      </div>
      <button @click="goBack" class="action-btn btn-grey">
        <i class="fa fa-arrow-left"></i> Back to Results
      </button>
    </div>

    <div v-if="isLoading" class="state-message">Loading explanation slices...</div>
    <div v-else-if="error" class="state-message error-message">{{ error }}</div>

    <div v-else class="scan-grid">
      <div class="grid-col-header">Original Slice (Unhighlighted)</div>
      <div class="grid-col-header">GradCAM Result (Highlighted)</div>

      <template v-for="slice in slices" :key="slice.slice_index">
        <figure class="scan-box">
          <img :src="imageUrl(slice.raw_slice_image_ref)" :alt="`Original slice ${slice.slice_index}`" />
          <figcaption>Slice {{ slice.slice_index }} Original</figcaption>
        </figure>
        <figure class="scan-box highlight-box">
          <img :src="imageUrl(slice.overlay_slice_image_ref)" :alt="`GradCAM slice ${slice.slice_index}`" />
          <figcaption>
            Slice {{ slice.slice_index }} Heatmap · {{ formatImportance(slice.importance) }} importance
          </figcaption>
        </figure>
      </template>

      <div v-if="slices.length === 0" class="state-message empty-state">
        No GradCAM slices are stored for this scan yet. Rerun the analysis to generate them.
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { patientService } from '../services/doctorServices/patientService.js'
import { imageService } from '../services/doctorServices/imageService.js'

const router = useRouter()
const route = useRoute()
const patientId = route.params.id

const slices = ref([])
const isLoading = ref(true)
const error = ref('')

//delegate the URL creation directly to the communications infrastructure
const imageUrl = (imageRef) => imageService.getImageUrl(imageRef)

const formatImportance = (importance) => `${((importance || 0) * 100).toFixed(1)}%`

const loadExplanation = async () => {
  try {
    const response = await patientService.getPatientResults(patientId)
    const patient = response.data || response
    const scan = patient.scans?.[0]
    const explanations = scan?.results?.explainability || []
    slices.value = explanations[0]?.top_slices || []
  } catch (err) {
    console.error('Failed to load GradCAM explanation:', err)
    error.value = err.response?.data?.detail || err.message || 'Failed to load explanation slices.'
  } finally {
    isLoading.value = false
  }
}

const goBack = () => router.push(`/results/${patientId}`)

onMounted(loadExplanation)
</script>

<style scoped>
.card-container { width: 100%; }
.card-container.wide { max-width: 1000px; }
.flex-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; border-bottom: 2px solid #f0f2f5; padding-bottom: 15px; }
.page-header h1 { color: #2c3e50; font-size: 28px; margin-bottom: 5px; }
.page-header p { color: #7f8c8d; font-size: 15px; }
.scan-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; align-items: start; }
.grid-col-header { font-weight: 700; color: #2c3e50; text-align: center; padding-bottom: 10px; border-bottom: 2px solid #e9ecef; }
.scan-box { margin: 0; background: #111; min-height: 250px; border-radius: 8px; overflow: hidden; border: 1px solid #dcdde1; }
.scan-box img { display: block; width: 100%; height: 250px; object-fit: contain; background: #111; }
.scan-box figcaption { padding: 10px; color: #dfe6e9; text-align: center; background: #1a1a1a; }
.highlight-box { border: 2px solid #0aa159; box-shadow: 0 0 15px rgba(10, 161, 89, 0.1); }
.state-message { grid-column: 1 / -1; padding: 50px; text-align: center; color: #7f8c8d; }
.error-message { color: #c62828; }
.action-btn { padding: 8px 16px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; }
.btn-grey { background: #f1f3f5; color: #495057; }
@media (max-width: 760px) { .scan-grid { grid-template-columns: 1fr; } .grid-col-header { display: none; } }
</style>
