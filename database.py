"""
Database connection and initialization
"""
import os
from urllib.parse import urlparse
import mysql.connector
from contextlib import contextmanager
import config


def get_database_url():
    """Get database URL from environment."""
    return os.getenv('DATABASE_URL')


@contextmanager
def get_db_connection():
    """
    Context manager for database connections.
    Automatically handles connection/cursor lifecycle.
    """
    conn = None
    cursor = None
    try:
        database_url = get_database_url()
        if not database_url:
            raise ValueError("DATABASE_URL not set in environment variables")
        
        # Parse MySQL connection string using urlparse
        # Format: mysql://user:password@host:port/database
        parsed = urlparse(database_url)
        
        conn = mysql.connector.connect(
            host=parsed.hostname,
            port=parsed.port or 3306,
            user=parsed.username,
            password=parsed.password,
            database=parsed.path.lstrip('/'),
            autocommit=False
        )
        cursor = conn.cursor(dictionary=True)
        yield cursor
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def init_database():
    """
    Initialize database tables if they don't exist.
    Called on bot startup.
    """
    with get_db_connection() as cursor:
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                telegram_id BIGINT UNIQUE NOT NULL,
                username VARCHAR(255),
                first_name VARCHAR(255),
                last_name VARCHAR(255),
                email VARCHAR(255),
                config JSON,
                registration_date TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                INDEX idx_telegram_id (telegram_id)
            )
        """)
        
        # Create accounts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                account_id VARCHAR(50) NOT NULL,
                account_name VARCHAR(255) NOT NULL,
                is_default BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_user_account (user_id, account_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create pairs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pairs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                pair_name VARCHAR(20) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE KEY unique_user_pair (user_id, pair_name),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create trades table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id INT AUTO_INCREMENT PRIMARY KEY,
                trade_id VARCHAR(50) UNIQUE NOT NULL,
                user_id INT NOT NULL,
                account_id VARCHAR(50) NOT NULL,
                pair VARCHAR(20) NOT NULL,
                direction VARCHAR(10) NOT NULL,
                entry_price DECIMAL(20, 5) NOT NULL,
                stop_loss DECIMAL(20, 5),
                take_profit DECIMAL(20, 5),
                status VARCHAR(20) NOT NULL,
                result VARCHAR(10),
                session VARCHAR(20),
                news_risk VARCHAR(20),
                notes TEXT,
                entry_datetime TIMESTAMP NOT NULL,
                exit_datetime TIMESTAMP NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Create indexes for better performance (MySQL compatible)
        # Try to create indexes, ignore if they already exist
        try:
            cursor.execute("CREATE INDEX idx_trades_user_id ON trades(user_id)")
        except mysql.connector.Error as e:
            if e.errno != 1061:  # Error 1061 = Duplicate key name
                raise
        
        try:
            cursor.execute("CREATE INDEX idx_trades_status ON trades(status)")
        except mysql.connector.Error as e:
            if e.errno != 1061:
                raise
        
        try:
            cursor.execute("CREATE INDEX idx_trades_entry_datetime ON trades(entry_datetime)")
        except mysql.connector.Error as e:
            if e.errno != 1061:
                raise
        
        print("✅ Database tables initialized successfully")


def test_connection():
    """Test database connection."""
    try:
        with get_db_connection() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result:
                print("✅ Database connection successful")
                return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False
    return False
