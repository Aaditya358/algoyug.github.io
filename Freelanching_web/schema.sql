-- schema.sql
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS portfolio_items;

CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  skills TEXT
);

CREATE TABLE portfolio_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL,
  filename TEXT NOT NULL,
  FOREIGN KEY (user_id) REFERENCES users (id)
);