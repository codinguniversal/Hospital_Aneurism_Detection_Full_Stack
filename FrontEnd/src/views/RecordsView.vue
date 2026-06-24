<template>
  <div class="card-container wide">
    <div class="page-header flex-header">
      <div>
        <h1>Patient Records</h1>
        <p>Manage and analyze patient scans</p>
      </div>
      <button @click="refreshRecords" class="action-btn btn-outline-green">
        <i class="fa fa-refresh"></i> Refresh Records
      </button>
    </div>

    <div class="table-responsive">
      <table class="clean-table">
        <thead>
          <tr>
            <th>Patient Name</th>
            <th>Image Taken</th>
            <th>AI Analysis Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="record in records" :key="record.id">
            <td class="fw-bold">{{ record.name }}</td>
            <td>{{ record.imageDate }}</td>
            
            <td class="status-cell">
              <template v-if="!record.analyzed">
                <button @click="runAnalysis(record)" class="action-btn btn-green">
                  <i class="fa fa-play-circle"></i> Run AI Analysis
                </button>
              </template>
              
              <template v-else>
                <div class="results-data">
                  <span class="timestamp">Completed: {{ record.timestamp }}</span>
                  <span v-if="record.urgency" class="badge" :class="record.urgency.toLowerCase()">
                    Urgency: {{ record.urgency }}
                  </span>
                  <button @click="viewResults(record)" class="action-btn btn-outline-green">
                    <i class="fa fa-eye"></i> View Results
                  </button>
                </div>
              </template>
            </td>

            <td>
              <button @click="goToPatient(record.id)" class="action-btn btn-grey">
                Patient Details
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const records = ref([
  { id: 'PT-001', name: 'Ahmed Hassan', imageDate: '2026-06-15 10:30 AM', analyzed: true, timestamp: '2026-06-15 10:45 AM', urgency: 'High' },
  { id: 'PT-002', name: 'Sara Mahmoud', imageDate: '2026-06-15 11:15 AM', analyzed: false, timestamp: null, urgency: null },
  { id: 'PT-003', name: 'Omar Farouk', imageDate: '2026-06-14 02:00 PM', analyzed: true, timestamp: '2026-06-14 02:30 PM', urgency: 'Low' }
])

const refreshRecords = () => {
  // Logic to fetch latest records from backend goes here
  alert('Fetching latest patient records from database...')
}

const runAnalysis = (record) => { 
  alert(`Sending ${record.name}'s scans to AI Service...`) 
}

const viewResults = (record) => { 
  router.push(`/results/${record.id}`) 
}

const goToPatient = (patientId) => { 
  alert(`Navigating to General Patient Details for ${patientId}`) 
}
</script>

<style scoped>
.card-container {width: 100%;}
.card-container.wide { max-width: 1100px; }

/* FLEX HEADER FOR BUTTON ALIGNMENT */
.flex-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; border-bottom: 2px solid #f0f2f5; padding-bottom: 15px; }
.page-header h1 { color: #2c3e50; font-size: 28px; margin-bottom: 5px; }
.page-header p { color: #7f8c8d; font-size: 15px; }

.table-responsive { width: 100%; overflow-x: auto; }
.clean-table { width: 100%; border-collapse: collapse; text-align: left; }
.clean-table th { padding: 15px; background-color: #f8f9fa; color: #5c6bc0; font-weight: 700; font-size: 14px; text-transform: uppercase; border-bottom: 2px solid #e9ecef; }
.clean-table td { padding: 15px; border-bottom: 1px solid #e9ecef; vertical-align: middle; color: #34495e; }
.clean-table tbody tr:hover { background-color: #f8f9fa; }
.fw-bold { font-weight: 600; }

.status-cell { min-width: 250px; }
.results-data { display: flex; flex-direction: column; gap: 6px; align-items: flex-start; }
.timestamp { font-size: 12px; color: #7f8c8d; }

.badge { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; text-transform: uppercase; }
.badge.high { background: #ffebee; color: #e53935; }
.badge.medium { background: #fff8e1; color: #f57c00; }
.badge.low { background: #e8f5e9; color: #43a047; }

/* BUTTONS */
.action-btn { padding: 8px 16px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 6px; }
.btn-green { background-color: #0aa159; color: white; }
.btn-green:hover { background-color: #088c4d; }
.btn-outline-green { background: transparent; color: #0aa159; border: 1px solid #0aa159; }
.btn-outline-green:hover { background: #e8f5e9; }
.btn-grey { background: #f1f3f5; color: #495057; border: none; }
.btn-grey:hover { background: #e9ecef; }
</style>