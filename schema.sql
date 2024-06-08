-- schema.sql
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    password TEXT NOT NULL
);

DROP TABLE IF EXISTS chores;
CREATE TABLE chores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    preset_amount REAL NOT NULL,
    type TEXT NOT NULL,
    time_of_day TEXT NOT NULL
);

DROP TABLE IF EXISTS completed_chores;
CREATE TABLE completed_chores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    chore_id INTEGER,
    amount_earned REAL NOT NULL,
    completion_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (chore_id) REFERENCES chores(id)
);

DROP TABLE IF EXISTS expenses;
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    preset_amount REAL NOT NULL,
    type TEXT NOT NULL
);

-- Completed expenses table
DROP TABLE IF EXISTS completed_expenses;
CREATE TABLE completed_expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    expense_id INTEGER,
    amount_deducted REAL NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (expense_id) REFERENCES expenses(id)
);


INSERT INTO chores (name, preset_amount, type, time_of_day) VALUES ('Act of Kindness', 1, 'preset', 'Any');
INSERT INTO chores (name, preset_amount, type, time_of_day) VALUES ('5 Minute Helpfulness', 5, 'preset', 'Any');
INSERT INTO chores (name, preset_amount, type, time_of_day) VALUES ('10 Minute Helpfulness', 10, 'preset', 'Any');

