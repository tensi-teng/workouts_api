
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from db import get_conn

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
          required:
            - username
            - password
    responses:
      201:
        description: User registered
      400:
        description: Bad request
    """
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error':'username and password required'}), 400
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id FROM users WHERE username=%s', (username,))
            if cur.fetchone():
                return jsonify({'error':'username exists'}), 400
            hashed = generate_password_hash(password)
            cur.execute('INSERT INTO users (username, password) VALUES (%s, %s) RETURNING id', (username, hashed))
            uid = cur.fetchone()[0]
    return jsonify({'message':'user registered', 'user_id': uid}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login and receive a JWT token
    ---
    tags:
      - Auth
    parameters:
      - in: body
        name: body
        schema:
          type: object
          properties:
            username:
              type: string
            password:
              type: string
          required:
            - username
            - password
    responses:
      200:
        description: JWT token
      401:
        description: Invalid credentials
    """
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error':'username and password required'}), 400
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id, password FROM users WHERE username=%s', (username,))
            row = cur.fetchone()
            if not row:
                return jsonify({'error':'invalid credentials'}), 401
            uid, hashed = row
            if not check_password_hash(hashed, password):
                return jsonify({'error':'invalid credentials'}), 401
    token = create_access_token(identity=str(uid))  # Convert uid to string
    return jsonify({'token': token}), 200
