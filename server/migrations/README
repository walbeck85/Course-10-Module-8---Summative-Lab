Got it. Writing a clear, professional README is the most important part of submitting a "from scratch" project. It demonstrates your understanding of the entire workflow.

Based on our work, the lab requirements, and your example, here is a complete `README.md` file. It's written in your preferred methodical tone and specifically addresses every command and potential issue an instructor (Chris) would encounter while grading.

-----

### 1\. 🌿 Branch: `feature/docs`

First, let's create our final branch:

```bash
git checkout -b feature/docs
```

-----

### 2\. 📝 Create `README.md`

Create a new file named `README.md` in the **root** of your project.

Please **replace the entire contents** of this file with the code below.

````markdown
# Summative Lab: Full Auth Flask Backend (Workout Logger)

This repository contains my implementation for the Course 10 Summative Lab. The goal is to build a secure, full-stack ready Flask API from scratch, demonstrating all concepts from Modules 1-4.

This backend API handles user authentication, password protection, and all CRUD operations for a user-owned resource (`Workout`). The implementation uses JSON Web Tokens (JWT) for stateless authentication and includes pagination and ownership-based authorization on all protected routes.

## Core Features

* **Full Authentication:** Secure user signup (`/api/signup`), login (`/api/login`), and session verification (`/api/me`) using **Flask-JWT-Extended**.
* **Password Hashing:** Passwords are never stored in plaintext. All user passwords are hashed using **Flask-Bcrypt**.
* **User-Owned Resource:** A `Workout` model is associated with a `User` model (one-to-many).
* **Full CRUD:** Complete Create, Read, Update, and Delete endpoints for the `Workout` resource.
* **Authorization:** All resource routes are protected. Ownership is enforced on all `PATCH` and `DELETE` routes, preventing users from modifying each other's data (returns `403 Forbidden`).
* **Pagination:** The `GET /api/workouts` endpoint is paginated, accepting `?page` and `?per_page` query parameters.
* **Database Migrations:** The database schema is managed via **Flask-Migrate**.
* **Seeding:** A seed script (`server/seed.py`) is provided to populate the database with sample users and workouts for testing.

## Environment

* Python 3.10
* Pipenv
* Flask, Flask-SQLAlchemy, Flask-Migrate
* Flask-RESTful, Flask-Marshmallow
* Flask-Bcrypt, Flask-JWT-Extended

## Setup

Clone and enter the project directory:

```bash
git clone git@github.com:walbeck85/Course-10-Module-8---Summative-Lab.git
cd Course-10-Module-8---Summative-Lab
````

Install all dependencies using Pipenv:

```bash
pipenv install
```

Activate the virtual environment:

```bash
pipenv shell
```

Set the required environment variables for the shell session. **This is a critical step** for the application to find its modules and connect to the database.

```bash
export FLASK_APP=server/app.py
export PYTHONPATH=$(pwd)
```

Create the database and apply all migrations:

```bash
# Note: The -d flag is required to point to our migrations folder
flask db upgrade -d server/migrations
```

Seed the database with sample users and workouts:

```bash
python server/seed.py
```

## File Structure

```
.
├── .env
├── .gitignore
├── Pipfile
├── Pipfile.lock
├── README.md
└── server
    ├── app.db
    ├── app.py
    ├── config.py
    ├── migrations
    │   ├── alembic.ini
    │   ├── env.py
    │   ├── script.py.mako
    │   └── versions
    │       └── ...migration_file.py
    ├── models.py
    └── seed.py
```

## How to Run the Server

From the project root with the virtual environment (`pipenv shell`) active and environment variables set:

```bash
# Set variables (if not already set in your session)
export FLASK_APP=server/app.py
export PYTHONPATH=$(pwd)

# Run the server on port 5555
flask run --port 5555
```

The API will be live and accessible at `http://127.0.0.1:5555`.

## API Endpoints

All resource endpoints (except auth) are protected and require a valid JWT. Authentication is handled via a `access_token_cookie`.

### Authentication

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/signup` | Creates a new user. Requires `username` and `password`. |
| `POST` | `/api/login` | Authenticates a user and sets an `access_token_cookie`. |
| `GET` | `/api/me` | Returns the currently logged-in user's data. |
| `DELETE`| `/api/logout` | Clears the auth cookie. |

### Workouts

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/workouts` | Returns a **paginated** list of the logged-in user's workouts. <br> *Query Params:* `?page=<int>` & `?per_page=<int>` |
| `POST` | `/api/workouts` | Creates a new workout record for the logged-in user. |
| `PATCH` | `/api/workouts/<int:id>` | Updates a specific workout. **(Owner only)** |
| `DELETE`| `/api/workouts/<int:id>` | Deletes a specific workout. **(Owner only)** |

