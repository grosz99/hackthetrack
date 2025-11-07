"""
Simple Snowflake connection service.

Combines best features from v1 and v2:
- Key-pair authentication (from v1)
- Logging and error handling (from v2)
- Simple, direct queries (no complex failover)
- JSON fallback when Snowflake unavailable

Philosophy: Keep it simple. If Snowflake is down, use local JSON.
No 3-layer caching, no complex retry logic, just clean code.
"""

import os
import json
import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

# Optional Snowflake imports - gracefully handle if not installed
try:
    import snowflake.connector
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    SNOWFLAKE_AVAILABLE = True
except ImportError:
    SNOWFLAKE_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Snowflake connector not available - using JSON fallback only")

load_dotenv()

logger = logging.getLogger(__name__)


class SnowflakeService:
    """Simple Snowflake connection service with JSON fallback."""

    def __init__(self):
        """Initialize with environment variables."""
        self.account = os.getenv("SNOWFLAKE_ACCOUNT")
        self.user = os.getenv("SNOWFLAKE_USER")
        self.password = os.getenv("SNOWFLAKE_PASSWORD")  # For password auth
        self.private_key_path = os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH")  # For key file
        self.private_key_base64 = os.getenv("SNOWFLAKE_PRIVATE_KEY_BASE64")  # For Railway
        self.warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
        self.database = os.getenv("SNOWFLAKE_DATABASE", "HACKTHETRACK")
        self.schema = os.getenv("SNOWFLAKE_SCHEMA", "TELEMETRY")
        self.role = os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN")
        self.enabled = os.getenv("USE_SNOWFLAKE", "false").lower() == "true"

        # JSON fallback directory
        self.data_dir = Path(__file__).parent.parent.parent / "data"

        # Connection (lazy loaded)
        self._connection = None

    def get_connection(self):
        """
        Get Snowflake connection with multiple authentication methods.

        Supports:
        1. Password auth (SNOWFLAKE_PASSWORD)
        2. Base64-encoded RSA key (SNOWFLAKE_PRIVATE_KEY_BASE64) - for Railway
        3. RSA key file path (SNOWFLAKE_PRIVATE_KEY_PATH)

        Returns:
            Active Snowflake connection or None if unavailable

        Raises:
            ValueError: If credentials are missing
        """
        if not SNOWFLAKE_AVAILABLE:
            logger.warning("Snowflake connector not installed")
            return None

        if not self.enabled:
            logger.info("Snowflake disabled (USE_SNOWFLAKE=false)")
            return None

        if not self.account or not self.user:
            raise ValueError("Missing SNOWFLAKE_ACCOUNT and SNOWFLAKE_USER")

        try:
            # Method 1: Password authentication (simplest for Railway)
            if self.password:
                logger.info("Using password authentication")
                conn = snowflake.connector.connect(
                    user=self.user,
                    password=self.password,
                    account=self.account,
                    warehouse=self.warehouse,
                    database=self.database,
                    schema=self.schema,
                    role=self.role,
                    client_session_keep_alive=True,
                )
                logger.info(f"✅ Connected to Snowflake: {self.database}.{self.schema}")
                return conn

            # Method 2: Base64-encoded private key (Railway-friendly)
            if self.private_key_base64:
                import base64
                logger.info("Using base64-encoded RSA key authentication")

                # Decode base64 key
                key_bytes = base64.b64decode(self.private_key_base64)
                p_key = serialization.load_pem_private_key(
                    key_bytes,
                    password=None,
                    backend=default_backend()
                )

                pkb = p_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )

                conn = snowflake.connector.connect(
                    user=self.user,
                    account=self.account,
                    private_key=pkb,
                    warehouse=self.warehouse,
                    database=self.database,
                    schema=self.schema,
                    role=self.role,
                    client_session_keep_alive=True,
                )
                logger.info(f"✅ Connected to Snowflake: {self.database}.{self.schema}")
                return conn

            # Method 3: Private key file path (original method)
            if self.private_key_path:
                logger.info("Using RSA key file authentication")

                with open(self.private_key_path, "rb") as key_file:
                    p_key = serialization.load_pem_private_key(
                        key_file.read(),
                        password=None,
                        backend=default_backend()
                    )

                pkb = p_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )

                conn = snowflake.connector.connect(
                    user=self.user,
                    account=self.account,
                    private_key=pkb,
                    warehouse=self.warehouse,
                    database=self.database,
                    schema=self.schema,
                    role=self.role,
                    client_session_keep_alive=True,
                )
                logger.info(f"✅ Connected to Snowflake: {self.database}.{self.schema}")
                return conn

            # No authentication method provided
            raise ValueError(
                "No Snowflake authentication method provided. "
                "Set one of: SNOWFLAKE_PASSWORD, SNOWFLAKE_PRIVATE_KEY_BASE64, "
                "or SNOWFLAKE_PRIVATE_KEY_PATH"
            )

        except Exception as e:
            logger.error(f"❌ Snowflake connection failed: {e}")
            return None

    def query(self, sql: str, params: Optional[List] = None) -> Optional[pd.DataFrame]:
        """
        Execute SQL query and return DataFrame.

        Args:
            sql: SQL query string
            params: Optional query parameters

        Returns:
            DataFrame with results, or None if query fails
        """
        try:
            conn = self.get_connection()
            if not conn:
                logger.warning("Snowflake unavailable, query skipped")
                return None

            cursor = conn.cursor()

            if params:
                cursor.execute(sql, params)
            else:
                cursor.execute(sql)

            # Fetch results
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()

            cursor.close()

            if data:
                df = pd.DataFrame(data, columns=columns)
                logger.info(f"✅ Query returned {len(df)} rows")
                return df
            else:
                logger.info("Query returned no data")
                return pd.DataFrame()

        except Exception as e:
            logger.error(f"❌ Query failed: {e}")
            return None

    def get_telemetry_data(self, track_id: str, race_num: int) -> Optional[pd.DataFrame]:
        """
        Get telemetry data for track and race.

        Tries Snowflake first, falls back to local JSON.

        Args:
            track_id: Track identifier
            race_num: Race number (1 or 2)

        Returns:
            DataFrame with telemetry data
        """
        # Try Snowflake first
        if self.enabled:
            sql = """
                SELECT *
                FROM HACKTHETRACK.TELEMETRY.TELEMETRY_DATA_ALL
                WHERE track_id = %s AND race_num = %s
                ORDER BY lap, distance_into_lap
            """
            df = self.query(sql, params=[track_id, race_num])

            if df is not None and not df.empty:
                logger.info(f"✅ Loaded {len(df)} telemetry rows from Snowflake")
                return df

        # Fallback to local JSON
        logger.warning("⚠️  Falling back to local JSON data")
        return self._load_from_json(f"telemetry_{track_id}_race{race_num}.json")

    def get_drivers_with_telemetry(self) -> List[int]:
        """
        Get list of driver numbers with telemetry data.

        Returns:
            List of driver numbers
        """
        # Try Snowflake first
        if self.enabled:
            sql = "SELECT DISTINCT vehicle_number FROM HACKTHETRACK.TELEMETRY.TELEMETRY_DATA_ALL ORDER BY vehicle_number"
            df = self.query(sql)

            if df is not None and not df.empty:
                # Snowflake returns column names in UPPERCASE
                column_name = 'VEHICLE_NUMBER' if 'VEHICLE_NUMBER' in df.columns else 'vehicle_number'
                drivers = df[column_name].tolist()
                logger.info(f"✅ Found {len(drivers)} drivers with telemetry")
                return drivers

        # Fallback to local data
        logger.warning("⚠️  Using local data for driver list")
        # Return hardcoded list based on known data
        return [7, 13, 18, 24, 27, 30, 51, 60]  # Update based on actual data

    def _load_from_json(self, filename: str) -> Optional[pd.DataFrame]:
        """
        Load data from local JSON file.

        Args:
            filename: JSON file name

        Returns:
            DataFrame or None if file not found
        """
        filepath = self.data_dir / filename

        if not filepath.exists():
            logger.error(f"❌ JSON file not found: {filepath}")
            return None

        try:
            with open(filepath, 'r') as f:
                data = json.load(f)

            df = pd.DataFrame(data)
            logger.info(f"✅ Loaded {len(df)} rows from {filename}")
            return df

        except Exception as e:
            logger.error(f"❌ Failed to load JSON: {e}")
            return None

    def health_check(self) -> Dict[str, Any]:
        """
        Check Snowflake connection health.

        Returns:
            Health status dict
        """
        if not self.enabled:
            return {
                "status": "disabled",
                "message": "Snowflake is disabled (USE_SNOWFLAKE=false)"
            }

        try:
            conn = self.get_connection()
            if conn:
                # Simple query to test connection
                cursor = conn.cursor()
                cursor.execute("SELECT CURRENT_VERSION()")
                version = cursor.fetchone()[0]
                cursor.close()

                return {
                    "status": "healthy",
                    "version": version,
                    "database": f"{self.database}.{self.schema}"
                }
            else:
                return {
                    "status": "unavailable",
                    "message": "Could not establish connection"
                }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


# Global instance
snowflake_service = SnowflakeService()
