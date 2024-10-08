import os
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

def connect_to_db(env="prod"):
    """
    Connect to the PostgreSQL database.
    Use 'env="dev"' for local db and 'env="prod"' for hosted db.
    """
    # Load environment variables
    load_dotenv()

    # Decide which environment to use
    if env == "dev":
        # Local DB credentials
        DB_NAME = os.getenv('DB_NAME')
        DB_USER = os.getenv('DB_USER')
        DB_PASSWORD = os.getenv('DB_PASSWORD')
        DB_HOST = os.getenv('DB_HOST', 'localhost')
        DB_PORT = os.getenv('DB_PORT', '5432')

        # Connect to local PostgreSQL
        return psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
    elif env == "prod":
        # Hosted DB credentials
        DB_URL = os.getenv('POSTGRES_URL')  # Full connection URL for hosted DB

        # Connect to hosted PostgreSQL
        return psycopg2.connect(DB_URL)
    else:
        raise ValueError(f"Invalid environment '{env}' specified. Use 'dev' or 'prod'.")

# create table queries
CREATE_TABLE_QUERIES = [
    # create the stocks table
    """
    CREATE TABLE IF NOT EXISTS stocks (
        id SERIAL PRIMARY KEY,
        ticker VARCHAR(10) NOT NULL,
        date TIMESTAMPTZ NOT NULL,
        open_price NUMERIC(10, 2),
        close_price NUMERIC(10, 2),
        high_price NUMERIC(10, 2),
        low_price NUMERIC(10, 2),
        volume BIGINT,
        UNIQUE (ticker, date)
    );
    """,

    # create the stock metadata table
    """
    CREATE TABLE IF NOT EXISTS lu_stock (
        id SERIAL PRIMARY KEY,
        ticker VARCHAR(10) NOT NULL UNIQUE,
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
        exchange_timezone_name VARCHAR(50),
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    , 

    # create the stock news table
    """
    CREATE TABLE IF NOT EXISTS stock_news (
        id SERIAL PRIMARY KEY,
        ticker VARCHAR(10) NOT NULL,           
        date TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        uuid VARCHAR(255) NOT NULL UNIQUE,
        title VARCHAR(255) NOT NULL,
        publisher VARCHAR(255),
        link TEXT,
        provider_publish_time TIMESTAMPTZ,
        type VARCHAR(50),
        thumbnail_url TEXT,
        thumbnail_width INT,
        thumbnail_height INT,
        UNIQUE (ticker, uuid)
    );
    """
]

def create_database():
    try:
        # connect to the PostgreSQL server
        conn = connect_to_db()
        conn.autocommit = True
        cursor = conn.cursor()

        # Create tables
        for query in CREATE_TABLE_QUERIES:
            cursor.execute(query)
        
        print("Tables created successfully.")

    except Exception as e:
        print(f"Error creating database: {e}")
    
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_database()
