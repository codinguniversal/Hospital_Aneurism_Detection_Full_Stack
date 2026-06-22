
import { apiRequest } from './api.js' // Assuming apiRequest is exported from api.js

export const patientService = {

  async getRecords() {
    return apiRequest('/patients/records', {
      method: 'GET', 
    })
  },


  async getPatientById(patientId) {
    return apiRequest(`/patients/${patientId}`, {
      method: 'GET'
    })
  }
}