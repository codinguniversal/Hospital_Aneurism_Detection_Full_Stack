<template>
  <div class="app-layout">
    <nav class="top-bar">
      <div class="nav-brand">
        <span class="material-symbols-outlined icon-fix">local_hospital</span>
        <span>NeuroScan AI</span>
      </div>
      
      <div v-if="!authStore.isAuthenticated" class="centered-header-title">
        Login
      </div>

      <div class="nav-links">
        <template v-if="authStore.isAuthenticated && ['doctor', 'radiologist'].includes(authStore.role?.toLowerCase())">
          <span class="role-display-label">
            <span class="material-symbols-outlined icon-fix">medical_services</span> Doctor
          </span>
          
          <button @click="handleLogout" class="nav-item logout-btn">
            <span class="material-symbols-outlined icon-fix">logout</span> Logout
          </button>
        </template>

        <template v-if="authStore.isAuthenticated && authStore.role?.toLowerCase() === 'admin'">
          <span class="role-display-label">
            <span class="material-symbols-outlined icon-fix">admin_panel_settings</span> Admin
          </span>
          <button @click="handleLogout" class="nav-item logout-btn">
            <span class="material-symbols-outlined icon-fix">logout</span> Logout
          </button>
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
body { background-color: #f4f7f6; color: #2c3e50; overflow-y: hidden; }
.app-layout { height: 100vh; display: flex; flex-direction: column; }

.top-bar { background-color: #ffffff; padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05); position: relative; z-index: 100; }
.nav-brand { font-size: 22px; font-weight: 700; color: #0aa159; display: flex; align-items: center; gap: 10px; width: 200px; }

/* Centered Header Text */
.centered-header-title { position: absolute; left: 50%; transform: translateX(-50%); font-size: 18px; font-weight: 700; color: #2c3e50; text-transform: uppercase; letter-spacing: 1px; }

.nav-links { display: flex; gap: 20px; align-items: center; justify-content: flex-end; min-width: 200px; }
.nav-item { text-decoration: none; color: #555; font-weight: 600; transition: color 0.2s; cursor: pointer; display: flex; align-items: center; gap: 6px; font-size: 16px; background: none; border: none; }
.nav-item:hover, .nav-item.router-link-active { color: #0aa159; }
.nav-item.btn-outline { border: 2px solid #0aa159; padding: 8px 16px; border-radius: 8px; color: #0aa159; }
.nav-item.btn-outline:hover { background-color: #0aa159; color: white; }

/* Dynamic Role Text Marker */
.role-display-label { font-size: 16px; font-weight: 700; color: #7f8c8d; text-transform: uppercase; display: inline-flex; align-items: center; gap: 6px; margin-right: 10px; border-right: 2px solid #e9ecef; padding-right: 20px; }

.logout-btn { color: #e53935; padding: 0; font-weight: 600; }
.logout-btn:hover { color: #c62828; }

.main-content { flex: 1; padding: 30px; display: flex; justify-content: center; position: relative; z-index: 1; overflow-y: auto; }
.action-btn { padding: 8px 16px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; justify-content: center; gap: 6px; }
.btn-green { background-color: #0aa159; color: white; box-shadow: 0 4px 6px rgba(10, 161, 89, 0.2); }
.btn-green:hover { background-color: #088c4d; transform: translateY(-2px); }

.material-symbols-outlined.icon-fix { font-size: 22px; vertical-align: middle; display: inline-block; line-height: 1; }
</style>
