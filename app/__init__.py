# __init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize the database object
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'kZD7rHGTSPNhEcfyWTcicgYKwkFhPqK0'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database with the app
    db.init_app(app)

    # Ensure tables are created when the app starts
    with app.app_context():
        db.create_all()  # Create tables

    # Import and initialize routes
    from .routes import init_app  # Import init_app function from routes.py
    init_app(app)  # Register the routes with the app

    return app
