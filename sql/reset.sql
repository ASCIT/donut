/*
 * This script resets the test database to a consistent state
 * and should be run at the beginning of each integration test.
 */

DROP DATABASE IF EXISTS donut_test;
CREATE DATABASE donut_test;
USE donut_test;

-- Create the database schema.
SET FOREIGN_KEY_CHECKS = 0; -- allow all tables to be dropped

SOURCE sql/calendar.sql
SOURCE sql/donut.sql
SOURCE sql/directory.sql
SOURCE sql/editor.sql
SOURCE sql/marketplace.sql
SOURCE sql/feedback.sql
SOURCE sql/rooms.sql
SOURCE sql/permissions.sql
SOURCE sql/voting.sql
SOURCE sql/courses.sql

SET FOREIGN_KEY_CHECKS = 1;

-- Populate with test data.
SOURCE sql/test_data.sql
