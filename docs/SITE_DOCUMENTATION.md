# Site Documentation: Fyyur Architecture & Technology

Comprehensive technical documentation for the Fyyur venue and artist booking platform.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Database Schema](#database-schema)
5. [Key Components](#key-components)
6. [API Endpoints](#api-endpoints)
7. [Development Workflow](#development-workflow)
8. [Deployment Considerations](#deployment-considerations)

---

## Project Overview

**Fyyur** is a web application that facilitates connections between musicians (artists) and performance venues. The platform enables:

- **Artists** to showcase their work, manage availability, and discover booking opportunities
- **Venues** to find talented performers and manage their event calendar
- **Shows** to be tracked, organized, and categorized by date

### Core Features

- Artist and Venue profile management
- Album and Song organization (artist discography)
- Show booking and scheduling
- Availability management with recurring schedules and exceptions
- Genre-based discovery and filtering
- Search capabilities across all entities
- Cascading data deletion for data integrity

---

## Technology Stack

### Backend
- **Framework**: Flask (Python web framework)
- **Database ORM**: SQLAlchemy
- **Database**: 
  - SQLite (development/testing)
  - PostgreSQL (production)
- **Forms**: WTForms with CSRF protection
- **Testing**: pytest with coverage reporting

### Frontend
- **Template Engine**: Jinja2
- **Styling**: Bootstrap CSS framework
- **JavaScript**: Minimal JavaScript, mostly HTML forms

### Development Tools
- **Package Manager**: pip
- **Environment**: Python 3.10+
- **Version Control**: Git
- **Container**: Docker (optional, via dev container)

---

## Project Structure

```
fyyur/
├── app.py                    # Flask application factory & initialization
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── Makefile                  # Development commands
│
├── controllers/              # Flask route handlers (blueprints)
│   ├── __init__.py
│   ├── main.py              # Home page routes
│   ├── artist.py            # Artist routes (/artists/*)
│   ├── venue.py             # Venue routes (/venues/*)
│   ├── album.py             # Album routes (/albums/*)
│   ├── song.py              # Song routes (/songs/*)
│   └── show.py              # Show routes (/shows/*)
│
├── services/                 # Business logic layer
│   ├── __init__.py
│   ├── common.py            # Shared utilities
│   ├── artist.py            # Artist business logic
│   ├── venue.py             # Venue business logic
│   ├── album.py             # Album business logic
│   ├── song.py              # Song business logic
│   ├── show.py              # Show business logic
│   └── availability.py      # Availability scheduling logic
│
├── dal/                      # Data Access Layer (Models)
│   ├── __init__.py          # Database initialization
│   ├── artist.py            # Artist model
│   ├── venue.py             # Venue model
│   ├── album.py             # Album model
│   ├── song.py              # Song model
│   ├── show.py              # Show model
│   ├── genre.py             # Genre model
│   └── availability.py      # Availability models
│
├── dto/                      # Data Transfer Objects
│   ├── __init__.py
│   ├── artist.py            # Artist DTO
│   ├── venue.py             # Venue DTO
│   ├── album.py             # Album DTO
│   └── show.py              # Show DTO
│
├── forms.py                  # WTForms form definitions
├── forms_constants.py        # Form choices (states, genres)
├── logging_config.py         # Logging configuration
│
├── templates/               # Jinja2 HTML templates
│   ├── layouts/
│   │   └── main.html        # Base layout
│   └── pages/
│       ├── index.html       # Home page
│       ├── artists.html     # Artists list
│       ├── venues.html      # Venues list
│       ├── shows.html       # Shows list
│       ├── albums.html      # Albums list
│       └── [entity]/        # Detail and form pages
│
├── static/                  # Static assets
│   ├── css/                 # Stylesheets
│   ├── js/                  # JavaScript files
│   └── ico/                 # Icons & favicons
│
├── tests/                   # Test suite
│   ├── conftest.py          # pytest configuration & fixtures
│   ├── test_models.py       # Database model tests
│   ├── test_routes.py       # Route/endpoint tests
│   ├── test_*_service.py    # Service layer tests
│   └── test_*.py            # Other tests
│
├── migrations/              # Database migrations (Flask-Migrate)
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│
├── docs/                    # Documentation
│   ├── MANUAL_TESTING_GUIDE.md
│   ├── BUSINESS_DECISIONS.md
│   └── HOW_TO_GUIDE.md
│
├── README.md                # Project overview
└── DEVCONTAINER.md          # Development environment setup
```

---

## Database Schema

### Core Tables

#### `artist`
- `id` (Primary Key)
- `name` (String, NOT NULL)
- `city` (String, NOT NULL)
- `state` (String, NOT NULL)
- `phone` (String)
- `website` (String)
- `facebook_link` (String)
- `image_link` (String)
- `seeking_venue` (Boolean, default: False)
- `seeking_description` (String)
- `created_at` (DateTime)
- Relationships: albums, shows, availability

#### `venue`
- `id` (Primary Key)
- `name` (String, NOT NULL)
- `address` (String, NOT NULL)
- `city` (String, NOT NULL)
- `state` (String, NOT NULL)
- `phone` (String)
- `website` (String)
- `facebook_link` (String)
- `image_link` (String)
- `seeking_talent` (Boolean, default: False)
- `seeking_description` (String)
- `created_at` (DateTime)
- Relationships: shows, genres

#### `album`
- `id` (Primary Key)
- `artist_id` (Foreign Key → artist, ON DELETE CASCADE)
- `title` (String, NOT NULL)
- `release_date` (Date)
- `description` (String)
- `image_link` (String)
- `spotify_link` (String)
- `created_at` (DateTime)
- Relationships: songs, artist

#### `song`
- `id` (Primary Key)
- `album_id` (Foreign Key → album, ON DELETE CASCADE)
- `title` (String, NOT NULL)
- `duration` (Integer) # Duration in seconds
- `spotify_link` (String)
- `created_at` (DateTime)
- Relationships: album

#### `show`
- `id` (Primary Key)
- `artist_id` (Foreign Key → artist)
- `venue_id` (Foreign Key → venue)
- `start_time` (DateTime, NOT NULL)
- `created_at` (DateTime)
- Relationships: artist, venue

#### `genre`
- `id` (Primary Key)
- `name` (String, UNIQUE, NOT NULL)

#### Association Tables
- `artist_genre` (artist_id, genre_id)
- `venue_genre` (venue_id, genre_id)

#### Availability Tables
- `artist_availability` (recurring time slots)
- `artist_availability_exception` (exceptions to recurring availability)

### Relationships Summary

```
Artist (1) ──→ (N) Album ──→ (N) Song
Artist (1) ──→ (N) Show (N←) Venue
Artist (N) ←──→ (N) Genre
Venue (N) ←──→ (N) Genre
```

---

## Key Components

### 1. Controllers (Route Handlers)

Controllers handle HTTP requests and responses. Each entity has its own blueprint:

**Example: Artist Routes**
- `GET /artists/` - List all artists
- `POST /artists/create` - Create artist form submission
- `GET /artists/<id>` - View artist details
- `POST /artists/<id>/edit` - Update artist
- `POST /artists/<id>/delete` - Delete artist
- `POST /artists/search` - Search artists

### 2. Services (Business Logic)

Services contain the core business logic, separate from HTTP handling:

```python
# Example: ArtistService
- get_all_artists()
- get_artist_by_id(artist_id)
- search_artist_by_name(search_term)
- create_artist(artist_data)
- update_artist(artist_id, artist_data)
- delete_artist(artist_id)
```

**Benefits**:
- Reusable across multiple interfaces (web, API, CLI)
- Testable without HTTP mocking
- Centralized error handling
- Clear business logic flow

### 3. Data Access Layer (Models)

SQLAlchemy ORM models represent database tables:

```python
class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    albums = db.relationship('Album', backref='artist', cascade='all, delete-orphan')
    genres = db.relationship('Genre', secondary='artist_genre', backref='artists')
```

**Key Features**:
- Cascade deletes for referential integrity
- Relationships defined for easy navigation
- Backrefs for reverse relationships
- Query methods for common operations

### 4. Data Transfer Objects (DTOs)

DTOs provide a clean interface between services and controllers:

```python
class ArtistDTO:
    id: Optional[int]
    name: str
    city: str
    state: str
    phone: str
    genres: List[str]
    upcoming_shows: List[ShowDTO]
    past_shows: List[ShowDTO]
```

**Benefits**:
- Decouples internal models from API/form data
- Explicit data contracts
- Easy to add computed fields

### 5. Forms (WTForms)

Forms handle HTML form parsing and validation:

```python
class ArtistForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    phone = StringField('Phone')
    seeking_venue = BooleanField('Seeking Venues?')
    csrf_token = HiddenField()
```

**Features**:
- Server-side validation
- CSRF token generation
- Error message generation
- Type conversion

---

## API Endpoints

### Artists
```
GET    /artists              - List all artists
GET    /artists/create       - Show create form
POST   /artists/create       - Create new artist
GET    /artists/<id>         - Show artist details
GET    /artists/<id>/edit    - Show edit form
POST   /artists/<id>/edit    - Update artist
POST   /artists/<id>/delete  - Delete artist
POST   /artists/search       - Search artists
POST   /artists/<id>/availability - Show availability management
POST   /artists/<id>/availability/new - Create availability slot
```

### Venues
```
GET    /venues               - List all venues
GET    /venues/create        - Show create form
POST   /venues/create        - Create new venue
GET    /venues/<id>          - Show venue details
GET    /venues/<id>/edit     - Show edit form
POST   /venues/<id>/edit     - Update venue
POST   /venues/<id>/delete   - Delete venue
POST   /venues/search        - Search venues
```

### Albums
```
GET    /albums               - List all albums
GET    /albums/create        - Show create form
POST   /albums/create        - Create new album
GET    /albums/<id>          - Show album details
GET    /albums/<id>/edit     - Show edit form
POST   /albums/<id>/edit     - Update album
POST   /albums/<id>/delete   - Delete album
```

### Songs
```
GET    /songs/create         - Show create form
POST   /songs/create         - Create new song
GET    /songs/<id>/edit      - Show edit form
POST   /songs/<id>/edit      - Update song
POST   /songs/<id>/delete    - Delete song
```

### Shows
```
GET    /shows                - List all shows
GET    /shows/create         - Show create form
POST   /shows/create         - Create new show
POST   /shows/search         - Search shows
POST   /shows/<id>/delete    - Delete show
```

---

## Development Workflow

### Setting Up Development Environment

```bash
# 1. Clone repository
git clone <repository>
cd fyyur

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
make db-init

# 5. (Optional) Seed with sample data
make db-seed

# 6. Start development server
make run
```

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Write tests first** (TDD approach)
   ```bash
   # Add test in tests/test_*.py
   make test  # Run to verify it fails initially
   ```

3. **Implement feature**
   - Add service logic in `services/`
   - Add route handler in `controllers/`
   - Add form validation in `forms.py`
   - Update template as needed

4. **Verify tests pass**
   ```bash
   make test       # Unit/integration tests
   make test-cov   # With coverage report
   ```

5. **Run linter**
   ```bash
   make lint
   ```

6. **Commit and push**
   ```bash
   git add .
   git commit -m "Feature: Add new feature"
   git push origin feature/new-feature
   ```

### Testing Strategy

**Unit Tests**: Test individual functions/methods in isolation
- Located in `tests/test_*_service.py`
- Mock external dependencies
- Fast execution

**Integration Tests**: Test components working together
- Located in `tests/test_routes.py`, `tests/test_models.py`
- Use real database (SQLite in-memory)
- Test full request/response cycle

**Test Execution**:
```bash
make test           # Run all tests
make test-cov       # With coverage report
pytest tests/test_models.py  # Specific file
pytest -k artist    # Specific test pattern
```

---

## Deployment Considerations

### Production Setup

1. **Database**
   - Use PostgreSQL (not SQLite)
   - Set `DATABASE_URL` environment variable
   - Run migrations: `flask db upgrade`

2. **Environment Variables**
   ```
   FLASK_ENV=production
   SQLALCHEMY_DATABASE_URI=postgresql://user:pass@host/dbname
   SECRET_KEY=<strong-random-key>
   ```

3. **Web Server**
   - Use production WSGI server (Gunicorn, uWSGI)
   - Not Flask development server
   - Example: `gunicorn -w 4 app:app`

4. **Security**
   - Enable HTTPS/SSL
   - Set secure SECRET_KEY
   - Enable CSRF protection (already configured)
   - Validate all user input

5. **Logging**
   - Configure production logging level
   - Log to files or centralized service
   - Monitor error rates

6. **Performance**
   - Use database connection pooling
   - Enable query result caching if needed
   - Optimize N+1 queries (use eager loading)
   - Consider CDN for static assets

### Scaling Strategies

**Immediate (100s-1000s of users)**
- Single PostgreSQL database
- Single application server
- Static files served by app

**Medium Scale (1000s-10000s)**
- Database: Primary + read replicas
- Load balancer with multiple app servers
- Separate CDN for static assets
- Redis for session/cache (if needed)

**Large Scale (10000s+)**
- Microservices architecture
- Database sharding
- Message queue for async jobs
- Search engine (Elasticsearch) for complex queries
- Rate limiting and API throttling

### Monitoring

Track these metrics in production:
- Request latency (p50, p95, p99)
- Error rates by endpoint
- Database query performance
- Resource usage (CPU, memory, disk)
- User activity trends

---

## Troubleshooting Common Issues

### Database Connection Errors

**Problem**: `psycopg2.OperationalError: could not connect to server`

**Solution**:
- Check PostgreSQL is running
- Verify `DATABASE_URL` is correct
- Check credentials and permissions
- Verify network connectivity

### Form Validation Failures

**Problem**: Form doesn't submit with validation error

**Solution**:
- Check error message displayed below field
- Verify all required fields filled
- Check field format (URL must start with http://)
- Look at form definition in `forms.py` for validation rules

### Missing Data After Delete

**Problem**: Deleted parent record, child records still exist

**Solution**: This is expected behavior change. Cascade deletes are now enabled. Verify in database:
```sql
SELECT * FROM album WHERE artist_id = <deleted_id>;  -- Should be empty
```

### Test Database Errors

**Problem**: Tests failing with "Test database is not SQLite!"

**Solution**:
```bash
# Ensure test database environment variable
export SQLALCHEMY_DATABASE_URI='sqlite:///:memory:'
make test
```

---

## Contributing Guidelines

1. Follow existing code style and patterns
2. Write tests for new features
3. Update documentation as needed
4. Keep commits focused and descriptive
5. Run full test suite before submitting
6. Update CHANGELOG.md for significant changes

---

## Additional Resources

- Flask Documentation: https://flask.palletsprojects.com/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- WTForms Documentation: https://wtforms.readthedocs.io/
- PostgreSQL Documentation: https://www.postgresql.org/docs/

