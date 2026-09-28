-- Motor Biomecânico Database Initialization Script
-- PostgreSQL 16
-- Runs automatically when container starts

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS clinical;
COMMENT ON SCHEMA clinical IS 'Clinical case management and patient data';

-- Set search path to include clinical schema
ALTER DATABASE motor_biomecanico SET search_path = public, clinical;

-- GRANT permissions to application user
GRANT CONNECT ON DATABASE motor_biomecanico TO motor_user;
GRANT USAGE ON SCHEMA public TO motor_user;
GRANT USAGE ON SCHEMA clinical TO motor_user;
GRANT CREATE ON SCHEMA clinical TO motor_user;

-- Tables will be created by SQLAlchemy ORM models
-- This script just sets up the database structure and permissions
COMMENT ON DATABASE motor_biomecanico IS 'Motor Biomecânico - Orthopedic Insole Design System';
