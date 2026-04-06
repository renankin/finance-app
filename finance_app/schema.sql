CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY,
    date date NOT NULL,
    symbol TEXT NOT NULL,
    shares REAL NOT NULL,
    price REAL NOT NULL,
    currency TEXT NOT NULL
);