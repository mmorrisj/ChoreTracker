-- schema.sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    password TEXT NOT NULL,
    UNIQUE (name,role)
);

CREATE TABLE IF NOT EXISTS chores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    assigned TEXT NOT NULL,
    time REAL NOT NULL,
    type TEXT NOT NULL,
    UNIQUE (name, assigned, time, type)
);

CREATE TABLE IF NOT EXISTS preset_behaviors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    behavior TEXT NOT NULL,
    amount REAL NOT NULL,
    type TEXT NOT NULL,
    UNIQUE (behavior, amount, type)
);

CREATE TABLE IF NOT EXISTS behaviors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    behavior TEXT NOT NULL,
    amount REAL NOT NULL,
    type TEXT NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS completed_chores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    chore_name TEXT NOT NULL,
    time REAL NOT NULL,
    amount_earned REAL NOT NULL,
    completion_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (chore_id) REFERENCES chores(id)
);

-- Completed expenses table
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    expense TEXT NOT NULL,
    amount REAL NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE (user_id, expense, date)
);