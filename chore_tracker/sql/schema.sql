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

CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    amount REAL NOT NULL,
    type TEXT NOT NULL
);

-- Completed expenses table
CREATE TABLE IF NOT EXISTS completed_expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    expense_id INTEGER,
    amount_deducted REAL NOT NULL,
    date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (expense_id) REFERENCES expenses(id)
);


CREATE TABLE IF NOT EXISTS to_do (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    assigned TEXT NOT NULL,
    time REAL NOT NULL,
    type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS completed_to_do (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    to_do_id INTEGER,
    time REAL NOT NULL,
    amount_earned REAL NOT NULL,
    completion_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (to_do_id) REFERENCES to_do(id)
);

CREATE TABLE IF NOT EXISTS open_chores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,,
    time REAL NOT NULL,
    type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS completed_open_chores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    open_chore_id INTEGER,
    time REAL NOT NULL,
    amount_earned REAL NOT NULL,
    completion_date DATE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (open_chore_id) REFERENCES open_chores(id)
);

INSERT OR IGNORE INTO users (name, role, password) VALUES ('Virginia', 'child', 'virginia');
INSERT OR IGNORE INTO users (name, role, password) VALUES ('Evelyn', 'child', 'evelyn');
INSERT OR IGNORE INTO users (name, role, password) VALUES ('Lucy', 'child', 'lucy');
INSERT OR IGNORE INTO users (name, role, password) VALUES ('Parent', 'parent', 'parent')

INSERT OR IGNORE INTO behaviors (name, amount, type) VALUES ('Act of Kindness', .25, 'good');
INSERT OR IGNORE INTO behaviors (name, amount, type) VALUES ('5 Minute Helpfulness', 1, 'good');
INSERT OR IGNORE INTO behaviors (name, amount, type) VALUES ('10 Minute Helpfulness', 2, 'good');

INSERT OR IGNORE INTO behaviors (name, amount, type) VALUES ('Good Behavior', .25, 'good');
INSERT OR IGNORE INTO behaviors (name, amount, type) VALUES ('Very Good Behavior', 1, 'good');
INSERT OR IGNORE INTO behaviors (name, amount, type) VALUES ('Bad Behavior', -.25, 'bad');
INSERT OR IGNORE INTO behaviors (name, amount, type) VALUES ('Very Bad Behavior', -1, 'bad');

INSERT OR IGNORE INTO chores (name,assigned,time,type) VALUES ('20 minute reading','Evelyn', 20, 'school');
INSERT OR IGNORE INTO chores (name,assigned,time,type) VALUES ('20 minute reading','Virginia', 20, 'school');
INSERT OR IGNORE INTO chores (name,assigned,time,type) VALUES ('10 minute reading','Lucy', 10, 'school');

INSERT OR IGNORE INTO to_do (name,assigned,time,type) VALUES ('20 minute reading','Evelyn', 20, 'school');
INSERT OR IGNORE INTO to_do (name,assigned,time,type) VALUES ('20 minute reading','Virginia', 20, 'school');
INSERT OR IGNORE INTO to_do (name,assigned,time,type) VALUES ('10 minute reading','Lucy', 10, 'school');
INSERT OR IGNORE INTO to_do (name,assigned,time,type) VALUES ('Get Ready For Day','Virginia', 10, 'morning');
INSERT OR IGNORE INTO to_do (name,assigned,time,type) VALUES ('Get Ready For Day','Evelyn', 10, 'morning');
INSERT OR IGNORE INTO to_do (name,assigned,time,type) VALUES ('Get Ready For Day','Lucy', 10, 'morning');
INSERT OR IGNORE INTO to_do (name,assigned,time,type) VALUES ('Make it to Bus on Time','Virginia', 5, 'morning');
INSERT OR IGNORE INTO to_do (name,assigned,time,type) VALUES ('Make it to Bus on Time','Evelyn', 5, 'morning');
INSERT OR IGNORE INTO to_do (name,assigned,time,type) VALUES ('Make it to Bus on Time','Lucy', 5, 'morning');
INSERT OR IGNORE INTO to_do (name,assigned,time,type) VALUES ('Get Ready For Bed','Virginia', 5, 'evening');
INSERT OR IGNORE INTO to_do (name,assigned,time,type) VALUES ('Get Ready For Bed','Evelyn', 5, 'evening');
INSERT OR IGNORE INTO to_do (name,assigned,time,type) VALUES ('Get Ready For Bed','Lucy', 5, 'evening');

INSERT OR IGNORE INTO open_chores (name,time,type) VALUES ('Empty Dishwasher', 5, 'house');
INSERT OR IGNORE INTO open_chores (name,time,type) VALUES ('Load Dishwasher', 5, 'house');
INSERT OR IGNORE INTO open_chores (name,time,type) VALUES ('Fold Laundry', 10, 'house');
INSERT OR IGNORE INTO open_chores (name,time,type) VALUES ('Put Away Laundry', 10, 'house');
INSERT OR IGNORE INTO open_chores (name,time,type) VALUES ('Tidy Living Room', 5, 'house');
INSERT OR IGNORE INTO open_chores (name,time,type) VALUES ('Tidy Bedroom', 5, 'house');
INSERT OR IGNORE INTO open_chores (name,time,type) VALUES ('Clear Table', 3, 'house');
INSERT OR IGNORE INTO open_chores (name,time,type) VALUES ('Sweep Floor', 10, 'house');
INSERT OR IGNORE INTO open_chores (name,time,type) VALUES ('Vacuum Floor', 10, 'house');
INSERT OR IGNORE INTO open_chores (name,time,type) VALUES ('Tidy Boot Bench', 5, 'house');
INSERT OR IGNORE INTO open_chores (name,time,type) VALUES ('Tidy Basement', 10, 'house');



