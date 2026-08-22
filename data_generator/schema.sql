-- DDL for PostgreSQL OLTP (saas_oltp)
CREATE TABLE IF NOT EXISTS plans (
    plan_id VARCHAR(50) PRIMARY KEY,
    plan_name VARCHAR(50) NOT NULL,
    monthly_price NUMERIC(10, 2) NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
    user_id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    company_name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id VARCHAR(50) PRIMARY KEY,
    user_id VARCHAR(50) REFERENCES users(user_id),
    plan_id VARCHAR(50) REFERENCES plans(plan_id),
    status VARCHAR(20) NOT NULL, -- 'active', 'canceled', 'past_due'
    mrr NUMERIC(10, 2) NOT NULL,
    start_date TIMESTAMP WITH TIME ZONE NOT NULL,
    end_date TIMESTAMP WITH TIME ZONE,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Seed static plans
INSERT INTO plans (plan_id, plan_name, monthly_price) VALUES
('plan_starter', 'Starter', 29.00),
('plan_pro', 'Pro', 99.00),
('plan_enterprise', 'Enterprise', 299.00)
ON CONFLICT (plan_id) DO NOTHING;