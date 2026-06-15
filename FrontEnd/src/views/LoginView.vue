<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h2>Welcome Back</h2>
        <p>Sign in to your account to continue</p>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="form-group">
          <label>Username or Email</label>
          <div class="input-wrapper">
            <i class="fa fa-user"></i>
            <input type="text" v-model="username" placeholder="Enter your username" required />
          </div>
        </div>

        <div class="form-group">
          <label>Password</label>
          <div class="input-wrapper">
            <i class="fa fa-lock"></i>
            <input type="password" v-model="password" placeholder="Enter your password" required />
          </div>
        </div>

        <div class="auth-actions">
          <label class="remember">
            <input type="checkbox" v-model="remember" />
            <span>Remember me</span>
          </label>
          <a href="#" class="forgot-link">Forgot password?</a>
        </div>

        <button type="submit" class="action-btn btn-green full-width">Sign In</button>

        <p class="auth-footer">
          Don't have an account? <router-link to="/register">Sign up</router-link>
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
const password = ref('')
const remember = ref(false)

const handleLogin = () => {
  if (!username.value || !password.value) {
    alert('Please fill in all fields')
    return
  }
  
  // 1. Tell the store we are logged in and pass the username
  authStore.login(username.value)
  
  // 2. Automatically redirect to the records page!
  router.push('/records')
}
</script>

<style scoped>
.auth-container {
  width: 100%;
  display: flex;
  justify-content: center;
  padding-top: 40px;
}

.auth-card {
  background: #ffffff;
  width: 100%;
  max-width: 450px;
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.auth-header {
  text-align: center;
  margin-bottom: 30px;
}

.auth-header h2 {
  color: #2c3e50;
  font-size: 26px;
  margin-bottom: 8px;
}

.auth-header p {
  color: #7f8c8d;
  font-size: 15px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  color: #34495e;
  margin-bottom: 8px;
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-wrapper i {
  position: absolute;
  left: 15px;
  color: #95a5a6;
}

.input-wrapper input {
  width: 100%;
  padding: 12px 15px 12px 40px;
  border: 1px solid #dcdde1;
  border-radius: 8px;
  font-size: 15px;
  color: #2c3e50;
  transition: all 0.2s;
  outline: none;
}

.input-wrapper input:focus {
  border-color: #0aa159;
  box-shadow: 0 0 0 3px rgba(10, 161, 89, 0.1);
}

.auth-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
  font-size: 14px;
}

.remember {
  display: flex;
  align-items: center;
  color: #7f8c8d;
  cursor: pointer;
}

.remember input {
  margin-right: 8px;
  accent-color: #0aa159;
}

.forgot-link {
  color: #0aa159;
  text-decoration: none;
  font-weight: 600;
}

.forgot-link:hover {
  text-decoration: underline;
}

.full-width {
  width: 100%;
  justify-content: center;
  padding: 12px;
  font-size: 16px;
}

.auth-footer {
  text-align: center;
  margin-top: 25px;
  font-size: 14px;
  color: #7f8c8d;
}

.auth-footer a {
  color: #0aa159;
  text-decoration: none;
  font-weight: 600;
  margin-left: 5px;
}

.auth-footer a:hover {
  text-decoration: underline;
}
</style>