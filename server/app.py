#!/usr/bin/env python3

# Import app, api, db, bcrypt, and jwt from config.py
from server.config import app, api, db, bcrypt, jwt

# Import models and schemas
from server.models import User, Workout, user_schema, workout_schema

# Import auth and error handling tools
from flask_restful import Resource
from flask import request, make_response, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, verify_jwt_in_request
from sqlalchemy.exc import IntegrityError
import traceback # Used for debugging

# --- Authentication Routes ---

class Signup(Resource):
    def post(self):
        data = request.get_json()
        
        # --- FIX IS HERE ---
        # 1. Pop the password out of the data before loading
        password = data.pop('password', None)
        if not password:
             return make_response(jsonify({"error": "Password is required"}), 422)
        # -------------------

        # Validate username
        try:
            # 2. Load the remaining data (just username)
            new_user = user_schema.load(data, session=db.session)
            
            # 3. Set the password hash
            new_user.password_hash = password
            
            db.session.add(new_user)
            db.session.commit()

            # Create an access token for the new user
            access_token = create_access_token(identity=str(new_user.id))
            
            response = make_response(
                jsonify(user_schema.dump(new_user)),
                201
            )
            response.set_cookie('access_token_cookie', access_token, httponly=True, samesite='Lax')
            return response

        except IntegrityError as e:
            db.session.rollback()
            return make_response(jsonify({"error": "Username already exists"}), 409) # 409 Conflict
        except ValueError as e:
            db.session.rollback()
            return make_response(jsonify({"errors": [str(e)]}), 422) # 422 Unprocessable Entity
        except Exception as e:
            db.session.rollback()
            traceback.print_exc() # Print detailed error to console
            return make_response(jsonify({"error": f"An unknown error occurred: {str(e)}"}), 500)

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return make_response(jsonify({"error": "Username and password are required"}), 400)

        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            # Create and set the access token
            access_token = create_access_token(identity=str(user.id))
            
            response = make_response(
                jsonify(user_schema.dump(user)),
                200
            )
            response.set_cookie('access_token_cookie', access_token, httponly=True, samesite='Lax')
            return response
        
        return make_response(jsonify({"error": "Invalid username or password"}), 401) # 401 Unauthorized

class Me(Resource):
    @jwt_required() # This decorator protects the route
    def get(self):
        # Get the user ID from the JWT
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user:
            return make_response(jsonify(user_schema.dump(user)), 200)
        
        return make_response(jsonify({"error": "User not found"}), 404)

class Logout(Resource):
    def delete(self):
        # JWT logout is handled client-side by deleting the token.
        # This endpoint is for session-based auth, but we can clear the cookie.
        response = make_response(jsonify({"message": "Logout successful"}), 200)
        response.delete_cookie('access_token_cookie')
        return response

# --- Authorization Hook ---

# This hook will run before every request
@app.before_request
def check_if_logged_in():
    # Define a list of endpoints that do NOT require authentication
    open_routes = [
        'login',
        'signup',
        'helloworld' # We'll remove this later
    ]
    
    # If the request endpoint is not in our "open" list,
    # we must verify that a valid JWT is present.
    if request.endpoint not in open_routes:
        try:
            # This function checks for a valid JWT in the cookies or headers
            verify_jwt_in_request()
        except Exception as e:
            # This will catch missing tokens, expired tokens, etc.
            return make_response(jsonify({"error": f"Authorization required: {str(e)}"}), 401)


# --- API Resource Routing ---

# A simple test route (we'll remove this later)
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/', endpoint='helloworld')
api.add_resource(Signup, '/api/signup', endpoint='signup')
api.add_resource(Login, '/api/login', endpoint='login')
api.add_resource(Me, '/api/me', endpoint='me')
api.add_resource(Logout, '/api/logout', endpoint='logout')

# This block is essential for running the app directly
if __name__ == '__main__':
    app.run(port=5555, debug=True)