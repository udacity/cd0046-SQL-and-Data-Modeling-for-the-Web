# Manual Testing Guide for Fyyur

This guide provides step-by-step instructions for manually testing all features of the Fyyur application. Follow these procedures to ensure the application works correctly.

## Prerequisites

- Flask application running: `make run`
- Open browser to `http://localhost:5000`

---

## 1. Artist Management Testing

### 1.1 Create an Artist
1. Navigate to "Artists" → "Create Artist" (or direct URL: `/artists/create`)
2. Fill in the following fields:
   - **Name**: "Test Artist Name"
   - **City**: "San Francisco"
   - **State**: "CA"
   - **Phone**: "404-555-0123"
   - **Website**: "https://testartist.com"
   - **Facebook Link**: "https://facebook.com/testartist"
   - **Image Link**: (any valid image URL)
   - **Seeking Venue**: Check "Yes" or "No"
   - **Seeking Description**: (if applicable) "Looking for venues"
   - **Genres**: Select at least one genre
3. Click "Create Artist"
4. **Expected**: Artist should be created and displayed on the artist detail page

### 1.2 View Artist Details
1. Go to "Artists" page
2. Click on any artist
3. **Expected**: 
   - Artist information displays (name, location, contact info, genres)
   - Upcoming and past shows display with dates
   - Image is visible
   - "Edit Profile", "Book a Show", "Manage Availability", "Add Album", "View Albums" buttons appear

### 1.3 Edit an Artist
1. On artist detail page, click "Edit Profile"
2. Modify any field (e.g., change phone number)
3. Click "Update"
4. **Expected**: Changes are saved and displayed on artist detail page

### 1.4 Search Artists
1. Go to "Artists" page
2. Enter search criteria:
   - **By Name**: Type partial artist name (e.g., "The")
   - **By Location**: Select City and/or State
   - **By Genre**: Select one or more genres
3. Click "Search"
4. **Expected**: Results display matching artists with city/state showing

### 1.5 Delete an Artist
1. On artist detail page, click "Delete Artist" button
2. Confirm deletion
3. **Expected**: 
   - Artist is removed
   - Associated albums and songs are also deleted (cascade delete)
   - Redirected to artists list

---

## 2. Venue Management Testing

### 2.1 Create a Venue
1. Navigate to "Venues" → "Create Venue" (or `/venues/create`)
2. Fill in fields:
   - **Name**: "Test Venue"
   - **Address**: "123 Main St"
   - **City**: "New York"
   - **State**: "NY"
   - **Phone**: "555-0456"
   - **Website**: "https://testvenue.com"
   - **Facebook Link**: "https://facebook.com/testvenue"
   - **Image Link**: (valid image URL)
   - **Seeking Talent**: Check Yes/No
   - **Seeking Description**: (if applicable)
   - **Genres**: Select genres
3. Click "Create Venue"
4. **Expected**: Venue is created and displayed

### 2.2 View Venue Details
1. Go to "Venues" page
2. Click on any venue
3. **Expected**:
   - Venue info displays with location, phone, website, genres
   - Upcoming and past shows display
   - Image is visible
   - Action buttons visible ("Edit Profile", "Book a Show", etc.)

### 2.3 Edit a Venue
1. On venue detail page, click "Edit Profile"
2. Modify fields (e.g., change address)
3. Click "Update"
4. **Expected**: Changes saved and displayed

### 2.4 Search Venues
1. Go to "Venues" page
2. Enter search criteria (by name, location, or genres)
3. Click "Search"
4. **Expected**: Matching venues display with city/state visible

### 2.5 Delete a Venue
1. On venue detail page, click "Delete Venue"
2. Confirm deletion
3. **Expected**: Venue is removed, associated shows are also deleted

---

## 3. Album Management Testing

### 3.1 Create an Album from Artist Page
1. View an artist detail page
2. Click "Add Album" button
3. Form should appear with:
   - Artist name prefilled (read-only or hidden)
   - **Title**: "New Album"
   - **Release Date**: (date picker)
   - **Description**: Album description
   - **Image Link**: (valid image URL)
   - **Spotify Link**: (Spotify URL)
