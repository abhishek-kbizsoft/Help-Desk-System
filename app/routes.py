from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  # Import db from __init__.py
from .models import User, Ticket

# Define routes in a function so that they can be added to the app later
def init_app(app):
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/register')
    def register_page():
        return render_template('auth/register.html')

    @app.route('/login')
    def login_page():
        return render_template('auth/login.html')

    @app.route('/auth/register', methods=['POST'])
    def user_register():
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')  # Get password input from the user

        # Check if the email already exists in the database
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists. Please use a different email.', 'error')  # Show flash message
            return redirect(url_for('register_page'))

        # Hash the password using Werkzeug with the correct method
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')  # Correct hash method

        # Create the new user with the hashed password
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Your registration was successfull', 'success')  # Show success message
        return redirect(url_for('index'))
    
    @app.route('/auth/login', methods=['POST'])
    def user_login():
        email = request.form.get('email')
        password = request.form.get('password')

        # Find the user in the database by email
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("Invalid email or password.", "error")
            return redirect(url_for('login_page'))

        # Check if the password matches the hashed password in the database
        if not check_password_hash(user.password, password):
            flash("Invalid email or password.", "error")
            return redirect(url_for('login_page'))

        # Successful login
        flash(f"Welcome back, {user.username}!", "success")
        return redirect(url_for('index'))
        

    @app.route('/add_ticket', methods=['POST'])
    def add_ticket():
        title = request.form.get('title')
        description = request.form.get('description')
        user_id = request.form.get('user_id')  # User ID should exist in the User table

        new_ticket = Ticket(title=title, description=description, user_id=user_id)
        db.session.add(new_ticket)
        db.session.commit()

        return redirect(url_for('index'))
    
    @app.route('/users')
    def users():
        all_users = User.query.all() 
        return render_template('users.html', users=all_users)
