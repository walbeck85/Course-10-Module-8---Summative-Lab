#!/usr/bin/env python3

# Import app, api, db, bcrypt, and jwt from config.py
from server.config import app, api, db, bcrypt, jwt

# Import models and schemas
from server.models import User, Workout, user_schema, workout_schema, workouts_schema

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
        
        # 1. Pop the password out of the data before loading
        password = data.pop('password', None)
        if not password:
             return make_response(jsonify({"error": "Password is required"}), 422)

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

# --- Workout Routes ---
    
class WorkoutsList(Resource):
    @jwt_required()
    def get(self):
        # Get pagination args, default to page 1, 5 items per page
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        
        # Get the user ID from the JWT
        current_user_id = get_jwt_identity()
        
        # Query and paginate workouts *only for the current user*
        workouts = Workout.query.filter_by(user_id=current_user_id).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Format the response with pagination metadata
        response_data = {
            "page": workouts.page,
            "per_page": workouts.per_page,
            "total": workouts.total,
            "total_pages": workouts.pages,
            "items": workouts_schema.dump(workouts.items)
        }
        
        return make_response(jsonify(response_data), 200)

    @jwt_required()
    def post(self):
        current_user_id = get_jwt_identity()
        data = request.get_json()

        try:
            # Load and validate the workout data
            new_workout = workout_schema.load(data, session=db.session)
            
            # Assign the workout to the logged-in user
            new_workout.user_id = current_user_id
            
            db.session.add(new_workout)
            db.session.commit()
            
            return make_response(workout_schema.dump(new_workout), 201)

        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"errors": [str(e)]}), 422)

class WorkoutById(Resource):
    @jwt_required()
    def patch(self, id):
        current_user_id = int(get_jwt_identity())
        
        workout = Workout.query.get(id)
        
        if not workout:
            return make_response(jsonify({"error": "Workout not found"}), 404)
        
        # --- OWNERSHIP CHECK ---
        if workout.user_id != current_user_id:
            return make_response(jsonify({"error": "Forbidden: You do not own this workout"}), 403)
        
        data = request.get_json()
        
        try:
            # Update the workout with new data
            workout_schema.load(data, instance=workout, partial=True, session=db.session)
            db.session.commit()
            
            return make_response(workout_schema.dump(workout), 200)

        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"errors": [str(e)]}), 422)

    @jwt_required()
    def delete(self, id):
        current_user_id = int(get_jwt_identity())
        
        workout = Workout.query.get(id)
        
        if not workout:
            return make_response(jsonify({"error": "Workout not found"}), 404)
        
        # --- OWNERSHIP CHECK ---
        if workout.user_id != current_user_id:
            return make_response(jsonify({"error": "Forbidden: You do not own this workout"}), 403)
            
        try:
            db.session.delete(workout)
            db.session.commit()
            
            return make_response({}, 204) # 204 No Content

        except Exception as e:
            db.session.rollback()
            return make_response(jsonify({"error": str(e)}), 500)

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

# Add the new workout routes
api.add_resource(WorkoutsList, '/api/workouts', endpoint='workouts')
api.add_resource(WorkoutById, '/api/workouts/<int:id>', endpoint='workout_by_id')

# This block is essential for running the app directly
if __name__ == '__main__':
    app.run(port=5555, debug=True)