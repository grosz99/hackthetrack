"""
Snowflake connection service for telemetry data storage.

This service provides methods to query telemetry data from Snowflake
instead of local CSV files, enabling cloud-based data storage.
"""

import os
import snowflake.connector
from typing import List, Dict, Optional
import pandas as pd
from functools import lru_cache
from dotenv import load_dotenv
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

load_dotenv()


class SnowflakeService:
    """Service for connecting to and querying Snowflake data warehouse."""

    def __init__(self):
        """Initialize Snowflake connection with environment variables."""
        self.account = os.getenv("SNOWFLAKE_ACCOUNT")
        self.user = os.getenv("SNOWFLAKE_USER")
        self.password = os.getenv("SNOWFLAKE_PASSWORD")
        self.private_key_path = os.getenv("SNOWFLAKE_PRIVATE_KEY_PATH")
        self.warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH")
        self.database = os.getenv("SNOWFLAKE_DATABASE", "HACKTHETRACK")
        self.schema = os.getenv("SNOWFLAKE_SCHEMA", "TELEMETRY")
        self.role = os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN")

    def get_connection(self):
        """
        Create and return a Snowflake connection with key-pair auth or password.

        Returns:
            snowflake.connector.connection: Active Snowflake connection

        Raises:
            ValueError: If required credentials are missing
        """
        if not all([self.account, self.user]):
            raise ValueError(
                "Missing Snowflake credentials. Set SNOWFLAKE_ACCOUNT "
                "and SNOWFLAKE_USER environment variables."
            )

        # Use key-pair authentication if private key is provided
        if self.private_key_path and os.path.exists(self.private_key_path):
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

            return snowflake.connector.connect(
                account=self.account,
                user=self.user,
                private_key=pkb,
                warehouse=self.warehouse,
                database=self.database,
                schema=self.schema,
                role=self.role
            )

        # Fall back to password authentication
        if not self.password:
            raise ValueError(
                "Missing authentication. Set either SNOWFLAKE_PRIVATE_KEY_PATH "
                "or SNOWFLAKE_PASSWORD environment variable."
            )

        return snowflake.connector.connect(
            account=self.account,
            user=self.user,
            password=self.password,
            warehouse=self.warehouse,
            database=self.database,
            schema=self.schema,
            role=self.role
        )

    @lru_cache(maxsize=100)
    def get_drivers_with_telemetry(self) -> List[int]:
        """
        Get list of driver numbers that have telemetry data.

        Returns:
            List[int]: Sorted list of driver numbers with telemetry data

        Example:
            >>> service = SnowflakeService()
            >>> drivers = service.get_drivers_with_telemetry()
            >>> print(drivers)
            [0, 2, 3, 5, 7, ...]
        """
        conn = self.get_connection()
        try:
            query = """
                SELECT DISTINCT vehicle_number
                FROM telemetry_data
                WHERE vehicle_number IS NOT NULL
                ORDER BY vehicle_number
            """
            cursor = conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            return [int(row[0]) for row in results]
        finally:
            conn.close()

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
        conn = self.get_connection()
        try:
            query = """
                SELECT * FROM telemetry_data
                WHERE track_id = %s AND race_num = %s
            """
            params = [track_id, race_num]

            if driver_number is not None:
                query += " AND vehicle_number = %s"
                params.append(driver_number)

            query += " ORDER BY vehicle_number, lap, sample_time"

            return pd.read_sql(query, conn, params=params)
        finally:
            conn.close()

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
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT CURRENT_VERSION(), CURRENT_DATABASE()")
            version, database = cursor.fetchone()
            conn.close()

            return {
                "status": "connected",
                "version": version,
                "database": database,
                "warehouse": self.warehouse,
                "schema": self.schema
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }


# Global instance
snowflake_service = SnowflakeService()
