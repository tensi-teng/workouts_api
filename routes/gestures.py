
from flask import Blueprint, request, jsonify
from db import get_conn
from flask_jwt_extended import jwt_required, get_jwt_identity

gestures_bp = Blueprint('gestures', __name__)

@gestures_bp.route('/gestures', methods=['POST'])
@jwt_required()
def set_gestures():
    """Set gesture mappings for the user
    ---
    tags:
      - Gestures
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
            mappings:
              type: array
              items:
                type: object
                properties:
                  name: {type: string}
                  action: {type: string}
    responses:
      200:
        description: Saved
    """
    data = request.get_json() or {}
    mappings = data.get('mappings', [])
    user_id = get_jwt_identity()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM gestures WHERE user_id=%s', (user_id,))
            for m in mappings:
                cur.execute('INSERT INTO gestures (name, action, user_id) VALUES (%s,%s,%s)', (m.get('name'), m.get('action'), user_id))
    return jsonify({'message':'saved'}), 200

@gestures_bp.route('/gestures', methods=['GET'])
@jwt_required()
def get_gestures():
    """Get gesture mappings for the user
    ---
    tags:
      - Gestures
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
    responses:
      200:
        description: List of mappings
    """
    user_id = get_jwt_identity()
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id, name, action FROM gestures WHERE user_id=%s', (user_id,))
            rows = cur.fetchall()
            out = [{'id':r[0],'name':r[1],'action':r[2]} for r in rows]
    return jsonify(out), 200
