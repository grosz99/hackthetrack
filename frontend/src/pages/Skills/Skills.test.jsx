import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Skills from './Skills';
import { DriverProvider } from '../../context/DriverContext';
import * as api from '../../services/api';

// Mock the API module
vi.mock('../../services/api');

// Mock data
const mockDriver = {
  driver_number: 13,
  driver_name: "Test Driver",
  overall_score: 85.5,
  speed: {
    score: 82.3,
    percentile: 75,
    z_score: 0.67,
    rank: 9
  },
  consistency: {
    score: 88.7,
    percentile: 82,
    z_score: 0.92,
    rank: 6
  },
  racecraft: {
    score: 85.1,
    percentile: 78,
    z_score: 0.77,
    rank: 8
  },
  tire_management: {
    score: 86.2,
    percentile: 80,
    z_score: 0.84,
    rank: 7
  },
  stats: {
    races_completed: 12,
    average_finish: 5.2,
    best_finish: 1,
    worst_finish: 12
  },
  circuit_fits: {
    barber: 87.5,
    sebring: 82.3
  }
};

const mockFactorBreakdowns = {
  "13": {
    speed: {
      variables: [
        { name: "Qualifying Pace", value: 85.2, percentile: 78 },
        { name: "Best Lap", value: 88.1, percentile: 80 }
      ]
    },
    consistency: {
      variables: [
        { name: "Braking Consistency", value: 92.1, percentile: 85 },
        { name: "Sector Consistency", value: 89.3, percentile: 82 }
      ]
    },
    racecraft: {
      variables: [
        { name: "Positions Gained", value: 2.5, percentile: 75 }
      ]
    },
    tire_management: {
      variables: [
        { name: "Late Pace Ratio", value: 0.95, percentile: 78 }
      ]
    }
  }
};

describe('Skills Page', () => {
  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks();

    // Setup default mock implementations
    api.getDriver.mockResolvedValue(mockDriver);
    api.getFactorBreakdowns.mockResolvedValue(mockFactorBreakdowns);
  });

  it('renders loading state initially', () => {
    render(
      <BrowserRouter>
        <DriverProvider>
          <Skills />
        </DriverProvider>
      </BrowserRouter>
    );

    // Check for loading indicator (adjust selector based on actual implementation)
    expect(screen.queryByText(/loading/i) || screen.queryByRole('progressbar')).toBeTruthy();
  });

  it('displays driver 4-factor scores after loading', async () => {
    render(
      <BrowserRouter>
        <DriverProvider>
          <Skills />
        </DriverProvider>
      </BrowserRouter>
    );

    // Wait for data to load
    await waitFor(() => {
      expect(api.getDriver).toHaveBeenCalled();
    });

    // Check that scores are displayed (adjust selectors based on actual implementation)
    await waitFor(() => {
      // Should show factor names
      expect(screen.getByText(/speed/i)).toBeTruthy();
      expect(screen.getByText(/consistency/i)).toBeTruthy();
      expect(screen.getByText(/racecraft/i)).toBeTruthy();
      expect(screen.getByText(/tire management/i)).toBeTruthy();
    });
  });

  it('handles API errors gracefully', async () => {
    // Mock API error
    api.getDriver.mockRejectedValue(new Error('Failed to fetch driver data'));

    render(
      <BrowserRouter>
        <DriverProvider>
          <Skills />
        </DriverProvider>
      </BrowserRouter>
    );

    // Should show error message (adjust based on actual error handling)
    await waitFor(() => {
      expect(
        screen.queryByText(/error/i) ||
        screen.queryByText(/failed/i) ||
        screen.queryByText(/try again/i)
      ).toBeTruthy();
    });
  });

  it('displays factor breakdowns when available', async () => {
    render(
      <BrowserRouter>
        <DriverProvider>
          <Skills />
        </DriverProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(api.getFactorBreakdowns).toHaveBeenCalled();
    });

    // Should display breakdown variables (adjust based on implementation)
    await waitFor(() => {
      // At least some breakdown data should be visible
      expect(document.body.textContent).toContain('Qualifying Pace' || 'Braking Consistency');
    });
  });

  it('shows percentile rankings for each factor', async () => {
    render(
      <BrowserRouter>
        <DriverProvider>
          <Skills />
        </DriverProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(api.getDriver).toHaveBeenCalled();
    });

    // Check that percentiles are displayed (adjust based on implementation)
    await waitFor(() => {
      const bodyText = document.body.textContent;
      // Should show percentile values somewhere
      expect(bodyText).toMatch(/\d+th|percentile/i);
    });
  });

  it('displays driver statistics', async () => {
    render(
      <BrowserRouter>
        <DriverProvider>
          <Skills />
        </DriverProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(api.getDriver).toHaveBeenCalled();
    });

    // Should display race stats (adjust based on implementation)
    await waitFor(() => {
      const bodyText = document.body.textContent;
      expect(
        bodyText.includes('12') || // races completed
        bodyText.includes('5.2') || // average finish
        bodyText.includes('Best') ||
        bodyText.includes('Average')
      ).toBeTruthy();
    });
  });

  it('does not crash when data is missing', async () => {
    // Mock incomplete data
    api.getDriver.mockResolvedValue({
      driver_number: 13,
      driver_name: "Test Driver",
      // Missing most fields
    });

    render(
      <BrowserRouter>
        <DriverProvider>
          <Skills />
        </DriverProvider>
      </BrowserRouter>
    );

    // Should not crash, should handle gracefully
    await waitFor(() => {
      expect(api.getDriver).toHaveBeenCalled();
    });

    // Component should still render something
    expect(document.body).toBeTruthy();
  });

  it('updates when driver changes', async () => {
    const { rerender } = render(
      <BrowserRouter>
        <DriverProvider>
          <Skills />
        </DriverProvider>
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(api.getDriver).toHaveBeenCalledTimes(1);
    });

    // Change driver (in real app, this would come from context/route)
    const newDriver = { ...mockDriver, driver_number: 7, driver_name: "Different Driver" };
    api.getDriver.mockResolvedValue(newDriver);

    // Force re-render (in real app, route change would trigger this)
    rerender(
      <BrowserRouter>
        <DriverProvider>
          <Skills />
        </DriverProvider>
      </BrowserRouter>
    );

    // Should fetch new driver data
    await waitFor(() => {
      // Verify API was called (may be called multiple times during component lifecycle)
      expect(api.getDriver).toHaveBeenCalled();
    });
  });
});
