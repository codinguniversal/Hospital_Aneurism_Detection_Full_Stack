import { reactive } from 'vue'

export const authStore = reactive({
  isAuthenticated: false,
  employeeId: '',
  role: '', 
  
  login(identifier, role) {
    this.isAuthenticated = true
    this.role = role
    this.employeeId = identifier
  },
  
  logout() {
    this.isAuthenticated = false
    this.employeeId = ''
    this.role = ''
  }
})