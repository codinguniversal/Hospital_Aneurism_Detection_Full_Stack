<template>
  <div class="dashboard-wrapper">
    <div class="dashboard-tabs">
      <button 
        @click="activeTab = 'config'" 
        class="tab-btn" 
        :class="{ active: activeTab === 'config' }"
      >
        <i class="fa fa-cogs"></i> System & AI Settings
      </button>
      <button 
        @click="activeTab = 'users'" 
        class="tab-btn" 
        :class="{ active: activeTab === 'users' }"
      >
        <i class="fa fa-users"></i> Manage Staff Registry
      </button>
    </div>

    <hr class="divider" />

    <div v-if="activeTab === 'config'" class="admin-grid">
      <div class="card-container">
        <div class="page-header">
          <h2><i class="fa fa-user-plus"></i> Register Staff Account</h2>
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
          <button type="submit" class="action-btn btn-green full-width" :disabled="submittingUser">
            {{ submittingUser ? 'Creating Account...' : 'Create Account' }}
          </button>
        </form>
      </div>

      <div class="card-container">
        <div class="page-header">
          <h2><i class="fa fa-cogs"></i> System & AI Configuration</h2>
        </div>
        <div v-if="loadingSettings" class="loading-state">
          <i class="fa fa-spinner fa-spin"></i> Loading system baseline records...
        </div>
        <form v-else @submit.prevent="saveSettings">
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
          <button type="submit" class="action-btn btn-outline-green full-width" :disabled="submittingSettings">
            {{ submittingSettings ? 'Saving...' : 'Save Configuration' }}
          </button>
        </form>
      </div>
    </div>

    <div v-if="activeTab === 'users'" class="card-container wide">
      <div class="page-header">
        <h2><i class="fa fa-users"></i> Manage Staff Accounts</h2>
      </div>
      <div v-if="loadingUsers" class="loading-state">
        <i class="fa fa-spinner fa-spin"></i> Loading system registry entries...
      </div>
      <table v-else class="clean-table">
        <thead>
          <tr>
            <th>Employee ID</th>
            <th>Email Address</th>
            <th>Role</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in users" :key="user.employee_id || user.employeeId || user.id">
            <td>
              <strong>{{ user.employee_id || user.employeeId || user.id }}</strong>
            </td>
            <td>{{ user.email }}</td>
            <td>
              <span class="badge" :class="user.role ? user.role.toLowerCase() : 'doctor'">
                {{ user.role || 'Doctor' }}
              </span>
            </td>
            <td>
              <button 
                @click="deleteUser(user.employee_id || user.employeeId || user.id)" 
                class="action-btn btn-danger"
                :disabled="(user.employee_id || user.employeeId || user.id) === '000001'"
              >
                <i class="fa fa-trash"></i> Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { settingsApi } from '../services/adminServices/settings.js' 
import { userService } from '../services/adminServices/manageUserService.js' 

// Tab Layout Control State
const activeTab = ref('config')

// Registration State
const newUser = ref({ employeeId: '', email: '', password: '' })
const submittingUser = ref(false)

// Configuration Panel State
const loadingSettings = ref(true)
const submittingSettings = ref(false)
const settings = ref({
  ai_api_url: '',
  ai_timeout_limit: 30000,
  automatic_scan_interval: 15,
  automatic_scan_start_hour: 1,
  automatic_scan_end_hour: 13,
  aneurysm_high_risk_threshold: 0.75,
  aneurysm_medium_risk_threshold: 0.30
})

// Registry Table State
const users = ref([])
const loadingUsers = ref(true)

const fetchCurrentSettings = async () => {
  try {
    loadingSettings.value = true
    const response = await settingsApi.getSettings()
    const backendData = response.data || response
    if (backendData) settings.value = { ...backendData }
  } catch (error) {
    console.error('Failed to query backend system parameters:', error)
  } finally {
    loadingSettings.value = false
  }
}

const fetchUsers = async () => {
  try {
    loadingUsers.value = true
    const response = await userService.getAllUsers()
    const responseData = response.data || response
    
    // Debug log to confirm key names during runtime
    console.log("USERS PAYLOAD SINK:", responseData)
    users.value = responseData
  } catch (error) {
    console.error('Failed to sync users registry:', error)
  } finally {
    loadingUsers.value = false
  }
}

const generateId = () => { 
  newUser.value.employeeId = Math.floor(100000 + Math.random() * 900000).toString() 
}

