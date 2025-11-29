/**
 * Error handling utilities for API requests
 */

/**
 * Extract user-friendly message from axios error
 * @param {Error} error - The error object from axios or other sources
 * @returns {string} User-friendly error message
 */
export function getErrorMessage(error) {
  // Handle axios errors
  if (error.response) {
    // Server responded with error status
    const status = error.response.status;
    const data = error.response.data;
    
    // Try to get message from response
    if (data?.detail) {
      return typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
    }
    
    if (data?.message) {
      return data.message;
    }
    
    // Default messages by status code
    switch (status) {
      case 400:
        return 'Invalid request. Please check your input.';
      case 401:
        return 'Unauthorized. Please log in.';
      case 403:
        return 'Access forbidden. You don\'t have permission to access this resource.';
      case 404:
        return 'Team not found. The resource you\'re looking for doesn\'t exist.';
      case 409:
        return 'Conflict. This resource already exists.';
      case 422:
        return 'Validation error. Please check your input.';
      case 429:
        return 'Too many requests. Please try again later.';
      case 500:
        return 'Server error. Something went wrong on our end.';
      case 502:
        return 'Bad gateway. The server is temporarily unavailable.';
      case 503:
        return 'Service unavailable. The server is temporarily down.';
      case 504:
        return 'Gateway timeout. The request took too long.';
      default:
        return `An error occurred (${status}). Please try again.`;
    }
  }
  
  // Handle network errors
  if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
    return 'Cannot connect to server. Please check your internet connection and ensure the backend is running.';
  }
  
  if (error.code === 'ECONNREFUSED') {
    return 'Connection refused. The server may not be running.';
  }
  
  if (error.code === 'ETIMEDOUT') {
    return 'Request timed out. Please try again.';
  }
  
  // Handle request errors (before sending)
  if (error.request) {
    return 'No response from server. Please check your connection.';
  }
  
  // Fallback to error message or generic message
  return error.message || 'An unexpected error occurred. Please try again.';
}

/**
 * Check if error is a network error
 * @param {Error} error - The error object
 * @returns {boolean} True if it's a network error
 */
export function isNetworkError(error) {
  return (
    error.code === 'ERR_NETWORK' ||
    error.code === 'ECONNREFUSED' ||
    error.code === 'ETIMEDOUT' ||
    error.message === 'Network Error' ||
    !error.response
  );
}

/**
 * Check if error is a validation error (4xx)
 * @param {Error} error - The error object
 * @returns {boolean} True if it's a validation error
 */
export function isValidationError(error) {
  const status = error.response?.status;
  return status >= 400 && status < 500;
}

/**
 * Check if error is a server error (5xx)
 * @param {Error} error - The error object
 * @returns {boolean} True if it's a server error
 */
export function isServerError(error) {
  const status = error.response?.status;
  return status >= 500 && status < 600;
}

/**
 * Check if error is a 404 Not Found
 * @param {Error} error - The error object
 * @returns {boolean} True if it's a 404 error
 */
export function isNotFoundError(error) {
  return error.response?.status === 404;
}

/**
 * Format error for logging
 * @param {Error} error - The error object
 * @returns {Object} Formatted error details
 */
export function formatErrorForLogging(error) {
  return {
    message: error.message,
    code: error.code,
    status: error.response?.status,
    statusText: error.response?.statusText,
    url: error.config?.url,
    method: error.config?.method,
    data: error.response?.data,
  };
}
