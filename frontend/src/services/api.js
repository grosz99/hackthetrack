/**
 * API service for communicating with Racing Analytics backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

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
 * Check API health
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  if (!response.ok) throw new Error('API health check failed');
  return response.json();
}
