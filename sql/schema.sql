-- schema.sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    password TEXT NOT NULL,
    UNIQUE (name)
);

CREATE TABLE IF NOT EXISTS chores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    assigned TEXT NOT NULL,
    time REAL NOT NULL,
    type TEXT NOT NULL,
);

CREATE TABLE IF NOT EXISTS behaviors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    amount REAL NOT NULL,
    type TEXT NOT NULL,
);

CREATE TABLE IF NOT EXISTS completed_chores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    chore_id INTEGER,
    time REAL NOT NULL,
    amount_earned REAL NOT NULL,
    completion_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (chore_id) REFERENCES chores(id)
);

DROP TABLE IF EXISTS expenses;
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    amount REAL NOT NULL,
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

INSERT INTO users (name, role, password) VALUES ('Virginia', 'child', 'virginia');
INSERT INTO users (name, role, password) VALUES ('Evelyn', 'child', 'evelyn');
INSERT INTO users (name, role, password) VALUES ('Lucy', 'child', 'lucy');
INSERT INTO users (name, role, password) VALUES ('Parent', 'parent', 'parent')

INSERT INTO behaviors (name, amount, type) VALUES ('Act of Kindness', .25, 'good');
INSERT INTO behaviors (name, amount, type) VALUES ('5 Minute Helpfulness', 1, 'good');
INSERT INTO behaviors (name, amount, type) VALUES ('10 Minute Helpfulness', 2, 'good');

INSERT INTO behaviors (name, amount, type) VALUES ('Good Behavior', .25, 'good');
INSERT INTO behaviors (name, amount, type) VALUES ('Very Good Behavior', 1, 'good');
INSERT INTO behaviors (name, amount, type) VALUES ('Bad Behavior', -.25, 'bad');
INSERT INTO behaviors (name, amount, type) VALUES ('Very Bad Behavior', -1, 'bad');

INSERT INTO chores (name,assigned,time,type) VALUES ('20 minute reading','Evelyn', 20, 'school');
INSERT INTO chores (name,assigned,time,type) VALUES ('20 minute reading','Virginia', 20, 'school');
INSERT INTO chores (name,assigned,time,type) VALUES ('10 minute reading','Lucy', 10, 'school');

