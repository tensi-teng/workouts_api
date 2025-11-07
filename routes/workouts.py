
import psycopg
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import get_conn
from utils.generate_checklist import generate_checklist

workouts_bp = Blueprint('workouts', __name__)

@workouts_bp.route('/workouts', methods=['POST'])
@jwt_required()
def create_workout():
    """Create a workout routine (auto-generates checklist)
    ---
    tags:
      - Workouts
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
        description: Bearer <JWT token>
      - in: body
        name: body
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
            equipment:
              type: array
              items:
                type: string
          required:
            - name
    responses:
      201:
        description: Workout created
      400:
        description: Bad request
    """
    data = request.get_json() or {}
    name = data.get('name')
    if not name:
        return jsonify({'error':'name required'}), 400
    description = data.get('description')
    equipment = data.get('equipment', [])
    user_id = int(get_jwt_identity())  # Convert JWT string ID to integer
    eq_str = ','.join(equipment) if isinstance(equipment, list) else (equipment or '')
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('INSERT INTO workouts (name, description, equipment, user_id) VALUES (%s,%s,%s,%s) RETURNING id', (name, description, eq_str, user_id))
            wid = cur.fetchone()[0]
            # generate checklist items
            items = generate_checklist(equipment)
            for it in items:
                cur.execute('INSERT INTO checklist_items (task, done, workout_id) VALUES (%s,%s,%s)', (it['task'], it['done'], wid))
    return jsonify({'message':'created','workout': {'id': wid, 'name':name, 'description':description, 'equipment': equipment}}), 201

@workouts_bp.route('/workouts', methods=['GET'])
@jwt_required()
def list_workouts():
    """List all workouts for the logged-in user
    ---
    tags:
      - Workouts
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
        description: Bearer <JWT token>
    responses:
      200:
        description: List of workouts
    """
    user_id = int(get_jwt_identity())  # Convert JWT string ID to integer
    with get_conn() as conn:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute('SELECT id, name, description, equipment FROM workouts WHERE user_id=%s ORDER BY created_at DESC', (user_id,))
            rows = cur.fetchall()
            out = []
            for r in rows:
                eq = [e for e in (r['equipment'] or '').split(',') if e]
                cur.execute('SELECT id, task, done FROM checklist_items WHERE workout_id=%s', (r['id'],))
                checklist = [{'id':c[0],'task':c[1],'done':c[2]} for c in cur.fetchall()]
                out.append({'id': r['id'], 'name': r['name'], 'description': r['description'], 'equipment': eq, 'checklist': checklist})
    return jsonify(out), 200


@workouts_bp.route('/workouts/<int:wid>', methods=['GET'])
@jwt_required()
def get_workout(wid):
    """Get a single workout belonging to the logged-in user
    ---
    tags:
      - Workouts
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
        description: Bearer <JWT token>
      - in: path
        name: wid
        type: integer
        required: true
    responses:
      200:
        description: Workout details
      404:
        description: Not found or not allowed
    """
    user_id = int(get_jwt_identity())
    with get_conn() as conn:
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cur:
            cur.execute('SELECT id, name, description, equipment FROM workouts WHERE id=%s AND user_id=%s', (wid, user_id))
            row = cur.fetchone()
            if not row:
                return jsonify({'error':'not found or not allowed'}), 404
            eq = [e for e in (row['equipment'] or '').split(',') if e]
            cur.execute('SELECT id, task, done FROM checklist_items WHERE workout_id=%s', (wid,))
            checklist = [{'id':c[0],'task':c[1],'done':c[2]} for c in cur.fetchall()]
            res = {'id': row['id'], 'name': row['name'], 'description': row['description'], 'equipment': eq, 'checklist': checklist}
    return jsonify(res), 200


