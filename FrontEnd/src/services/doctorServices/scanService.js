import apiClient from '../apiClient';

export const scanService = {
  analyzeScan(scanId, analysisRequestData) {
    return apiClient.post(
      `/api/scans/${scanId}/analyze`, 
      analysisRequestData,
      {
        timeout: 300000 
      }
    );
  }
};