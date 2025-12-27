import psycopg2
import os

DATABASE_URL = os.getenv('DATABASE_URL')

# Connect to your Heroku PostgreSQL database
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()

# Drop the table if it exists
cur.execute("DROP TABLE IF EXISTS users;")

# Create the table
cur.execute("""
    CREATE TABLE user_info (
        id SERIAL PRIMARY KEY,
        user_name VARCHAR(50) UNIQUE NOT NULL,
        user_email VARCHAR(100) UNIQUE NOT NULL,
        user_password TEXT NOT NULL,
        user_comments VARCHAR(100),
        img_url VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

# Commit and close
conn.commit()
cur.close()
conn.close()
