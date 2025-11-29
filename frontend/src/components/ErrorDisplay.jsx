import { Component } from 'react';
import './ErrorDisplay.css';
import { getErrorMessage, isNetworkError } from '../utils/errors';

export function ErrorDisplay({ error, onRetry }) {
  const errorMessage = getErrorMessage(error);
  const isNetwork = isNetworkError(error);
  const status = error?.response?.status;
  
  let errorType = 'error';
  if (isNetwork) {
    errorType = 'network';
  } else if (status === 404) {
    errorType = 'not-found';
  } else if (status === 500) {
    errorType = 'server';
  } else if (status >= 400 && status < 500) {
    errorType = 'validation';
  }
  
  const errorTypeClass = `error-type-${errorType}`;
  
  return (
    <div className={`error-display ${errorTypeClass}`}>
      <div className="error-icon">
        {isNetwork && '📡'}
        {status === 404 && '🔍'}
        {status === 500 && '⚠️'}
        {errorType === 'validation' && '❌'}
        {errorType === 'error' && '⚠️'}
      </div>
      <div className="error-content">
        <h3 className="error-title">
          {isNetwork && 'Connection Error'}
          {status === 404 && 'Not Found'}
          {status === 500 && 'Server Error'}
          {errorType === 'validation' && 'Validation Error'}
          {errorType === 'error' && 'An Error Occurred'}
        </h3>
        <p className="error-message">{errorMessage}</p>
        {isNetwork && (
          <p className="error-hint">
            Please check your internet connection and ensure the backend server is running.
          </p>
        )}
        {status === 404 && (
          <p className="error-hint">
            The resource you're looking for doesn't exist.
          </p>
        )}
        {onRetry && (
          <button onClick={onRetry} className="error-retry-button">
            Try Again
          </button>
        )}
      </div>
    </div>
  );
}

export class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.state = { hasError: true, error, errorInfo };
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div className="error-boundary">
          <div className="error-boundary-content">
            <h2>Something went wrong</h2>
            <p>We're sorry, but something unexpected happened.</p>
            <details className="error-details">
              <summary>Error details</summary>
              <pre>{this.state.error?.toString()}</pre>
              {this.state.errorInfo && (
                <pre>{this.state.errorInfo.componentStack}</pre>
              )}
            </details>
            <button
              onClick={() => window.location.reload()}
              className="error-boundary-reload"
            >
              Reload Page
            </button>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
