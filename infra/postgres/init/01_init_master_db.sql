-- PostgreSQL initialization script for Rainer Platform Master DB
-- Runs automatically when postgres container starts for the first time

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create master database if not exists (already created via POSTGRES_DB env var)
-- This script runs in the rainer_master database

-- Grant superuser privileges for tenant DB provisioning (dev only)
-- In production, use a dedicated provisioner role with limited permissions
ALTER USER rainer CREATEDB;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Rainer Platform Master DB initialized at %', NOW();
END $$;
