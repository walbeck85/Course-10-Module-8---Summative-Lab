#!/usr/bin/env python3

# Import app, api, and db from config.py
from server.config import app, api, db

# Import resources
from flask_restful import Resource

# Define a simple test route
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

api.add_resource(HelloWorld, '/')

# This block is essential for running the app directly
if __name__ == '__main__':
    app.run(port=5555, debug=True)