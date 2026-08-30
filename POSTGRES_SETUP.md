# PostgreSQL Setup for Fyyur

## Configuration Status

✅ **App Configuration** (app.py + config.py)
- Default: PostgreSQL at `postgresql://postgres:postgres@localhost:5432/fyyur`
- Can override with: `SQLALCHEMY_DATABASE_URI` environment variable

✅ **Test Configuration** (tests/conftest.py)
- Tests use SQLite in-memory database (`sqlite:///:memory:`)
- Isolated from production database
- No external dependencies

## Running the App

### Option 1: Local PostgreSQL (Linux/Mac/WSL)

1. **Start PostgreSQL**
   ```bash
   # On Linux (systemctl)
   systemctl start postgresql
   
   # On Mac (brew)
   brew services start postgresql
   ```

2. **Create the database**
   ```bash
   createdb -U postgres fyyur
   ```

3. **Initialize database schema**
   ```bash
   cd /workspace
   python -c "
   from app import app
   from dal import db
   with app.app_context():
       db.create_all()
   "
   ```

4. **Seed sample data**
   ```bash
   python -c "
   from app import app
   from dal import db
   from test_helpers.seed import seed_database
   with app.app_context():
       seed_database()
   "
   ```

5. **Run the app**
   ```bash
   python app.py
   ```
   App available at: http://localhost:5000

### Option 2: Docker Dev Container (Recommended)

1. **Ensure Docker Desktop is running**

2. **In VS Code:**
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P`)
   - Search "Dev Containers: Reopen in Container"
   - Select it

3. **In container terminal:**
   ```bash
   # Initialize database
   python -c "
   from app import app
   from dal import db
   with app.app_context():
       db.create_all()
   "
   
   # Seed data
   python -c "
   from app import app
   from dal import db
   from test_helpers.seed import seed_database
   with app.app_context():
       seed_database()
   "
   
   # Run app
   python app.py
   ```
   App available at: http://localhost:5000

### Option 3: Use Different PostgreSQL Host

```bash
# Point to remote PostgreSQL
export SQLALCHEMY_DATABASE_URI='postgresql://user:password@host:5432/fyyur'
python app.py
```

## Running Tests

Tests automatically use SQLite in-memory database (no PostgreSQL needed):

```bash
# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=. --cov-report=html

# Run specific test file
python -m pytest tests/test_venue_service.py -v
```

## Database Commands

```bash
# Connect to PostgreSQL directly
psql -U postgres -d fyyur

# Reset database (warning: deletes all data)
dropdb -U postgres fyyur
createdb -U postgres fyyur
python -c "
from app import app
from dal import db
with app.app_context():
    db.create_all()
"
```

## Troubleshooting

### "connection refused" error
- PostgreSQL is not running
- Check port 5432: `lsof -i :5432`
- Start PostgreSQL (see Option 1 or 2 above)

### "database 'fyyur' does not exist"
- Create it: `createdb -U postgres fyyur`

### Tests failing with database errors
- Tests use SQLite (not PostgreSQL)
- Should not need external dependencies
- Check if conftest.py has `SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'`
