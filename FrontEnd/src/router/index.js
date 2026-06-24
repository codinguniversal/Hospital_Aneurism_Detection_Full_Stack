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
    { path: '/', redirect: () => authStore.role === 'admin' ? '/admin' : '/login' },
    { path: '/login', name: 'login', component: LoginView },
    
    // Admin Realm (All tabs are handled inside AdminView)
    { path: '/admin', name: 'admin', component: AdminView, meta: { requiresAuth: true, role: 'admin' } },

    // Doctor Realm
    { path: '/records', name: 'records', component: RecordsView, meta: { requiresAuth: true, role: 'doctor' } },
    { path: '/profile', name: 'profile', component: ProfileView, meta: { requiresAuth: true, role: 'doctor' } },
    { path: '/results/:id', name: 'results', component: ResultsView, meta: { requiresAuth: true, role: 'doctor' } },
    { path: '/explain/:id', name: 'explain', component: ExplainView, meta: { requiresAuth: true, role: 'doctor' } }
  ]
})

router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next("/login")
  } 
  else if (to.meta.requiresAuth && to.meta.role !== authStore.role) {
    next(authStore.role === 'admin' ? '/admin' : '/records')
  } 
  else if (to.path === '/login' && authStore.isAuthenticated) {
    next(authStore.role === 'admin' ? '/admin' : '/records')
  } 
  else {
    next()
  }
})

export default router