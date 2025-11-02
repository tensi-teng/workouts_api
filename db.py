import psycopg
import json

# Connect to PostgreSQL
conn = psycopg.connect(
    "postgresql://<username>:<password>@<host>/<database>"
)
cur = conn.cursor()


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


with open("workouts.json", "r") as f:
    workouts = json.load(f)

for w in workouts:
    cur.execute("""
        INSERT INTO workouts (type, name, muscles, equipment, instructions, level)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (w["type"], w["name"], w["muscles"], w["equipment"], w["instructions"], w["level"]))

conn.commit()
cur.close()
conn.close()

print("Workouts loaded into database!")
