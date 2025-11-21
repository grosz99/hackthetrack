import React from 'react';

/**
 * Error Boundary Component
 *
 * Catches JavaScript errors anywhere in the component tree and displays a fallback UI
 * instead of crashing the entire application.
 *
 * Usage:
 * <ErrorBoundary>
 *   <YourComponent />
 * </ErrorBoundary>
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    // Log error details for debugging
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo
    });
  }

  handleReload = () => {
    // Reload the page to reset the error state
    window.location.reload();
  };

  render() {
    if (this.state.hasError) {
      // Fallback UI
      return (
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          padding: '20px',
          backgroundColor: '#f5f5f5',
          fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
        }}>
          <div style={{
            maxWidth: '600px',
            backgroundColor: 'white',
            borderRadius: '8px',
            padding: '40px',
            boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
            textAlign: 'center'
          }}>
            <h1 style={{
              fontSize: '24px',
              fontWeight: 'bold',
              marginBottom: '16px',
              color: '#d32f2f'
            }}>
              Something went wrong
            </h1>

            <p style={{
              fontSize: '16px',
              color: '#666',
              marginBottom: '24px',
              lineHeight: '1.5'
            }}>
              We encountered an unexpected error. Don't worry, your data is safe.
            </p>

            <button
              onClick={this.handleReload}
              style={{
                backgroundColor: '#d32f2f',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                padding: '12px 24px',
                fontSize: '16px',
                fontWeight: '500',
                cursor: 'pointer',
                transition: 'background-color 0.2s'
              }}
              onMouseOver={(e) => e.target.style.backgroundColor = '#b71c1c'}
              onMouseOut={(e) => e.target.style.backgroundColor = '#d32f2f'}
            >
              Refresh Page
            </button>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details style={{
                marginTop: '24px',
                padding: '16px',
                backgroundColor: '#f5f5f5',
                borderRadius: '4px',
                textAlign: 'left'
              }}>
                <summary style={{
                  cursor: 'pointer',
                  fontWeight: '500',
                  marginBottom: '8px',
                  color: '#333'
                }}>
                  Error Details (Development Only)
                </summary>
                <pre style={{
                  fontSize: '12px',
                  overflow: 'auto',
                  color: '#d32f2f',
                  whiteSpace: 'pre-wrap',
                  wordWrap: 'break-word'
                }}>
                  {this.state.error && this.state.error.toString()}
                  {this.state.errorInfo && this.state.errorInfo.componentStack}
                </pre>
              </details>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
