<template>
  <div class="card-container wide">
    <div class="page-header flex-header">
      <div>
        <h1>Patient Analysis: {{ patientId }}</h1>
        <p>Review AI detection results and imaging</p>
      </div>
      <div class="header-actions">
        <button @click="rerunAnalysis" class="action-btn btn-outline-green">
          <i class="fa fa-refresh"></i> Rerun Analysis
        </button>
        <button @click="explainResults" class="action-btn btn-green">
          <i class="fa fa-magic"></i> Explain Results
        </button>
        <button @click="goBack" class="action-btn btn-grey">
          <i class="fa fa-arrow-left"></i> Back
        </button>
      </div>
    </div>

    <div class="patient-dashboard-grid">
      <div class="dashboard-side">
        <div class="info-card">
          <h3><i class="fa fa-address-card-o"></i> Patient Details</h3>
          <div class="detail-row"><span>Name:</span> <strong>Ahmed Hassan</strong></div>
          <div class="detail-row"><span>Age / Sex:</span> <strong>54 / M</strong></div>
          <div class="detail-row"><span>Scan Date:</span> <strong>2026-06-15</strong></div>
          <div class="detail-row"><span>Modality:</span> <strong>CT Angiography</strong></div>
        </div>
      </div>

      <div class="dashboard-main">
        <div class="results-header">
          <h3><i class="fa fa-braille"></i> AI Aneurysm Detection Results</h3>
          <span class="badge high">Analysis Complete</span>
        </div>

        <table class="clean-table">
          <thead>
            <tr>
              <th>Arterial Location</th>
              <th>Probability</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="loc in displayedLocations" :key="loc.id">
              <td class="fw-bold">{{ loc.name }}</td>
              <td>
                <div class="probability-container">
                  <span class="prob-text">{{ loc.probability }}%</span>
                  <div class="prob-bar-bg">
                    <div class="prob-bar-fill" 
                         :style="{ width: loc.probability + '%' }"
                         :class="getRiskClass(loc.probability)">
                    </div>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="toggle-container">
          <button @click="toggleExpand" class="action-btn btn-outline-green full-width">
            <i class="fa" :class="expanded ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
            {{ expanded ? 'Show Top 5 Locations Only' : 'View All 13 Locations' }}
          </button>
        </div>
      </div>
    </div>

    <div class="dicom-section">
      <h3><i class="fa fa-picture-o"></i> Medical Imaging (DICOM Viewer)</h3>
      <div class="dicom-placeholder">
        <i class="fa fa-plus-square-o"></i>
        <p>DICOM Viewer Initialization Pending</p>
        <span class="dicom-subtext">Awaiting integration with imaging backend API.</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const patientId = route.params.id || 'Unknown Patient'
const expanded = ref(false)

const allLocations = ref([
  { id: 1, name: 'Anterior Communicating Artery (ACom)', probability: 92 },
  { id: 2, name: 'Middle Cerebral Artery (MCA) - Right', probability: 78 },
  { id: 3, name: 'Internal Carotid Artery (ICA) - Left', probability: 45 },
  { id: 4, name: 'Posterior Communicating Artery (PCom)', probability: 30 },
  { id: 5, name: 'Basilar Artery Tip', probability: 15 },
  { id: 6, name: 'Anterior Cerebral Artery (ACA)', probability: 12 },
  { id: 7, name: 'Posterior Cerebral Artery (PCA)', probability: 8 },
  { id: 8, name: 'Superior Cerebellar Artery (SCA)', probability: 5 },
  { id: 9, name: 'Anterior Inferior Cerebellar Artery (AICA)', probability: 4 },
  { id: 10, name: 'Posterior Inferior Cerebellar Artery (PICA)', probability: 3 },
  { id: 11, name: 'Vertebral Artery', probability: 2 },
  { id: 12, name: 'Ophthalmic Artery', probability: 1 },
  { id: 13, name: 'Pericallosal Artery', probability: 1 }
])

const displayedLocations = computed(() => expanded.value ? allLocations.value : allLocations.value.slice(0, 5))
const toggleExpand = () => expanded.value = !expanded.value

const rerunAnalysis = () => alert('Re-triggering AI model for this patient...')
const explainResults = () => router.push(`/explain/${patientId}`)
const goBack = () => router.push('/records')

const getRiskClass = (prob) => {
  if (prob >= 75) return 'high'
  if (prob >= 30) return 'medium'
  return 'low'
}
</script>

<style scoped>
.card-container { width: 100%; }
.card-container.wide { max-width: 1200px; }
.flex-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; border-bottom: 2px solid #f0f2f5; padding-bottom: 15px; }
.header-actions { display: flex; gap: 10px; }
.page-header h1 { color: #2c3e50; font-size: 28px; margin-bottom: 5px; }
.page-header p { color: #7f8c8d; font-size: 15px; }
.patient-dashboard-grid { display: grid; grid-template-columns: 1fr 2fr; gap: 30px; margin-bottom: 30px; }
@media (max-width: 900px) { .patient-dashboard-grid { grid-template-columns: 1fr; } }
.info-card { background: #f8f9fa; padding: 20px; border-radius: 10px; border: 1px solid #e9ecef; margin-bottom: 20px; }
.info-card h3 { color: #2c3e50; font-size: 16px; border-bottom: 1px solid #dcdde1; padding-bottom: 10px; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }
.detail-row { display: flex; justify-content: space-between; margin-bottom: 10px; font-size: 14px; }
.detail-row span { color: #7f8c8d; }
.detail-row strong { color: #2c3e50; }
.dashboard-main { background: #ffffff; border: 1px solid #e9ecef; border-radius: 10px; padding: 20px; }
.results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
.results-header h3 { color: #2c3e50; font-size: 18px; display: flex; align-items: center; gap: 8px; }
.clean-table { margin-bottom: 15px; }
.clean-table th { padding: 12px 15px; background-color: #f8f9fa; color: #5c6bc0; font-weight: 700; font-size: 13px; text-transform: uppercase; border-bottom: 2px solid #e9ecef; }
.clean-table td { padding: 12px 15px; border-bottom: 1px solid #e9ecef; vertical-align: middle; color: #34495e; font-size: 14px; }
.clean-table tbody tr:hover { background-color: #f8f9fa; }
.fw-bold { font-weight: 600; }
.probability-container { display: flex; align-items: center; gap: 10px; }
.prob-text { width: 40px; font-weight: 600; }
.prob-bar-bg { flex: 1; height: 8px; background: #e9ecef; border-radius: 4px; overflow: hidden; }
.prob-bar-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease-in-out; }
.prob-bar-fill.high { background: #e53935; }
.prob-bar-fill.medium { background: #f57c00; }
.prob-bar-fill.low { background: #43a047; }
.badge { padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
.badge.high { background: #ffebee; color: #e53935; border: 1px solid #ffcdd2; }
.dicom-section h3 { color: #2c3e50; font-size: 18px; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }
.dicom-placeholder { background: #1a1a1a; border-radius: 10px; height: 400px; display: flex; flex-direction: column; justify-content: center; align-items: center; color: #7f8c8d; border: 2px dashed #34495e; }
.dicom-placeholder i { font-size: 48px; color: #0aa159; margin-bottom: 15px; opacity: 0.8; }
.dicom-placeholder p { font-size: 18px; font-weight: 600; color: #ecf0f1; margin-bottom: 5px; }
.dicom-subtext { font-size: 14px; color: #95a5a6; }
</style>