PRAGMA foreign_keys = OFF;  -- Disable foreign key constraints

DROP TABLE IF EXISTS completed_expenses;
DROP TABLE IF EXISTS completed_chores;
DROP TABLE IF EXISTS expenses;
DROP TABLE IF EXISTS behaviors;
DROP TABLE IF EXISTS open_chores;
DROP TABLE IF EXISTS to_do;
DROP TABLE IF EXISTS chores;
DROP TABLE IF EXISTS users;

PRAGMA foreign_keys = ON;  -- Re-enable foreign key constraints