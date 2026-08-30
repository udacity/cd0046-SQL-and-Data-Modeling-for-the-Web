# Dev Container Setup for Fyyur

This project is configured to run in a Docker Dev Container with PostgreSQL.

## Prerequisites

- **Docker Desktop** installed and running
- **VS Code** with the "Dev Containers" extension (`ms-vscode-remote.remote-containers`)

## Getting Started

### 1. Install the Dev Containers Extension
```
VS Code → Extensions → Search "Dev Containers" → Install
```

### 2. Open in Dev Container
1. Open this folder in VS Code
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Search for "Dev Containers: Reopen in Container"
4. Select it

VS Code will:
- Build the Docker image
- Start PostgreSQL container
- Install Python dependencies
- Mount your code for editing

### 3. Initialize the Database

Once the container starts, open the integrated terminal and run:

```powershell
# Initialize Flask-Migrate (only needed once)
flask db init

# Create initial migration from models
flask db migrate -m "Initial models"

# Apply migration to database
flask db upgrade
```

### 4. Run the App

```powershell
python app.py
```

The app will be available at: **http://localhost:5000**

## Useful Commands

```powershell
# Run the Flask development server
python app.py

# Create a new migration after changing models
flask db migrate -m "Your migration message"

# Apply pending migrations
flask db upgrade

# Rollback last migration
flask db downgrade

# Connect to PostgreSQL directly
psql -h postgres -U postgres -d fyyur

# View PostgreSQL logs
docker-compose -f .devcontainer/docker-compose.yml logs postgres

# Reset everything (warning: deletes database)
docker-compose -f .devcontainer/docker-compose.yml down -v
docker-compose -f .devcontainer/docker-compose.yml up
```

## Database Access

- **Host:** `postgres` (within container) or `localhost` (from host machine)
- **Port:** `5432`
- **User:** `postgres`
- **Password:** `postgres`
- **Database:** `fyyur`

**Connection String (inside container):**
```
postgresql://postgres:postgres@postgres:5432/fyyur
```

**Connection String (from host machine):**
```
postgresql://postgres:postgres@localhost:5432/fyyur
```

## Troubleshooting

### Container won't start
- Make sure Docker Desktop is running
- Check Docker logs: `docker-compose logs`
- Rebuild: `docker-compose down && docker-compose up --build`

### PostgreSQL connection refused
- Wait 10-15 seconds after container starts (PostgreSQL needs time to start)
- Check PostgreSQL logs: `docker-compose logs postgres`
- Ensure `depends_on` in docker-compose.yml includes healthcheck

### Changes to code not reflected
- Code is mounted via volume, so changes should be instant
- Restart Flask: `Ctrl+C` then `python app.py` again

### Want to exit dev container
- Press `Ctrl+Shift+P` → "Dev Containers: Reopen Folder Locally"

## Environment Variables

The dev container automatically sets:
- `SQLALCHEMY_DATABASE_URI=postgresql://postgres:postgres@postgres:5432/fyyur`
- `FLASK_APP=app.py`
- `FLASK_ENV=development`

For local development outside the container, update these in a `.env` file or your system environment.

## Pushing to Production

When submitting this project:
1. The grader will have their own PostgreSQL setup
2. They'll use `config.py` to set `SQLALCHEMY_DATABASE_URI`
3. Docker is just for your development convenience
4. Make sure code works with standard Flask + PostgreSQL setup too
