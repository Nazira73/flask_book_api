# Instead of storing data in variables or Python lists that reset every time the server restarts, 
# databases give us permanent, structured storage.

# SQLAlchemy is an Object Relational Mapper (ORM) in Python. Instead of writing raw SQL like: SELECT * FROM users WHERE id = 1;
# You can do:  user = User.query.get(1)
# This makes database work easier, cleaner, and more Pythonic.

# Make sure you have:

# ✅ PostgreSQL installed
# ✅ A database created (you can name it flask_db or anything)
# ✅ A user with password (e.g., username=postgres, password=yourpass)

# If not sure, you can do this in psql:

# CREATE DATABASE flask_db;
# CREATE USER flask_user WITH PASSWORD 'yourpass';

# Once done
# GRANT ALL PRIVILEGES ON DATABASE flask_db TO flask_user;
# GRANT ALL PRIVILEGES ON SCHEMA public TO flask_user;
# ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO flask_user;

# using pgAdmin (the graphical interface for PostgreSQL), follow these steps:

# 1. Create the Database
    # Open pgAdmin and connect to your PostgreSQL server.
    # In the Object Browser (left sidebar):
    # Right-click on Databases > Create > Database.
    # In the Create Database dialog:
    # Database: flask_db
    # Owner: Leave as postgres for now (we’ll assign privileges later)
    # Click Save.

# 2. Create the User (Role)
    # In the left sidebar:
    # Expand Login/Group Roles under your server.
    # Right-click it > Create > Login/Group Role.
    # In the Create Role dialog:
    # Name: flask_user
    # Go to the Definition tab:
    # Set the Password to 'yourpass' (you can hide/unhide to confirm)
    # Go to the Privileges tab:
    # Check Can login? (this makes it a user)
    # Leave others unchecked for now.
    # Click Save.

# 3. Grant Privileges on Database
    # In the left sidebar:
    # Expand Databases > right-click on flask_db > Properties.
    # In the dialog:
    # Go to the Security tab -> Privileges.
    # Click the + icon to add a new row:
    # Role: Select flask_user
    # Check All (or specifically check: CONNECT, TEMPORARY, etc.)
    # Click Save.

# 4. Grant Schema Privileges to flask_user

    # flask_db → Schemas → public (right-click) → Properties
    # Go to the Privileges tab
    # Click the ➕ button to add a role
    # In the new row:
    # Role: flask_user
    # Privileges: Check ✅ ALL
    # Click Save


# pip install flask_sqlalchemy psycopg2-binary
# pip install python-dotenv

import os

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv


load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# PostgreSQL Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('sqlalchemy_url')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False   # disables a feature that tracks object changes 
                                                       # (which isn't usually needed and uses extra memory).

# Initialize DB
db = SQLAlchemy(app)

# Model
class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "year": self.year
        }

# Create tables (Run only once or guard with a flag in production)
with app.app_context():
    db.create_all()

# Home Route
@app.route('/')
def home():
    return {"message": "Welcome to Flask + PostgreSQL Book API"}

# GET: All Books
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([book.to_dict() for book in books])

# POST: Create Book
@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    if 'title' not in data or 'author' not in data:
        return {"error": "Title and Author are required fields"}, 400
    new_book = Book(
        title=data['title'],
        author=data['author'],
        year=data.get('year')  # Optional
    )
    db.session.add(new_book)
    db.session.commit()
    return {"message": "Book created successfully!"}, 201

# PUT: Update Book Fully
@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    # book = Book.query.get_or_404(id)
    book = Book.query.get(id)
    if not book:
        return {"error": "Book not found"}, 404

    data = request.get_json()
    book.title = data['title']
    book.author = data['author']
    book.year = data.get('year')
    db.session.commit()
    return {"message": "Book updated successfully"}

# PATCH: Update Book Partially
@app.route('/books/<int:id>', methods=['PATCH'])
def patch_book(id):
    book = Book.query.get(id)
    if not book:
        return {"error": "Book not found"}, 404

    data = request.get_json()
    if 'title' in data:
        book.title = data['title']
    if 'author' in data:
        book.author = data['author']
    if 'year' in data:
        book.year = data['year']
    db.session.commit()
    return {"message": "Book partially updated"}

# DELETE: Remove Book
@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get(id)
    if not book:
        return {"error": "Book not found"}, 404

    db.session.delete(book)
    db.session.commit()
    return {"message": "Book deleted successfully"}

# Run the app
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)

# Better Practice:
    # app.py – your main application setup
    # models.py – defines your database structure (tables)
    # create_db.py – used once to create tables

# For other databases
# mysql/mariadb: app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@host:port/dbname' + pip install pymysql
# Microsoft SQL Server : app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://username:password@dsn_name' + pip install pyodbc
# Oracle: app.config['SQLALCHEMY_DATABASE_URI'] = 'oracle+cx_oracle://username:password@host:port/dbname' + + pip install cx_Oracle