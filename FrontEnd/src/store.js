import { reactive } from 'vue'

export const authStore = reactive({
  isAuthenticated: Boolean(localStorage.getItem('access_token')),
  employeeId: localStorage.getItem('employee_id') || '',
  role: localStorage.getItem('user_role') || '',

  
  login(identifier, role) {
    this.isAuthenticated = true
    this.role = role
    this.employeeId = identifier
  },
  
  logout() {
    this.isAuthenticated = false
    this.employeeId = ''
    this.role = ''
    localStorage.removeItem('access_token')
    localStorage.removeItem('employee_id')
    localStorage.removeItem('user_role')
  }
})
