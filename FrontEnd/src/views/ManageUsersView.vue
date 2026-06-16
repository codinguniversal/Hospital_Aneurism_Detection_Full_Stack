<template>
  <div class="card-container wide">
    <div class="page-header">
      <h1>Manage Staff Accounts</h1>
    </div>

    <table class="clean-table">
      <thead>
        <tr>
          <th>Employee ID</th>
          <th>Email Address</th>
          <th>Role</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="user in users" :key="user.id">
          <td><strong>{{ user.id }}</strong></td>
          <td>{{ user.email }}</td>
          <td><span class="badge">{{ user.role }}</span></td>
          <td>
            <button @click="deleteUser(user.id)" class="action-btn btn-danger">
              <i class="fa fa-trash"></i> Delete
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const users = ref([
  { id: '123456', email: 'ahmed@hospital.org', role: 'Doctor' },
  { id: '654321', email: 'sara@hospital.org', role: 'Doctor' }
])

const deleteUser = (id) => {
  if (confirm(`Are you sure you want to delete user ${id}?`)) {
    users.value = users.value.filter(u => u.id !== id)
  }
}
</script>

<style scoped>
.card-container { background: #ffffff; border-radius: 12px; padding: 30px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); width: 1000px; }
.page-header { border-bottom: 2px solid #f0f2f5; padding-bottom: 15px; margin-bottom: 20px; }
.clean-table { width: 100%; border-collapse: collapse; text-align: left; }
.clean-table th { padding: 15px; background-color: #f8f9fa; color: #5c6bc0; font-weight: 700; font-size: 14px; text-transform: uppercase; border-bottom: 2px solid #e9ecef; }
.clean-table td { padding: 15px; border-bottom: 1px solid #e9ecef; vertical-align: middle; color: #34495e; }
.badge { background: #e8f5e9; color: #43a047; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 700; }
.btn-danger { background: #ffebee; color: #e53935; border: 1px solid #ffcdd2; }
.btn-danger:hover { background: #e53935; color: white; }
</style>