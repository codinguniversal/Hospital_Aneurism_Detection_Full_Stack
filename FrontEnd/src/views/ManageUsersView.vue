<template>
  <div class="card-container wide">
    <div class="page-header">
      <h1>Manage Staff Accounts</h1>
    </div>

    <div v-if="loading" class="loading-state">
      <i class="fa ref fa-spinner fa-spin"></i> Loading system registry entries...
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
        <tr v-for="user in users" :key="user.employee_id">
          <td><strong>{{ user.employee_id }}</strong></td>
          <td>{{ user.email }}</td>
          <td>
            <span class="badge" :class="user.role.toLowerCase()">
              {{ user.role }}
            </span>
          </td>
          <td>
            <button 
              @click="deleteUser(user.employee_id)" 
              class="action-btn btn-danger"
              :disabled="user.employee_id === '000001'"
            >
              <i class="fa fa-trash"></i> Delete
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { userService } from '../services/adminServices/manageUserService.js' // Ensure path matches your folder structure

const users = ref([])
const loading = ref(true)

//  Fetch users from FastAPI database on mount
const fetchUsers = async () => {
  try {
    loading.value = true
    const response = await userService.getAllUsers()
    const data = response.data || response
    
    //  INSPECTOR LOG: Open your browser dev tools console (F12) to see the key names!
    console.log("RAW BACKEND USER RECORDS:", data)
    // Dynamically handles unwrapping whether your apiClient returns raw data or the full Axios object
    users.value = response.data || response
  } catch (error) {
    console.error('Failed to sync users registry:', error)
    alert('Could not synchronize staff accounts from database.')
  } finally {
    loading.value = false
  }
}

//  Send DELETE query to the backend layer
const deleteUser = async (employeeId) => {
  if (confirm(`Are you sure you want to completely delete staff user ${employeeId}?`)) {
    try {
      await userService.deleteUser(employeeId)
      
      // 🚀 Optimistically clear out the user locally on success so the UI updates instantly
      users.value = users.value.filter(u => u.employee_id !== employeeId)
    } catch (error) {
      console.error('Account deletion execution failure:', error)
      alert('Failed to remove user account from system.')
    }
  }
}

// Automatically trigger hydration when view opens
onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.card-container { width: 1000px; margin: 0 auto; }
.page-header { border-bottom: 2px solid #f0f2f5; padding-bottom: 15px; margin-bottom: 20px; }
.clean-table { width: 100%; border-collapse: collapse; }
.clean-table th { padding: 15px; background-color: #f8f9fa; color: #5c6bc0; font-weight: 700; font-size: 14px; text-transform: uppercase; border-bottom: 2px solid #e9ecef; text-align: left; }
.clean-table td { padding: 15px; border-bottom: 1px solid #e9ecef; vertical-align: middle; color: #34495e; text-align: left; }

.loading-state { text-align: center; padding: 40px; color: #7f8c8d; font-style: italic; font-size: 16px; }

/* Dynamic styling classes based on role casing */
.badge { padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; display: inline-block; }
.badge.admin { background: #e3f2fd; color: #1565c0; }
.badge.radiologist { background: #e8f5e9; color: #43a047; }
.badge.doctor { background: #fff3e0; color: #ef6c00; }

.btn-danger { background: #ffebee; color: #e53935; border: 1px solid #ffcdd2; padding: 6px 12px; border-radius: 6px; cursor: pointer; transition: all 0.2s; }
.btn-danger:hover:not(:disabled) { background: #e53935; color: white; }
.btn-danger:disabled { opacity: 0.4; cursor: not-allowed; border-color: #cbd5e1; color: #94a3b8; background-color: #f1f5f9; }
</style>