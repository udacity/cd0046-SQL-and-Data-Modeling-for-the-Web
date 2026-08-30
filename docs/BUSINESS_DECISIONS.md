# Business Decisions & Design Documentation

This document outlines key architectural and business decisions made for the Fyyur platform.

## Overview

Fyyur is a venue and artist booking platform that connects musicians (artists) with performance venues. The application enables:
- Artists to manage their profiles, availability, and performances
- Venues to discover and book artists
- Shows to be managed and categorized by date

---

## Core Business Entities

### 1. Artists
**Purpose**: Represent musicians and performers

**Key Attributes**:
- Name, Location (City, State)
- Contact Information (Phone, Website, Facebook)
- Image
- Seeking Status (actively seeking venues or not)
- Genres
- Availability Scheduling

**Business Logic**:
- Artists control their own profiles
- Can set availability (time slots when they can perform)
- Can manage exceptions to availability
- Each artist can have multiple albums and songs
- Deletion cascades to associated albums and songs

### 2. Venues
**Purpose**: Represent performance locations

**Key Attributes**:
- Name, Address, Location (City, State)
- Contact Information (Phone, Website, Facebook)
- Image
- Seeking Status (looking for talent or not)
- Genres (music styles they feature)

**Business Logic**:
- Venues manage their profiles independently
- Can specify genres they typically host
- Can book artists for specific dates/times
- Deletion cascades to associated shows

### 3. Albums
**Purpose**: Organize songs and music by collection

**Key Attributes**:
- Title, Release Date
- Description
- Image/Cover Art
- Spotify Link
- Artist Reference

**Business Logic**:
- Albums belong to exactly one artist
- Can contain multiple songs
- Represent a body of work
- Deletion cascades to associated songs

### 4. Songs
**Purpose**: Individual tracks within albums

**Key Attributes**:
- Title
- Duration (in seconds)
- Spotify Link
- Album Reference

**Business Logic**:
- Songs belong to exactly one album
- Duration tracked for show/performance planning
- Can be edited independently

### 5. Shows
**Purpose**: Represent scheduled performances

**Key Attributes**:
- Artist ID (performer)
- Venue ID (location)
- Start Time (date and time)

**Business Logic**:
- Link artists with venues for specific dates
- Automatically categorized as "Upcoming" or "Past" based on current date
- Used for availability checking and scheduling

---

## Database Architecture Decisions

### 1. SQLite for Development
**Decision**: Use SQLite in-memory database for testing

**Rationale**:
- Fast, isolated test execution
- No external service dependencies
- Safe (never connects to production database)
- Easy to reset between tests

### 2. PostgreSQL for Production
**Decision**: Production database uses PostgreSQL

**Rationale**:
- Robust for concurrent connections
- Better scaling than SQLite
- Supports complex queries
- Production-ready reliability

### 3. Cascade Deletes
**Decision**: Use database cascade deletes for referential integrity

**Rationale**:
- Prevents orphaned records
- Ensures data consistency
- Simplifies delete operations
- Clear semantic meaning: deleting an artist removes their albums and songs

### 4. Availability Scheduling
**Decision**: Separate availability table for recurring time slots

**Rationale**:
- Artists have regular schedules (e.g., "Available Thursdays 7pm-11pm")
- Availability exceptions (e.g., "Unavailable Dec 25")
- Decouples recurring patterns from one-off shows
- Enables efficient availability lookups

---

## API & Form Design Decisions

### 1. Flask Blueprint Organization
**Decision**: Organize routes by entity (artists.py, venues.py, albums.py, shows.py, songs.py)

**Rationale**:
- Clear separation of concerns
- Easy to locate related routes
- Scalable for large applications
- Follows Flask best practices

### 2. Service Layer Pattern
**Decision**: Implement business logic in separate service layer

**Rationale**:
- Separation of concerns (routes vs. business logic)
- Testable business logic independent of HTTP layer
- Reusable across different interfaces (API, CLI, etc.)
- Centralized error handling

### 3. Form Validation
**Decision**: Use WTForms for server-side validation

**Rationale**:
- Protection against invalid/malicious input
- Consistent validation across all forms
- CSRF protection included
- User feedback on errors

### 4. Search Capabilities
**Decision**: Support multi-criteria search (name, location, genre)

**Rationale**:
- Artists need to find venues by location
- Venues need to find artists by genre preferences
- Users want flexible filtering options

---

## Data Integrity Decisions

