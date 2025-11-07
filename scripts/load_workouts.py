
import psycopg, os
from dotenv import load_dotenv
load_dotenv()
DB_URL = os.getenv('DATABASE_URL')
if not DB_URL:
    raise RuntimeError('DATABASE_URL environment variable is not set')
with psycopg.connect(DB_URL, autocommit=True) as conn:
    with conn.cursor() as cur:
        cur.execute(open('db_init.sql','r').read())
print('Main schema created (users, workouts, checklist_items, gestures, public_workouts).')
