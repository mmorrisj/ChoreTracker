CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('child', 'parent')),
    password TEXT NOT NULL
);

CREATE TABLE chores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    preset_amount REAL NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('preset', 'custom')),
    time_of_day TEXT NOT NULL CHECK (time_of_day IN ('Morning', 'Afternoon', 'Evening', 'Any'))
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

INSERT INTO chores (name, preset_amount, type, time_of_day) VALUES ('Act of Kindness', 1, 'preset', 'Any');
INSERT INTO chores (name, preset_amount, type, time_of_day) VALUES ('5 Minute Helpfulness', 5, 'preset', 'Any');
INSERT INTO chores (name, preset_amount, type, time_of_day) VALUES ('10 Minute Helpfulness', 10, 'preset', 'Any');
