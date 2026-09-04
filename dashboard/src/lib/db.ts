import { Pool, types } from 'pg';

types.setTypeParser(1082, (val) => val);

const pool = new Pool({
  host: process.env.WAREHOUSE_HOST || '127.0.0.1',
  port: parseInt(process.env.WAREHOUSE_PORT || '5433'),
  database: process.env.WAREHOUSE_DB || 'saas_warehouse',
  user: process.env.WAREHOUSE_USER || 'warehouse_user',
  password: process.env.WAREHOUSE_PASSWORD || 'warehouse_password',
});

export default pool;