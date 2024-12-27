from flask import render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from . import db  # Import db from __init__.py
from .models import User, Ticket

# Define routes in a function so that they can be added to the app later
def init_app(app):
    
    # @app.before_request
    # def check_login():
    #     # Define the routes where user needs to be authenticated
    #     if 'user_id' not in session and request.endpoint not in ['login_page', 'register_page',]:
    #         flash("You must be logged in to view this page.", "error")
    #         return redirect(url_for('login_page'))
    
    @app.route('/')
    def index():
        # Check if the user is already logged in
        if 'user_id' in session:
            flash("You are already logged in", "success")
            return redirect(url_for('tickets'))
        return render_template('auth/login.html')

    @app.route('/register')
    def register_page():
        # Check if the user is already logged in
        if 'user_id' in session:
            flash("You are already logged in", "success")
            return redirect(url_for('tickets'))
        return render_template('auth/register.html')

    @app.route('/login')
    def login_page():
        # Check if the user is already logged in
        if 'user_id' in session:
            flash("You are already logged in", "success")
            return redirect(url_for('tickets'))
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
        
        # Check if the password length is less than 8 characters
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return redirect(url_for('register_page'))

        # Hash the password using Werkzeug with the correct method
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')  # Correct hash method

        # Create the new user with the hashed password
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        session['user_id'] = new_user.id
        session['username'] = new_user.username

        flash('Your registration was successfull', 'success')  # Show success message
        return redirect(url_for('tickets'))
    
    @app.route('/auth/login', methods=['POST'])
    def user_login():
        email = request.form.get('email')
        password = request.form.get('password')

        # Find the user in the database by email
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("User not found.", "error")
            return redirect(url_for('login_page'))

        # Check if the password matches the hashed password in the database
        if not check_password_hash(user.password, password):
            flash("Invalid email or password.", "error")
            return redirect(url_for('login_page'))

        # Successful login
        session['user_id'] = user.id
        session['username'] = user.username
        flash(f"Welcome back, {user.username}!", "success")
        return redirect(url_for('tickets'))
    
    @app.route('/users')
    def users():
        all_users = User.query.order_by(User.id.desc()).all()

        for user in all_users:
            user.created_at_formatted = user.created_at.strftime('%d-%m-%Y') 

        return render_template('users.html', users=all_users)
    
    @app.route('/tickets')
    def tickets():
        if 'user_id' not in session:
            flash("You must be logged in to view this page.", "error")
            return redirect(url_for('login_page'))
        
        search_term = request.args.get('search', '')
        
        if search_term:
            tickets = Ticket.query.filter(
            Ticket.user_id == session['user_id'],
            (Ticket.title.contains(search_term) | Ticket.description.contains(search_term))
        ).order_by(Ticket.id.desc()).all()
        else:
            tickets = Ticket.query.filter_by(user_id=session['user_id']).order_by(Ticket.id.desc()).all()
        

        for ticket in tickets:
            ticket.created_at_formatted = ticket.created_at.strftime('%d-%m-%Y')  # Format the created_at date

        return render_template('tickets/index.html', tickets=tickets, search_term=search_term)
    
    @app.route('/add-ticket', methods=['GET'])
    def add_ticket_view():
        if 'user_id' not in session:
            flash("You must be logged in to view this page.", "error")
            return redirect(url_for('login_page'))
        
        return render_template('tickets/add-ticket.html')

    @app.route('/edit-ticket/<int:ticket_id>', methods=['GET'])
    def edit_ticket_view(ticket_id):
        if 'user_id' not in session:
            flash("You must be logged in to view this page.", "error")
            return redirect(url_for('login_page'))
        
        # Retrieve the ticket by ID
        ticket = Ticket.query.get(ticket_id)
        
        if not ticket:
            flash("Ticket not found.", "error")
            return redirect(url_for('tickets'))
        
        return render_template('tickets/edit-ticket.html', ticket=ticket)
    
    @app.route('/update-ticket/<int:ticket_id>', methods=['POST'])
    def update_ticket(ticket_id):
        # Retrieve the ticket by ID
        ticket = Ticket.query.get(ticket_id)
        
        if not ticket:
            flash("Ticket not found.", "error")
            return redirect(url_for('tickets'))

        # Check if the current user is the one who created the ticket
        if ticket.user_id != session['user_id']:
            flash("You can only edit your own tickets.", "error")
            return redirect(url_for('tickets'))

        # Get the updated data from the form
        title = request.form.get('title')
        description = request.form.get('description')

        # Update ticket fields
        ticket.title = title
        ticket.description = description

        # Commit the changes to the database
        db.session.commit()

        flash("Ticket updated successfully!", "success")
        return redirect(url_for('tickets'))

        
    @app.route('/add-ticket', methods=['POST'])
    def add_ticket():
        title = request.form.get('title')
        description = request.form.get('description')
        user = User.query.get(session['user_id'])
        
        if user is None:
            flash("User not found.", "error")
            return redirect(url_for('login_page'))

        new_ticket = Ticket(title=title, description=description, user_id=user.id)
        db.session.add(new_ticket)
        db.session.commit()

        flash("Ticket created successfully", "success")
        return redirect(url_for('tickets'))
    
    @app.route("/delete_ticket", methods=['POST'])
    def delete_ticket():
        ticket_id = request.form.get('id')
        
        # Find the ticket by ID
        ticket = Ticket.query.get(ticket_id)
        
        if ticket:
            # If ticket exists, delete it
            db.session.delete(ticket)
            db.session.commit()
            flash("Ticket deleted successfully", "success")
        else:
            # If ticket does not exist, show error
            flash("Ticket not found", "error")

        return redirect(url_for('tickets'))
    
    @app.route('/')
    
    
    @app.route('/auth/logout')
    def user_logout():
        session.clear()
        flash("You have been logged out.", "success")
        return redirect(url_for('login_page'))

