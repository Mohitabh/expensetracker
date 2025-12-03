# db.py
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    db_url = os.getenv("DATABASE_URL")

    try:
        if db_url:
            return psycopg2.connect(db_url)
        else:
            return psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                database=os.getenv('POSTGRES_DB', 'expense_tracker'),
                user=os.getenv('POSTGRES_USER', 'postgres'),
                password=os.getenv('POSTGRES_PASSWORD'),
                port=os.getenv('POSTGRES_PORT', '5432')
            )
    except psycopg2.Error as e:
        print("Error connecting to PostgreSQL database:", e)
        return None
