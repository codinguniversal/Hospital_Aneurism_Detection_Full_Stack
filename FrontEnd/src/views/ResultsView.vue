<template>
  <div class="card-container wide">
    <div v-if="isLoading" class="loading-overlay">
      <i class="fa fa-spinner fa-spin"></i>
      <p>Loading Analysis Results & Imaging Series...</p>
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
          <p>ID: {{ patientId }} | Reviewing AI detection results and imaging</p>
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

      <div class="dicom-section">
        <h3><i class="fa fa-picture-o"></i> Medical Imaging (DICOM Viewer)</h3>
        
        <div v-if="dicomLoading" class="dicom-viewer-loading">
          <i class="fa fa-circle-o-notch fa-spin"></i> Loading Medical Imagery Engine Slices...
        </div>

        <div class="dicom-viewer-container" v-show="!dicomLoading">
          <div class="viewer-wrapper">
            <div id="cornerstone-element" ref="dicomCanvas" class="dicom-canvas" @wheel.prevent="handleScrollWheel"></div>
            
            <div class="viewer-overlay top-left">
              <p>Patient: {{ patientData.name }}</p>
              <p>ID: {{ patientId }}</p>
            </div>
            <div class="viewer-overlay top-right">
              <p>Modality: CTA</p>
              <p>Slice: {{ currentSliceIndex + 1 }} / {{ totalSlices }}</p>
            </div>
          </div>

          <div class="viewer-controls" v-if="totalSlices > 1">
            <button @click="stepSlice(-1)" class="step-btn"><i class="fa fa-chevron-left"></i></button>
            <input 
              type="range" 
              :min="0" 
              :max="totalSlices - 1" 
              v-model.number="currentSliceIndex" 
              @input="renderActiveSlice"
              class="slice-slider"
            />
            <button @click="stepSlice(1)" class="step-btn"><i class="fa fa-chevron-right"></i></button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick } from 'vue'
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

// 🌌 DICOM Engine Viewport States
const dicomCanvas = ref(null)
const dicomLoading = ref(false)
const currentSliceIndex = ref(0)
const totalSlices = ref(0)
let dicomImageIds = [] // Holds the parsed string array pointers to medical frames

const fetchPatientData = async () => {
  isLoading.value = true
  error.value = null
  try {
    const response = await patientService.getPatientResults(patientId)
    const rawData = response.data || response

    const activeScan = rawData.scans && rawData.scans.length > 0 ? rawData.scans[0] : null

    let computedAge = 'N/A'
    if (rawData.birth_date) {
      const birthYear = new Date(rawData.birth_date).getFullYear()
      const currentYear = new Date().getFullYear()
      computedAge = currentYear - birthYear
    }

    patientData.value = {
      name: rawData.patient_name || 'Unknown Patient',
      age: computedAge,
      sex: rawData.sex || 'N/A',
      scanId: activeScan ? activeScan.id : null,
      scanDate: activeScan ? activeScan.scan_date : null,
      urgency: activeScan?.results?.overall?.probability >= 0.7 ? 'High' : 'Low'
    }

    const scanResults = activeScan?.results
    if (scanResults && scanResults.locations) {
      allLocations.value = Object.keys(scanResults.locations)
        .map(key => ({
          name: key.replace(/([A-Z])/g, ' $1').trim(),
          probability: Math.round(scanResults.locations[key] * 100)
        }))
        .sort((a, b) => b.probability - a.probability)
    } else {
      allLocations.value = []
    }

    // Initialize DICOM Engine setup directly after verifying scan registration parameters
    if (patientData.value.scanId) {
      initDicomViewer(patientData.value.scanId)
    }
  } catch (err) {
    console.error('Failed fetching data pipeline window:', err)
    error.value = 'Failed loading patient analysis records.'
  } finally {
    isLoading.value = false
  }
}

// 🩻 Cornerstone JS Initialization & Image Stream Factory Routing Loop
const initDicomViewer = async (scanId) => {
  dicomLoading.value = true
  try {
    // Dynamic runtime safe-load hook checker to dynamically bind parsing scripts to DOM
    await loadCornerstoneLibraries()

    // Configure cornerstone structural properties
    const element = document.getElementById('cornerstone-element') || dicomCanvas.value
    if (!element) return
    
    // Register rendering frame layout with the native runtime context
    try {
      window.cornerstone.enable(element)
    } catch(e) { /* Catch initialization safety re-entry crashes */ }

    // FETCH DICOM FILES: Modify this URL route mapping rule configuration matching your back-end streaming configuration rules!
    // Since you are tracking binary files matching scan paths, this should return a JSON string array pointing to your slice instances or routes.
    // Replace with: const sliceUrls = await scanService.getScanSlices(scanId);
    
    // Fallback simulation mock layers if direct list array route isn't running yet:
    const mockTotalSlices = 24
    dicomImageIds = []
    for(let i = 1; i <= mockTotalSlices; i++) {
      // WADO plugin pattern linking directly to backend streaming slice binary objects
      dicomImageIds.push(`wadouri:http://localhost:8000/api/scans/${scanId}/slices/${i}`)
    }
    
    totalSlices.value = dicomImageIds.length
    currentSliceIndex.value = 0

    await renderActiveSlice()
  } catch (err) {
    console.error('Cornerstone graphics layout exception:', err)
  } finally {
    dicomLoading.value = false
  }
}

