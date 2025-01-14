
CREATE TABLE IF NOT EXISTS documents (
    document_id SERIAL PRIMARY KEY,
    filename VARCHAR(255),
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS processed_data (
    data_id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES documents(document_id),
    data JSONB
);
