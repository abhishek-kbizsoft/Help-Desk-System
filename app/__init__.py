from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Initialize the database object
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'kZD7rHGTSPNhEcfyWTcicgYKwkFhPqK0'
    # SQLite Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database with the app
    db.init_app(app)

    # Import and initialize routes
    from .routes import init_app  # Import init_app function from routes.py
    init_app(app)  # Register the routes with the app

    return app
