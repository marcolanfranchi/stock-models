import os
import psycopg2
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