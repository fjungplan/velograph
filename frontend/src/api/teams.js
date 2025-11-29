import apiClient from './client';

export const teamsApi = {
  getTimeline: (params) => 
    apiClient.get('/api/v1/timeline', { params }),
  
  getTeamHistory: (nodeId) =>
    apiClient.get(`/api/v1/teams/${nodeId}/history`),
  
  getTeams: (params) =>
    apiClient.get('/api/v1/teams', { params }),
};