@workouts_bp.route('/workouts/import/<int:pid>', methods=['POST'])
@jwt_required()
def import_public_workout(pid):
    """Import a public workout into the user's workouts
    ---
    tags:
      - Workouts
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
        description: Bearer <JWT token>
      - in: path
        name: pid
        type: integer
        required: true
        description: public workout id
    responses:
      201:
        description: Imported
      404:
        description: Public workout not found
    """
    user_id = int(get_jwt_identity())
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT type, name, muscles, equipment, instructions, level FROM public_workouts WHERE id=%s', (pid,))
            prow = cur.fetchone()
            if not prow:
                return jsonify({'error':'public workout not found'}), 404
            p_type, name, muscles, equipment, instructions, level = prow
            # Normalize equipment into comma-separated string
            if isinstance(equipment, (list, tuple)):
                eq_str = ','.join(equipment)
            else:
                eq_str = equipment or ''
            cur.execute('INSERT INTO workouts (name, description, equipment, user_id) VALUES (%s,%s,%s,%s) RETURNING id', (name, instructions, eq_str, user_id))
            wid = cur.fetchone()[0]
            items = generate_checklist(eq_str.split(',') if eq_str else [])
            for it in items:
                cur.execute('INSERT INTO checklist_items (task, done, workout_id) VALUES (%s,%s,%s)', (it['task'], it['done'], wid))
    return jsonify({'message':'imported','workout': {'id': wid, 'name': name}}), 201

@workouts_bp.route('/workouts/<int:wid>', methods=['PUT'])
@jwt_required()
def update_workout(wid):
    """Update a workout (replace equipment regenerates checklist)
    ---
    tags:
      - Workouts
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
      - in: path
        name: wid
        type: integer
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
      200:
        description: Updated
    """
    data = request.get_json() or {}
    user_id = int(get_jwt_identity())  # Convert JWT string ID to integer
    name = data.get('name')
    description = data.get('description')
    equipment = data.get('equipment')
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT user_id FROM workouts WHERE id=%s', (wid,))
            row = cur.fetchone()
            if not row or row[0] != user_id:
                return jsonify({'error':'not found or not allowed'}), 404
            if name: cur.execute('UPDATE workouts SET name=%s WHERE id=%s', (name, wid))
            if description is not None: cur.execute('UPDATE workouts SET description=%s WHERE id=%s', (description, wid))
            if equipment is not None:
                eq_str = ','.join(equipment) if isinstance(equipment, list) else equipment
                cur.execute('UPDATE workouts SET equipment=%s WHERE id=%s', (eq_str, wid))
                # regenerate checklist
                cur.execute('DELETE FROM checklist_items WHERE workout_id=%s', (wid,))
                items = generate_checklist(equipment)
                for it in items:
                    cur.execute('INSERT INTO checklist_items (task, done, workout_id) VALUES (%s,%s,%s)', (it['task'], it['done'], wid))
    return jsonify({'message':'updated'}), 200

@workouts_bp.route('/workouts/<int:wid>', methods=['DELETE'])
@jwt_required()
def delete_workout(wid):
    """Delete a workout
    ---
    tags:
      - Workouts
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
      - in: path
        name: wid
        type: integer
        required: true
    responses:
      200:
        description: Deleted
    """
    user_id = int(get_jwt_identity())  # Convert JWT string ID to integer
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT user_id FROM workouts WHERE id=%s', (wid,))
            row = cur.fetchone()
            if not row or row[0] != user_id:
                return jsonify({'error':'not found or not allowed'}), 404
            cur.execute('DELETE FROM workouts WHERE id=%s', (wid,))
    return jsonify({'message':'deleted'}), 200

@workouts_bp.route('/checklist/<int:item_id>', methods=['PATCH'])
@jwt_required()
def toggle_checklist(item_id):
    """Toggle a checklist item (done/undone)
    ---
    tags:
      - Workouts
    parameters:
      - in: header
        name: Authorization
        type: string
        required: true
      - in: path
        name: item_id
        type: integer
        required: true
    responses:
      200:
        description: Toggled
    """
    user_id = int(get_jwt_identity())  # Convert JWT string ID to integer
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT ci.done, w.user_id FROM checklist_items ci JOIN workouts w ON ci.workout_id=w.id WHERE ci.id=%s', (item_id,))
            row = cur.fetchone()
            if not row or row[1] != user_id:
                return jsonify({'error':'not allowed'}), 403
            new_done = not row[0]
            cur.execute('UPDATE checklist_items SET done=%s WHERE id=%s', (new_done, item_id))
    return jsonify({'message':'toggled','done': new_done}), 200
