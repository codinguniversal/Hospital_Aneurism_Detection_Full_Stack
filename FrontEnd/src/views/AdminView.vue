<template>
  <div class="admin-grid">
    
    <div class="card-container">
      <div class="page-header">
        <h2><i class="fa fa-user-plus"></i> Register Doctor Account</h2>
      </div>
      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label>Employee ID (6 Digits)</label>
          <div class="input-with-button">
            <input type="text" v-model="newUser.employeeId" class="form-control" placeholder="e.g., 654321" maxlength="6" required />
            <button type="button" @click="generateId" class="action-btn btn-grey">Generate</button>
          </div>
        </div>
        <div class="form-group">
          <label>Email</label>
          <input type="email" v-model="newUser.email" class="form-control" placeholder="e.g., doctor@hospital.org" required />
        </div>
        <div class="form-group">
          <label>Password</label>
          <input type="password" v-model="newUser.password" class="form-control" placeholder="Create a secure password" required />
        </div>
        <button type="submit" class="action-btn btn-green full-width">Create Account</button>
      </form>
    </div>

    <div class="card-container">
      <div class="page-header">
        <h2><i class="fa fa-cogs"></i> System & AI Configuration</h2>
      </div>
      <form @submit.prevent="saveSettings">
        
        <div class="form-group">
          <label>AI API URL</label>
          <input type="url" v-model="settings.ai_api_url" class="form-control" placeholder="https://..." required />
        </div>

        <div class="settings-row">
          <div class="form-group half">
            <label>AI Timeout Limit (ms)</label>
            <input type="number" v-model="settings.ai_timeout_limit" class="form-control" required />
          </div>
          <div class="form-group half">
            <label>Scan Interval (min)</label>
            <input type="number" v-model="settings.automatic_scan_interval" class="form-control" required />
          </div>
        </div>

        <div class="form-group">
          <label>Automatic Scan Window (24h Format)</label>
          <div class="time-grid">
            <div class="time-input-group">
              <label class="sub-label">Start Hour</label>
              <input type="number" v-model="settings.automatic_scan_start_hour" class="form-control" placeholder="e.g., 1" min="0" max="23" required />
            </div>
            <div class="time-divider">to</div>
            <div class="time-input-group">
              <label class="sub-label">End Hour</label>
              <input type="number" v-model="settings.automatic_scan_end_hour" class="form-control" placeholder="e.g., 13" min="0" max="23" required />
            </div>
          </div>
        </div>

        <div class="settings-row">
          <div class="form-group half">
            <label>High Risk Threshold (0.0 - 1.0)</label>
            <input type="number" step="0.01" min="0" max="1" v-model="settings.aneurysm_high_risk_threshold" class="form-control" required />
          </div>
          <div class="form-group half">
            <label>Medium Risk Threshold (0.0 - 1.0)</label>
            <input type="number" step="0.01" min="0" max="1" v-model="settings.aneurysm_medium_risk_threshold" class="form-control" required />
          </div>
        </div>

        <button type="submit" class="action-btn btn-outline-green full-width">Save Configuration</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const newUser = ref({ employeeId: '', email: '', password: '' })

// Centralized Settings Data Model
const settings = ref({
  ai_api_url: 'https://api.neuroscan.org/v1/analyze',
  ai_timeout_limit: 30000,
  automatic_scan_interval: 15,
  automatic_scan_start_hour: 1,
  automatic_scan_end_hour: 13,
  aneurysm_high_risk_threshold: 0.75,
  aneurysm_medium_risk_threshold: 0.30
})

const generateId = () => { 
  newUser.value.employeeId = Math.floor(100000 + Math.random() * 900000).toString() 
}

const handleRegister = () => {
  if (!/^\d{6}$/.test(newUser.value.employeeId.trim())) return alert("ID must be 6 digits.")
  alert("Account Created Successfully!")
  newUser.value = { employeeId: '', email: '', password: '' }
}

const saveSettings = () => { 
  console.log('Saved Configuration:', settings.value)
  alert('System settings updated successfully.') 
}
</script>

<style scoped>
.admin-grid { display: grid; grid-template-columns: 1fr 1.2fr; gap: 30px; width: 100%; max-width: 1100px; }
.card-container { background: #ffffff; border-radius: 12px; padding: 30px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); }
.page-header { border-bottom: 2px solid #f0f2f5; padding-bottom: 15px; margin-bottom: 20px; }
.page-header h2 { color: #2c3e50; font-size: 20px; }

/* Form Group Layouts */
.form-group { margin-bottom: 20px; }
.settings-row { display: flex; gap: 15px; }
.half { flex: 1; }

.form-group label { display: block; font-size: 14px; font-weight: 600; color: #34495e; margin-bottom: 8px; }
.form-control { width: 100%; padding: 10px; border: 1px solid #dcdde1; border-radius: 8px; outline: none; }
.form-control:focus { border-color: #0aa159; }
.form-control::placeholder { color: #b2bec3; }

/* Sub-layouts */
.input-with-button { display: flex; gap: 10px; }
.time-grid { display: flex; align-items: flex-end; gap: 15px; }
.time-input-group { flex: 1; }
.sub-label { font-size: 12px; color: #7f8c8d; font-weight: 600; text-transform: uppercase; margin-bottom: 5px; display: block; }
.time-divider { padding-bottom: 10px; font-weight: 600; color: #95a5a6; }

/* Buttons */
.btn-outline-green { background: transparent; color: #0aa159; border: 1px solid #0aa159; }
.btn-outline-green:hover { background: #e8f5e9; }
.btn-grey { background: #f1f3f5; color: #495057; border: none; }
.btn-grey:hover { background: #e9ecef; }
.full-width { width: 100%; padding: 12px; margin-top: 10px; }
.action-btn { border: none; border-radius: 8px; font-weight: 600; cursor: pointer; padding: 8px 16px; transition: all 0.2s; display: inline-flex; align-items: center; justify-content: center; gap: 6px; }
.btn-green { background-color: #0aa159; color: white; box-shadow: 0 4px 6px rgba(10, 161, 89, 0.2); }
.btn-green:hover { background-color: #088c4d; transform: translateY(-2px); }
</style>