const renderActiveSlice = async () => {
  const element = document.getElementById('cornerstone-element')
  if (!element || !dicomImageIds.length) return

  try {
    const imageId = dicomImageIds[currentSliceIndex.value]
    const image = await window.cornerstone.loadImage(imageId)
    window.cornerstone.displayImage(element, image)
  } catch (err) {
    console.error('Image viewport execution breakdown:', err)
  }
}

const stepSlice = (direction) => {
  const nextIndex = currentSliceIndex.value + direction
  if (nextIndex >= 0 && nextIndex < totalSlices.value) {
    currentSliceIndex.value = nextIndex
    renderActiveSlice()
  }
}

const handleScrollWheel = (event) => {
  const direction = event.deltaY > 0 ? 1 : -1
  stepSlice(direction)
}

// Async dynamic dependency injector script factory mapping hook loaders
const loadCornerstoneLibraries = () => {
  return new Promise((resolve, reject) => {
    if (window.cornerstone && window.cornerstoneWADOImageLoader) return resolve()

    const cornerstoneScript = document.createElement('script')
    cornerstoneScript.src = 'https://unpkg.com/cornerstone-core@2.3.0/dist/cornerstone.js'
    document.head.appendChild(cornerstoneScript)

    cornerstoneScript.onload = () => {
      const loaderScript = document.createElement('script')
      loaderScript.src = 'https://unpkg.com/cornerstone-wado-image-loader@3.3.2/dist/cornerstoneWADOImageLoader.bundle.min.js'
      document.head.appendChild(loaderScript)
      
      loaderScript.onload = () => {
        // Initialize structural WADO loader hooks definitions
        window.cornerstoneWADOImageLoader.external.cornerstone = window.cornerstone
        resolve()
      }
      loaderScript.onerror = () => reject(new Error('WADO Bundle Script pipeline failure.'))
    }
    cornerstoneScript.onerror = () => reject(new Error('Cornerstone Core load breakdown.'))
  })
}

const handleRerun = async () => {
  if (!patientData.value.scanId) return
  isProcessing.value = true
  try {
    const analysisRequestData = {
      patient_name: patientData.value.name,
      scan_id: patientData.value.scanId
    }
    await scanService.analyzeScan(patientData.value.scanId, analysisRequestData)
    await fetchPatientData()
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

onBeforeUnmount(() => {
  const element = document.getElementById('cornerstone-element')
  if (element && window.cornerstone) {
    window.cornerstone.disable(element)
  }
})
</script>

<style scoped>
/* 🎨 EXISTING LAYOUT CORE STYLES */
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
.badge.low { background: #e8f5e9; color: #43a047; border: 1px solid #a5d6a7; }

.toggle-container { margin-top: 15px; }
.full-width { width: 100%; justify-content: center; }

/* 🖥️ DYNAMIC RETROFITTED CLINICAL VIEWER VIEWPORT STYLES */
.dicom-section h3 { color: #2c3e50; font-size: 18px; margin-top: 25px; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; }
.dicom-viewer-loading { background: #111; color: #0aa159; height: 420px; border-radius: 10px; display: flex; justify-content: center; align-items: center; font-size: 16px; gap: 10px; font-weight: 600; }
.dicom-viewer-container { background: #000; border-radius: 10px; border: 2px solid #2c3e50; overflow: hidden; display: flex; flex-direction: column; }
.viewer-wrapper { position: relative; width: 100%; height: 450px; background-color: #000; }
.dicom-canvas { width: 100%; height: 100%; cursor: row-resize; }
.viewer-overlay { position: absolute; color: #00ff00; font-family: monospace; font-size: 12px; pointer-events: none; padding: 12px; line-height: 1.4; text-shadow: 1px 1px 2px #000; }
.viewer-overlay.top-left { top: 0; left: 0; }
.viewer-overlay.top-right { top: 0; right: 0; text-align: right; }

.viewer-controls { background: #14191f; display: flex; align-items: center; gap: 15px; padding: 10px 20px; border-top: 1px solid #2c3e50; }
.slice-slider { flex: 1; accent-color: #0aa159; cursor: pointer; height: 6px; background: #232d38; border-radius: 3px; }
.step-btn { background: #232d38; color: #ecf0f1; border: none; padding: 6px 12px; border-radius: 4px; cursor: pointer; }
.step-btn:hover { background: #34495e; color: #0aa159; }

.loading-overlay, .error-container { text-align: center; padding: 80px; color: #7f8c8d; font-size: 16px; font-weight: 600; }
.loading-overlay i { font-size: 44px; color: #0aa159; margin-bottom: 15px; display: block; }
.action-btn { padding: 8px 16px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; display: inline-flex; align-items: center; gap: 6px; }
.btn-green { background-color: #0aa159; color: white; }
.btn-outline-green { background: transparent; color: #0aa159; border: 1px solid #0aa159; }
.btn-grey { background: #f1f3f5; color: #495057; }
</style>