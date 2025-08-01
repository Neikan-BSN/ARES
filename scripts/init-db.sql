-- ARES Database Initialization Script
-- Creates the database and sets up initial configuration

-- Create database if not exists (for PostgreSQL)
-- This is primarily for development - production databases should be created separately

-- Ensure UTF8 encoding
SET client_encoding = 'UTF8';

-- Create extensions for production use
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create indexes for performance
-- Note: These will be managed by Alembic migrations, but included here for reference

-- Performance optimization settings
SET shared_preload_libraries = 'pg_stat_statements';
SET pg_stat_statements.track = all;

-- Basic logging configuration
SET log_destination = 'stderr';
SET log_statement = 'all';
SET log_min_duration_statement = 1000;  -- Log queries taking more than 1 second