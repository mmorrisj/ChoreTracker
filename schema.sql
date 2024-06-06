CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('child', 'parent'))
);

CREATE TABLE chores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    preset_amount REAL NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('preset', 'custom'))
);

CREATE TABLE completed_chores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    chore_id INTEGER NOT NULL,
    time_spent REAL,
    amount_earned REAL,
    completion_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id),
    FOREIGN KEY (chore_id) REFERENCES chores (id)
);
