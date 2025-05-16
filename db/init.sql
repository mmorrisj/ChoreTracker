CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    password TEXT NOT NULL,
    UNIQUE (name, role)
);

CREATE TABLE chores (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    assigned TEXT NOT NULL,
    time REAL NOT NULL,
    type TEXT NOT NULL,
    UNIQUE (name, assigned, time, type)
);

CREATE TABLE completed_chores (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    chore_id INTEGER REFERENCES chores(id),
    time REAL NOT NULL,
    amount_earned REAL NOT NULL,
    completion_date DATE NOT NULL
);

CREATE TABLE expenses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    expense TEXT NOT NULL,
    amount REAL NOT NULL,
    date DATE NOT NULL,
    UNIQUE (user_id, expense, date)
);

CREATE TABLE completed_expenses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    expense_id INTEGER REFERENCES expenses(id),
    amount_deducted REAL NOT NULL,
    date DATE NOT NULL
);

CREATE TABLE open_chores (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    time REAL NOT NULL,
    type TEXT NOT NULL
);

CREATE TABLE behaviors (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    behavior TEXT NOT NULL,
    amount REAL NOT NULL,
    type TEXT NOT NULL,
    date DATE NOT NULL
);

CREATE TABLE completed_behaviors (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    behavior_id INTEGER REFERENCES behaviors(id),
    amount REAL NOT NULL,
    date DATE NOT NULL
);