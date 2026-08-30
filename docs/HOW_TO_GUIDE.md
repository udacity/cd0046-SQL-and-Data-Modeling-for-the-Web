# How-To Guide: Fyyur Application

This guide provides practical instructions for common tasks in the Fyyur application.

## Table of Contents

1. [Setup & Running](#setup--running)
2. [Managing Your Artist Profile](#managing-your-artist-profile)
3. [Managing Your Venue Profile](#managing-your-venue-profile)
4. [Creating & Organizing Music](#creating--organizing-music)
5. [Booking Shows](#booking-shows)
6. [Managing Availability](#managing-availability)
7. [Troubleshooting](#troubleshooting)

---

## Setup & Running

### Starting the Application

```bash
# Install dependencies (first time only)
make install

# Start the Flask development server
make run
```

The application will be available at `http://localhost:5000`

### Running Tests

```bash
# Run all unit and integration tests
make test

# Run tests with coverage report
make test-cov
# View report: open htmlcov/index.html
```

### Database Management

```bash
# Initialize database (create tables)
make db-init

# Seed database with sample data
make db-seed

# Reset database (drops and recreates all tables)
make db-reset

# Reset and seed in one command
make db-refresh
```

---

## Managing Your Artist Profile

### Creating Your Artist Profile

1. Click **"Artists"** in the navigation menu
2. Click **"Create Artist"** button
3. Fill in your information:
   - **Name**: Your artist/band name
   - **City & State**: Your primary location
   - **Phone**: Contact number
   - **Website**: Your official website URL
   - **Facebook Link**: Your Facebook page
   - **Image Link**: URL to your artist photo (1000x1000px recommended)
   - **Genres**: Select all genres that apply to your music
   - **Seeking Venues**: Check if you're actively looking for shows
   - **Seeking Description**: Brief description of what you're looking for
4. Click **"Create Artist"**

### Editing Your Profile

1. Click your artist name to view your profile
2. Click **"Edit Profile"** button
3. Update any information
4. Click **"Update"**

### Viewing Your Shows

Your artist profile displays:
- **Upcoming Shows**: Performances scheduled for future dates
- **Past Shows**: Completed performances

Shows are automatically categorized based on the current date.

---

## Managing Your Venue Profile

### Creating Your Venue Profile

1. Click **"Venues"** in the navigation
2. Click **"Create Venue"** button
3. Fill in your venue information:
   - **Name**: Venue name
   - **Address**: Street address
   - **City & State**: Location
   - **Phone**: Contact number
   - **Website**: Venue website
   - **Facebook Link**: Venue Facebook page
   - **Image Link**: Photo of venue (1000x1000px recommended)
   - **Genres**: Music genres you typically feature
   - **Seeking Talent**: Check if you're looking to book artists
   - **Seeking Description**: What you're looking for in artists
4. Click **"Create Venue"**

### Editing Your Venue

1. Click your venue name to view details
2. Click **"Edit Profile"** button
3. Update information
4. Click **"Update"**

### Viewing Your Booked Shows

Shows section displays:
- **Upcoming Shows**: Artists booked for future dates
- **Past Shows**: Previous performances

---

## Creating & Organizing Music

### Creating an Album

**As an Artist:**
1. Go to your artist profile
2. Click **"Add Album"** button
3. Fill in:
   - **Title**: Album name
   - **Release Date**: Date album was/will be released
   - **Description**: Album details or concept
   - **Image Link**: Album cover art URL
   - **Spotify Link**: Link to album on Spotify (optional)
4. Click **"Create Album"**

Your artist will be automatically associated with the album.

### Adding Songs to an Album

1. Navigate to the album detail page
2. Click **"Add Song"** button
3. Fill in:
   - **Title**: Song name
   - **Duration**: Length in seconds (e.g., 240 for 4-minute song)
   - **Spotify Link**: Direct link to song (optional)
4. Click **"Create Song"**

### Organizing Your Discography

1. Go to **"Albums"** page
2. Filter by your artist ID using: `?artist_id=YOUR_ID`
3. View all your albums in one place
4. Click any album to view or edit songs

### Editing Songs

1. View album detail page
2. Find the song you want to edit
3. Click **"Edit"** next to the song
4. Update title or duration
5. Click **"Update"**

### Deleting Songs or Albums

**To delete a song:**
1. View album containing the song
2. Click **"Delete"** next to the song
3. Confirm deletion

**To delete an album:**
1. View album detail page
2. Click **"Delete Album"** button
3. Confirm deletion
4. All songs in the album will also be deleted

---

## Booking Shows

### Creating a Show Booking

1. Go to an artist's profile
2. Click **"Book a Show"** button
3. Or go to a venue's profile and click **"Book a Show"**

4. Fill in the show details:
   - **Artist**: Select the performer (if not already selected)
   - **Venue**: Select the venue location (if not already selected)
   - **Date & Time**: When the show will occur
5. Click **"Create Show"**

### Finding Show Opportunities

**Search for Artists:**
1. Go to **"Artists"** page
2. Search by:
   - Name (partial matches work)
   - Location (City/State)
   - Genres
3. View artist profile and their seeking status
4. Click **"Book a Show"** if interested

**Search for Venues:**
1. Go to **"Venues"** page
2. Search by:
   - Venue name
   - Location
   - Genres they feature
3. View venue profile and their seeking status
4. Click **"Book a Show"** to propose a date

### Searching Your Shows

1. Go to **"Shows"** page
2. Filter by:
   - **Artist ID**: Find shows by specific artist
   - **Venue ID**: Find shows at specific venue
   - Both: Find shows between specific artist and venue
3. Click **"Search"**

---

## Managing Availability

### Setting Availability (Artists)

1. Go to your artist profile
2. Click **"Manage Availability"** button
3. Click **"Add Availability Slot"** button
4. Set your recurring availability:
   - **Day of Week**: Which days you're available
   - **Time Range**: Start and end times
   - Example: "Available every Thursday 7:00 PM - 11:00 PM"
5. Click **"Create Slot"**

### Creating Availability Exceptions

1. On availability management page
2. Click **"Add Exception"** button
3. Set exception details:
   - **Date**: Specific date of exception
   - **Time Range**: Times you're unavailable
   - Example: "Unavailable Dec 25-26 (all day)"
4. Click **"Create Exception"**

### Editing Your Schedule

1. View your availability slots
2. Click **"Edit"** next to any slot/exception
3. Update the times or dates
4. Click **"Update"**

### Removing Availability

1. View your availability slots
2. Click **"Delete"** next to the slot/exception
3. Confirm deletion

---

## Troubleshooting

### Common Issues

#### Profile Not Saving
**Problem**: Changes don't appear after clicking "Update"
**Solution**:
- Check that all required fields are filled
- Ensure phone numbers and URLs are valid format
- Try clearing browser cache and refreshing
- Check browser console for error messages (F12)

#### Image Not Displaying
**Problem**: Artist/Venue/Album images show as broken
**Solution**:
- Verify the image URL is correct and accessible
- Use direct image links (ending in .jpg, .png, etc.)
- Check that URL starts with http:// or https://
- Ensure image isn't blocked by CORS policies

#### Show Not Appearing
**Problem**: Just-created show doesn't show on profiles
**Solution**:
- Refresh the page (Ctrl+R or Cmd+R)
- Check that show date is correct
- Verify both artist and venue were selected
- Past shows only appear if date/time has passed

#### Search Results Empty
**Problem**: Search doesn't return expected results
**Solution**:
- Check spelling of search terms
- Try searching by partial name instead of exact
- Verify artist/venue actually exists in system
- Try clearing search filters and search again

#### Form Validation Errors
**Problem**: Can't submit form - getting validation errors
**Solution**:
- Required fields: Name, City, State, Address (for venue)
- Phone: Any format accepted (555-1234, etc.)
- Website/Links: Must start with http:// or https://
- Duration: Must be positive number
- Genres: Must select at least one
- Look for red error messages below each field

#### Cascade Delete Issues
**Problem**: Deleting artist/album deletes more than expected
**Expected Behavior**:
- Deleting an artist removes all their albums AND songs
- Deleting an album removes all its songs
- This is by design to prevent orphaned data
- No undo available - data is permanently deleted

### Performance Tips

1. **Search efficiently**: Use specific criteria rather than browsing all records
2. **Manage album size**: Keep albums to reasonable number of songs
3. **Check availability calendar**: Use availability management instead of manual scheduling
4. **Regular backups**: Export important data periodically (database backups)

### Getting Help

If you encounter issues not covered here:
1. Check the README.md for general documentation
2. Review MANUAL_TESTING_GUIDE.md for expected behaviors
3. Check browser developer tools (F12) for error messages
4. Contact the development team with error details

---

## Best Practices

### For Artists
- Keep your profile updated with current information
- Use high-quality images (venue owners prefer professional photos)
- Set realistic availability to increase booking chances
- Respond quickly to booking inquiries
- Update past shows regularly

### For Venues
- Clearly indicate what genres you prefer
- Set accurate availability (when you book shows)
- Write descriptive seeking information
- Update your venue image and information
- Review artist profiles before booking

### For Everyone
- Use complete URLs with http:// or https://
- Keep genre selections relevant
- Update information when it changes
- Delete shows/albums you no longer need
- Review your profile from visitor perspective regularly

---

## Keyboard Shortcuts (Optional)

While browsing:
- `Ctrl/Cmd + K`: Focus search (if implemented)
- `Ctrl/Cmd + S`: Save form (if implemented)
- Standard browser shortcuts work (back, forward, refresh)

---

## Related Documentation

- **README.md**: Project overview and setup
- **MANUAL_TESTING_GUIDE.md**: Detailed testing procedures
- **BUSINESS_DECISIONS.md**: Technical architecture decisions
- **DEVCONTAINER.md**: Development environment setup

