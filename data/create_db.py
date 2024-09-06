import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# load environment variables from .env file
load_dotenv()

# get database connection details from environment variables
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')

# create table queries
CREATE_TABLE_QUERIES = [
    """
    CREATE TABLE IF NOT EXISTS stocks (
        id SERIAL PRIMARY KEY,
        ticker VARCHAR(10) NOT NULL,
        date DATE NOT NULL,
        open_price NUMERIC(10, 2),
        close_price NUMERIC(10, 2),
        high_price NUMERIC(10, 2),
        low_price NUMERIC(10, 2),
        volume BIGINT,
        UNIQUE (ticker, date)  -- This ensures no duplicate (ticker, date) pairs are allowed
    );

    """,

    
    """
    CREATE TABLE IF NOT EXISTS lu_stock (
        id SERIAL PRIMARY KEY,
        symbol VARCHAR(10) NOT NULL UNIQUE,
        currency VARCHAR(10),
        exchange_name VARCHAR(50),
        full_exchange_name VARCHAR(50),
        instrument_type VARCHAR(50),
        first_trade_date TIMESTAMP,
        regular_market_price NUMERIC(10, 4),
        fifty_two_week_high NUMERIC(10, 4),
        fifty_two_week_low NUMERIC(10, 4),
        regular_market_day_high NUMERIC(10, 4),
        regular_market_day_low NUMERIC(10, 4),
        regular_market_volume BIGINT,
        long_name VARCHAR(255),
        short_name VARCHAR(255),
        chart_previous_close NUMERIC(10, 4),
        timezone VARCHAR(50),
        exchange_timezone_name VARCHAR(50)
);
"""
]

def create_database():
    try:
        # Connect to the PostgreSQL server
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()

        # Create tables
        for query in CREATE_TABLE_QUERIES:
            cursor.execute(query)
        
        print("Database and tables created successfully.")

    except Exception as e:
        print(f"Error creating database: {e}")
    
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_database()