4. Click "Create Album"
5. **Expected**: Album created, artist context preserved

### 3.2 View All Albums
1. Go to "Albums" page or click "View Albums" from artist detail
2. **Expected**: All albums display in a list format

### 3.3 View Album Details
1. Click on any album
2. **Expected**:
   - Album info displays (title, artist, image, description)
   - All songs for the album display
   - Song list shows: title, duration
   - "Add Song", "Edit Album", "Delete Album" buttons visible

### 3.4 Filter Albums by Artist
1. Go to "Albums" page
2. Add query parameter: `?artist_id=1` (or any artist ID)
3. **Expected**: Only albums for that artist display

### 3.5 Edit an Album
1. On album detail page, click "Edit Album"
2. Modify fields (e.g., description)
3. Click "Update"
4. **Expected**: Changes saved

### 3.6 Delete an Album
1. On album detail page, click "Delete Album"
2. Confirm deletion
3. **Expected**:
   - Album deleted
   - Associated songs also deleted (cascade delete)
   - Redirected to albums page

---

## 4. Song Management Testing

### 4.1 Add a Song to an Album
1. On album detail page, click "Add Song"
2. Form should display with:
   - Album prefilled/context preserved
   - **Title**: "New Song"
   - **Duration**: "180" (in seconds)
   - **Spotify Link**: (optional)
3. Click "Create Song"
4. **Expected**: Song added to album and displays in song list

### 4.2 View Songs in Album
1. Click on any album
2. **Expected**:
   - All songs display with titles and durations
   - "Edit" and "Delete" buttons visible for each song

### 4.3 Edit a Song
1. On album detail page, find song and click "Edit"
2. Modify duration or title
3. Click "Update"
4. **Expected**: Changes saved and displayed

### 4.4 Delete a Song
1. On album detail page, find song and click "Delete"
2. Confirm deletion
3. **Expected**:
   - Song deleted
   - Album still exists with remaining songs

### 4.5 Form Validation Testing
1. Try adding a song with:
   - **Empty title**: Form should show error
   - **Negative duration**: Form should show error
   - **Invalid Spotify URL**: Form should show error
2. **Expected**: Validation errors display and form data is preserved

---

## 5. Show Management Testing

### 5.1 Create a Show
1. Click "Create Show" (from artist or venue detail)
2. Fill in:
   - **Artist**: Select from dropdown
   - **Venue**: Select from dropdown
   - **Show Date/Time**: Pick date and time
3. Click "Create Show"
4. **Expected**: Show created and displays in upcoming shows

### 5.2 Search Shows
1. Go to "Shows" page
2. Enter search criteria (artist ID, venue ID, or both)
3. Click "Search"
4. **Expected**: Matching shows display with venue/artist info

### 5.3 Show Categorization
1. Create a show with a **past date** (before today)
2. Create a show with a **future date** (after today)
3. View artist or venue detail page
4. **Expected**:
   - Past shows appear under "Past Shows" section
   - Upcoming shows appear under "Upcoming Shows" section
   - Counts are correct

### 5.4 Delete a Show
1. Find a show and click "Delete"
2. Confirm deletion
3. **Expected**: Show removed from all views

---

## 6. Data Integrity Testing

### 6.1 Cascade Delete - Artist
1. Create an artist
2. Create 2+ albums for that artist
3. Add songs to those albums
4. Delete the artist
5. **Expected**:
   - Artist deleted
   - All associated albums deleted
   - All songs in those albums deleted

### 6.2 Cascade Delete - Album
1. Create an album with 3+ songs
2. Delete the album
3. **Expected**:
   - Album deleted
   - All songs in album deleted
   - Artist still exists

### 6.3 Genre Association
1. Create artist/venue with multiple genres
2. Edit and change genres
3. Delete genre from selection
4. **Expected**: Genres update correctly in database

