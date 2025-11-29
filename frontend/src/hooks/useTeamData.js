import { useQuery } from '@tanstack/react-query';
import { teamsApi } from '../api/teams';

/**
 * Custom hook to fetch timeline data
 * @param {Object} params - Query parameters for timeline (start_year, end_year, etc.)
 * @returns {Object} React Query result with data, isLoading, error, refetch
 */
export function useTimeline(params = {}) {
  return useQuery({
    queryKey: ['timeline', params],
    queryFn: async () => {
      const response = await teamsApi.getTimeline(params);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });
}

/**
 * Custom hook to fetch team history by node ID
 * @param {string} nodeId - The team node ID
 * @returns {Object} React Query result with data, isLoading, error, refetch
 */
export function useTeamHistory(nodeId) {
  return useQuery({
    queryKey: ['teamHistory', nodeId],
    queryFn: async () => {
      const response = await teamsApi.getTeamHistory(nodeId);
      return response.data;
    },
    enabled: !!nodeId, // Only run query if nodeId exists
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });
}

/**
 * Custom hook to fetch list of teams
 * @param {Object} params - Query parameters (skip, limit, filters)
 * @returns {Object} React Query result with data, isLoading, error, refetch
 */
export function useTeams(params = {}) {
  return useQuery({
    queryKey: ['teams', params],
    queryFn: async () => {
      const response = await teamsApi.getTeams(params);
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: 1,
  });
}
