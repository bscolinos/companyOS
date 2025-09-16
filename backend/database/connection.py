import singlestoredb as s2
from contextlib import contextmanager
import logging
from backend.config import settings
from typing import Generator
import asyncio
import threading

logger = logging.getLogger(__name__)

# Connection pool configuration
_connection_pool = None
_pool_lock = threading.Lock()

def get_connection_pool():
    """Get or create connection pool"""
    global _connection_pool
    
    if _connection_pool is None:
        with _pool_lock:
            if _connection_pool is None:
                try:
                    _connection_pool = s2.connect(
                        host=settings.singlestore_host,
                        port=settings.singlestore_port,
                        user=settings.singlestore_user,
                        password=settings.singlestore_password,
                        database=settings.singlestore_database,
                        autocommit=False,
                        local_infile=True,
                        charset='utf8mb4'
                    )
                    logger.info("SingleStore connection pool created successfully")
                except Exception as e:
                    logger.error(f"Failed to create SingleStore connection pool: {e}")
                    raise
    
    return _connection_pool

@contextmanager
def get_database() -> Generator[s2.Connection, None, None]:
    """Get a database connection from the pool"""
    conn = None
    try:
        conn = get_connection_pool()
        yield conn
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Database operation failed: {e}")
        raise
    finally:
        if conn:
            conn.close()

def get_db_connection():
    """Get a new database connection (for use in agents)"""
    try:
        return s2.connect(
            host=settings.singlestore_host,
            port=settings.singlestore_port,
            user=settings.singlestore_user,
            password=settings.singlestore_password,
            database=settings.singlestore_database,
            autocommit=False,
            local_infile=True,
            charset='utf8mb4'
        )
    except Exception as e:
        logger.error(f"Failed to create database connection: {e}")
        raise

