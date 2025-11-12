/**
 * API service for communicating with Racing Analytics backend.
 */

// Determine API base URL based on environment
// Always use VITE_API_URL environment variable
// Production: Points to Railway backend (set in Vercel dashboard)
// Development: Points to localhost backend
const getApiBaseUrl = () => {
  // Always use environment variable, fallback to localhost for development
  return import.meta.env.VITE_API_URL || 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

/**
 * Fetch all tracks
 */
export async function getTracks() {
  const response = await fetch(`${API_BASE_URL}/api/tracks`);
  if (!response.ok) throw new Error('Failed to fetch tracks');
  return response.json();
}

/**
 * Fetch specific track
 */
export async function getTrack(trackId) {
  const response = await fetch(`${API_BASE_URL}/api/tracks/${trackId}`);
  if (!response.ok) throw new Error(`Failed to fetch track ${trackId}`);
  return response.json();
}

/**
 * Fetch all drivers (optionally filtered by track)
 */
export async function getDrivers(trackId = null) {
  const url = trackId
    ? `${API_BASE_URL}/api/drivers?track_id=${trackId}`
    : `${API_BASE_URL}/api/drivers`;

  const response = await fetch(url);
  if (!response.ok) throw new Error('Failed to fetch drivers');
  return response.json();
}

/**
 * Fetch specific driver
 */
export async function getDriver(driverNumber) {
  const response = await fetch(`${API_BASE_URL}/api/drivers/${driverNumber}`);
  if (!response.ok) throw new Error(`Failed to fetch driver ${driverNumber}`);
  return response.json();
}

/**
 * Predict driver performance at track
 */
export async function predictPerformance(driverNumber, trackId) {
  const response = await fetch(`${API_BASE_URL}/api/predict`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      driver_number: driverNumber,
      track_id: trackId,
    }),
  });

  if (!response.ok) throw new Error('Failed to predict performance');
  return response.json();
}

/**
 * Send chat message to AI strategy bot
 */
export async function sendChatMessage(message, driverNumber, trackId, history = []) {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      message,
      driver_number: driverNumber,
      track_id: trackId,
      history,
    }),
  });

  if (!response.ok) throw new Error('Failed to send chat message');
  return response.json();
}

/**
 * Compare telemetry between two drivers
 */
export async function compareTelemetry(trackId, driver1, driver2, raceNum = 1) {
  const response = await fetch(
    `${API_BASE_URL}/api/telemetry/compare?track_id=${trackId}&driver_1=${driver1}&driver_2=${driver2}&race_num=${raceNum}`
  );

  if (!response.ok) throw new Error('Failed to compare telemetry');
  return response.json();
}

/**
 * Get detailed telemetry with three-tier comparison
 */
export async function getDetailedTelemetry(trackId, raceNum, driverNumber, lapNumber = null) {
  const params = new URLSearchParams({
    track_id: trackId,
    race_num: raceNum,
    driver_number: driverNumber,
    data_type: 'speed_trace'
  });

  if (lapNumber !== null) {
    params.append('lap_number', lapNumber);
  }

  const response = await fetch(`${API_BASE_URL}/api/telemetry/detailed?${params}`);
  if (!response.ok) throw new Error('Failed to fetch detailed telemetry');
  return response.json();
}

/**
 * Check API health
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  if (!response.ok) throw new Error('API health check failed');
  return response.json();
}

/**
 * Default export - Axios-like interface for backward compatibility
 * Mimics Axios error structure for consistent error handling
 */
const api = {
  get: async (url) => {
    try {
      const response = await fetch(`${API_BASE_URL}${url}`);
      if (!response.ok) {
        // Create axios-like error with response details
        const error = new Error(`Failed to fetch ${url}`);
        error.response = {
          status: response.status,
          statusText: response.statusText,
          data: await response.json().catch(() => null)
        };
        error.config = { url: `${API_BASE_URL}${url}` };
        throw error;
      }
      const data = await response.json();
      return { data };
    } catch (err) {
      // If error already has response (from above), re-throw
      if (err.response) throw err;

      // Otherwise, wrap network/parse errors
      const error = new Error(err.message);
      error.response = { status: 0, statusText: 'Network Error', data: null };
      error.config = { url: `${API_BASE_URL}${url}` };
      throw error;
    }
  },
  post: async (url, body) => {
    try {
      const response = await fetch(`${API_BASE_URL}${url}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(body),
      });
      if (!response.ok) {
        // Create axios-like error with response details
        const error = new Error(`Failed to post to ${url}`);
        error.response = {
          status: response.status,
          statusText: response.statusText,
          data: await response.json().catch(() => null)
        };
        error.config = { url: `${API_BASE_URL}${url}`, method: 'POST' };
        throw error;
      }
      const data = await response.json();
      return { data };
    } catch (err) {
      // If error already has response (from above), re-throw
      if (err.response) throw err;

      // Otherwise, wrap network/parse errors
      const error = new Error(err.message);
      error.response = { status: 0, statusText: 'Network Error', data: null };
      error.config = { url: `${API_BASE_URL}${url}`, method: 'POST' };
      throw error;
    }
  },
};

export default api;
