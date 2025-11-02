import psycopg
import json

# Connect to PostgreSQL
DB_URL = "postgresql://<username>:<password>@<host>/<database>"

with psycopg.connect(DB_URL, autocommit=True) as conn:  # autocommit avoids explicit commit for DDL
    with conn.cursor() as cur:
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
