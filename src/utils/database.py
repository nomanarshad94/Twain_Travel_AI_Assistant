import psycopg2
from psycopg2 import pool
from src.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from src.utils.constants import DB_POOL_MIN_CONNECTIONS, DB_POOL_MAX_CONNECTIONS
import logging

logger = logging.getLogger(__name__)

# Connection pool for scalability
connection_pool = None


def init_connection_pool():
    """Initialize PostgreSQL connection pool"""
    global connection_pool
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            DB_POOL_MIN_CONNECTIONS,
            DB_POOL_MAX_CONNECTIONS,
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logger.info("PostgreSQL connection pool created successfully")
    except Exception as e:
        logger.error(f"Error creating connection pool: {e}")
        raise


def get_db_connection():
    """Get a database connection from the pool"""
    if connection_pool:
        return connection_pool.getconn()
    raise Exception("Connection pool not initialized")


def release_db_connection(conn):
    """Release a database connection back to the pool"""
    if connection_pool and conn:
        connection_pool.putconn(conn)


def init_db():
    """Initialize the database with required tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Create conversations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                conversation_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                is_user BOOLEAN NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            )
        ''')

        conn.commit()
        cursor.close()
        release_db_connection(conn)

        logger.info("Database tables initialized successfully")

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise
