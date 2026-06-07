-- ═══════════════════════════════════════════════════════════
-- HomeServices – MySQL Database Setup
-- Run this FIRST before starting Django
-- ═══════════════════════════════════════════════════════════

-- Step 1: Create the database
CREATE DATABASE IF NOT EXISTS homeservices_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE homeservices_db;

-- Step 2: Create a dedicated user (optional but recommended)
-- CREATE USER 'homeservices_user'@'localhost' IDENTIFIED BY 'StrongPassword123!';
-- GRANT ALL PRIVILEGES ON homeservices_db.* TO 'homeservices_user'@'localhost';
-- FLUSH PRIVILEGES;

-- Step 3: Verify
SHOW DATABASES LIKE 'homeservices_db';
SELECT 'Database ready! Now run: python manage.py migrate' AS message;

-- ═══════════════════════════════════════════════════════════
-- NOTE: All tables are created automatically by Django migrations
-- You do NOT need to create tables manually.
-- Just run:
--   python manage.py makemigrations
--   python manage.py migrate
-- ═══════════════════════════════════════════════════════════