## How to Test

You can test the API using `curl` or an API client like Postman.

**Example `curl` Test Flow:**

```bash
# 1. Log in as "Chris" (password: "password") and save the cookie
curl -i -X POST -H "Content-Type: application/json" \
     -d '{"username":"Chris", "password":"password"}' \
     -c cookie_jar.txt \
     [http://127.0.0.1:5555/api/login](http://127.0.0.1:5555/api/login)

# 2. Verify login by fetching user data
curl -i -b cookie_jar.txt [http://127.0.0.1:5555/api/me](http://127.0.0.1:5555/api/me)

# 3. Get the first page of Chris's workouts (3 per page)
curl -i -b cookie_jar.txt "[http://127.0.0.1:5555/api/workouts?page=1&per_page=3](http://127.0.0.1:5555/api/workouts?page=1&per_page=3)"

# 4. Create a new workout for Chris
curl -i -X POST -H "Content-Type: application/json" \
     -d '{"title":"Test Run", "duration":20, "date":"2025-11-01"}' \
     -b cookie_jar.txt \
     [http://127.0.0.1:5555/api/workouts](http://127.0.0.1:5555/api/workouts)

# 5. Delete the new workout (e.g., if its ID is 27)
curl -i -X DELETE -b cookie_jar.txt [http://127.0.0.1:5555/api/workouts/27](http://127.0.0.1:5555/api/workouts/27)
```

## Rubric Alignment

  * **Auth (Login / Logout / Signup / Me):** All auth endpoints are implemented at `/api/signup`, `/api/login`, `/api/me`, and `/api/logout`.
  * **Auth (Model and Password):** The `User` model uses `flask-bcrypt` via a `_password_hash` hybrid property and an `authenticate` method.
  * **Resource CRUD and Pagination:** Full CRUD for `/api/workouts` is implemented. The `GET` endpoint is paginated via `?page` and `?per_page` params.
  * **Protected Routes:** All routes besides auth and a root test route are protected. `PATCH` and `DELETE` endpoints perform ownership checks and return `403 Forbidden` if the user is not the owner.
  * **Code Structure:** The project is structured with a `server/` directory and uses a `config.py` file to manage app, db, and extension instances, preventing circular imports.
  * **Seed File:** `server/seed.py` successfully populates the database with 3 users and 5-10 workouts for each.
  * **README:** This file includes all required documentation.
  * **Git Workflow:** All work was completed on feature branches (`feature/setup`, `feature/models`, `feature/auth`, etc.) and merged to `main`.

## Notes on Third-Party Packages

  * **Flask-Bcrypt:** Used for securely hashing user passwords.
  * **Flask-JWT-Extended:** Used for stateless, token-based authentication. Configured to use secure `HttpOnly` cookies (`JWT_TOKEN_LOCATION = ['cookies']`) for token transport.
  * **Flask-Migrate:** Used to manage all database schema changes.
  * **Flask-RESTful:** Used to build class-based, RESTful API resources.
  * **Marshmallow-SQLAlchemy:** Used to serialize and deserialize data, providing validation and clean JSON output.

## Troubleshooting

  * **Error: `ModuleNotFoundError: No module named 'server'`**

      * **Cause:** Python cannot find the local `server` modules.
      * **Fix:** Ensure you have set the `PYTHONPATH` variable in your shell: `export PYTHONPATH=$(pwd)`

  * **Error: `Error: No such command 'db'`**

      * **Cause:** The `flask` command cannot find the `flask-migrate` extensions.
      * **Fix:** Ensure your `pipenv shell` is active and `FLASK_APP` is set. If it persists, exit and re-enter `pipenv shell`.

  * **Error: `Error: Path doesn't exist: migrations`**

      * **Cause:** `flask db` is looking for `migrations/` in the wrong place.
      * **Fix:** You must use the `-d server/migrations` flag with your `flask db` commands: `flask db upgrade -d server/migrations`

## Instructor Checklist

  * Activate `pipenv shell`.
  * Set `FLASK_APP` and `PYTHONPATH` variables.
  * Run `flask db upgrade -d server/migrations`.
  * Run `python server/seed.py`.
  * Run `flask run --port 5555`.
  * Test auth and CRUD endpoints via Postman or `curl`.

<!-- end list -->

````

---