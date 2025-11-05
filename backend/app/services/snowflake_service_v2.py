"""
Snowflake connection service for telemetry data storage - Vercel Compatible.

This is an improved version of snowflake_service.py with:
- Environment variable-based private key loading (Vercel compatible)
- Connection timeouts for serverless environments
- Retry logic with exponential backoff
- Structured logging
- Better error handling

After testing, rename this file to snowflake_service.py to replace the original.
"""

import os
import time
import socket
import logging
from typing import List, Dict, Optional
from functools import lru_cache

import pandas as pd
import snowflake.connector
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from dotenv import load_dotenv

load_dotenv()

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SnowflakeService:
    """
    Service for connecting to and querying Snowflake data warehouse.

    Optimized for Vercel serverless deployment with:
    - Environment variable-based authentication
    - Connection timeouts
    - Retry logic
    - Proper error handling
    """

    def __init__(self):
        """Initialize Snowflake connection with environment variables."""
        self.account = os.getenv("SNOWFLAKE_ACCOUNT")
        self.user = os.getenv("SNOWFLAKE_USER")
        self.password = os.getenv("SNOWFLAKE_PASSWORD")
        self.warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
        self.database = os.getenv("SNOWFLAKE_DATABASE", "HACKTHETRACK")
        self.schema = os.getenv("SNOWFLAKE_SCHEMA", "TELEMETRY")
        self.role = os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN")

        # New: Support both file path and environment variable for private key
        self.private_key_path = os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH")
        self.private_key_content = os.getenv("SNOWFLAKE_PRIVATE_KEY")

        # Connection timeouts for serverless (in seconds)
        self.login_timeout = int(os.getenv("SNOWFLAKE_LOGIN_TIMEOUT", "10"))
        self.network_timeout = int(os.getenv("SNOWFLAKE_NETWORK_TIMEOUT", "30"))

        # Retry configuration
        self.max_retries = int(os.getenv("SNOWFLAKE_MAX_RETRIES", "3"))

    def _load_private_key(self) -> Optional[bytes]:
        """
        Load private key from environment variable or file.

        Priority:
        1. SNOWFLAKE_PRIVATE_KEY environment variable (for Vercel)
        2. SNOWFLAKE_PRIVATE_KEY_PATH file path (for local dev)

        Returns:
            bytes: Private key in DER/PKCS8 format, or None if not available

        Raises:
            ValueError: If private key format is invalid
        """
        try:
            # Option 1: Load from environment variable (Vercel compatible)
            if self.private_key_content:
                logger.info("Loading private key from environment variable")

                # Handle escaped newlines in environment variable
                key_content = self.private_key_content.replace('\\n', '\n')

                # Load private key from string
                private_key = serialization.load_pem_private_key(
                    key_content.encode('utf-8'),
                    password=None,
                    backend=default_backend()
                )

                # Convert to DER/PKCS8 format for Snowflake
                pkb = private_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )

                logger.info("Successfully loaded private key from environment variable")
                return pkb

            # Option 2: Load from file path (local development)
            if self.private_key_path and os.path.exists(self.private_key_path):
                logger.info(f"Loading private key from file: {self.private_key_path}")

                with open(self.private_key_path, "rb") as key_file:
                    private_key = serialization.load_pem_private_key(
                        key_file.read(),
                        password=None,
                        backend=default_backend()
                    )

                pkb = private_key.private_bytes(
                    encoding=serialization.Encoding.DER,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                )

                logger.info("Successfully loaded private key from file")
                return pkb

            # No private key available
            logger.warning("No private key configured (neither env var nor file path)")
            return None

        except Exception as e:
            logger.error(f"Failed to load private key: {str(e)}", exc_info=True)
            raise ValueError(f"Invalid private key format: {str(e)}")

    def get_connection(self, retry_attempt: int = 0):
        """
        Create and return a Snowflake connection with retry logic.

        Args:
            retry_attempt: Current retry attempt (for internal use)

        Returns:
            snowflake.connector.connection: Active Snowflake connection

        Raises:
            ValueError: If required credentials are missing
            Exception: If connection fails after all retries
        """
        # Validate required credentials
        if not all([self.account, self.user]):
            error_msg = (
                "Missing Snowflake credentials. "
                "Set SNOWFLAKE_ACCOUNT and SNOWFLAKE_USER environment variables."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

        try:
            # Try private key authentication first
            private_key = self._load_private_key()

            if private_key:
                logger.info(
                    f"Connecting to Snowflake with key-pair auth "
                    f"(account: {self.account}, user: {self.user})"
                )

                conn = snowflake.connector.connect(
                    account=self.account,
                    user=self.user,
                    private_key=private_key,
                    warehouse=self.warehouse,
                    database=self.database,
                    schema=self.schema,
                    role=self.role,
                    # CRITICAL: Set timeouts for serverless environment
                    login_timeout=self.login_timeout,
                    network_timeout=self.network_timeout,
                )

                logger.info("Successfully connected to Snowflake with key-pair auth")
                return conn

            # Fall back to password authentication
            if not self.password:
                error_msg = (
                    "Missing authentication. Set either SNOWFLAKE_PRIVATE_KEY or "
                    "SNOWFLAKE_PRIVATE_KEY_PATH or SNOWFLAKE_PASSWORD environment variable."
                )
                logger.error(error_msg)
                raise ValueError(error_msg)

            logger.info(
                f"Connecting to Snowflake with password auth "
                f"(account: {self.account}, user: {self.user})"
            )

            conn = snowflake.connector.connect(
                account=self.account,
                user=self.user,
                password=self.password,
                warehouse=self.warehouse,
                database=self.database,
                schema=self.schema,
                role=self.role,
                login_timeout=self.login_timeout,
                network_timeout=self.network_timeout,
            )

            logger.info("Successfully connected to Snowflake with password auth")
            return conn

        except (socket.timeout, ConnectionError, OSError) as e:
            # Retryable errors - network issues
            if retry_attempt < self.max_retries - 1:
                # Exponential backoff: 1s, 2s, 4s
                sleep_time = 2 ** retry_attempt
                logger.warning(
                    f"Connection attempt {retry_attempt + 1} failed with {type(e).__name__}: {str(e)}. "
                    f"Retrying in {sleep_time}s..."
                )
                time.sleep(sleep_time)
                return self.get_connection(retry_attempt=retry_attempt + 1)
            else:
                logger.error(
                    f"Connection failed after {self.max_retries} attempts: {str(e)}",
                    exc_info=True
                )
                raise

        except Exception as e:
            # Non-retryable errors - authentication, configuration, etc.
            logger.error(
                f"Snowflake connection failed (non-retryable): {type(e).__name__}: {str(e)}",
                exc_info=True
            )
            raise

    @lru_cache(maxsize=100)
    def get_drivers_with_telemetry(self) -> List[int]:
        """
        Get list of driver numbers that have telemetry data.

        Note: @lru_cache works within a single process but won't persist
        across Vercel serverless function invocations. Consider using
        Vercel Edge Config or KV for persistent caching.

        Returns:
            List[int]: Sorted list of driver numbers with telemetry data

        Example:
            >>> service = SnowflakeService()
            >>> drivers = service.get_drivers_with_telemetry()
            >>> print(drivers)
            [0, 2, 3, 5, 7, ...]
        """
        logger.info("Fetching drivers with telemetry from Snowflake")
        start_time = time.time()

        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
                SELECT DISTINCT vehicle_number
                FROM TELEMETRY_DATA_ALL
                WHERE vehicle_number IS NOT NULL
                ORDER BY vehicle_number
                LIMIT 100
            """

            cursor.execute(query)
            results = cursor.fetchall()
            drivers = [int(row[0]) for row in results]

            elapsed_ms = (time.time() - start_time) * 1000
            logger.info(
                f"Successfully fetched {len(drivers)} drivers in {elapsed_ms:.0f}ms",
                extra={"driver_count": len(drivers), "query_time_ms": elapsed_ms}
            )

            return drivers

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Failed to fetch drivers after {elapsed_ms:.0f}ms: {str(e)}",
                exc_info=True,
                extra={"error_type": type(e).__name__, "query_time_ms": elapsed_ms}
            )
            raise

        finally:
            if conn:
                try:
                    conn.close()
                    logger.debug("Connection closed successfully")
                except Exception as e:
                    logger.warning(f"Error closing connection: {str(e)}")

    def get_telemetry_data(
        self,
        track_id: str,
        race_num: int,
        driver_number: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get telemetry data from Snowflake for a specific track and race.

        Args:
            track_id: Track identifier (e.g., 'barber', 'cota')
            race_num: Race number (1 or 2)
            driver_number: Optional driver number to filter by

        Returns:
            pd.DataFrame: Telemetry data with all columns

        Example:
            >>> service = SnowflakeService()
            >>> df = service.get_telemetry_data('barber', 1, 13)
            >>> print(df.columns)
            ['vehicle_number', 'lap', 'speed', 'throttle', 'brake', ...]
        """
        logger.info(
            f"Fetching telemetry data for track={track_id}, race={race_num}, driver={driver_number}"
        )
        start_time = time.time()

        conn = None
        try:
            conn = self.get_connection()

            # Parameterized query to prevent SQL injection
            query = """
                SELECT * FROM TELEMETRY_DATA_ALL
                WHERE track_id = %s AND race_num = %s
            """
            params = [track_id, race_num]

            if driver_number is not None:
                query += " AND vehicle_number = %s"
                params.append(driver_number)

            query += " ORDER BY vehicle_number, lap, timestamp"

            df = pd.read_sql(query, conn, params=params)

            elapsed_ms = (time.time() - start_time) * 1000
            logger.info(
                f"Successfully fetched {len(df)} rows in {elapsed_ms:.0f}ms",
                extra={
                    "track_id": track_id,
                    "race_num": race_num,
                    "driver_number": driver_number,
                    "row_count": len(df),
                    "query_time_ms": elapsed_ms
                }
            )

            return df

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(
                f"Failed to fetch telemetry data after {elapsed_ms:.0f}ms: {str(e)}",
                exc_info=True,
                extra={
                    "track_id": track_id,
                    "race_num": race_num,
                    "driver_number": driver_number,
                    "error_type": type(e).__name__,
                    "query_time_ms": elapsed_ms
                }
            )
            raise

        finally:
            if conn:
                try:
                    conn.close()
                    logger.debug("Connection closed successfully")
                except Exception as e:
                    logger.warning(f"Error closing connection: {str(e)}")

    def check_connection(self) -> Dict[str, str]:
        """
        Test Snowflake connection and return status.

        Returns:
            Dict with connection status and info

        Example:
            >>> service = SnowflakeService()
            >>> status = service.check_connection()
            >>> print(status)
            {'status': 'connected', 'database': 'HACKTHETRACK', ...}
        """
        logger.info("Running Snowflake health check")
        start_time = time.time()

        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT CURRENT_VERSION(), CURRENT_DATABASE()")
            version, database = cursor.fetchone()

            elapsed_ms = (time.time() - start_time) * 1000

            status = {
                "status": "connected",
                "version": version,
                "database": database,
                "warehouse": self.warehouse,
                "schema": self.schema,
                "connection_time_ms": round(elapsed_ms, 0)
            }

            logger.info(
                f"Health check passed in {elapsed_ms:.0f}ms",
                extra=status
            )

            return status

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000

            # Sanitize error message - don't expose credentials
            error_message = str(e)
            if self.password and self.password in error_message:
                error_message = error_message.replace(self.password, "***")

            status = {
                "status": "error",
                "error": error_message,
                "error_type": type(e).__name__,
                "connection_time_ms": round(elapsed_ms, 0)
            }

            logger.error(
                f"Health check failed after {elapsed_ms:.0f}ms: {error_message}",
                extra=status
            )

            return status

        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    logger.warning(f"Error closing connection: {str(e)}")


# Global instance
snowflake_service = SnowflakeService()
