import apiClient from '../apiClient';

export const scanService = {
    async analyzeScan(scanId, analysisRequestData){
        return apiClient.post(`/api/scans/${scanId}/analyze`, analysisRequestData);
    }
};