<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h2>Welcome Back</h2>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Employee ID (6 Digits) or Email</label>
          <div class="input-wrapper">
            <span class="material-symbols-outlined input-icon">badge</span>
            <input 
              type="text" 
              v-model="loginIdentifier" 
              class="form-control" 
              placeholder="e.g., 123456 or dr@hospital.org" 
              required 
            />
          </div>
        </div>

        <div class="form-group">
          <label>Password</label>
          <div class="input-wrapper">
            <span class="material-symbols-outlined input-icon">lock</span>
            <input 
              type="password" 
              v-model="password" 
              class="form-control" 
              placeholder="Enter your password" 
              required 
            />
          </div>
        </div>

        <button type="submit" class="action-btn btn-green full-width">
          Sign In
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authStore } from '../store.js'
import { authService } from '../services/authService.js'

const router = useRouter()
const loginIdentifier = ref('')
const password = ref('')
const isAdmin = ref(false) 

const handleLogin = async () => {
  const identifierValue = loginIdentifier.value.trim()
  const isSixDigitId = /^\d{6}$/.test(identifierValue)
  const isEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(identifierValue)

  if (!isSixDigitId && !isEmail) {
    alert("Enter a valid 6-digit ID or email.")
    return
  }

  // --- 🛑 FRONTEND BYPASS CHEAT CODES 🛑 ---
  if (identifierValue === 'admin@bypass.com') {
    authStore.login('999999', 'admin')
    router.push('/admin')
    return
  }
  
  if (identifierValue === 'doctor@bypass.com') {
    authStore.login('123456', 'doctor')
    router.push('/records')
    return
  }
  // ----------------------------------------

  try {
    const user = await authService.login(
      identifierValue,
      password.value,
      isAdmin.value
    )
    
    authStore.login(user.employeeId, user.role)
    
    const normalizedRole = user.role.toLowerCase()
    if (normalizedRole === 'admin') {
      router.push('/admin')
    } else {
      router.push('/records')
    }
  } catch (error) {
    alert('Login failed. Please check your credentials or ensure the backend is running.')
    console.error('Login integration exception:', error)
  }
}
</script>

<style scoped>
.auth-container { width: 100%; display: flex; justify-content: center; padding-top: 40px; }
.auth-card { background: #ffffff; width: 100%; max-width: 400px; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); }
.auth-header { text-align: center; margin-bottom: 30px; }
.auth-header h2 { color: #2c3e50; font-size: 26px; }

/* Role Toggle */
.role-toggle-container { display: flex; align-items: center; justify-content: center; gap: 15px; margin-bottom: 25px; padding: 10px; background: #f8f9fa; border-radius: 12px; border: 1px solid #e9ecef; }
.role-label { font-size: 15px; font-weight: 600; color: #95a5a6; transition: color 0.3s; }
.role-label.active { color: #0aa159; }
.switch { position: relative; display: inline-block; width: 54px; height: 28px; }
.switch input { opacity: 0; width: 0; height: 0; }
.slider { position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0; background-color: #cbd5e1; transition: .4s; border-radius: 34px; }
.slider:before { position: absolute; content: ""; height: 20px; width: 20px; left: 4px; bottom: 4px; background-color: white; transition: .4s; border-radius: 50%; }
input:checked + .slider { background-color: #0aa159; }
input:checked + .slider:before { transform: translateX(26px); }

.form-group { margin-bottom: 20px; }
.form-group label { display: block; font-size: 13px; font-weight: 600; color: #34495e; margin-bottom: 8px; }

.input-wrapper { position: relative; display: flex; align-items: center; }
.input-wrapper .input-icon { position: absolute; left: 15px; color: #95a5a6; pointer-events: none; font-size: 20px; }
.form-control { width: 100%; padding: 12px 15px 12px 40px; border: 1px solid #dcdde1; border-radius: 8px; font-size: 15px; outline: none; transition: border-color 0.2s;}
.form-control:focus { border-color: #0aa159; box-shadow: 0 0 0 3px rgba(10, 161, 89, 0.1); }
.form-control::placeholder { color: #b2bec3; }

.full-width { width: 100%; padding: 12px; margin-top: 10px; }
.action-btn { border: none; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; justify-content: center; gap: 6px; }
.btn-green { background-color: #0aa159; color: white; box-shadow: 0 4px 6px rgba(10, 161, 89, 0.2); }
.btn-green:hover { background-color: #088c4d; transform: translateY(-2px); }
</style>