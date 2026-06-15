<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h2>Create Account</h2>
        <p>Register for a new NeuroScan AI account</p>
      </div>

      <form @submit.prevent="handleRegister">
        <div class="form-group">
          <label>Username</label>
          <div class="input-wrapper">
            <i class="fa fa-user"></i>
            <input type="text" v-model="username" placeholder="Choose a username" required />
          </div>
        </div>

        <div class="form-group">
          <label>Email Address</label>
          <div class="input-wrapper">
            <i class="fa fa-envelope"></i>
            <input type="email" v-model="email" placeholder="Enter your email" required />
          </div>
        </div>

        <div class="form-group">
          <label>Password</label>
          <div class="input-wrapper">
            <i class="fa fa-lock"></i>
            <input type="password" v-model="password" placeholder="Create a password" required />
          </div>
        </div>

        <div class="form-group">
          <label>Confirm Password</label>
          <div class="input-wrapper">
            <i class="fa fa-lock"></i>
            <input type="password" v-model="confirmPassword" placeholder="Confirm your password" required />
          </div>
        </div>

        <div class="form-group gender-group">
          <label>Sex:</label>
          <div class="radio-options">
            <label class="radio-label">
              <input type="radio" v-model="gender" value="female" /> Female
            </label>
            <label class="radio-label">
              <input type="radio" v-model="gender" value="male" /> Male
            </label>
          </div>
        </div>

        <button type="submit" class="action-btn btn-green full-width">Sign Up</button>

        <p class="auth-footer">
          Already have an account? <router-link to="/login">Sign in</router-link>
        </p>
      </form>
    </div>
  </div>
</template>
<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authStore } from '../store.js'

const router = useRouter()
const username = ref('')
const email = ref('')
const password = ref('')
const confirmPassword = ref('')
const gender = ref('')

const handleRegister = () => {
  if (password.value !== confirmPassword.value) {
    alert("Passwords do not match!")
    return
  }
  
  // 1. Tell the store we are logged in with their new username
  authStore.login(username.value)
  
  // 2. Automatically redirect to the records page!
  router.push('/records')
}
</script>

<style scoped>
/* Reusing the exact same clean card styles */
.auth-container { width: 100%; display: flex; justify-content: center; padding-top: 20px; padding-bottom: 40px; }
.auth-card { background: #ffffff; width: 100%; max-width: 450px; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05); }
.auth-header { text-align: center; margin-bottom: 30px; }
.auth-header h2 { color: #2c3e50; font-size: 26px; margin-bottom: 8px; }
.auth-header p { color: #7f8c8d; font-size: 15px; }

.form-group { margin-bottom: 20px; }
.form-group label { display: block; font-size: 13px; font-weight: 600; color: #34495e; margin-bottom: 8px; }

.input-wrapper { position: relative; display: flex; align-items: center; }
.input-wrapper i { position: absolute; left: 15px; color: #95a5a6; }
.input-wrapper input { width: 100%; padding: 12px 15px 12px 40px; border: 1px solid #dcdde1; border-radius: 8px; font-size: 15px; color: #2c3e50; transition: all 0.2s; outline: none; }
.input-wrapper input:focus { border-color: #0aa159; box-shadow: 0 0 0 3px rgba(10, 161, 89, 0.1); }

.gender-group { margin-bottom: 25px; }
.radio-options { display: flex; gap: 20px; margin-top: 5px; }
.radio-label { display: flex; align-items: center; font-size: 14px; color: #2c3e50; font-weight: normal; cursor: pointer; }
.radio-label input { margin-right: 8px; accent-color: #0aa159; cursor: pointer; }

.full-width { width: 100%; justify-content: center; padding: 12px; font-size: 16px; }
.auth-footer { text-align: center; margin-top: 25px; font-size: 14px; color: #7f8c8d; }
.auth-footer a { color: #0aa159; text-decoration: none; font-weight: 600; margin-left: 5px; }
.auth-footer a:hover { text-decoration: underline; }
</style>