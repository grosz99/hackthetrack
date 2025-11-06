-- Snowflake Database Setup for HackTheTrack Telemetry Data
-- Run this script in Snowflake Web UI to create the database schema

-- Create database
CREATE DATABASE IF NOT EXISTS HACKTHETRACK;

-- Use the database
USE DATABASE HACKTHETRACK;

-- Create schema
CREATE SCHEMA IF NOT EXISTS TELEMETRY;

-- Use the schema
USE SCHEMA TELEMETRY;

-- Create telemetry data table
CREATE TABLE IF NOT EXISTS telemetry_data (
    -- Identifiers
    track_id VARCHAR(50) NOT NULL,
    race_num INTEGER NOT NULL,
    vehicle_number INTEGER NOT NULL,
    lap INTEGER NOT NULL,

    -- Time and position
    sample_time FLOAT,
    distance FLOAT,

    -- Speed and motion
    speed FLOAT,
    rpm FLOAT,
    gear INTEGER,

    -- Control inputs
    throttle FLOAT,
    brake FLOAT,
    steering FLOAT,

    -- Aerodynamics and forces
    lateral_g FLOAT,
    longitudinal_g FLOAT,

    -- GPS coordinates
    gps_lat FLOAT,
    gps_long FLOAT,
    gps_alt FLOAT,

    -- Additional telemetry (if available)
    fuel_level FLOAT,
    fuel_pressure FLOAT,
    oil_temp FLOAT,
    oil_pressure FLOAT,
    water_temp FLOAT,

    -- Metadata
    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),

    -- Constraints
    PRIMARY KEY (track_id, race_num, vehicle_number, lap, sample_time)
);

-- Note: Indexes will be created automatically based on clustering keys
-- Snowflake uses micro-partitions for efficient querying
