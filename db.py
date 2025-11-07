<<<<<<< HEAD
import psycopg
import json
import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")  
if not DB_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")


with psycopg.connect(DB_URL, autocommit=True) as conn:  
        # Drop and create table
        cur.execute("""
        DROP TABLE IF EXISTS workouts;
        CREATE TABLE workouts (
            id SERIAL PRIMARY KEY,
            type VARCHAR(50),
            name VARCHAR(100),
            muscles TEXT[],
            equipment VARCHAR(100),
            instructions TEXT,
            level VARCHAR(20)
        );
        """)

        # Load JSON data
        with open("workouts.json", "r") as f:
            workouts = json.load(f)

        # Insert data
        for w in workouts:
            cur.execute("""
            INSERT INTO workouts (type, name, muscles, equipment, instructions, level)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (w["type"], w["name"], w["muscles"], w["equipment"], w["instructions"], w["level"]))

print("Workouts loaded into database!")
=======

import os
import psycopg
from dotenv import load_dotenv
load_dotenv()

print("\nDatabase Environment:")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL', '')[:20]}...{os.getenv('DATABASE_URL', '')[-4:] if os.getenv('DATABASE_URL') else 'not set'}")
print("Attempting database connection...")

DB_URL = os.getenv('DATABASE_URL')
if not DB_URL:
    raise RuntimeError('DATABASE_URL environment variable is not set')

def get_conn():
    try:
        conn = psycopg.connect(DB_URL, autocommit=True)
        print("✓ Database connected successfully!")
        return conn
    except Exception as e:
        print(f"✗ Database connection failed: {str(e)}")
        raise
>>>>>>> 2f24dcc (major changes)
