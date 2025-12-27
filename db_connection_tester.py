import psycopg2
import os

def test_db_connection():
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        print("Database connection successful.")
    except Exception as e:
        print(f"Database connection failed: {e}")

if __name__ == "__main__":
    test_db_connection()
