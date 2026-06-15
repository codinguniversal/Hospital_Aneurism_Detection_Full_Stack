<template>
  <div class="app-layout">
    <nav class="top-bar">
      <div class="nav-brand">
        <i class="fa fa-hospital-o"></i>
        <span>NeuroScan AI</span>
      </div>
      
      <div class="nav-links">
        <template v-if="authStore.isAuthenticated">
          <router-link to="/records" class="nav-item">Records</router-link>
          
          <div class="dropdown-container">
            <button @click="toggleMenu" class="nav-item dropdown-btn">
              Hello, {{ authStore.userName }} <i class="fa fa-caret-down"></i>
            </button>
            
            <div v-if="menuOpen" class="dropdown-menu">
              <router-link to="/profile" @click="menuOpen = false" class="dropdown-item">
                <i class="fa fa-user-circle-o"></i> Profile
              </router-link>
              <button @click="handleLogout" class="dropdown-item text-danger">
                <i class="fa fa-sign-out"></i> Logout
              </button>
            </div>
          </div>
        </template>

        <template v-else>
          <router-link to="/login" class="nav-item">Login</router-link>
          <router-link to="/register" class="nav-item btn-outline">Sign Up</router-link>
        </template>
      </div>
    </nav>

    <main class="main-content">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { authStore } from './store.js' // Import our new store

const router = useRouter()
const menuOpen = ref(false)

const toggleMenu = () => {
  menuOpen.value = !menuOpen.value
}

const handleLogout = () => {
  authStore.logout()
  menuOpen.value = false
  router.push('/login') // Send them back to login screen
}
</script>

<style>
/* Keeping your exact global styles */
* { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }
body { background-color: #f4f7f6; color: #2c3e50; }
.app-layout { min-height: 100vh; display: flex; flex-direction: column; }

/* TOP BAR STYLES */
.top-bar { background-color: #ffffff; padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05); z-index: 100; }
.nav-brand { font-size: 22px; font-weight: 700; color: #0aa159; display: flex; align-items: center; gap: 10px; }
.nav-links { display: flex; gap: 20px; align-items: center; }
.nav-item { text-decoration: none; color: #555; font-weight: 600; transition: color 0.2s; cursor: pointer; }
.nav-item:hover, .nav-item.router-link-active { color: #0aa159; }
.nav-item.btn-outline { border: 2px solid #0aa159; padding: 8px 16px; border-radius: 8px; color: #0aa159; }
.nav-item.btn-outline:hover { background-color: #0aa159; color: white; }
.main-content { flex: 1; padding: 40px; display: flex; justify-content: center; }

/* DROPDOWN STYLES */
.dropdown-container { position: relative; }
.dropdown-btn { background: none; border: none; font-size: 16px; display: flex; align-items: center; gap: 5px; }
.dropdown-menu {
  position: absolute; top: 100%; right: 0; margin-top: 10px; background: white;
  min-width: 150px; border-radius: 8px; box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  display: flex; flex-direction: column; overflow: hidden; border: 1px solid #e9ecef;
}
.dropdown-item {
  padding: 12px 15px; text-decoration: none; color: #2c3e50; font-size: 14px;
  display: flex; align-items: center; gap: 8px; border: none; background: none; text-align: left; cursor: pointer;
}
.dropdown-item:hover { background: #f8f9fa; color: #0aa159; }
.text-danger { color: #e53935; }
.text-danger:hover { color: #e53935; background: #ffebee; }

/* GLOBAL BUTTON STYLES */
.action-btn { padding: 8px 16px; border: none; border-radius: 8px; font-size: 14px; font-weight: 600; cursor: pointer; transition: all 0.2s; display: inline-flex; align-items: center; gap: 6px; }
.btn-green { background-color: #0aa159; color: white; box-shadow: 0 4px 6px rgba(10, 161, 89, 0.2); }
.btn-green:hover { background-color: #088c4d; transform: translateY(-2px); }
</style>