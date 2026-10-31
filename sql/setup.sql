-- Snowflake environment setup for m5-inventory-sim
-- Run in a Snowflake worksheet (Snowsight)

-- 1. Run as SYSADMIN
USE ROLE SYSADMIN;

CREATE WAREHOUSE IF NOT EXISTS m5_wh
  WAREHOUSE_SIZE = 'XSMALL' AUTO_SUSPEND = 60 AUTO_RESUME = TRUE;
CREATE DATABASE IF NOT EXISTS m5;
CREATE SCHEMA IF NOT EXISTS m5.raw;

-- 2. Key-pair auth: requires ACCOUNTADMIN
--    Generate keys locally first (see README); never commit the private key
USE ROLE ACCOUNTADMIN;

ALTER USER "<your_username>" SET RSA_PUBLIC_KEY='<your_public_key>';
DESC USER "<your_username>";  -- confirm RSA_PUBLIC_KEY_FP is set

USE ROLE SYSADMIN;