<template>
  <div class="card-container wide flex-card">
    <div class="admin-tabs fixed-tabs">
      <button 
        class="tab-btn" 
        :class="{ active: currentTab === 'manage' }" 
        @click="currentTab = 'manage'">
        Manage Users
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: currentTab === 'settings' }" 
        @click="currentTab = 'settings'">
        System Settings
      </button>
      <button 
        class="tab-btn" 
        :class="{ active: currentTab === 'register' }" 
        @click="currentTab = 'register'">
        Register Staff
      </button>
    </div>

    <div v-if="currentTab === 'manage'" class="tab-content">
      <div class="page-header">
        <h2>Manage Staff Accounts</h2>
        <p>View and remove active personnel</p>
      </div>

      <div v-if="isLoadingUsers" class="loading-state">
        Loading backend staff records...
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
          <tr v-for="user in filteredStaff" :key="user.employee_id || user.id">
            <td><strong>{{ user.employee_id || user.id }}</strong></td>
            <td>{{ user.email }}</td>
            <td><span class="badge">{{ user.role || 'Doctor' }}</span></td>
            <td>
              <button @click="handleDeleteUser(user.employee_id || user.id)" class="action-btn btn-danger">
                Delete
              </button>
            </td>
          </tr>
          <tr v-if="filteredStaff.length === 0">
            <td colspan="4" class="empty-row text-center">No staff accounts found in the database.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="currentTab === 'settings'" class="tab-content">
      <div class="page-header flex-header">
        <div>
          <h2>System & AI Configuration</h2>
          <p>Global parameters for the NeuroScan backend</p>
        </div>
        <button v-if="!isEditingSettings" @click="isEditingSettings = true" class="action-btn btn-outline-green">
          Edit Mode
        </button>
      </div>

      <form @submit.prevent="saveSettings" class="settings-form">
        <div class="form-group">
          <label>AI API URL</label>
          <input type="url" v-model="settings.ai_api_url" class="form-control" :disabled="!isEditingSettings" autocomplete="off" required />
        </div>

        <div class="settings-row">
          <div class="form-group half">
            <label>API Timeout Limit (ms)</label>
            <input type="number" v-model="settings.ai_timeout_limit" class="form-control" :disabled="!isEditingSettings" autocomplete="off" required />
          </div>
          <div class="form-group half">
            <label>Scan Interval (min)</label>
            <input type="number" v-model="settings.automatic_scan_interval" class="form-control" :disabled="!isEditingSettings" autocomplete="off" required />
          </div>
        </div>

        <div class="form-group">
          <label>Automatic Scan Window (24h Format)</label>
          <div class="time-grid">
            <div class="time-input-group">
              <label class="sub-label">Start Hour</label>
              <input type="number" v-model="settings.automatic_scan_start_hour" class="form-control" min="0" max="23" :disabled="!isEditingSettings" autocomplete="off" required />
            </div>
            <div class="time-divider">to</div>
            <div class="time-input-group">
              <label class="sub-label">End Hour</label>
              <input type="number" v-model="settings.automatic_scan_end_hour" class="form-control" min="0" max="23" :disabled="!isEditingSettings" autocomplete="off" required />
            </div>
          </div>
        </div>

        <div class="settings-row">
          <div class="form-group half">
            <label>High Risk Threshold (0.0 - 1.0)</label>
            <input type="number" step="0.01" min="0" max="1" v-model="settings.aneurysm_high_risk_threshold" class="form-control" :disabled="!isEditingSettings" autocomplete="off" required />
          </div>
          <div class="form-group half">
            <label>Medium Risk Threshold (0.0 - 1.0)</label>
            <input type="number" step="0.01" min="0" max="1" v-model="settings.aneurysm_medium_risk_threshold" class="form-control" :disabled="!isEditingSettings" autocomplete="off" required />
          </div>
        </div>

        <div v-if="isEditingSettings" class="form-actions">
          <button type="button" @click="isEditingSettings = false" class="action-btn btn-grey">Cancel</button>
          <button type="submit" class="action-btn btn-green">Save Configuration</button>
        </div>
      </form>
    </div>

    <div v-if="currentTab === 'register'" class="tab-content">
      <div class="page-header">
        <h2>Register New Account</h2>
        <p>Provision access credentials for hospital staff</p>
      </div>

      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label>Email Address</label>
          <input 
            type="email" 
            v-model="newUser.email" 
            @input="handleEmailInput"
            class="form-control" 
            placeholder="staff@hospital.org" 
            autocomplete="email"
            required 
          />
          <small v-if="isCheckingEmail" class="form-text text-muted">Checking availability...</small>
          <small v-else-if="emailExistsWarning" class="form-text text-error">This email is already taken.</small>
          <small v-else-if="isEmailFormatValid" class="form-text text-success">
            This email address is available.
          </small>
        </div>

        <div class="form-group">
          <label>Password</label>
          <input :type="showPassword ? 'text' : 'password'" v-model="newUser.password" class="form-control" placeholder="Enter password" autocomplete="new-password" required />
        </div>

        <div class="form-group">
          <label>Confirm Password</label>
          <input :type="showPassword ? 'text' : 'password'" v-model="newUser.confirmPassword" class="form-control" placeholder="Re-enter password" autocomplete="new-password" required />
        </div>

        <div class="visibility-toggle">
          <label class="checkbox-label">
            <input type="checkbox" v-model="showPassword" />
            Show Passwords
          </label>
        </div>

        <button 
          type="submit" 
          class="action-btn btn-green full-width" 
          :disabled="isCheckingEmail || emailExistsWarning || isRegistering"
        >
          <span v-if="isRegistering">Provisioning Account...</span>
          <span v-else>Provision Account</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { userService } from '../services/adminServices/manageUserService.js' 

