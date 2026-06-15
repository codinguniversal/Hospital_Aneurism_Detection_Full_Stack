import { reactive } from 'vue'

export const authStore = reactive({
  isAuthenticated: false,
  userName: '',
  
  login(name) {
    this.isAuthenticated = true
    this.userName = name
  },
  
  logout() {
    this.isAuthenticated = false
    this.userName = ''
  }
})