import { createRouter, createWebHistory } from 'vue-router'
import { authStore } from '../store.js'

import LoginView from '../views/LoginView.vue'
import AdminView from '../views/AdminView.vue'
import RecordsView from '../views/RecordsView.vue'
import ProfileView from '../views/ProfileView.vue'
import ResultsView from '../views/ResultsView.vue'
import ExplainView from '../views/ExplainView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: () => authStore.role?.toLowerCase() === 'admin' ? '/admin' : '/login' },
    { path: '/login', name: 'login', component: LoginView },
    
    // Admin Realm
    { path: '/admin', name: 'admin', component: AdminView, meta: { requiresAuth: true, role: 'admin' } },

    // Doctor Realm
    { path: '/records', name: 'records', component: RecordsView, meta: { requiresAuth: true, role: 'doctor' } },
    { path: '/profile', name: 'profile', component: ProfileView, meta: { requiresAuth: true, role: 'doctor' } },
    { path: '/results/:id', name: 'results', component: ResultsView, meta: { requiresAuth: true, role: 'doctor' } },
    { path: '/explain/:id', name: 'explain', component: ExplainView, meta: { requiresAuth: true, role: 'doctor' } }
  ]
})

// 🟢 Modern Vue Router v4 Navigation Guard (Warning & Loop Free)
router.beforeEach((to, from) => {
  const isAuthenticated = authStore.isAuthenticated
  const userRole = authStore.role ? authStore.role.toLowerCase() : ''
  const targetRole = to.meta.role ? to.meta.role.toLowerCase() : ''

  // 1. Unauthenticated users trying to access protected routes go to login
  if (to.meta.requiresAuth && !isAuthenticated) {
    return '/login'
  } 
  
  // 2. Authenticated users attempting to access a route belonging to another role
  if (to.meta.requiresAuth && targetRole !== userRole) {
    const fallbackPath = userRole === 'admin' ? '/admin' : '/records'
    // ONLY redirect if we aren't already going to that exact fallback path
    if (to.path !== fallbackPath) return fallbackPath
  } 
  
  // 3. Authenticated users going back to login get pushed straight to their dashboard
  if (to.path === '/login' && isAuthenticated) {
    return userRole === 'admin' ? '/admin' : '/records'
  }
  
  // Allow navigation to proceed safely
  return true
})

export default router