CREATE TABLE accounts (
    account_id INTEGER PRIMARY KEY,
    account_name TEXT NOT NULL UNIQUE,
    currency TEXT NOT NULL
);
CREATE TABLE assets (
    asset_id INTEGER PRIMARY KEY,
    asset_name TEXT NOT NULL UNIQUE,
    asset_type TEXT NOT NULL,
    account_id INT NOT NULL,
    still_open INT NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);
CREATE TABLE dividends (
    date DATE NOT NULL,
    asset_id INT NOT NULL,
    dividend_value REAL NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id),
    UNIQUE (date, asset_id)
);
CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY,
    asset_id INT NOT NULL,
    date date NOT NULL,
    shares REAL NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);
CREATE TABLE prices (
    date DATE NOT NULL,
    asset_id INT NOT NULL,
    unit_price FLOAT NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id),
    UNIQUE (date, asset_id)
);
CREATE TABLE stock_splits (
    date DATE NOT NULL,
    asset_id INT NOT NULL,
    split_ratio FLOAT NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id),
    UNIQUE (date, asset_id)
);