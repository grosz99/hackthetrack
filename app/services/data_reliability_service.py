"""
BULLETPROOF Data Reliability Service

ZERO TOLERANCE for "no data" bugs.

This service implements multiple layers of failover to ensure
data is ALWAYS available, even if Snowflake is down.

Architecture:
1. Try Snowflake (primary)
2. Fall back to local JSON (backup)
3. Serve from cache (last resort)
4. Log and alert on any failures
"""

import logging
from typing import List, Dict, Optional, Any
from enum import Enum
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Track which data source was used for observability."""
    SNOWFLAKE = "snowflake"
    LOCAL_JSON = "local_json"
    CACHE = "cache"
    NONE = "none"  # UNACCEPTABLE - triggers alert


class DataReliabilityService:
    """
    Ensures data is ALWAYS available through multiple fallback layers.

    CRITICAL: This service must NEVER return empty data without
    raising an exception.
    """

    def __init__(self):
        self.snowflake_service = None  # Lazy loaded
        self.cache = {}  # Simple in-memory cache (upgrade to Redis later)
        self.data_dir = Path(__file__).parent.parent.parent.parent / "data"

    def get_drivers_with_telemetry(self) -> Dict[str, Any]:
        """
        Get list of drivers with telemetry data.

        Returns GUARANTEED non-empty driver list or raises exception.

        Returns:
            {
                "drivers": List[int],  # NEVER empty
                "source": str,  # Which data source was used
                "cached": bool,  # Was this served from cache
                "health": str  # "healthy" or "degraded"
            }

        Raises:
            DataUnavailableError: If ALL sources fail (triggers alert)
        """

        # Layer 1: Try Snowflake (preferred)
        try:
            drivers = self._get_drivers_from_snowflake()
            if drivers and len(drivers) > 0:
                # Cache the successful result
                self.cache['drivers'] = drivers
                logger.info(f"✅ Snowflake: Retrieved {len(drivers)} drivers")
                return {
                    "drivers": drivers,
                    "source": DataSource.SNOWFLAKE.value,
                    "cached": False,
                    "health": "healthy"
                }
        except Exception as e:
            logger.warning(f"⚠️ Snowflake failed: {e}")
            # Continue to fallback

        # Layer 2: Try Local JSON (backup)
        try:
            drivers = self._get_drivers_from_json()
            if drivers and len(drivers) > 0:
                logger.warning(f"⚠️ Falling back to JSON: {len(drivers)} drivers")
                return {
                    "drivers": drivers,
                    "source": DataSource.LOCAL_JSON.value,
                    "cached": False,
                    "health": "degraded"  # Snowflake is down
                }
        except Exception as e:
            logger.error(f"❌ JSON fallback failed: {e}")
            # Continue to cache

        # Layer 3: Serve from cache (last resort)
        if 'drivers' in self.cache and len(self.cache['drivers']) > 0:
            logger.error("🚨 SERVING FROM CACHE - Both Snowflake and JSON failed!")
            return {
                "drivers": self.cache['drivers'],
                "source": DataSource.CACHE.value,
                "cached": True,
                "health": "critical"  # Both sources down
            }

        # Layer 4: TOTAL FAILURE - Raise exception
        error_msg = "🚨 CRITICAL: NO DATA AVAILABLE FROM ANY SOURCE"
        logger.critical(error_msg)
        raise DataUnavailableError(error_msg)

    def _get_drivers_from_snowflake(self) -> List[int]:
        """Fetch drivers from Snowflake with validation."""
        if not self.snowflake_service:
            from app.services.snowflake_service import snowflake_service
            self.snowflake_service = snowflake_service

        drivers = self.snowflake_service.get_drivers_with_telemetry()

        # VALIDATION: Must have drivers
        if not drivers or len(drivers) == 0:
            raise ValueError("Snowflake returned empty driver list")

        # VALIDATION: Must be reasonable count
        if len(drivers) > 200:  # Sanity check
            logger.warning(f"Unusual driver count: {len(drivers)}")

        return sorted(drivers)

    def _get_drivers_from_json(self) -> List[int]:
        """
        Fetch drivers from local JSON files (fallback).

        Scans telemetry JSON files to find unique driver numbers.
        """
        drivers = set()

        # Check if we have the JSON data directory
        json_dir = self.data_dir / "json"
        if not json_dir.exists():
            logger.error(f"JSON directory not found: {json_dir}")
            raise FileNotFoundError(f"JSON data directory missing: {json_dir}")

        # Scan driver mapping files
        driver_mapping_files = list(json_dir.glob("**/driver_mapping_*.json"))

        if not driver_mapping_files:
            logger.error("No driver mapping JSON files found")
            raise FileNotFoundError("No driver mapping files found")

        for file_path in driver_mapping_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Extract driver numbers from mapping
                    if isinstance(data, dict):
                        drivers.update(int(k) for k in data.keys() if k.isdigit())
                    elif isinstance(data, list):
                        drivers.update(int(d['vehicle_number']) for d in data if 'vehicle_number' in d)
            except Exception as e:
                logger.warning(f"Failed to read {file_path}: {e}")
                continue

        if not drivers:
            raise ValueError("No drivers found in JSON files")

        return sorted(list(drivers))

    def get_telemetry_data(
        self,
        track_id: str,
        race_num: int,
        driver_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get telemetry data with guaranteed availability.

        Args:
            track_id: Track identifier (e.g., 'barber', 'cota')
            race_num: Race number (1 or 2)
            driver_number: Optional driver filter

        Returns:
            {
                "data": DataFrame or dict,  # Telemetry data
                "source": str,  # Data source used
                "row_count": int,  # Number of data points
                "health": str  # System health
            }

        Raises:
            DataUnavailableError: If no data available
        """

        # Layer 1: Try Snowflake
        try:
            data = self._get_telemetry_from_snowflake(track_id, race_num, driver_number)
            if data is not None and len(data) > 0:
                cache_key = f"telemetry_{track_id}_{race_num}_{driver_number}"
                self.cache[cache_key] = data

                return {
                    "data": data,
                    "source": DataSource.SNOWFLAKE.value,
                    "row_count": len(data),
                    "health": "healthy"
                }
        except Exception as e:
            logger.warning(f"⚠️ Snowflake telemetry failed: {e}")

        # Layer 2: Try Local JSON
        try:
            data = self._get_telemetry_from_json(track_id, race_num, driver_number)
            if data is not None and len(data) > 0:
                return {
                    "data": data,
                    "source": DataSource.LOCAL_JSON.value,
                    "row_count": len(data),
                    "health": "degraded"
                }
        except Exception as e:
            logger.error(f"❌ JSON telemetry failed: {e}")

        # Layer 3: Cache
        cache_key = f"telemetry_{track_id}_{race_num}_{driver_number}"
        if cache_key in self.cache:
            logger.error("🚨 SERVING TELEMETRY FROM CACHE")
            data = self.cache[cache_key]
            return {
                "data": data,
                "source": DataSource.CACHE.value,
                "row_count": len(data),
                "health": "critical"
            }

        # Total failure
        error_msg = f"No telemetry data available for {track_id} race {race_num}"
        logger.critical(error_msg)
        raise DataUnavailableError(error_msg)

    def _get_telemetry_from_snowflake(self, track_id, race_num, driver_number):
        """Fetch telemetry from Snowflake."""
        if not self.snowflake_service:
            from app.services.snowflake_service import snowflake_service
            self.snowflake_service = snowflake_service

        return self.snowflake_service.get_telemetry_data(
            track_id, race_num, driver_number
        )

    def _get_telemetry_from_json(self, track_id, race_num, driver_number):
        """Fetch telemetry from local JSON files."""
        # Look for JSON file
        json_path = self.data_dir / "json" / f"{track_id}_r{race_num}_telemetry.json"

        if not json_path.exists():
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        with open(json_path, 'r') as f:
            data = json.load(f)

        # Filter by driver if specified
        if driver_number is not None:
            data = [d for d in data if d.get('vehicle_number') == driver_number]

        return data

    def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive health check of all data sources.

        Returns:
            {
                "snowflake": {"available": bool, "driver_count": int},
                "local_json": {"available": bool, "file_count": int},
                "cache": {"size": int, "keys": List[str]},
                "overall_health": str,  # "healthy", "degraded", "critical"
                "recommendations": List[str]
            }
        """
        health = {
            "snowflake": {"available": False, "driver_count": 0},
            "local_json": {"available": False, "file_count": 0},
            "cache": {"size": len(self.cache), "keys": list(self.cache.keys())},
            "overall_health": "critical",
            "recommendations": []
        }

        # Test Snowflake
        try:
            drivers = self._get_drivers_from_snowflake()
            health["snowflake"] = {
                "available": True,
                "driver_count": len(drivers)
            }
        except Exception as e:
            health["recommendations"].append(f"Snowflake unavailable: {e}")

        # Test Local JSON
        try:
            drivers = self._get_drivers_from_json()
            json_dir = self.data_dir / "json"
            file_count = len(list(json_dir.glob("**/*.json"))) if json_dir.exists() else 0
            health["local_json"] = {
                "available": True,
                "file_count": file_count
            }
        except Exception as e:
            health["recommendations"].append(f"JSON files unavailable: {e}")

        # Determine overall health
        if health["snowflake"]["available"]:
            health["overall_health"] = "healthy"
        elif health["local_json"]["available"]:
            health["overall_health"] = "degraded"
            health["recommendations"].append("Using fallback data source (JSON)")
        elif len(self.cache) > 0:
            health["overall_health"] = "critical"
            health["recommendations"].append("Only cache available - both sources down!")
        else:
            health["overall_health"] = "failed"
            health["recommendations"].append("NO DATA SOURCES AVAILABLE - IMMEDIATE ACTION REQUIRED")

        return health


class DataUnavailableError(Exception):
    """Raised when ALL data sources fail - triggers alerting."""
    pass


# Global instance
data_reliability_service = DataReliabilityService()
