import apiClient from './apiClient';

export const settingsApi = {
    async getSettings() {
        return apiClient.get('/admin/settings');
    },

    async updateSettings(newSettings){
        return apiClient.put('/admin/settings', newSettings);
    }
}
     




