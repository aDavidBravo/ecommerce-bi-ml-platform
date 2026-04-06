-- ==========================================
-- DATA WAREHOUSE SCHEMA - SNOWFLAKE/REDSHIFT
-- E-Commerce Analytics Database
-- ==========================================

-- Create schemas
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS dwh;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS ml_features;

-- ==========================================
-- DIMENSION TABLES
-- ==========================================

-- Dimension: Customers
CREATE TABLE IF NOT EXISTS dwh.dim_customer (
    customer_sk BIGINT PRIMARY KEY IDENTITY(1,1),
    customer_id VARCHAR(50) NOT NULL,
    customer_name VARCHAR(200),
    email VARCHAR(200),
    phone VARCHAR(50),
    country VARCHAR(100),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    signup_date DATE,
    customer_segment VARCHAR(50),
    lifetime_value DECIMAL(15,2),
    is_active BOOLEAN,
    effective_date DATE NOT NULL,
    expiration_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_customer_id ON dwh.dim_customer(customer_id);
CREATE INDEX idx_dim_customer_segment ON dwh.dim_customer(customer_segment);

-- Dimension: Products
CREATE TABLE IF NOT EXISTS dwh.dim_product (
    product_sk BIGINT PRIMARY KEY IDENTITY(1,1),
    product_id VARCHAR(50) NOT NULL,
    product_name VARCHAR(300),
    description TEXT,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    brand VARCHAR(100),
    supplier_id VARCHAR(50),
    unit_cost DECIMAL(10,2),
    unit_price DECIMAL(10,2),
    is_active BOOLEAN,
    effective_date DATE NOT NULL,
    expiration_date DATE,
    is_current BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_dim_product_id ON dwh.dim_product(product_id);
CREATE INDEX idx_dim_product_category ON dwh.dim_product(category);
CREATE INDEX idx_dim_product_brand ON dwh.dim_product(brand);

-- Dimension: Date
CREATE TABLE IF NOT EXISTS dwh.dim_date (
    date_sk BIGINT PRIMARY KEY,
    full_date DATE NOT NULL,
    day_of_week INT,
    day_of_week_name VARCHAR(10),
    day_of_month INT,
    day_of_year INT,
    week_of_year INT,
    month INT,
    month_name VARCHAR(10),
    quarter INT,
    year INT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    fiscal_year INT,
    fiscal_quarter INT,
    fiscal_month INT
);

CREATE UNIQUE INDEX idx_dim_date_full_date ON dwh.dim_date(full_date);

-- Dimension: Geography
CREATE TABLE IF NOT EXISTS dwh.dim_geography (
    geography_sk BIGINT PRIMARY KEY IDENTITY(1,1),
    country VARCHAR(100),
    country_code VARCHAR(3),
    state VARCHAR(100),
    state_code VARCHAR(10),
    city VARCHAR(100),
    postal_code VARCHAR(20),
    region VARCHAR(50),
    continent VARCHAR(50),
    latitude DECIMAL(10,6),
    longitude DECIMAL(10,6)
);

CREATE INDEX idx_dim_geo_country ON dwh.dim_geography(country);
CREATE INDEX idx_dim_geo_city ON dwh.dim_geography(city);

-- ==========================================
-- FACT TABLES
-- ==========================================

-- Fact: Sales
CREATE TABLE IF NOT EXISTS dwh.fact_sales (
    sales_sk BIGINT PRIMARY KEY IDENTITY(1,1),
    order_id VARCHAR(50) NOT NULL,
    order_item_id VARCHAR(50),
    date_sk BIGINT NOT NULL,
    customer_sk BIGINT NOT NULL,
    product_sk BIGINT NOT NULL,
    geography_sk BIGINT,
    
    -- Measures
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0,
    tax_amount DECIMAL(10,2) DEFAULT 0,
    shipping_cost DECIMAL(10,2) DEFAULT 0,
    total_amount DECIMAL(15,2) NOT NULL,
    cost_amount DECIMAL(15,2),
    profit_amount DECIMAL(15,2),
    
    -- Attributes
    order_status VARCHAR(50),
    payment_method VARCHAR(50),
    shipping_method VARCHAR(50),
    channel VARCHAR(50),
    
    -- Metadata
    order_datetime TIMESTAMP,
    shipped_datetime TIMESTAMP,
    delivered_datetime TIMESTAMP,
    load_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (date_sk) REFERENCES dwh.dim_date(date_sk),
    FOREIGN KEY (customer_sk) REFERENCES dwh.dim_customer(customer_sk),
    FOREIGN KEY (product_sk) REFERENCES dwh.dim_product(product_sk),
    FOREIGN KEY (geography_sk) REFERENCES dwh.dim_geography(geography_sk)
);

CREATE INDEX idx_fact_sales_date ON dwh.fact_sales(date_sk);
CREATE INDEX idx_fact_sales_customer ON dwh.fact_sales(customer_sk);
CREATE INDEX idx_fact_sales_product ON dwh.fact_sales(product_sk);
CREATE INDEX idx_fact_sales_order ON dwh.fact_sales(order_id);

-- Fact: Web Analytics
CREATE TABLE IF NOT EXISTS dwh.fact_web_analytics (
    analytics_sk BIGINT PRIMARY KEY IDENTITY(1,1),
    date_sk BIGINT NOT NULL,
    geography_sk BIGINT,
    
    -- Dimensions
    session_id VARCHAR(100),
    user_id VARCHAR(100),
    device_category VARCHAR(50),
    browser VARCHAR(50),
    operating_system VARCHAR(50),
    traffic_source VARCHAR(100),
    campaign_name VARCHAR(200),
    
    -- Measures
    sessions INT DEFAULT 1,
    page_views INT DEFAULT 0,
    unique_users INT DEFAULT 0,
    new_users INT DEFAULT 0,
    bounce_rate DECIMAL(5,2),
    avg_session_duration INT,
    conversions INT DEFAULT 0,
    revenue DECIMAL(15,2) DEFAULT 0,
    
    -- Timestamps
    session_start TIMESTAMP,
    session_end TIMESTAMP,
    load_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (date_sk) REFERENCES dwh.dim_date(date_sk),
    FOREIGN KEY (geography_sk) REFERENCES dwh.dim_geography(geography_sk)
);

CREATE INDEX idx_fact_analytics_date ON dwh.fact_web_analytics(date_sk);
CREATE INDEX idx_fact_analytics_session ON dwh.fact_web_analytics(session_id);

-- Fact: Customer Interactions
CREATE TABLE IF NOT EXISTS dwh.fact_customer_interactions (
    interaction_sk BIGINT PRIMARY KEY IDENTITY(1,1),
    date_sk BIGINT NOT NULL,
    customer_sk BIGINT NOT NULL,
    
    -- Attributes
    interaction_type VARCHAR(50),  -- email_open, click, support_ticket, chat, etc.
    channel VARCHAR(50),
    campaign_id VARCHAR(100),
    
    -- Measures
    interaction_count INT DEFAULT 1,
    engagement_score DECIMAL(5,2),
    response_time_seconds INT,
    satisfaction_score INT,
    
    -- Timestamps
    interaction_datetime TIMESTAMP,
    load_date DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (date_sk) REFERENCES dwh.dim_date(date_sk),
    FOREIGN KEY (customer_sk) REFERENCES dwh.dim_customer(customer_sk)
);

CREATE INDEX idx_fact_interactions_date ON dwh.fact_customer_interactions(date_sk);
CREATE INDEX idx_fact_interactions_customer ON dwh.fact_customer_interactions(customer_sk);

-- ==========================================
-- ANALYTICS TABLES
-- ==========================================

-- Customer 360 View
CREATE OR REPLACE VIEW analytics.customer_360 AS
SELECT 
    c.customer_id,
    c.customer_name,
    c.email,
    c.country,
    c.customer_segment,
    c.signup_date,
    DATEDIFF(day, c.signup_date, CURRENT_DATE) as tenure_days,
    
    -- Purchase metrics
    COUNT(DISTINCT f.order_id) as total_orders,
    SUM(f.total_amount) as total_revenue,
    AVG(f.total_amount) as avg_order_value,
    MAX(d.full_date) as last_purchase_date,
    DATEDIFF(day, MAX(d.full_date), CURRENT_DATE) as days_since_last_purchase,
    
    -- Engagement metrics
    SUM(CASE WHEN d.full_date >= CURRENT_DATE - 30 THEN f.total_amount ELSE 0 END) as revenue_30d,
    SUM(CASE WHEN d.full_date >= CURRENT_DATE - 90 THEN f.total_amount ELSE 0 END) as revenue_90d,
    SUM(CASE WHEN d.full_date >= CURRENT_DATE - 365 THEN f.total_amount ELSE 0 END) as revenue_12m,
    
    -- Product preferences
    MODE() WITHIN GROUP (ORDER BY p.category) as favorite_category,
    MODE() WITHIN GROUP (ORDER BY p.brand) as favorite_brand,
    
    c.lifetime_value,
    c.is_active

FROM dwh.dim_customer c
LEFT JOIN dwh.fact_sales f ON c.customer_sk = f.customer_sk
LEFT JOIN dwh.dim_date d ON f.date_sk = d.date_sk
LEFT JOIN dwh.dim_product p ON f.product_sk = p.product_sk
WHERE c.is_current = TRUE
GROUP BY 
    c.customer_id, c.customer_name, c.email, c.country,
    c.customer_segment, c.signup_date, c.lifetime_value, c.is_active;

-- Product Performance Dashboard
CREATE OR REPLACE VIEW analytics.product_performance AS
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    p.subcategory,
    p.brand,
    
    -- Sales metrics
    COUNT(DISTINCT f.order_id) as total_orders,
    SUM(f.quantity) as units_sold,
    SUM(f.total_amount) as total_revenue,
    SUM(f.profit_amount) as total_profit,
    AVG(f.unit_price) as avg_selling_price,
    
    -- Performance indicators
    SUM(f.total_amount) / NULLIF(SUM(SUM(f.total_amount)) OVER (PARTITION BY p.category), 0) * 100 as category_revenue_share,
    
    -- Trends
    SUM(CASE WHEN d.full_date >= CURRENT_DATE - 30 THEN f.total_amount ELSE 0 END) as revenue_30d,
    SUM(CASE WHEN d.full_date >= CURRENT_DATE - 90 THEN f.total_amount ELSE 0 END) as revenue_90d,
    
    p.is_active

FROM dwh.dim_product p
LEFT JOIN dwh.fact_sales f ON p.product_sk = f.product_sk
LEFT JOIN dwh.dim_date d ON f.date_sk = d.date_sk
WHERE p.is_current = TRUE
GROUP BY 
    p.product_id, p.product_name, p.category, p.subcategory, p.brand, p.is_active;

-- ==========================================
-- ML FEATURE TABLES
-- ==========================================

-- Customer Features for ML
CREATE TABLE IF NOT EXISTS ml_features.customer_features (
    customer_id VARCHAR(50) PRIMARY KEY,
    
    -- RFM Features
    recency INT,
    frequency INT,
    monetary DECIMAL(15,2),
    
    -- Behavioral Features
    avg_order_value DECIMAL(10,2),
    max_order_value DECIMAL(10,2),
    min_order_value DECIMAL(10,2),
    std_order_value DECIMAL(10,2),
    
    -- Temporal Features
    tenure_days INT,
    days_since_last_order INT,
    avg_days_between_orders DECIMAL(10,2),
    
    -- Product Preferences
    num_unique_products INT,
    num_unique_categories INT,
    favorite_category VARCHAR(100),
    category_diversity_score DECIMAL(5,2),
    
    -- Engagement Features
    total_page_views INT,
    total_sessions INT,
    avg_session_duration INT,
    email_open_rate DECIMAL(5,2),
    email_click_rate DECIMAL(5,2),
    
    -- Predictive Features
    churn_probability DECIMAL(5,4),
    predicted_ltv DECIMAL(15,2),
    propensity_to_buy DECIMAL(5,4),
    
    -- Segments
    rfm_segment VARCHAR(50),
    behavioral_cluster INT,
    value_tier VARCHAR(20),
    
    -- Metadata
    feature_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ml_customer_segment ON ml_features.customer_features(rfm_segment);
CREATE INDEX idx_ml_customer_cluster ON ml_features.customer_features(behavioral_cluster);

-- Product Features for Recommendations
CREATE TABLE IF NOT EXISTS ml_features.product_embeddings (
    product_id VARCHAR(50) PRIMARY KEY,
    
    -- Embedding vectors (adjust dimension as needed)
    embedding_vector SUPER,  -- JSON array for Redshift, or appropriate type for your DWH
    
    -- Similarity metrics
    popularity_score DECIMAL(5,4),
    conversion_rate DECIMAL(5,4),
    avg_rating DECIMAL(3,2),
    num_reviews INT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- HELPER FUNCTIONS / STORED PROCEDURES
-- ==========================================

-- Procedure to refresh customer features
CREATE OR REPLACE PROCEDURE ml_features.refresh_customer_features()
AS $$
BEGIN
    TRUNCATE TABLE ml_features.customer_features;
    
    INSERT INTO ml_features.customer_features
    SELECT 
        c.customer_id,
        
        -- RFM
        DATEDIFF(day, MAX(s.order_datetime), CURRENT_DATE) as recency,
        COUNT(DISTINCT s.order_id) as frequency,
        SUM(s.total_amount) as monetary,
        
        -- Behavioral
        AVG(s.total_amount) as avg_order_value,
        MAX(s.total_amount) as max_order_value,
        MIN(s.total_amount) as min_order_value,
        STDDEV(s.total_amount) as std_order_value,
        
        -- Temporal
        DATEDIFF(day, c.signup_date, CURRENT_DATE) as tenure_days,
        DATEDIFF(day, MAX(s.order_datetime), CURRENT_DATE) as days_since_last_order,
        DATEDIFF(day, MIN(s.order_datetime), MAX(s.order_datetime)) / 
            NULLIF(COUNT(DISTINCT s.order_id) - 1, 0) as avg_days_between_orders,
        
        -- Product preferences
        COUNT(DISTINCT p.product_id) as num_unique_products,
        COUNT(DISTINCT p.category) as num_unique_categories,
        MODE() WITHIN GROUP (ORDER BY p.category) as favorite_category,
        1.0 - (COUNT(*) / NULLIF(COUNT(DISTINCT p.category), 0)) as category_diversity_score,
        
        -- Engagement (placeholder - adjust based on your data)
        0 as total_page_views,
        0 as total_sessions,
        0 as avg_session_duration,
        0.0 as email_open_rate,
        0.0 as email_click_rate,
        
        -- Predictive (will be updated by ML models)
        NULL as churn_probability,
        NULL as predicted_ltv,
        NULL as propensity_to_buy,
        
        -- Segments
        NULL as rfm_segment,
        NULL as behavioral_cluster,
        CASE 
            WHEN SUM(s.total_amount) > 10000 THEN 'VIP'
            WHEN SUM(s.total_amount) > 5000 THEN 'High Value'
            WHEN SUM(s.total_amount) > 1000 THEN 'Medium Value'
            ELSE 'Low Value'
        END as value_tier,
        
        CURRENT_DATE as feature_date,
        CURRENT_TIMESTAMP as created_at,
        CURRENT_TIMESTAMP as updated_at
        
    FROM dwh.dim_customer c
    LEFT JOIN dwh.fact_sales s ON c.customer_sk = s.customer_sk
    LEFT JOIN dwh.dim_product p ON s.product_sk = p.product_sk
    WHERE c.is_current = TRUE
    GROUP BY c.customer_id, c.signup_date;
    
    COMMIT;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT ALL ON SCHEMA staging TO data_engineer_role;
GRANT ALL ON SCHEMA dwh TO data_engineer_role;
GRANT ALL ON SCHEMA analytics TO analytics_role;
GRANT ALL ON SCHEMA ml_features TO ml_engineer_role;

GRANT SELECT ON ALL TABLES IN SCHEMA dwh TO analytics_role;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO business_user_role;