const currentTab = ref('manage') 

// --- MANAGE USERS ---
const users = ref([])
const isLoadingUsers = ref(false)

const filteredStaff = computed(() => {
  return users.value.filter(user => user.role !== 'Admin')
})

const fetchAllAccounts = async () => {
  isLoadingUsers.value = true
  try {
    const response = await userService.getAllUsers()
    users.value = response.data || response
  } catch (error) {
    console.error('Failed fetching user list:', error)
    // alert('Could not retrieve active personnel records.')
  } finally {
    isLoadingUsers.value = false
  }
}

const handleDeleteUser = async (id) => {
  if (confirm(`Are you sure you want to permanently delete user ID: ${id}?`)) {
    try {
      await userService.deleteUser(id)
      alert(`User profile ${id} successfully removed.`)
      await fetchAllAccounts()
    } catch (error) {
      console.error('Failed to run delete operation:', error)
      alert('Delete worker action rejected by API.')
    }
  }
}

onMounted(() => {
  fetchAllAccounts()
})

// --- SETTINGS STATE ---
const isEditingSettings = ref(false)
const settings = ref({
  ai_api_url: 'https://api.neuroscan.org/v1/analyze',
  ai_timeout_limit: 30000,
  automatic_scan_interval: 15,
  automatic_scan_start_hour: 1,
  automatic_scan_end_hour: 13,
  aneurysm_high_risk_threshold: 0.75,
  aneurysm_medium_risk_threshold: 0.30
})

const saveSettings = () => { 
  alert('System settings updated successfully.') 
  isEditingSettings.value = false 
}

// --- REGISTER STAFF ---
const showPassword = ref(false)
const isRegistering = ref(false)
const isCheckingEmail = ref(false)
const emailExistsWarning = ref(false)

const newUser = ref({ 
  email: '', 
  password: '', 
  confirmPassword: '' 
})

const isEmailFormatValid = computed(() => {
  const currentEmail = newUser.value.email.trim()
  const domainPart = currentEmail.split('@')[1] || ''
  const dotIndex = domainPart.lastIndexOf('.')
  return currentEmail.includes('@') && dotIndex !== -1 && domainPart.length - dotIndex - 1 >= 2
})

let debounceTimer = null

const handleEmailInput = () => {
  const targetEmail = newUser.value.email.trim()
  
  if (!targetEmail) {
    emailExistsWarning.value = false
    isCheckingEmail.value = false
    return
  }

  clearTimeout(debounceTimer)
  
  debounceTimer = setTimeout(async () => {
    if (!isEmailFormatValid.value) {
      emailExistsWarning.value = false
      return
    }

    isCheckingEmail.value = true
    try {
      emailExistsWarning.value = await userService.checkEmailExists(targetEmail)
    } catch (error) {
      console.error('AJAX unique check execution fault:', error)
    } finally {
      isCheckingEmail.value = false
    }
  }, 300)
}

const handleRegister = async () => {
  if (newUser.value.password !== newUser.value.confirmPassword) {
    alert("Passwords do not match. Please verify.")
    return
  }
  if (emailExistsWarning.value) {
    alert("Cannot proceed. This email address is already registered.")
    return
  }

  isRegistering.value = true
  try {
    const response = await userService.register(
      newUser.value.email,
      newUser.value.password
    )
    
    const data = response.data || response
    alert(`Account provisioned successfully on MongoDB! Generated Employee ID: ${data.user_id}`)
    
    newUser.value = { email: '', password: '', confirmPassword: '' }
    showPassword.value = false
    emailExistsWarning.value = false
    
    currentTab.value = 'manage'
    await fetchAllAccounts()
  } catch (error) {
    console.error('Error registering profile:', error)
    
    if (error.response && error.response.data && error.response.data.detail) {
      const details = error.response.data.detail
      if (Array.isArray(details)) {
        const errorMessages = details.map(err => `${err.loc.join(' -> ')}: ${err.msg}`).join('\n')
        alert(`Validation Error:\n${errorMessages}`)
      } else {
        alert(`Server Error: ${details}`)
      }
    } else {
      alert(error.message || 'Registration process rejected by the server.')
    }
  } finally {
    isRegistering.value = false
  }
}
</script>