def init_database():
    """Initialize database tables"""
    try:
        with get_database() as conn:
            cursor = conn.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.singlestore_database}")
            cursor.execute(f"USE {settings.singlestore_database}")
            
            # Create tables with SingleStore-optimized DDL
            create_tables_sql = """
            -- Users table
            -- Shard key: id (auto-increment provides good distribution)
            -- Sort key: email (frequent lookup), created_at (for admin queries)
            CREATE TABLE IF NOT EXISTS users (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                username VARCHAR(100) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                first_name VARCHAR(100),
                last_name VARCHAR(100),
                phone VARCHAR(20),
                is_active BOOLEAN DEFAULT TRUE,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                SHARD KEY (id),
                SORT KEY (email, created_at),
                INDEX(email) USING HASH,
                INDEX(username) USING HASH,
                INDEX(is_active) USING HASH
            );

            -- Categories table  
            -- Shard key: id (good distribution for small table)
            -- Sort key: name (frequent lookups), is_active (filtering)
            CREATE TABLE IF NOT EXISTS categories (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                parent_id BIGINT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                SHARD KEY (id),
                SORT KEY (name, is_active),
                INDEX(name) USING HASH,
                INDEX(is_active) USING HASH,
                INDEX(parent_id) USING HASH
            );

            -- Products table
            -- Shard key: id (high cardinality, good distribution) 
            -- Sort key: is_featured, demand_score, created_at (matches ORDER BY in queries)
            CREATE TABLE IF NOT EXISTS products (
                id BIGINT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                sku VARCHAR(100) UNIQUE NOT NULL,
                category_id BIGINT,
                base_price DECIMAL(10,2) NOT NULL,
                current_price DECIMAL(10,2) NOT NULL,
                cost_price DECIMAL(10,2),
                stock_quantity INT DEFAULT 0,
                min_stock_level INT DEFAULT 10,
                max_stock_level INT DEFAULT 1000,
                weight DECIMAL(8,3),
                dimensions JSON,
                images JSON,
                tags JSON,
                is_active BOOLEAN DEFAULT TRUE,
                is_featured BOOLEAN DEFAULT FALSE,
                demand_score DECIMAL(3,2) DEFAULT 0.0,
                price_elasticity DECIMAL(5,2) DEFAULT 1.0,
                seasonality_factor DECIMAL(5,2) DEFAULT 1.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                SHARD KEY (id),
                SORT KEY (is_featured, demand_score, created_at),
                INDEX(sku) USING HASH,
                INDEX(category_id) USING HASH,
                INDEX(is_active) USING HASH,
                INDEX(is_featured) USING HASH,
                INDEX(current_price) USING BTREE,
                INDEX(stock_quantity) USING BTREE,
                INDEX(name) USING HASH
            );

            -- Orders table
            -- Shard key: user_id (distributes by customer, enables efficient user queries)
            -- Sort key: created_at (time-based queries), status (filtering)
            CREATE TABLE IF NOT EXISTS orders (
                id BIGINT AUTO_INCREMENT,
                user_id BIGINT NOT NULL,
                order_number VARCHAR(50) UNIQUE NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                total_amount DECIMAL(10,2) NOT NULL,
                tax_amount DECIMAL(10,2) DEFAULT 0.0,
                shipping_amount DECIMAL(10,2) DEFAULT 0.0,
                discount_amount DECIMAL(10,2) DEFAULT 0.0,
                shipping_address JSON,
                billing_address JSON,
                shipping_method VARCHAR(100),
                tracking_number VARCHAR(100),
                payment_method VARCHAR(50),
                payment_status VARCHAR(50) DEFAULT 'pending',
                payment_id VARCHAR(100),
                risk_score DECIMAL(3,2) DEFAULT 0.0,
                priority_score DECIMAL(3,2) DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                shipped_at TIMESTAMP NULL,
                delivered_at TIMESTAMP NULL,
                PRIMARY KEY (user_id, id),
                SHARD KEY (user_id),
                SORT KEY (created_at, status),
                INDEX(id) USING HASH,
                INDEX(order_number) USING HASH,
                INDEX(status) USING HASH,
                INDEX(created_at) USING BTREE,
                INDEX(payment_status) USING HASH
            );

            -- Order Items table
            -- Shard key: order_id (groups items with orders, enables efficient order queries)
            -- Sort key: product_id (for product analysis)
            CREATE TABLE IF NOT EXISTS order_items (
                id BIGINT AUTO_INCREMENT,
                order_id BIGINT NOT NULL,
                product_id BIGINT NOT NULL,
                quantity INT NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                total_price DECIMAL(10,2) NOT NULL,
                PRIMARY KEY (order_id, id),
                SHARD KEY (order_id),
                SORT KEY (product_id),
                INDEX(product_id) USING HASH,
                INDEX(id) USING HASH
            );

            -- Cart Items table
            -- Shard key: user_id (distributes by user, enables efficient user cart queries)
            -- Sort key: created_at (for cart ordering)
            CREATE TABLE IF NOT EXISTS cart_items (
                id BIGINT AUTO_INCREMENT,
                user_id BIGINT NOT NULL,
                product_id BIGINT NOT NULL,
                quantity INT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, id),
                SHARD KEY (user_id),
                SORT KEY (created_at),
                INDEX(product_id) USING HASH,
                INDEX(id) USING HASH
            );

            -- Reviews table
            -- Shard key: product_id (distributes by product, enables efficient product review queries)
            -- Sort key: created_at (for chronological ordering), rating (for filtering)
            CREATE TABLE IF NOT EXISTS reviews (
                id BIGINT AUTO_INCREMENT,
                user_id BIGINT NOT NULL,
                product_id BIGINT NOT NULL,
                rating INT NOT NULL,
                title VARCHAR(255),
                comment TEXT,
                is_verified_purchase BOOLEAN DEFAULT FALSE,
                is_approved BOOLEAN DEFAULT TRUE,
                sentiment_score DECIMAL(3,2),
                helpful_votes INT DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (product_id, id),
                SHARD KEY (product_id),
                SORT KEY (created_at, rating),
                INDEX(user_id) USING HASH,
                INDEX(rating) USING HASH,
                INDEX(is_approved) USING HASH,
                INDEX(id) USING HASH
            );

            -- Inventory Logs table
            -- Shard key: product_id (distributes by product, enables efficient product history queries)
            -- Sort key: created_at (time-series data), change_type (for filtering)
            CREATE TABLE IF NOT EXISTS inventory_logs (
                id BIGINT AUTO_INCREMENT,
                product_id BIGINT NOT NULL,
                change_type VARCHAR(50) NOT NULL,
                quantity_change INT NOT NULL,
                previous_quantity INT NOT NULL,
                new_quantity INT NOT NULL,
                reason VARCHAR(255),
                agent_action BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (product_id, id),
                SHARD KEY (product_id),
                SORT KEY (created_at, change_type),
                INDEX(change_type) USING HASH,
                INDEX(agent_action) USING HASH,
                INDEX(created_at) USING BTREE,
                INDEX(id) USING HASH
            );

            -- Price History table
            -- Shard key: product_id (distributes by product, enables efficient product price history)
            -- Sort key: created_at (time-series data), agent_action (for filtering)
            CREATE TABLE IF NOT EXISTS price_history (
                id BIGINT AUTO_INCREMENT,
                product_id BIGINT NOT NULL,
                old_price DECIMAL(10,2) NOT NULL,
                new_price DECIMAL(10,2) NOT NULL,
                change_reason VARCHAR(255),
                agent_action BOOLEAN DEFAULT FALSE,
                market_data JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (product_id, id),
                SHARD KEY (product_id),
                SORT KEY (created_at, agent_action),
                INDEX(agent_action) USING HASH,
                INDEX(created_at) USING BTREE,
                INDEX(id) USING HASH
            );

            -- Agent Logs table
            -- Shard key: agent_name (distributes by agent, enables efficient per-agent queries)
            -- Sort key: created_at (time-series data), action_type (for filtering)
            CREATE TABLE IF NOT EXISTS agent_logs (
                id BIGINT AUTO_INCREMENT,
                agent_name VARCHAR(100) NOT NULL,
                action_type VARCHAR(100) NOT NULL,
                target_id BIGINT,
                target_type VARCHAR(50),
                action_data JSON,
                result VARCHAR(50) NOT NULL,
                error_message TEXT,
                execution_time DECIMAL(8,3),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (agent_name, id),
                SHARD KEY (agent_name),
                SORT KEY (created_at, action_type),
                INDEX(action_type) USING HASH,
                INDEX(result) USING HASH,
                INDEX(created_at) USING BTREE,
                INDEX(target_id) USING HASH,
                INDEX(id) USING HASH
            );

            -- Customer Interactions table
            -- Shard key: user_id (distributes by customer, enables efficient user interaction queries)
            -- Sort key: created_at (time-series data), status (for filtering)
            CREATE TABLE IF NOT EXISTS customer_interactions (
                id BIGINT AUTO_INCREMENT,
                user_id BIGINT,
                interaction_type VARCHAR(50) NOT NULL,
                subject VARCHAR(255),
                message TEXT,
                response TEXT,
                status VARCHAR(50) DEFAULT 'open',
                priority VARCHAR(20) DEFAULT 'medium',
                agent_handled BOOLEAN DEFAULT FALSE,
                satisfaction_score INT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resolved_at TIMESTAMP NULL,
                PRIMARY KEY (user_id, id),
                SHARD KEY (user_id),
                SORT KEY (created_at, status),
                INDEX(interaction_type) USING HASH,
                INDEX(status) USING HASH,
                INDEX(priority) USING HASH,
                INDEX(agent_handled) USING HASH,
                INDEX(created_at) USING BTREE,
                INDEX(id) USING HASH
            );
            """
            
            # Execute table creation
            for statement in create_tables_sql.split(';'):
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
            
            conn.commit()
            logger.info("Database tables created successfully")
            
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def test_connection():
    """Test database connection"""
    try:
        with get_database() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False

def close_connection_pool():
    """Close the connection pool"""
    global _connection_pool
    if _connection_pool:
        _connection_pool.close()
        _connection_pool = None
        logger.info("Connection pool closed")