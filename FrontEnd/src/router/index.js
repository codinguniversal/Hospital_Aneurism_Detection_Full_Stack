import { createRouter, createWebHistory } from 'vue-router'
import { authStore } from '../store.js'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import RecordsView from '../views/RecordsView.vue'
import ProfileView from '../views/ProfileView.vue'
import ResultsView from '../views/ResultsView.vue' 

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/register', name: 'register', component: RegisterView },
    { path: '/records', name: 'records', component: RecordsView, meta: {requiresAuth: true} },
    { path: '/profile', name: 'profile', component: ProfileView, meta: {requiresAuth: true} },
  
    { path: '/results/:id', name: 'results', component: ResultsView, meta: {requiresAuth: true} } 
  ]
})
router.beforeEach((to, from, next)=>{
  if (to.meta.requiresAuth && !authStore.isAuthenticated){
    next("/login")
  }else {
    next()
  }
}
)
export default router