import { describe, it, expect, beforeEach, vi } from 'vitest';
import * as api from './api';

describe('API Service', () => {
  beforeEach(() => {
    global.fetch = vi.fn();
  });

  describe('getDrivers', () => {
    it('should fetch all drivers successfully', async () => {
      const mockDrivers = [
        { driver_number: 7, name: 'Test Driver', overall_score: 85.5 },
        { driver_number: 13, name: 'Another Driver', overall_score: 82.3 },
      ];

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockDrivers,
      });

      const result = await api.getDrivers();

      expect(result).toEqual(mockDrivers);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/drivers')
      );
    });

    it('should handle fetch errors gracefully', async () => {
      global.fetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(api.getDrivers()).rejects.toThrow('Failed to fetch drivers');
    });

    it('should filter by track when trackId provided', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => [],
      });

      await api.getDrivers(1);

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/drivers?track_id=1')
      );
    });
  });

  describe('getDriver', () => {
    it('should fetch specific driver details', async () => {
      const mockDriver = {
        driver_number: 7,
        name: 'Test Driver',
        speed: 85.5,
        consistency: 78.2,
        racecraft: 82.1,
        tire_management: 80.5,
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockDriver,
      });

      const result = await api.getDriver(7);

      expect(result).toEqual(mockDriver);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/drivers/7')
      );
    });

    it('should throw error for non-OK responses', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
      });

      await expect(api.getDriver(999)).rejects.toThrow('Failed to fetch driver 999');
    });
  });

  describe('getTracks', () => {
    it('should fetch all tracks', async () => {
      const mockTracks = [
        { track_id: 1, name: 'Barber Motorsports Park' },
        { track_id: 2, name: 'Road Atlanta' },
      ];

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockTracks,
      });

      const result = await api.getTracks();

      expect(result).toEqual(mockTracks);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/tracks')
      );
    });
  });

  describe('compareTelemetry', () => {
    it('should compare telemetry between two drivers', async () => {
      const mockComparison = {
        driver_1: 7,
        driver_2: 13,
        data: { laps: [] },
      };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockComparison,
      });

      const result = await api.compareTelemetry(1, 7, 13);

      expect(result).toEqual(mockComparison);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/telemetry/compare')
      );
    });
  });

  describe('checkHealth', () => {
    it('should check API health', async () => {
      const mockHealth = { status: 'healthy' };

      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockHealth,
      });

      const result = await api.checkHealth();

      expect(result).toEqual(mockHealth);
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/health')
      );
    });
  });

  describe('Default API object', () => {
    it('should support get method', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ test: 'data' }),
      });

      const result = await api.default.get('/test');

      expect(result.data).toEqual({ test: 'data' });
    });

    it('should support post method', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true }),
      });

      const result = await api.default.post('/test', { foo: 'bar' });

      expect(result.data).toEqual({ success: true });
    });

    it('should handle errors with axios-like structure', async () => {
      global.fetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        json: async () => null,
      });

      try {
        await api.default.get('/test');
        expect.fail('Should have thrown an error');
      } catch (error) {
        expect(error.response).toBeDefined();
        expect(error.response.status).toBe(500);
      }
    });
  });
});
