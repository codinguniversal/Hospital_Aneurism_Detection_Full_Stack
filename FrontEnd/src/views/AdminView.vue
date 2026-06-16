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
        <h2><i class="fa fa-server"></i> Backend AI Schedule</h2>
      </div>
      <form @submit.prevent="saveSettings">
        <div class="form-group">
          <label>Operating Window (24h Format)</label>
          <div class="time-grid">
            <div class="time-input-group">
              <label class="sub-label">Start Hour</label>
              <input type="number" v-model="startHour" class="form-control" placeholder="e.g., 1" min="0" max="23" required />
            </div>
            <div class="time-divider">to</div>
            <div class="time-input-group">
              <label class="sub-label">End Hour</label>
              <input type="number" v-model="endHour" class="form-control" placeholder="e.g., 13" min="0" max="23" required />
            </div>
          </div>
        </div>
        <button type="submit" class="action-btn btn-outline-green full-width">Save Settings</button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const newUser = ref({ employeeId: '', email: '', password: '' })
const startHour = ref(1) 
const endHour = ref(13) 

const generateId = () => { newUser.value.employeeId = Math.floor(100000 + Math.random() * 900000).toString() }

const handleRegister = () => {
  if (!/^\d{6}$/.test(newUser.value.employeeId.trim())) return alert("ID must be 6 digits.")
  alert("Account Created!")
  newUser.value = { employeeId: '', email: '', password: '' }
}

const saveSettings = () => { alert(`AI runs from ${startHour.value}:00 to ${endHour.value}:00`) }
</script>

<style scoped>
.admin-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; width: 1000px; }
.card-container { background: #ffffff; border-radius: 12px; padding: 30px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); }
.page-header { border-bottom: 2px solid #f0f2f5; padding-bottom: 15px; margin-bottom: 20px; }
.form-group { margin-bottom: 20px; }
.form-group label { display: block; font-size: 14px; font-weight: 600; color: #34495e; margin-bottom: 8px; }
.form-control { width: 100%; padding: 10px; border: 1px solid #dcdde1; border-radius: 8px; outline: none; }
.form-control::placeholder { color: #b2bec3; }
.input-with-button { display: flex; gap: 10px; }
.time-grid { display: flex; align-items: flex-end; gap: 15px; }
.time-input-group { flex: 1; }
.sub-label { font-size: 12px; color: #7f8c8d; font-weight: 600; text-transform: uppercase; }
.time-divider { padding-bottom: 10px; font-weight: 600; color: #95a5a6; }
.btn-outline-green { background: transparent; color: #0aa159; border: 1px solid #0aa159; }
.btn-grey { background: #f1f3f5; color: #495057; border: none; }
.full-width { width: 100%; padding: 12px; margin-top: 10px; }
.action-btn { border: none; border-radius: 8px; font-weight: 600; cursor: pointer; padding: 8px 16px; transition: all 0.2s; display: inline-flex; align-items: center; justify-content: center; gap: 6px; }
.btn-green { background-color: #0aa159; color: white; box-shadow: 0 4px 6px rgba(10, 161, 89, 0.2); }
.btn-green:hover { background-color: #088c4d; transform: translateY(-2px); }
</style>