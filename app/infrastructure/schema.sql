-- Esquema relacional de Dulce Nube (SQLite)
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL,
 password TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('Administrador','Vendedor'))
);
CREATE TABLE IF NOT EXISTS products (
 id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT NOT NULL,
 price REAL NOT NULL CHECK(price >= 0), stock INTEGER NOT NULL CHECK(stock >= 0),
 image TEXT NOT NULL DEFAULT '', active INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS sales (
 id INTEGER PRIMARY KEY AUTOINCREMENT, total REAL NOT NULL CHECK(total >= 0), created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS sale_items (
 id INTEGER PRIMARY KEY AUTOINCREMENT, sale_id INTEGER NOT NULL REFERENCES sales(id),
 product_id INTEGER NOT NULL REFERENCES products(id), name TEXT NOT NULL,
 price REAL NOT NULL, qty INTEGER NOT NULL CHECK(qty > 0)
);
CREATE TABLE IF NOT EXISTS orders (
 id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE NOT NULL, customer TEXT NOT NULL,
 phone TEXT NOT NULL, delivery_at TEXT NOT NULL, decoration TEXT NOT NULL,
 dedication TEXT DEFAULT '', notes TEXT DEFAULT '', status TEXT NOT NULL, created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_orders_status_delivery ON orders(status,delivery_at);
CREATE INDEX IF NOT EXISTS idx_sales_created_at ON sales(created_at);
