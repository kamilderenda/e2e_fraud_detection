CREATE TABLE IF NOT EXISTS prod_table (
    id SERIAL PRIMARY KEY,
    "V1" FLOAT,
    "V2" FLOAT,
    "V3" FLOAT,
    "V4" FLOAT,
    "V5" FLOAT,
    "V7" FLOAT,
    "V9" FLOAT,
    "V10" FLOAT,
    "V11" FLOAT,
    "V12" FLOAT,
    "V14" FLOAT,
    "V16" FLOAT,
    "V17" FLOAT,
    "V18" FLOAT,
    prediction INTEGER,
    true_value INTEGER,
    probability FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mlflow_experiments (
    id SERIAL PRIMARY KEY,
    model_name TEXT,
    model_uri TEXT,
    run_id TEXT,
    alias TEXT,
    version TEXT,
    recall FLOAT,
    precision FLOAT,
    f1_score FLOAT,
    accuracy FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);