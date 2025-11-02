from flask import Flask, jsonify, request
import psycopg
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
print(os.getenv("DATABASE_URL"))
print(os.getenv("API_KEY"))

API_KEY = os.getenv("API_KEY")

app = Flask(__name__)

DB_URL = os.getenv("DATABASE_URL")
if not DB_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")


def verify_api_key(request):
    api_key = request.headers.get('X-API-KEY')
    if api_key != API_KEY:
        return jsonify({"error": "you need a valid api key"}), 403
    return None


@app.route("/protected", methods=['GET'])
def protected_resource():
    verification_response = verify_api_key(request)
    if verification_response:
        return verification_response
    return jsonify({"message": "this is a protected API!"})


@app.route("/workouts/filter", methods=["POST"])
def filter_workouts():
    payload = request.get_json() or {}

    type_filter = payload.get("type")
    muscle_filter = payload.get("muscle")
    level_filter = payload.get("level")

    for name, val in (("type", type_filter), ("muscle", muscle_filter), ("level", level_filter)):
        if val is not None and not isinstance(val, str):
            return jsonify({"error": f"'{name}' must be a string"}), 400

    try:
        # Use psycopg 3 connection and dict_row factory
        with psycopg.connect(DB_URL, autocommit=True) as conn:
            with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
                query = (
                    "SELECT id, type, name, muscles, equipment, instructions, level "
                    "FROM workouts WHERE 1=1"
                )
                params = []

                if type_filter:
                    query += " AND LOWER(type) = LOWER(%s)"
                    params.append(type_filter.strip())
                if muscle_filter:
                    query += (
                        " AND EXISTS (SELECT 1 FROM unnest(muscles) m "
                        "WHERE LOWER(m) = LOWER(%s))"
                    )
                    params.append(muscle_filter.strip())
                if level_filter:
                    query += " AND LOWER(level) = LOWER(%s)"
                    params.append(level_filter.strip())

                cur.execute(query, params)
                rows = cur.fetchall()
                workouts = [dict(row) for row in rows]

    except psycopg.Error as e:
        app.logger.exception("Database error while filtering workouts")
        return jsonify({"error": "database error", "detail": str(e)}), 500

    return jsonify({"count": len(workouts), "workouts": workouts})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
