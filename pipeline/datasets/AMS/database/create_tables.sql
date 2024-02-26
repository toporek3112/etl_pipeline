CREATE TABLE IF NOT EXISTS registered_unemployed (
    id SERIAL PRIMARY KEY,
    month DATE,
    rgs_code TEXT,
    rgs_name TEXT,
    gender TEXT,
    age_group TEXT,
    nationality TEXT,
    employment_promise BOOLEAN,
    health_restrictions BOOLEAN,
    stock_at_date INT,
    entry_in_month INT,
    exit_in_month INT,
);
