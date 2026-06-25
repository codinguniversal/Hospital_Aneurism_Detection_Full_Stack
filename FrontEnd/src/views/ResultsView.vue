<template>
  <div class="card-container wide">
    <div v-if="isLoading" class="loading-overlay">
      <i class="fa fa-spinner fa-spin"></i>
      <p>Loading Analysis Results...</p>
    </div>

    <div v-if="error" class="error-container">
      <i class="fa fa-exclamation-triangle"></i>
      <p>{{ error }}</p>
      <button @click="goBack" class="action-btn btn-grey">Go Back to Records</button>
    </div>

    <template v-else>
      <div class="page-header flex-header">
        <div>
          <h1>Patient Analysis: {{ patientData.name }}</h1>
          <p>ID: {{ patientId }} | Reviewing AI detection results</p>
        </div>
        <div class="header-actions">
          <button @click="handleRerun" class="action-btn btn-outline-green" :disabled="isProcessing">
            <i class="fa fa-refresh" :class="{ 'fa-spin': isProcessing }"></i> Rerun Analysis
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
            <div class="detail-row"><span>Name:</span> <strong>{{ patientData.name }}</strong></div>
            <div class="detail-row"><span>Age / Sex:</span> <strong>{{ patientData.age || 'N/A' }} / {{ patientData.sex || 'N/A' }}</strong></div>
            <div class="detail-row"><span>Scan Date:</span> <strong>{{ formatDate(patientData.scanDate) }}</strong></div>
            <div class="detail-row"><span>Modality:</span> <strong>CT Angiography</strong></div>
          </div>
        </div>

        <div class="dashboard-main">
          <div class="results-header">
            <h3><i class="fa fa-braille"></i> AI Aneurysm Detection Results</h3>
            <span class="badge" :class="patientData.urgency?.toLowerCase() || 'low'">
              Urgency: {{ patientData.urgency }}
            </span>
          </div>

          <table class="clean-table">
            <thead>
              <tr>
                <th>Arterial Location</th>
                <th>Probability</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="loc in displayedLocations" :key="loc.name">
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
              <tr v-if="allLocations.length === 0">
                <td colspan="2" class="empty-results">No location probabilities calculated yet.</td>
              </tr>
            </tbody>
          </table>

          <div class="toggle-container" v-if="allLocations.length > 5">
            <button @click="toggleExpand" class="action-btn btn-outline-green full-width">
              <i class="fa" :class="expanded ? 'fa-chevron-up' : 'fa-chevron-down'"></i>
              {{ expanded ? 'Show Top 5 Locations Only' : `View All ${allLocations.length} Locations` }}
            </button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { patientService } from '../services/doctorServices/patientService.js'
import { scanService } from '../services/doctorServices/scanService.js'

const router = useRouter()
const route = useRoute()
const patientId = route.params.id

// Structural UI States
const isLoading = ref(true)
const isProcessing = ref(false)
const error = ref(null)
const expanded = ref(false)

// Backend Mapped Models
const patientData = ref({})
const allLocations = ref([])

// Helper to map and format data payloads adaptively
const parsePayload = (rawData) => {
  // 🔍 DEBUG TRACE LOGS
  console.log("%c=== DISPATCHING BACKEND DATA INSPECTION ===", "color: #1abc9c; font-weight: bold;");
  console.log("Raw Payload Arrived:", rawData);

  const isDirectScanSchema = !!rawData.scan_id;
  console.log("Is direct ScanAnalysisResponseSchema?", isDirectScanSchema);
  
  let activeScanId = null;
  let activeScanDate = null;
  let scanResultsObj = null;

  if (isDirectScanSchema) {
    activeScanId = rawData.scan_id;
    activeScanDate = rawData.analysis_timestamp;
    scanResultsObj = rawData.result;
  } else {
    console.log("Evaluating scans array field structural context...", rawData.scans);
    const scanContainer = rawData.scans && rawData.scans.length > 0 ? rawData.scans[0] : null;
    if (scanContainer) {
      activeScanId = scanContainer.id;
      activeScanDate = scanContainer.scan_date;
      scanResultsObj = scanContainer.result || scanContainer.results;
    }
  }

  console.log("Extracted Scan Results Sub-Object:", scanResultsObj);
  if (scanResultsObj) {
    console.log("Locations target raw evaluation block:", scanResultsObj.locations);
  }

  let computedAge = 'N/A';
  if (rawData.birth_date) {
    const birthYear = new Date(rawData.birth_date).getFullYear();
    const currentYear = new Date().getFullYear();
    computedAge = currentYear - birthYear;
  } else if (patientData.value.age) {
    computedAge = patientData.value.age;
  }

  const targetProbability = scanResultsObj?.overall?.probability || 0;
  
  patientData.value = {
    name: rawData.patient_name || patientData.value.name || 'Unknown Patient',
    age: computedAge,
    sex: rawData.sex || patientData.value.sex || 'N/A',
    scanId: activeScanId,
    scanDate: activeScanDate,
    urgency: targetProbability >= 0.7 ? 'High' : targetProbability >= 0.3 ? 'Medium' : 'Low'
  };
if (scanResultsObj && scanResultsObj.locations) {
  allLocations.value = Object.keys(scanResultsObj.locations)
    .map(key => {
      const rawValue = scanResultsObj.locations[key] || 0;
      const percentage = rawValue * 100;
      
      // If it's greater than 0 but ultra-low, show 3 decimal places. Otherwise, keep it clean.
      const formattedProbability = percentage > 0 && percentage < 1 
        ? parseFloat(percentage.toFixed(3)) 
        : parseFloat(percentage.toFixed(1));

      return {
        name: key.replace(/([A-Z])/g, ' $1').trim(),
        probability: formattedProbability
      };
    })
    .sort((a, b) => b.probability - a.probability);
}
}

