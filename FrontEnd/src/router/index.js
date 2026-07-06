import { createRouter, createWebHistory } from 'vue-router'
import { authStore } from '../store.js'

import LoginView from '../views/LoginView.vue'
import AdminView from '../views/AdminView.vue'
import RecordsView from '../views/RecordsView.vue'
import ResultsView from '../views/ResultsView.vue'
import ExplainView from '../views/ExplainView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { 
      path: '/', 
      redirect: () => authStore.role?.toLowerCase() === 'admin' ? '/admin' : '/records' 
    },
    { path: '/login', name: 'login', component: LoginView },
    
    // Admin Realm
    { path: '/admin', name: 'admin', component: AdminView, meta: { requiresAuth: true, role: 'admin' } },

    // Doctor/Radiologist Realm (Using an array for multiple allowed roles makes this much cleaner!)
    { path: '/records', name: 'records', component: RecordsView, meta: { requiresAuth: true, roles: ['doctor', 'radiologist'] } },
    { path: '/results/:id', name: 'results', component: ResultsView, meta: { requiresAuth: true, roles: ['doctor', 'radiologist'] } },
    { path: '/explain/:id', name: 'explain', component: ExplainView, meta: { requiresAuth: true, roles: ['doctor', 'radiologist'] } }
  ]
})

// Modern Vue Router v4 Navigation Guard
router.beforeEach((to, from) => {
  const isAuthenticated = authStore.isAuthenticated
  const userRole = authStore.role ? authStore.role.toLowerCase() : ''

  // 1. Unauthenticated users trying to access protected routes go to login
  if (to.meta.requiresAuth && !isAuthenticated) {
    return '/login'
  } 
  
  // 2. Authenticated users going back to login get pushed straight to their dashboard
  if (to.path === '/login' && isAuthenticated) {
    return userRole === 'admin' ? '/admin' : '/records'
  }
  
  // 3. Authorization Check: Role matching
  if (to.meta.requiresAuth) {
    // Check if route uses a single meta.role (like admin) or a meta.roles array
    const allowedRoles = to.meta.roles || [to.meta.role]
    
    const hasPermission = allowedRoles.includes(userRole)

    if (!hasPermission) {
      // Determine user's native home path if they are lost
      const fallbackPath = userRole === 'admin' ? '/admin' : '/records'
      return fallbackPath
    }
  }  
  
  // Allow navigation to proceed safely
  return true
})

export default router