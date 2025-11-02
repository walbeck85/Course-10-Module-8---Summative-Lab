# Import necessary libraries
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
import os

# Get the absolute path of the directory containing this file
basedir = os.path.abspath(os.path.dirname(__file__))

# Create a Flask app instance
app = Flask(__name__)

# Configure the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False  # Makes JSON responses more readable in development

# Set a secret key for JWT (replace with a real, random key in production)
app.config['JWT_SECRET_KEY'] = 'your-super-secret-jwt-key' 

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
api = Api(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
ma = Marshmallow(app)