const fetchPatientData = async () => {
  isLoading.value = true
  error.value = null
  try {
    const response = await patientService.getPatientResults(patientId)
    const rawData = response.data || response
    parsePayload(rawData)
  } catch (err) {
    console.error('Failed fetching data pipeline window:', err)
    error.value = 'Failed loading patient analysis records.'
  } finally {
    isLoading.value = false
  }
}

const handleRerun = async () => {
  if (!patientData.value.scanId) return
  isProcessing.value = true
  try {
    const analysisRequestData = {
      patient_name: patientData.value.name,
      scan_id: patientData.value.scanId
    }
    const response = await scanService.analyzeScan(patientData.value.scanId, analysisRequestData)
    const rawData = response.data || response
    
    // Parse the response schema directly instead of calling fetchPatientData again
    parsePayload(rawData)
    alert('Analysis completed successfully.')
  } catch (err) {
    alert('Rerun failed: ' + (err.response?.data?.detail || err.message))
  } finally {
    isProcessing.value = false
  }
}

const displayedLocations = computed(() => 
  expanded.value ? allLocations.value : allLocations.value.slice(0, 5)
)

const toggleExpand = () => expanded.value = !expanded.value
const explainResults = () => router.push(`/explain/${patientId}`)
const goBack = () => router.push('/records')

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  const parsed = new Date(dateStr)
  return isNaN(parsed.getTime()) ? dateStr : parsed.toLocaleDateString()
}

const getRiskClass = (prob) => {
  if (prob >= 75) return 'high'
  if (prob >= 30) return 'medium'
  return 'low'
}

onMounted(() => {
  fetchPatientData()
})
</script>

<style scoped>
.card-container { width: 100%; }
.card-container.wide { max-width: 1200px; margin: 0 auto; }
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

.clean-table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
.clean-table th { padding: 12px 15px; background-color: #f8f9fa; color: #5c6bc0; font-weight: 700; font-size: 13px; text-transform: uppercase; border-bottom: 2px solid #e9ecef; }
.clean-table td { padding: 12px 15px; border-bottom: 1px solid #e9ecef; vertical-align: middle; color: #34495e; font-size: 14px; text-align: left; }
.fw-bold { font-weight: 600; }
.empty-results { padding: 20px; text-align: center; color: #7f8c8d; font-style: italic; }

.probability-container { display: flex; align-items: center; gap: 10px; }
.prob-text { width: 45px; font-weight: 600; }
.prob-bar-bg { flex: 1; height: 8px; background: #e9ecef; border-radius: 4px; overflow: hidden; }
.prob-bar-fill { height: 100%; border-radius: 4px; transition: width 0.5s ease-in-out; }
.prob-bar-fill.high { background: #e53935; }
.prob-bar-fill.medium { background: #f57c00; }
.prob-bar-fill.low { background: #43a047; }

.badge { padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; text-transform: uppercase; }
.badge.high { background: #ffebee; color: #e53935; border: 1px solid #ffcdd2; }
.badge.medium { background: #fff3e0; color: #f57c00; border: 1px solid #ffe0b2; }
.badge.low { background: #e8f5e9; color: #43a047; border: 1px solid #a5d6a7; }

.toggle-container { margin-top: 15px; }
.full-width { width: 100%; justify-content: center; }

.loading-overlay, .error-container { text-align: center; padding: 80px; color: #7f8c8d; font-size: 16px; font-weight: 600; }
.loading-overlay i { font-size: 44px; color: #0aa159; margin-bottom: 15px; display: block; }
.action-btn { padding: 8px 16px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; }
.btn-green { background-color: #0aa159; color: white; }
.btn-outline-green { background: transparent; color: #0aa159; border: 1px solid #0aa159; }
.btn-grey { background: #f1f3f5; color: #495057; }
</style>