import apiClient from './client';

export const editsApi = {
  editMetadata: (data) => 
    apiClient.post('/api/v1/edits/metadata', data),
  
  createMerge: (data) =>
    apiClient.post('/api/v1/edits/merge', data),
  
  createSplit: (data) =>
    apiClient.post('/api/v1/edits/split', data),
  
  getMyEdits: () =>
    apiClient.get('/api/v1/edits/my-edits'),
  
  getPendingEdits: () =>
    apiClient.get('/api/v1/edits/pending'),
};
