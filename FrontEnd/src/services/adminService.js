import {apiRequest } from './config.js'


export const settingsApi = {
    async getSettings() {
        return apiRequest('/admin/settings',{
            method: 'GET'
        })
    },

    async updateSettings(newSettings){
        return apiRequest('/admin/settings',{
            method: 'PUT',
            body: JSON.stringify(newSettings)
        })
    }
}

