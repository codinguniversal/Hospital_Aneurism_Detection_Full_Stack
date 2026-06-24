<template>
  <div class="app-layout">
    <nav class="top-bar">
      <div class="nav-brand">
        <i class="fa fa-hospital-o"></i>
        <span>NeuroScan AI</span>
      </div>
      
      <div class="nav-links">
        <template v-if="authStore.isAuthenticated && authStore.role === 'doctor'">
          <router-link to="/records" class="nav-item">Records</router-link>
          <router-link to="/profile" class="nav-item profile-link">
            <i class="fa fa-user-circle-o"></i> Profile
          </router-link>
          <button @click="handleLogout" class="nav-item logout-btn"><i class="fa fa-sign-out"></i> Logout</button>
        </template>

        <template v-if="authStore.isAuthenticated && authStore.role === 'admin'">
          <router-link to="/admin" class="nav-item">Settings</router-link>
          <!-- <router-link to="/manage" class="nav-item btn-outline"><i class="fa fa-users"></i> Manage Users</router-link> -->
          <button @click="handleLogout" class="nav-item logout-btn"><i class="fa fa-sign-out"></i> Logout</button>
        </template>
        
        <template v-if="!authStore.isAuthenticated">
          <router-link to="/login" class="nav-item">Login</router-link>
        </template>
      </div>
    </nav>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { authStore } from './store.js'

const router = useRouter()

const handleLogout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }
body { background-color: #f4f7f6; color: #2c3e50; }
.app-layout { min-height: 100vh; display: flex; flex-direction: column; }

.top-bar { background-color: #ffffff; padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05); position: relative; z-index: 100; }
.nav-brand { font-size: 22px; font-weight: 700; color: #0aa159; display: flex; align-items: center; gap: 10px; }
.nav-links { display: flex; gap: 20px; align-items: center; }

.nav-item { text-decoration: none; color: #555; font-weight: 600; transition: color 0.2s; cursor: pointer; display: flex; align-items: center; gap: 6px; font-size: 16px; background: none; }
.nav-item:hover, .nav-item.router-link-active { color: #0aa159; }

.nav-item.btn-outline { border: 2px solid #0aa159; padding: 8px 16px; border-radius: 8px; color: #0aa159; }
.nav-item.btn-outline:hover { background-color: #0aa159; color: white; }

.profile-link { color: #34495e; }
.logout-btn { border: none; color: #e53935; padding: 0; }
.logout-btn:hover { color: #c62828; }

.main-content { flex: 1; padding: 40px; display: flex; justify-content: center; position: relative; z-index: 1; }
.action-btn { padding: 8px 16px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; justify-content: center; gap: 6px; }
.btn-green { background-color: #0aa159; color: white; box-shadow: 0 4px 6px rgba(10, 161, 89, 0.2); }
.btn-green:hover { background-color: #088c4d; transform: translateY(-2px); }
</style>