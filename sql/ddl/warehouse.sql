CREATE TABLE IF NOT EXISTS dim_date (date_key INTEGER PRIMARY KEY, full_date DATE UNIQUE NOT NULL, year INTEGER NOT NULL, month INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS dim_customer (customer_key BIGSERIAL PRIMARY KEY, customer_id INTEGER UNIQUE NOT NULL, name TEXT NOT NULL, state TEXT);
CREATE TABLE IF NOT EXISTS dim_product (product_key BIGSERIAL PRIMARY KEY, product_id INTEGER UNIQUE NOT NULL, product_name TEXT NOT NULL, category TEXT, supplier_id INTEGER, cost NUMERIC(12,2));
CREATE TABLE IF NOT EXISTS dim_store (store_key BIGSERIAL PRIMARY KEY, store_id INTEGER UNIQUE NOT NULL, store_name TEXT NOT NULL, state TEXT, region TEXT);
CREATE TABLE IF NOT EXISTS dim_supplier (supplier_key BIGSERIAL PRIMARY KEY, supplier_id INTEGER UNIQUE NOT NULL, supplier_name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS fact_sales (sales_id BIGSERIAL PRIMARY KEY, date_key INTEGER REFERENCES dim_date(date_key), customer_key BIGINT REFERENCES dim_customer(customer_key), product_key BIGINT REFERENCES dim_product(product_key), store_key BIGINT REFERENCES dim_store(store_key), quantity INTEGER NOT NULL CHECK (quantity > 0), revenue NUMERIC(12,2) NOT NULL, discount NUMERIC(12,2) DEFAULT 0, profit NUMERIC(12,2) NOT NULL);
CREATE INDEX IF NOT EXISTS idx_fact_sales_store_date ON fact_sales(store_key, date_key);
