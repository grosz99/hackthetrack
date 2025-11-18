import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { DriverProvider, useDriver } from './DriverContext';

// Test component to access context
function TestComponent() {
  const { drivers, selectedDriver, setSelectedDriver, loading } = useDriver();

  return (
    <div>
      <div data-testid="loading">{loading.toString()}</div>
      <div data-testid="driver-count">{drivers.length}</div>
      <div data-testid="selected-driver">{selectedDriver || 'none'}</div>
      <button onClick={() => setSelectedDriver(7)}>Select Driver 7</button>
    </div>
  );
}

describe('DriverContext', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  it('should provide initial state', () => {
    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => [],
    });

    render(
      <DriverProvider>
        <TestComponent />
      </DriverProvider>
    );

    expect(screen.getByTestId('loading')).toHaveTextContent('true');
    expect(screen.getByTestId('driver-count')).toHaveTextContent('0');
    expect(screen.getByTestId('selected-driver')).toHaveTextContent('none');
  });

  it('should load drivers on mount', async () => {
    const mockDrivers = [
      { driver_number: 7, name: 'Test Driver 1' },
      { driver_number: 13, name: 'Test Driver 2' },
    ];

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDrivers,
    });

    render(
      <DriverProvider>
        <TestComponent />
      </DriverProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
    });

    await waitFor(() => {
      expect(screen.getByTestId('driver-count')).toHaveTextContent('2');
    });
  });

  it('should handle loading errors gracefully', async () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});

    global.fetch.mockRejectedValueOnce(new Error('Network error'));

    render(
      <DriverProvider>
        <TestComponent />
      </DriverProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
    });

    expect(consoleError).toHaveBeenCalled();
    consoleError.mockRestore();
  });

  it('should allow selecting a driver', async () => {
    const mockDrivers = [
      { driver_number: 7, name: 'Test Driver 1' },
    ];

    global.fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockDrivers,
    });

    const { getByText } = render(
      <DriverProvider>
        <TestComponent />
      </DriverProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
    });

    const button = getByText('Select Driver 7');
    button.click();

    await waitFor(() => {
      expect(screen.getByTestId('selected-driver')).toHaveTextContent('7');
    });
  });
});
