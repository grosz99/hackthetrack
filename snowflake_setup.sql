-- ============================================================================
-- Snowflake Schema Setup for HackTheTrack Telemetry Data
-- ============================================================================
-- This script creates the database, schema, and table structure needed
-- to store telemetry CSV files in Snowflake for cloud-based access.
--
-- Usage:
-- 1. Run this script in Snowflake Web UI or SnowSQL
-- 2. Upload telemetry CSV files using the commands below
-- 3. Update backend environment variables with Snowflake credentials
-- ============================================================================

-- Step 1: Create Database and Schema
CREATE DATABASE IF NOT EXISTS HACKTHETRACK;
USE DATABASE HACKTHETRACK;

CREATE SCHEMA IF NOT EXISTS TELEMETRY;
USE SCHEMA TELEMETRY;

-- Step 2: Create Warehouse (if needed)
CREATE WAREHOUSE IF NOT EXISTS COMPUTE_WH
    WAREHOUSE_SIZE = 'XSMALL'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE;

-- Step 3: Create Telemetry Data Table
CREATE OR REPLACE TABLE telemetry_data (
    -- Identifiers
    track_id VARCHAR(50),
    race_num INTEGER,
    vehicle_number INTEGER,

    -- Lap and timing data
    lap INTEGER,
    sample_time FLOAT,
    elapsed_time FLOAT,

    -- Speed and position
    speed FLOAT,
    gps_latitude FLOAT,
    gps_longitude FLOAT,
    gps_altitude FLOAT,

    -- Driver inputs
    throttle FLOAT,
    brake FLOAT,
    clutch FLOAT,
    steering FLOAT,

    -- Vehicle state
    gear INTEGER,
    rpm FLOAT,
    engine_temp FLOAT,

    -- Calculated metrics
    lateral_accel FLOAT,
    longitudinal_accel FLOAT,

    -- Metadata
    data_source VARCHAR(100),
    uploaded_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Step 4: Create indexes for query performance
CREATE OR REPLACE INDEX idx_telemetry_track_race
    ON telemetry_data(track_id, race_num);

CREATE OR REPLACE INDEX idx_telemetry_vehicle
    ON telemetry_data(vehicle_number);

CREATE OR REPLACE INDEX idx_telemetry_lap
    ON telemetry_data(lap);

-- Step 5: Create Stage for CSV Upload
CREATE OR REPLACE STAGE telemetry_stage
    FILE_FORMAT = (
        TYPE = 'CSV'
        FIELD_DELIMITER = ','
        SKIP_HEADER = 1
        FIELD_OPTIONALLY_ENCLOSED_BY = '"'
        NULL_IF = ('NULL', 'null', '')
        EMPTY_FIELD_AS_NULL = TRUE
        ERROR_ON_COLUMN_COUNT_MISMATCH = FALSE
    );

-- ============================================================================
-- CSV Upload Commands
-- ============================================================================
-- Run these commands to upload your telemetry CSV files to Snowflake.
-- Replace the file paths with your actual CSV file locations.
--
-- Note: Run these commands one at a time for each CSV file.
-- The format is: PUT file://path/to/local/file @stage_name
-- ============================================================================

-- Example: Upload barber race 1 telemetry
-- PUT file:///Users/justingrosz/Documents/AI-Work/hackthetrack-master/data/telemetry/barber_r1_wide.csv @telemetry_stage;

-- After uploading files to stage, copy them to the table with metadata:
-- COPY INTO telemetry_data(track_id, race_num, vehicle_number, lap, sample_time,
--     elapsed_time, speed, gps_latitude, gps_longitude, gps_altitude,
--     throttle, brake, clutch, steering, gear, rpm, engine_temp,
--     lateral_accel, longitudinal_accel, data_source)
-- FROM (
--     SELECT
--         'barber' as track_id,
--         1 as race_num,
--         $1, $2, $3, $4, $5, $6, $7, $8, $9,
--         $10, $11, $12, $13, $14, $15, $16, $17, $18,
--         'barber_r1_wide.csv' as data_source
--     FROM @telemetry_stage/barber_r1_wide.csv
-- )
-- FILE_FORMAT = (
--     TYPE = 'CSV'
--     FIELD_DELIMITER = ','
--     SKIP_HEADER = 1
--     FIELD_OPTIONALLY_ENCLOSED_BY = '"'
--     NULL_IF = ('NULL', 'null', '')
--     EMPTY_FIELD_AS_NULL = TRUE
-- );

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Check uploaded data count
SELECT track_id, race_num, COUNT(*) as record_count
FROM telemetry_data
GROUP BY track_id, race_num
ORDER BY track_id, race_num;

-- Check distinct vehicles per track
SELECT track_id, race_num, COUNT(DISTINCT vehicle_number) as driver_count
FROM telemetry_data
GROUP BY track_id, race_num
ORDER BY track_id, race_num;

-- View sample data for verification
SELECT *
FROM telemetry_data
WHERE track_id = 'barber' AND race_num = 1
LIMIT 10;

-- ============================================================================
-- Grant Permissions (Optional - for production use)
-- ============================================================================

-- Create read-only role for the application
-- CREATE ROLE IF NOT EXISTS hackthetrack_reader;
-- GRANT USAGE ON DATABASE HACKTHETRACK TO ROLE hackthetrack_reader;
-- GRANT USAGE ON SCHEMA HACKTHETRACK.TELEMETRY TO ROLE hackthetrack_reader;
-- GRANT SELECT ON ALL TABLES IN SCHEMA HACKTHETRACK.TELEMETRY TO ROLE hackthetrack_reader;
-- GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE hackthetrack_reader;

-- ============================================================================
-- Cleanup Commands (Use with caution!)
-- ============================================================================

-- Drop table (deletes all data)
-- DROP TABLE IF EXISTS telemetry_data;

-- Drop schema
-- DROP SCHEMA IF EXISTS TELEMETRY;

-- Drop database
-- DROP DATABASE IF EXISTS HACKTHETRACK;
