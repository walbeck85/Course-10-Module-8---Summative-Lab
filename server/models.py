# Import db, ma, and bcrypt from config.py
from server.config import db, ma, bcrypt 

# Import SQLAlchemy extras
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property

# Import the schema base class
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    _password_hash = db.Column(db.String, nullable=False)
    
    # 1-to-Many relationship: A User has many Workouts
    # cascade="all, delete-orphan": If a User is deleted, their Workouts are deleted too.
    workouts = db.relationship('Workout', back_populates='user', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.username}>'

    @hybrid_property
    def password_hash(self):
        # This getter blocks reading the hash
        raise AttributeError('Password hashes may not be viewed.')

    @password_hash.setter
    def password_hash(self, password):
        # This setter hashes the password on assignment
        password_hash = bcrypt.generate_password_hash(password.encode('utf-8'))
        self._password_hash = password_hash.decode('utf-8')

    def authenticate(self, password):
        # This method checks the password against the stored hash
        return bcrypt.check_password_hash(self._password_hash, password.encode('utf-8'))

    @validates('username')
    def validate_username(self, key, username):
        if not username:
            raise ValueError("Username is required")
        if len(username) < 4:
            raise ValueError("Username must be at least 4 characters long")
        return username

class Workout(db.Model):
    __tablename__ = 'workouts'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    duration = db.Column(db.Integer) # Duration in minutes
    date = db.Column(db.Date)
    
    # Foreign key to link to the User
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Many-to-1 relationship: A Workout belongs to a User
    user = db.relationship('User', back_populates='workouts')

    def __repr__(self):
        return f'<Workout {self.id}: {self.title}>'

    @validates('title')
    def validate_title(self, key, title):
        if not title:
            raise ValueError("Workout title is required")
        return title

    @validates('duration')
    def validate_duration(self, key, duration):
        if duration is not None and duration <= 0:
            raise ValueError("Duration must be a positive number")
        return duration

# --- Schemas ---

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        # We tell Marshmallow to *exclude* the password hash when serializing
        load_dump_defaults = True
        load_instance = True
        exclude = ('_password_hash',) 
        
    # We only want to dump (serialize) workouts, not load (deserialize) them
    # when working with a User object.
    workouts = ma.Nested('WorkoutSchema', many=True, exclude=('user',))

class WorkoutSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Workout
        load_dump_defaults = True
        load_instance = True
        
    # Include the user data when dumping a workout, but only basic info
    user = ma.Nested(UserSchema(only=("id", "username")),)

# Instantiate our schemas
user_schema = UserSchema()
users_schema = UserSchema(many=True)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)