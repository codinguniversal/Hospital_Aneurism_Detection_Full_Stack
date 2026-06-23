import apiClient from './apiClient';

export const userService = {
    async getAllUsers(){
        return apiClient.get('/users');
    },

    async deleteUser(userId){
        return apiClient.delete(`/users/${userId}`);
    }
};