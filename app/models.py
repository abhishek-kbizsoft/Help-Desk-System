from . import db

# Define the User model (table)
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary Key for User
    username = db.Column(db.String(150), unique=True, nullable=False)  # Unique Username
    email = db.Column(db.String(120), unique=True, nullable=False)  # Unique Email
    password = db.Column(db.String(200), nullable=False)  # Password (hashed)

    def __repr__(self):
        return f'<User {self.username}>'

# Define the Ticket model (table)
class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Primary Key for Ticket
    title = db.Column(db.String(200), nullable=False)  # Title of the ticket
    description = db.Column(db.Text, nullable=False)  # Description of the issue
    status = db.Column(db.String(50), nullable=False, default="Open")  # Default status is "Open"
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User

    # Define the relationship with the User model
    user = db.relationship('User', backref=db.backref('tickets', lazy=True))

    def __repr__(self):
        return f'<Ticket {self.title}>'