const handleRegister = async () => {
  const cleanId = newUser.value.employeeId.trim()
  if (!/^\d{6}$/.test(cleanId)) return alert("ID must be exactly 6 digits.")
  try {
    submittingUser.value = true
    await userService.register(cleanId, newUser.value.email.trim(), newUser.value.password)
    alert("Account Created Successfully!")
    newUser.value = { employeeId: '', email: '', password: '' }
    await fetchUsers()
  } catch (error) {
    console.error('Registration error:', error)
    alert('Failed to register user.')
  } finally {
    submittingUser.value = false
  }
}

const deleteUser = async (targetId) => {
  if (confirm(`Are you sure you want to completely delete staff user ${targetId}?`)) {
    try {
      await userService.deleteUser(targetId)
      users.value = users.value.filter(u => (u.employee_id || u.employeeId || u.id) !== targetId)
    } catch (error) {
      console.error('Account deletion failure:', error)
      alert('Failed to remove user account.')
    }
  }
}

// Watch active tab selection to download user rows
watch(activeTab, (newTab) => {
  if (newTab === 'users') fetchUsers()
})

onMounted(() => {
  fetchCurrentSettings()
})
</script>

<style scoped>
.dashboard-wrapper { width: 100%; max-width: 1100px; margin: 0 auto; padding-top: 10px; }
.dashboard-tabs { display: flex; gap: 10px; margin-bottom: 5px; }
.tab-btn { background: #f1f3f5; border: none; padding: 10px 20px; font-weight: 600; font-size: 15px; color: #495057; border-radius: 8px; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 8px; }
.tab-btn.active { background: #0aa159; color: white; }
.divider { border: 0; height: 1px; background: #e9ecef; margin: 20px 0 25px 0; }

.admin-grid { display: grid; grid-template-columns: 1fr 1.2fr; gap: 30px; }
.card-container { background: #ffffff; border-radius: 12px; padding: 30px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); height: max-content; }
.card-container.wide { width: 100%; box-sizing: border-box; }
.page-header { border-bottom: 2px solid #f0f2f5; padding-bottom: 15px; margin-bottom: 20px; }
.page-header h2 { color: #2c3e50; font-size: 20px; margin: 0; text-align: left; }

.form-group { margin-bottom: 20px; }
.settings-row { display: flex; gap: 15px; }
.half { flex: 1; }
.form-group label { display: block; font-size: 14px; font-weight: 600; color: #34495e; margin-bottom: 8px; text-align: left; }
.form-control { width: 100%; padding: 10px; border: 1px solid #dcdde1; border-radius: 8px; outline: none; box-sizing: border-box; }
.form-control:focus { border-color: #0aa159; }

.input-with-button { display: flex; gap: 10px; }
.time-grid { display: flex; align-items: flex-end; gap: 15px; }
.time-input-group { flex: 1; }
.sub-label { font-size: 12px; color: #7f8c8d; font-weight: 600; text-transform: uppercase; margin-bottom: 5px; display: block; text-align: left; }
.time-divider { padding-bottom: 10px; font-weight: 600; color: #95a5a6; }

/* Registry Table Styles */
.clean-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
.clean-table th { padding: 15px; background-color: #f8f9fa; color: #5c6bc0; font-weight: 700; font-size: 14px; text-transform: uppercase; border-bottom: 2px solid #e9ecef; text-align: left; }
.clean-table td { padding: 15px; border-bottom: 1px solid #e9ecef; vertical-align: middle; color: #34495e; text-align: left; }
.badge { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; display: inline-block; text-transform: capitalize; }
.badge.admin { background: #e3f2fd; color: #1565c0; }
.badge.radiologist { background: #e8f5e9; color: #43a047; }
.badge.doctor { background: #fff3e0; color: #ef6c00; }

.loading-state { text-align: center; padding: 40px; color: #7f8c8d; font-style: italic; }
.btn-outline-green { background: transparent; color: #0aa159; border: 1px solid #0aa159; }
.btn-outline-green:hover:not(:disabled) { background: #e8f5e9; }
.btn-grey { background: #f1f3f5; color: #495057; border: none; }
.full-width { width: 100%; padding: 12px; margin-top: 10px; }
.action-btn { border: none; border-radius: 8px; font-weight: 600; cursor: pointer; padding: 8px 16px; transition: all 0.2s; display: inline-flex; align-items: center; justify-content: center; gap: 6px; }
.action-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-green { background-color: #0aa159; color: white; }
.btn-green:hover:not(:disabled) { background-color: #088c4d; transform: translateY(-2px); }
.btn-danger { background: #ffebee; color: #e53935; border: 1px solid #ffcdd2; }
.btn-danger:hover:not(:disabled) { background: #e53935; color: white; }
</style>