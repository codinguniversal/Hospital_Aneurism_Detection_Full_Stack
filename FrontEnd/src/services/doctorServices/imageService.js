import apiClient from '../apiClient';

export const imageService = {
  getImageUrl(imageRef) {
    if (!imageRef) return '';
    
    const baseUrl = apiClient.defaults.baseURL || window.location.origin;
    
    return `${baseUrl}/api/v1/images?image_ref=${encodeURIComponent(imageRef)}`;
  }
};