/**
 * Utility function to test API connectivity
 * Can be imported and called from components to verify backend is accessible
 */
import { teamsApi } from './teams';

export const testApiConnection = async () => {
  try {
    const response = await teamsApi.getTimeline();
    console.log('✓ API Connection successful:', response.data);
    return { success: true, data: response.data };
  } catch (error) {
    console.error('✗ API Connection failed:', error.message);
    return { success: false, error: error.message };
  }
};

export default testApiConnection;