### 1. Genre Many-to-Many Relationships
**Decision**: Artists and Venues both can have multiple genres

**Rationale**:
- Artists perform multiple genres
- Venues host multiple genre styles
- Improves searchability and matching

### 2. Soft Delete vs. Hard Delete
**Decision**: Implement hard deletes with cascade

**Rationale**:
- Simpler data model
- Reduced storage requirements
- Clear delete semantics
- Audit trail handled separately if needed

### 3. Timezone Handling
**Decision**: Store times in application timezone, display in local format

**Rationale**:
- Consistent database representation
- Avoids timezone confusion in stored data
- Template formatting handles display

---

## Testing Strategy Decisions

### 1. Automated Unit & Integration Tests
**Decision**: Use pytest for backend testing

**Rationale**:
- Comprehensive coverage of business logic
- Fast execution (274 tests run in ~14 seconds)
- Fixtures for test data setup
- Prevents regressions

### 2. Manual Testing for UI
**Decision**: Manual browser testing for user interface

**Rationale**:
- UX validation requires human judgment
- Easier to spot UI issues manually
- Cost-effective for small team
- Provides real-world testing scenarios

### 3. No Automated Browser Tests in Container
**Decision**: Skip browser E2E tests in containerized environment

**Rationale**:
- Container lacks graphical display (no X11)
- Missing system libraries for Chromium
- Browser tests better run on local developer machines
- Manual testing provides adequate coverage for this scale

---

## Security Decisions

### 1. CSRF Protection
**Decision**: Enable CSRF protection on all forms

**Rationale**:
- Prevents cross-site request forgery attacks
- Enabled by WTForms by default
- No performance impact

### 2. SQL Injection Prevention
**Decision**: Use SQLAlchemy ORM for all database operations

**Rationale**:
- Parameterized queries prevent SQL injection
- No raw SQL strings in application code
- Better for maintainability

### 3. Input Validation
**Decision**: Validate all user input on server side

**Rationale**:
- Client-side validation can be bypassed
- Consistent validation regardless of client
- Protection against malicious input

---

## Scalability Decisions

### 1. Service Layer Abstraction
**Decision**: Business logic separated from routes

**Rationale**:
- Enables future API layer (REST API, GraphQL, etc.)
- Allows caching at service layer if needed
- Supports batch operations

### 2. Database Query Optimization
**Decision**: Use eager loading for related data to avoid N+1 queries

**Rationale**:
- Improves performance with large datasets
- Reduces database round trips
- Essential for shows listing with venue/artist details

### 3. Pagination Consideration
**Decision**: Not implemented initially (appropriate for small scale)

**Rationale**:
- Simpler user experience for small result sets
- Can be added if dataset grows significantly
- Bootstrap UI can handle reasonable list sizes

---

## Feature Decisions

### 1. Availability Management
**Decision**: Artist-centric availability scheduling

**Rationale**:
- Artists control their own schedules
- Flexible recurring patterns with exceptions
- Enables smart show booking

### 2. Show Search
**Decision**: Search shows by artist or venue

**Rationale**:
- Users want to see shows for specific artist/venue
- Simpler than complex date range searches initially
- Can be enhanced later

### 3. Genre Classification
**Decision**: Fixed set of predefined genres

**Rationale**:
- Consistent categorization
- Easier searching and filtering
- Can be extended as business grows

---

## Future Enhancement Opportunities

1. **Artist-to-Artist Collaborations**: Multiple artists per show
2. **Show Reviews & Ratings**: Feedback after performances
3. **Payment Integration**: Commission tracking, artist payments
4. **Admin Dashboard**: Overview of platform activity
5. **Automated Availability Suggestions**: ML-based show recommendations
6. **Mobile App**: iOS/Android companion apps
7. **Real-time Notifications**: New bookings, availability changes
8. **Analytics**: Performance tracking, booking trends
9. **Multi-currency Support**: International artists/venues
10. **Venue Capacity Management**: Track attendee limits

---

## Success Metrics

The application successfully serves its purpose when:
1. Artists can easily manage profiles and availability
2. Venues can discover and book artists efficiently
3. Shows are properly tracked and categorized
4. Data remains consistent (cascade deletes work properly)
5. Search functions find relevant results
6. Users receive clear feedback on actions
7. The system performs well with reasonable data volumes

---

## Version History

- **v1.0** (Current): Core artist/venue/show management with availability scheduling
- **v0.1**: Initial project setup and database schema
