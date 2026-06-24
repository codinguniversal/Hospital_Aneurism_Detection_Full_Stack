import { createRouter, createWebHistory } from 'vue-router'
import { authStore } from '../store.js'

import LoginView from '../views/LoginView.vue'
import AdminView from '../views/AdminView.vue'
import ManageUsersView from '../views/ManageUsersView.vue'
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
    { path: '/manage', name: 'manage', component: ManageUsersView, meta: { requiresAuth: true, role: 'admin' } },

    // Doctor Realm
    { path: '/records', name: 'records', component: RecordsView, meta: { requiresAuth: true, role: 'doctor' } },
    { path: '/profile', name: 'profile', component: ProfileView, meta: { requiresAuth: true, role: 'doctor' } },
    { path: '/results/:id', name: 'results', component: ResultsView, meta: { requiresAuth: true, role: 'doctor' } },
    { path: '/explain/:id', name: 'explain', component: ExplainView, meta: { requiresAuth: true, role: 'doctor' } }
  ]
})

// The Modern Bouncer (Vue Router v4 Style)
router.beforeEach((to, from) => {
  if (!to.meta.requiresAuth) {
    // If user is logged in and hits login view, redirect to dashboard
    if (to.path === '/login' && authStore.isAuthenticated) {
      const currentRole = authStore.role?.toLowerCase() || '';
      return currentRole === 'admin' ? '/admin' : '/records'
    }
    return; // Allow public routes
  }

  // 1. Guard against unauthenticated sessions
  if (!authStore.isAuthenticated) {
    return "/login"
  } 
  
  const userRole = authStore.role?.toLowerCase() || '';
  const requiredRole = to.meta.role?.toLowerCase() || '';

  // 2. Validate multi-tier role access controls cleanly
  let hasAccess = false;
  if (requiredRole === 'admin' && userRole === 'admin') {
    hasAccess = true;
  } else if (requiredRole === 'doctor' && userRole !== 'admin') {
    // 🎯 Captures 'Radiologist', 'Doctor', etc. without locking them out
    hasAccess = true;
  }

  // 3. Prevent unauthorized jumping or infinite redirection loops
  if (!hasAccess) {
    const targetDashboard = userRole === 'admin' ? '/admin' : '/records';
    if (to.path !== targetDashboard) {
      return targetDashboard;
    }
  }
})

export default router