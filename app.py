<<<<<<< HEAD
from functools import wraps
from flask import Flask, jsonify, request
import psycopg
from flasgger import Swagger
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("API_KEY")
DB_URL = os.getenv("DATABASE_URL")

if not DB_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

app = Flask(__name__)
Swagger(app)


# --- API key decorator ---
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get("X-API-KEY")
        if api_key != API_KEY:
            return jsonify({"error": "you need a valid api key"}), 403
        return f(*args, **kwargs)
    return decorated_function


# --- General workouts endpoint ---
@app.route("/workouts", methods=["GET"])
@require_api_key
def get_workouts():
    """
    Get all workouts or filter by type, muscle, level
    ---
    tags:
      - Workouts
    parameters:
      - name: X-API-KEY
        in: header
        type: string
        required: true
        description: Your API key
      - name: type
        in: query
        type: string
        required: false
        description: Filter by workout type
      - name: muscle
        in: query
        type: string
        required: false
        description: Filter by muscle
      - name: level
        in: query
        type: string
        required: false
        description: Filter by level
    responses:
      200:
        description: List of workouts
      403:
        description: Invalid API key
      500:
        description: Database error
    """
    type_filter = request.args.get("type")
    muscle_filter = request.args.get("muscle")
    level_filter = request.args.get("level")

    try:
        with psycopg.connect(DB_URL, autocommit=True) as conn:
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                query = "SELECT id, type, name, muscles, equipment, instructions, level FROM workouts WHERE 1=1"
                params = []

                if type_filter:
                    query += " AND LOWER(type) = LOWER(%s)"
                    params.append(type_filter.strip())
                if muscle_filter:
                    query += " AND EXISTS (SELECT 1 FROM unnest(muscles) m WHERE LOWER(m) = LOWER(%s))"
                    params.append(muscle_filter.strip())
                if level_filter:
                    query += " AND LOWER(level) = LOWER(%s)"
                    params.append(level_filter.strip())

                cur.execute(query, params)
                rows = cur.fetchall()
                workouts = [dict(row) for row in rows]

    except psycopg.Error as e:
        app.logger.exception("Database error while fetching workouts")
        return jsonify({"error": "database error", "detail": str(e)}), 500

    return jsonify({"count": len(workouts), "workouts": workouts})


# --- Protected endpoint ---
@app.route("/protected", methods=["GET"])
@require_api_key
def protected_resource():
    """
    Protected endpoint
    ---
    tags:
      - Authentication
    responses:
      200:
        description: Successful response
      403:
        description: Invalid API key
    """
    return jsonify({"message": "this is a protected API!"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8000)))
=======
from flask import Flask
from dotenv import load_dotenv
import os
load_dotenv()

print("\nEnvironment variables loaded:")
print(f"JWT_SECRET_KEY: {'*' * 8}{os.getenv('JWT_SECRET_KEY', '')[-4:] if os.getenv('JWT_SECRET_KEY') else 'not set'}")
print(f"API_KEY: {os.getenv('API_KEY', '')[:6]}...{os.getenv('API_KEY', '')[-4:] if os.getenv('API_KEY') else 'not set'}")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL', '')[:20]}...{os.getenv('DATABASE_URL', '')[-4:] if os.getenv('DATABASE_URL') else 'not set'}")
print()

from flasgger import Swagger
from flask_jwt_extended import JWTManager

from routes.auth import auth_bp
from routes.workouts import workouts_bp
from routes.public_api import public_bp
from routes.importer import import_bp
from routes.gestures import gestures_bp

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret')

Swagger(app)

jwt = JWTManager(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(workouts_bp, url_prefix='')
app.register_blueprint(public_bp, url_prefix='/api')
app.register_blueprint(import_bp, url_prefix='')
app.register_blueprint(gestures_bp, url_prefix='/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
>>>>>>> 2f24dcc (major changes)
