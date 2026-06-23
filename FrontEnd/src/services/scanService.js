import apiClient from './apiClient';

export const scanService = {
    async analyzeScan(scanId, analysisRequestData){
        return apiClient.post(`/scans/${scanId}/analyze`, analysisRequestData);
    }
};