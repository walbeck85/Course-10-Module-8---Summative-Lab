#!/usr/bin/env python3

# Import necessary tools
from faker import Faker
from random import choice as rc, randint
from datetime import datetime

# Import from config and models
from server.config import app, db
from server.models import User, Workout

# Initialize Faker (we'll still use it for dates)
fake = Faker()

def seed_database():
    print("Seeding database...")

    # Clear existing data
    Workout.query.delete()
    User.query.delete()
    db.session.commit()

    # --- Create Users ---
    # Use the specific list of usernames provided
    user_names_list = ["Chris", "Mathias", "Will"]
    users = []

    for name in user_names_list:
        user = User(username=name)
        # Use the password_hash setter to hash 'password'
        user.password_hash = 'password' 
        users.append(user)

    db.session.add_all(users)
    db.session.commit()
    print("Users seeded.")

    # --- Create Workouts ---
    workouts = []
    # Use the specific list of workout titles provided
    workout_titles = [
        'Bench Press', 'Bicep Curl', 'Lat Row', 'Lunge', 'Squat', 
        'Tricep Extension', 'Crunch', 'Plank', 'Leg Extension', 'Deadlift'
    ]

    for user in users:
        # Create 5 to 10 workouts per user
        for _ in range(randint(5, 10)):
            workout = Workout(
                title=rc(workout_titles),
                duration=randint(30, 90), # Duration between 30 and 90 minutes
                date=fake.date_between(start_date='-1y', end_date='today'), # Workouts from the past year
                user_id=user.id
            )
            workouts.append(workout)

    db.session.add_all(workouts)
    db.session.commit()
    print("Workouts seeded.")
    print("Database seeding complete.")

if __name__ == '__main__':
    # We must wrap our seed call in the app context
    with app.app_context():
        seed_database()