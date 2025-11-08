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
