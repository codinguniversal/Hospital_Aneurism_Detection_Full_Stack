import apiClient from './apiClient';

export const patientService = {
  
  getAllRecords() {
    return apiClient.get('/patients/records');
  },

  getPatientResults(patientId) {
    return apiClient.get(`/patients/${patientId}`);
  }
};