---

## 7. Edge Cases & Error Handling

### 7.1 Duplicate Prevention
1. Try creating two artists/venues with identical names
2. **Expected**: System allows this (duplicates are valid)

### 7.2 Special Characters in Names
1. Create artist/venue/album with special characters: `"Test & Co."`, `"O'Brien's Bar"`, `"Café ☕"`
2. **Expected**: All data saved and displayed correctly

### 7.3 Long Text Fields
1. Create artist with:
   - Very long name (100+ characters)
   - Long seeking description (500+ characters)
2. **Expected**: Text truncated/displayed correctly on all pages

### 7.4 URL Validation
1. Try entering invalid URLs in Image Link, Website, Spotify Link fields
2. **Expected**: System accepts them (URLs not validated) or shows appropriate error

### 7.5 Phone Number Formats
1. Try different phone formats:
   - `555-0123`
   - `(555) 012-3456`
   - `5550123`
   - `+1-555-0123`
2. **Expected**: All formats accepted without validation error

### 7.6 Empty Database
1. Delete all artists/venues/albums/songs
2. Navigate to all pages
3. **Expected**: Pages display empty states gracefully

### 7.7 Non-existent IDs
1. Try accessing `/artists/9999`, `/venues/9999`, `/albums/9999`, `/songs/9999`
2. **Expected**: 404 error or redirect with error message

### 7.8 Form Re-submission
1. Create an artist successfully
2. Use browser back button
3. Submit form again
4. **Expected**: Does not create duplicate (browser handles this)

---

## 8. UI/UX Testing

### 8.1 Navigation
1. Test all navigation links work correctly
2. Verify breadcrumb navigation (if applicable)
3. **Expected**: All links navigate to correct pages

### 8.2 Images Display
1. Navigate to all detail pages
2. **Expected**: Artist/Venue/Album images load correctly

### 8.3 Responsive Design (if applicable)
1. Test on different screen sizes (mobile, tablet, desktop)
2. **Expected**: Layout adjusts appropriately

### 8.4 Form Submission Feedback
1. Submit any form
2. **Expected**:
   - Success message displays
   - Page updates immediately
   - User feedback is clear

---

## 9. Database Verification

After completing manual tests, verify data persistence:

```bash
# Check database contains expected data
make db-seed    # Seeds sample data
make test       # Run automated tests to verify data integrity
```

---

## 10. Test Checklist

Use this checklist to track manual testing progress:

```
Artists:
  [ ] Create artist
  [ ] View artist details
  [ ] Edit artist
  [ ] Search artists
  [ ] Delete artist

Venues:
  [ ] Create venue
  [ ] View venue details
  [ ] Edit venue
  [ ] Search venues
  [ ] Delete venue

Albums:
  [ ] Create album
  [ ] View albums
  [ ] View album details
  [ ] Filter albums by artist
  [ ] Edit album
  [ ] Delete album

Songs:
  [ ] Add song to album
  [ ] View songs in album
  [ ] Edit song
  [ ] Delete song
  [ ] Form validation

Shows:
  [ ] Create show
  [ ] Search shows
  [ ] Verify show categorization (past/upcoming)
  [ ] Delete show

Data Integrity:
  [ ] Cascade delete: artist
  [ ] Cascade delete: album
  [ ] Genre associations

Edge Cases:
  [ ] Duplicate names
  [ ] Special characters
  [ ] Long text fields
  [ ] URL validation
  [ ] Phone number formats
  [ ] Empty database
  [ ] Non-existent IDs
  [ ] Form re-submission

UI/UX:
  [ ] Navigation
  [ ] Image display
  [ ] Responsive design
  [ ] Form feedback
```

---

## Notes

- When testing shows, ensure show times are set correctly for past/upcoming categorization
- Test both "seeking" and "not seeking" states for artists and venues
- Verify that deleting a parent record properly cascades to child records
- Check that form validation errors preserve user input for correction
