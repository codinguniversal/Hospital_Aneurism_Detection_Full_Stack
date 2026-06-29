<template>
  <div class="card-container wide">
    <div class="page-header flex-header">
      <div>
        <h1>Patient Records</h1>
        <p>Manage and analyze patient scans</p>
      </div>
      <button @click="refreshRecords" class="action-btn btn-outline-green" :disabled="isLoading">
        <i class="fa fa-refresh" :class="{ 'fa-spin': isLoading }"></i> Refresh Records
      </button>
    </div>

    <div class="table-responsive">
      <div v-if="isLoading" class="loading-state">
        Loading patient records...
      </div>
      
      <table v-else class="clean-table">
        <thead>
          <tr>
            <th>Patient Name</th>
            <th>Assigned Doctor</th>
            <th>Image Taken</th>
            <th>AI Analysis Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="record in records" :key="record.id">
            <td class="fw-bold">{{ record.name }}</td>
            <td>{{ record.assignedDoc }}</td>
            <td>{{ record.imageDate }}</td>
            
            <td class="status-cell">
              <div v-if="!record.analyzed">
                <span class="status-placeholder-text">
                  <i class="fa fa-circle-o-notch"></i> Awaiting Analysis
                </span>
              </div>
              
              <div v-else class="results-data">
                <span class="timestamp">Completed: {{ record.timestamp }}</span>
                <span v-if="record.urgency" class="badge" :class="record.urgency.toLowerCase()">
                  Urgency: {{ record.urgency }}
                </span>
              </div>
            </td>

            <td>
              <div v-if="!record.analyzed">
                <AiLoader v-if="processingScans[record.id]" />

                <button 
                  v-else
                  @click="runAnalysis(record)" 
                  class="action-btn btn-green"
                >
                  <i class="fa fa-play-circle"></i>
                  Run AI Analysis
                </button>
              </div>

              <div v-else>
                <button @click="viewResults(record.id)" class="action-btn btn-outline-blue">
                  <i class="fa fa-file-text-o"></i> View Results
                </button>
              </div>
            </td>
            
          </tr>
          
          <tr v-if="records.length === 0">
            <td colspan="4" class="empty-row">No patient records available.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { patientService } from '../services/doctorServices/patientService.js'
import { scanService } from '../services/doctorServices/scanService.js'
import AiLoader from '../components/common/AiLoader.vue'

const router = useRouter()
const records = ref([])
const isLoading = ref(false)
const processingScans = ref({})

const fetchRecords = async () => {
  isLoading.value = true
  try {
    const response = await patientService.getAllRecords()
    const rawData = response.data || response
    
    console.log('RAW BACKEND DATA ARRIVED:', rawData)

    records.value = rawData.map(patient => {
      let formattedDate = 'N/A'
      if (patient.scan_date) {
        const dateObj = new Date(patient.scan_date)
        formattedDate = isNaN(dateObj.getTime()) 
          ? patient.scan_date 
          : dateObj.toLocaleString()
      }

      return {
        id: patient.id,          
        scanId: patient.scan_id, 
        name: patient.name || 'Unknown Patient',
        assignedDoc: patient.assigned_doc || 'Unassigned',
        imageDate: formattedDate,
        analyzed: patient.analyzed || false, 
        timestamp: patient.scan_analysis_date 
          ? new Date(patient.scan_analysis_date).toLocaleString() 
          : 'N/A',
        urgency: patient.urgency || null
      }
    })
  } catch (error) {
    console.error('Error fetching patient records:', error)
    const detail = error.response?.data?.detail || error.message || 'Unknown server error'
    alert(`Failed to load patient records: ${detail}`)
  } finally {
    isLoading.value = false
  }
}

const refreshRecords = () => {
  fetchRecords()
}

const runAnalysis = async (record) => { 
  processingScans.value[record.id] = true
  try {
    const analysisRequestData = {
      patient_name: record.name,
      scan_id: record.scanId
    } 
    
    const response = await scanService.analyzeScan(record.scanId, analysisRequestData)
    const resultData = response.data || response
    
    alert(`AI Analysis finalized successfully for ${record.name}!`)
    
    record.analyzed = true
    record.timestamp = resultData.analysis_timestamp  
      ? new Date(resultData.analysis_timestamp).toLocaleString()  
      : new Date().toLocaleString()
    
    record.urgency = resultData.urgency || 'Unknown'
  } catch (error) {
    console.error('AI Analysis execution fault:', error)
    alert(`Analysis failed: ${error.response?.data?.detail || error.message || 'Server connection error'}`)
  } finally {
    delete processingScans.value[record.id]
  }
}

const viewResults = (patientId) => { 
  router.push(`/results/${patientId}`) 
}

onMounted(() => {
  fetchRecords()
})
</script>

<style scoped>
.card-container { width: 100%; }
.card-container.wide { max-width: 1100px; margin: 0 auto; }

.flex-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; border-bottom: 2px solid #f0f2f5; padding-bottom: 15px; }
.page-header h1 { color: #2c3e50; font-size: 28px; margin-bottom: 5px; }
.page-header p { color: #7f8c8d; font-size: 15px; }

.table-responsive { width: 100%; overflow-x: auto; }
.clean-table { width: 100%; border-collapse: collapse; text-align: left; }
.clean-table th { padding: 15px; background-color: #f8f9fa; color: #5c6bc0; font-weight: 700; font-size: 14px; text-transform: uppercase; border-bottom: 2px solid #e9ecef; }
.clean-table td { padding: 15px; border-bottom: 1px solid #e9ecef; vertical-align: middle; color: #34495e; }
.clean-table tbody tr:hover { background-color: #f8f9fa; }
.fw-bold { font-weight: 600; }

.status-cell { min-width: 220px; }
.status-placeholder-text { font-size: 13px; color: #94a3b8; font-style: italic; display: inline-flex; align-items: center; gap: 6px; }
.results-data { display: flex; flex-direction: column; gap: 6px; align-items: flex-start; }
.timestamp { font-size: 12px; color: #7f8c8d; }

.badge { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; text-transform: uppercase; }
.badge.high { background: #ffebee; color: #e53935; }
.badge.medium { background: #fff8e1; color: #f57c00; }
.badge.low { background: #e8f5e9; color: #43a047; }

.loading-state { padding: 30px; text-align: center; color: #7f8c8d; font-weight: 600; }
.empty-row { text-align: center; color: #7f8c8d; padding: 30px !important; font-style: italic; }

.action-btn { 
  padding: 8px 16px; 
  border: none; 
  border-radius: 8px; 
  font-size: 14px; 
  font-weight: 600; 
  cursor: pointer; 
  transition: all 0.2s; 
  display: inline-flex; 
  align-items: center; 
  gap: 6px; 
  width: 153.5px;
  height: 37px;
  justify-content: center;
  box-sizing: border-box;
}
.action-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-green { background-color: #0aa159; color: white; }
.btn-green:hover { background-color: #088c4d; }
.btn-outline-green { background: transparent; color: #0aa159; border: 1px solid #0aa159; width: auto; }
.btn-outline-green:hover { background: #e8f5e9; }
.btn-grey { background: #f1f3f5; color: #495057; border: none; }
.btn-grey:hover { background: #e9ecef; }

.btn-outline-blue { background: transparent; color: #5c6bc0; border: 1px solid #5c6bc0; }
.btn-outline-blue:hover { background: #f0f2f5; color: #3f51b5; }
</style>