<style scoped>
/* Flex card setup to trap scrolling inside tabs */
.card-container { background: #ffffff; border-radius: 12px; padding: 0; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); width: 100%; margin: 0 auto; overflow: hidden; }
.card-container.wide { max-width: 900px; }
.flex-card { display: flex; flex-direction: column; max-height: calc(100vh - 120px); }

/* Ensure tabs stay pinned to the top */
.admin-tabs.fixed-tabs { display: flex; gap: 12px; border-bottom: 2px solid #e9ecef; padding: 20px 30px 0 30px; margin-bottom: 0; background: #fff; z-index: 10; }
.tab-btn { background: none; border: none; padding: 15px 25px; font-size: 16px; font-weight: 600; color: #7f8c8d; cursor: pointer; transition: all 0.2s; border-bottom: 3px solid transparent; margin-bottom: -2px; }
.tab-btn:hover { color: #0aa159; }
.tab-btn.active { color: #0aa159; border-bottom-color: #0aa159; }

/* Dynamic inner scroll for large content */
.tab-content { padding: 30px; overflow-y: auto; flex: 1; min-height: 0; animation: fadeIn 0.3s ease-in-out; }
.tab-content::-webkit-scrollbar { width: 8px; }
.tab-content::-webkit-scrollbar-track { background: #f8f9fa; border-radius: 4px; }
.tab-content::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }
.tab-content::-webkit-scrollbar-thumb:hover { background: #95a5a6; }

@keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }

.page-header { margin-bottom: 25px; border-bottom: 2px solid #f0f2f5; padding-bottom: 15px; }
.flex-header { display: flex; justify-content: space-between; align-items: center; }
.page-header h2 { color: #2c3e50; font-size: 24px; margin-bottom: 5px; }
.page-header p { color: #7f8c8d; font-size: 14px; }
.loading-state { padding: 40px; text-align: center; color: #7f8c8d; font-weight: 600; font-size: 16px; }
.empty-row { color: #95a5a6; font-style: italic; padding: 30px !important; }
.form-text { display: block; font-size: 12px; margin-top: 5px; font-weight: 600; }
.text-muted { color: #7f8c8d; }
.text-error { color: #e53935; }
.text-success { color: #0aa159; }
.clean-table { width: 100%; border-collapse: collapse; text-align: left; }
.clean-table th { padding: 15px; background-color: #f8f9fa; color: #5c6bc0; font-weight: 700; font-size: 14px; text-transform: uppercase; border-bottom: 2px solid #e9ecef; }
.clean-table td { padding: 15px; border-bottom: 1px solid #e9ecef; vertical-align: middle; color: #34495e; }
.badge { background: #e8f5e9; color: #43a047; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; }
.btn-danger { background: #ffebee; color: #e53935; border: 1px solid #ffcdd2; }
.btn-danger:hover { background: #e53935; color: white; }

.settings-form, .register-form { max-width: 600px; }
.form-group { margin-bottom: 20px; }
.settings-row { display: flex; gap: 15px; }
.half { flex: 1; }
.form-group label { display: block; font-size: 14px; font-weight: 600; color: #34495e; margin-bottom: 8px; }

/* Adjusted form control (No left padding for icons) */
.form-control { width: 100%; padding: 12px 15px; border: 1px solid #dcdde1; border-radius: 8px; font-size: 15px; outline: none; transition: border-color 0.2s;}
.form-control:focus { border-color: #0aa159; box-shadow: 0 0 0 3px rgba(10, 161, 89, 0.1); }
.form-control:disabled { background-color: #f8f9fa; color: #95a5a6; cursor: not-allowed; border-color: #e9ecef; }
.form-control::placeholder { color: #b2bec3; }

.time-grid { display: flex; align-items: flex-end; gap: 15px; }
.time-input-group { flex: 1; }
.sub-label { font-size: 12px; color: #7f8c8d; font-weight: 600; text-transform: uppercase; margin-bottom: 5px; display: block; }
.time-divider { padding-bottom: 12px; font-weight: 600; color: #95a5a6; }
.visibility-toggle { margin-bottom: 25px; display: flex; justify-content: flex-end; }
.checkbox-label { font-size: 14px; color: #7f8c8d; cursor: pointer; display: flex; align-items: center; gap: 8px; }
.checkbox-label input { accent-color: #0aa159; cursor: pointer; }
.form-actions { display: flex; gap: 15px; margin-top: 30px; justify-content: flex-end; }
.btn-outline-green { background: transparent; color: #0aa159; border: 1px solid #0aa159; }
.btn-outline-green:hover { background: #e8f5e9; }
.btn-grey { background: #f1f3f5; color: #495057; border: none; }
.btn-grey:hover { background: #e9ecef; }
.full-width { width: 100%; padding: 14px; font-size: 16px; margin-top: 10px; }
.action-btn { border: none; border-radius: 8px; font-weight: 600; cursor: pointer; padding: 8px 16px; transition: all 0.2s; display: inline-flex; align-items: center; justify-content: center; gap: 6px; border: 1px solid transparent; }
.action-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-green { background-color: #0aa159; color: white; box-shadow: 0 4px 6px rgba(10, 161, 89, 0.2); }
.btn-green:hover { background-color: #088c4d; transform: translateY(-2px); }
</style>