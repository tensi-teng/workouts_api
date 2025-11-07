
FitLife Backend (psycopg-only, no geotag) - Final
=================================================
Features:
- psycopg (psycopg[binary]) for PostgreSQL (no SQLAlchemy)
- JWT auth for protected routes (flask-jwt-extended)
- Public API (API key protected) with concise Swagger docs (flasgger)
- Workouts CRUD, checklist generation, checklist toggle, import, gestures
- Public_workouts table + loader script for the public API
- No Twilio/SMS and no geotag support

Quickstart:
1. Copy `.env.example` -> `.env` and fill values:
    DATABASE_URL=postgresql://user:pass@host:5432/dbname
    API_KEY=your_public_api_key
    JWT_SECRET_KEY=your_jwt_secret
2. Create virtualenv and install:
    python -m venv venv
    source venv/bin/activate   # or venv\Scripts\activate on Windows
    pip install -r requirements.txt
3. Initialize DB and load sample data:
    python load_workouts.py            # creates main schema
    python load_public_api_workouts.py # creates public_workouts table and loads sample data
4. Run the app:
    python app.py
5. Open Swagger UI:
    http://localhost:5000/apidocs
