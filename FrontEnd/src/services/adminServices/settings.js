import apiClient from '../apiClient';

export const settingsApi = {
    async getSettings() {
        return apiClient.get('/admin/settings');
    },

   updateSystemSettings(configPayload) {
    return apiClient.put('/admin/settings', configPayload); 
  }
}
     




