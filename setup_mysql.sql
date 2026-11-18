-- ==============================================================================
-- BloodConnect MySQL Database Setup Script
-- ==============================================================================
-- Open this file in MySQL Workbench:
-- 1. File -> Open SQL Script -> Select this file (setup_mysql.sql)
-- 2. Click the Lightning Bolt (Execute) icon or press Ctrl + Shift + Enter
-- ==============================================================================

-- Create the database with UTF-8 support
CREATE DATABASE IF NOT EXISTS bloodconnect_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Select the database
USE bloodconnect_db;

-- Verify database creation
SELECT 'Database bloodconnect_db is ready for BloodConnect migrations!' AS Status;

-- ==============================================================================
-- Next steps in Windows PowerShell:
-- 1. In your .env file, ensure:
--      DB_ENGINE=mysql
--      DB_NAME=bloodconnect_db
--      DB_USER=root
--      DB_PASSWORD=your_mysql_password
--
-- 2. Run migrations:
--      python manage.py migrate
--
-- 3. Seed demo data:
--      python manage.py seed_data
-- ==============================================================================
