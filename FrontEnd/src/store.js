import { reactive } from 'vue'

export const authStore = reactive({
  isAuthenticated: false,
  employeeId: '',
  role: '', 
  emai: '',
  
  login(identifier, role, email) {
    this.isAuthenticated = true
    this.role = role
    this.employeeId = identifier
    this.emial = emial
  },
  
  logout() {
    this.isAuthenticated = false
    this.employeeId = ''
    this.role = ''
    this.email = ''
  }
})