
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import get_conn
from utils.generate_checklist import generate_checklist

import_bp = Blueprint('importer', __name__)

@import_bp.route('/import', methods=['POST'])
@jwt_required()
def import_workout():
    """Import a workout (JSON payload)
    ---
    tags:
      - Import
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
      - in: body
        name: body
        schema:
          type: object
          properties:
            name: {type: string}
            description: {type: string}
            equipment:
              type: array
              items: {type: string}
    responses:
      201:
        description: Imported
    """
    data = request.get_json() or {}
    name = data.get('name')
    description = data.get('description')
    equipment = data.get('equipment', [])
    if not name:
        return jsonify({'error':'name required'}), 400
    user_id = get_jwt_identity()
    eq_str = ','.join(equipment) if isinstance(equipment, list) else equipment
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO workouts (name, description, equipment, user_id) VALUES (%s,%s,%s,%s) RETURNING id', (name, description, eq_str, user_id))
            wid = cur.fetchone()[0]
            checklist = generate_checklist(equipment)
            for it in checklist:
                cur.execute('INSERT INTO checklist_items (task, done, workout_id) VALUES (%s,%s,%s)', (it['task'], it['done'], wid))
    return jsonify({'message':'imported', 'workout_id': wid}), 201
