-- Accounts
CREATE TABLE IF NOT EXISTS  accounts (
    account_id INTEGER PRIMARY KEY,
    account_name TEXT NOT NULL UNIQUE,
    currency TEXT NOT NULL
);

-- Assets
CREATE TABLE IF NOT EXISTS assets (
    asset_id INTEGER PRIMARY KEY,
    asset_name TEXT NOT NULL UNIQUE,
    asset_type TEXT NOT NULL,
    account_id INTEGER NOT NULL,
    still_open INTEGER NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(account_id)
);

CREATE TABLE IF NOT EXISTS asset_type (
    asset_type_id INTEGER PRIMARY KEY,
    asset_type_name TEXT NOT NULL UNIQUE,
    asset_id INTEGER NOT NULL,
    market_source_id INTEGER NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
    FOREIGN KEY (market_source_id) REFERENCES market_source(market_source_id)
);

-- Transactions
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id INTEGER PRIMARY KEY,
    asset_id INTEGER NOT NULL,
    date date NOT NULL,
    shares REAL NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id)
);

-- Market data
CREATE TABLE IF NOT EXISTS market_sources (
    source_id INTEGER PRIMARY KEY,
    source_name TEXT NOT NULL,

    -- Capabilities
    supports_prices INTEGER DEFAULT 1,
    supports_dividends INTEGER DEFAULT 0,
    supports_stock_splits INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS dividends (
    date DATE NOT NULL,
    asset_id INTEGER NOT NULL,
    dividend_value REAL NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id),
    UNIQUE (date, asset_id)
);

CREATE TABLE IF NOT EXISTS prices (
    date DATE NOT NULL,
    asset_id INTEGER NOT NULL,
    unit_price FLOAT NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id),
    UNIQUE (date, asset_id)
);

CREATE TABLE IF NOT EXISTS stock_splits (
    date DATE NOT NULL,
    asset_id INTEGER NOT NULL,
    split_ratio FLOAT NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(asset_id),
    UNIQUE (date, asset_id)
);