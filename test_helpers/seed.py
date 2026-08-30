"""Database seeding helper functions."""

from datetime import datetime
from sqlalchemy import text
from dal import db, Venue, Artist, Show
from dal.genre import Genre
from dal.album import Album
from dal.song import Song


def seed_database():
    """Seed database with test data.
    
    Process:
    1. Create and commit Genre objects (PostgreSQL auto-generates IDs)
    2. Create Venue objects with genre relationships
    3. Create Artist objects with genre relationships
    4. Commit venues and artists (SQLAlchemy inserts into junction tables)
    5. Create Show objects with venue and artist foreign keys
    6. Commit shows
    """
    try:
        # Clear existing data (in reverse order of dependencies)
        # Must delete from junction tables first to avoid foreign key violations
        db.session.query(Show).delete()
        db.session.query(Song).delete()
        db.session.query(Album).delete()
        # Delete from junction tables before the main tables
        db.session.execute(text('DELETE FROM artist_genre'))
        db.session.execute(text('DELETE FROM venue_genre'))
        db.session.query(Artist).delete()
        db.session.query(Venue).delete()
        db.session.query(Genre).delete()
        db.session.commit()

        # Step 1: Create and commit genres first (no manual IDs)
        genres_data = [
            'Jazz', 'Reggae', 'Swing', 'Classical', 'Folk',
            'Rock n Roll', 'R&B', 'Hip-Hop'
        ]
        genres_dict = {}
        for genre_name in genres_data:
            genre = Genre(name=genre_name)
            genres_dict[genre_name] = genre
            db.session.add(genre)
        
        db.session.commit()

        # Step 2 & 3: Create venues and artists with genre relationships (no manual IDs)
        venue1 = Venue(
            name='The Musical Hop',
            city='San Francisco',
            state='CA',
            address='1015 Folsom Street',
            phone='123-123-1234',
            website='https://www.themusicalhop.com',
            facebook_link='https://www.facebook.com/TheMusicalHop',
            image_link='https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60',
            seeking_talent=True,
            seeking_description='We are on the lookout for a local artist to play every two weeks. Please call us.'
        )
        venue1.genres.extend([genres_dict['Jazz'], genres_dict['Reggae'], genres_dict['Swing'], genres_dict['Classical'], genres_dict['Folk']])

        venue2 = Venue(
            name='The Dueling Pianos Bar',
            city='New York',
            state='NY',
            address='335 Delancey Street',
            phone='914-003-1132',
            website='https://www.theduelingpianos.com',
            facebook_link='https://www.facebook.com/theduelingpianos',
            image_link='https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80',
            seeking_talent=False,
            seeking_description=''
        )
        venue2.genres.extend([genres_dict['Classical'], genres_dict['R&B'], genres_dict['Hip-Hop']])

        venue3 = Venue(
            name='Park Square Live Music & Coffee',
            city='San Francisco',
            state='CA',
            address='34 Whiskey Moore Ave',
            phone='415-000-1234',
            website='https://www.parksquarelivemusicandcoffee.com',
            facebook_link='https://www.facebook.com/ParkSquareLiveMusicAndCoffee',
            image_link='https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80',
            seeking_talent=False,
            seeking_description=''
        )
        venue3.genres.extend([genres_dict['Rock n Roll'], genres_dict['Jazz'], genres_dict['Classical'], genres_dict['Folk']])

        artist1 = Artist(
            name='Guns N Petals',
            city='San Francisco',
            state='CA',
            phone='326-123-5000',
            website='https://www.gunsnpetalsband.com',
            facebook_link='https://www.facebook.com/GunsNPetals',
            image_link='https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80',
            seeking_venue=True,
            seeking_description='Looking for shows to perform at in the San Francisco Bay Area!'
        )
        artist1.genres.append(genres_dict['Rock n Roll'])

        artist2 = Artist(
            name='Matt Quevedo',
            city='New York',
            state='NY',
            phone='300-400-5000',
            website='',
            facebook_link='https://www.facebook.com/mattquevedo923251523',
            image_link='https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80',
            seeking_venue=False,
            seeking_description=''
        )
        artist2.genres.append(genres_dict['Jazz'])

        artist3 = Artist(
            name='The Wild Sax Band',
            city='San Francisco',
            state='CA',
            phone='432-325-5432',
            website='',
            facebook_link='https://www.facebook.com/thewildsaxband',
            image_link='https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80',
            seeking_venue=False,
            seeking_description=''
        )
        artist3.genres.extend([genres_dict['Jazz'], genres_dict['Classical']])

        # Add venues and artists to session, then commit
        # SQLAlchemy will handle junction table inserts via the relationships
        db.session.add_all([venue1, venue2, venue3])
        db.session.add_all([artist1, artist2, artist3])
        db.session.commit()

        # Step 4: Create shows with ForeignKey references to venues and artists
        # SQLAlchemy will automatically use the committed IDs
        show1 = Show(
            venue_id=venue1.id,
            artist_id=artist1.id,
            start_time=datetime(2026, 9, 10, 19, 30, 0),
            end_time=datetime(2026, 9, 10, 21, 30, 0)
        )

        show2 = Show(
            venue_id=venue3.id,
            artist_id=artist2.id,
            start_time=datetime(2026, 9, 15, 20, 0, 0),
            end_time=datetime(2026, 9, 15, 22, 0, 0)
        )

        show3 = Show(
            venue_id=venue3.id,
            artist_id=artist3.id,
            start_time=datetime(2026, 9, 20, 21, 0, 0),
            end_time=datetime(2026, 9, 20, 23, 0, 0)
        )

        show4 = Show(
            venue_id=venue2.id,
            artist_id=artist1.id,
            start_time=datetime(2026, 9, 25, 20, 0, 0),
            end_time=datetime(2026, 9, 25, 22, 30, 0)
        )

        show5 = Show(
            venue_id=venue1.id,
            artist_id=artist2.id,
            start_time=datetime(2026, 10, 5, 19, 0, 0),
            end_time=datetime(2026, 10, 5, 21, 0, 0)
        )

        show6 = Show(
            venue_id=venue2.id,
            artist_id=artist3.id,
            start_time=datetime(2026, 10, 10, 20, 30, 0),
            end_time=datetime(2026, 10, 10, 22, 30, 0)
        )

        show7 = Show(
            venue_id=venue3.id,
            artist_id=artist1.id,
            start_time=datetime(2026, 10, 15, 21, 0, 0),
            end_time=datetime(2026, 10, 15, 23, 0, 0)
        )

        show8 = Show(
            venue_id=venue1.id,
            artist_id=artist3.id,
            start_time=datetime(2026, 10, 22, 19, 30, 0),
            end_time=datetime(2026, 10, 22, 21, 30, 0)
        )

        # Add and commit shows
        db.session.add_all([show1, show2, show3, show4, show5, show6, show7, show8])
        db.session.commit()

        # Step 5: Create albums for artists
        album1 = Album(
            artist_id=artist1.id,
            title='Appetite for Destruction',
            release_date=datetime(1987, 7, 21).date(),
            description='A legendary debut album that changed rock music forever.',
            image_link='https://images.unsplash.com/photo-1510915361894-db8b60106cb1?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
            spotify_link='https://open.spotify.com/album/example1'
        )

        album2 = Album(
            artist_id=artist1.id,
            title='G N\'R Lies',
            release_date=datetime(1988, 11, 29).date(),
            description='Acoustic and unplugged tracks showcasing raw emotion.',
            image_link='https://images.unsplash.com/photo-1470225620780-dba8ba36b745?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
            spotify_link='https://open.spotify.com/album/example2'
        )

        album3 = Album(
            artist_id=artist2.id,
            title='Bossa Nova Dreams',
            release_date=datetime(2020, 3, 15).date(),
            description='A smooth collection of jazz standards and original compositions.',
            image_link='https://images.unsplash.com/photo-1514525253161-7a46d19cd819?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
            spotify_link='https://open.spotify.com/album/example3'
        )

        album4 = Album(
            artist_id=artist3.id,
            title='Wild Sax Sessions',
            release_date=datetime(2019, 8, 22).date(),
            description='High-energy jazz performances featuring incredible saxophone work.',
            image_link='https://images.unsplash.com/photo-1493225457124-a3eb161ffa5f?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
            spotify_link='https://open.spotify.com/album/example4'
        )

        db.session.add_all([album1, album2, album3, album4])
        db.session.commit()

        # Step 6: Create songs for albums
        # Songs for album1
        song1 = Song(album_id=album1.id, title='Welcome to the Jungle', duration=300)
        song2 = Song(album_id=album1.id, title='Sweet Child o\' Mine', duration=356)
        song3 = Song(album_id=album1.id, title='Patience', duration=376)
        song4 = Song(album_id=album1.id, title='Paradise City', duration=384)

        # Songs for album2
        song5 = Song(album_id=album2.id, title='Don\'t Cry', duration=356)
        song6 = Song(album_id=album2.id, title='Perfect Crime', duration=301)
        song7 = Song(album_id=album2.id, title='Dust N\' Bones', duration=385)

        # Songs for album3
        song8 = Song(album_id=album3.id, title='The Girl from Ipanema', duration=315)
        song9 = Song(album_id=album3.id, title='Bossa Nova Nights', duration=298)
        song10 = Song(album_id=album3.id, title='Carioca Moon', duration=340)

        # Songs for album4
        song11 = Song(album_id=album4.id, title='Midnight Sax', duration=420)
        song12 = Song(album_id=album4.id, title='Urban Jazz', duration=385)
        song13 = Song(album_id=album4.id, title='Saxophonic Dreams', duration=365)
        song14 = Song(album_id=album4.id, title='Syncopation', duration=310)

        db.session.add_all([
            song1, song2, song3, song4, song5, song6, song7, song8,
            song9, song10, song11, song12, song13, song14
        ])
        db.session.commit()
        
        return True, '✅ Database seeded successfully!'
    except Exception as e:
        db.session.rollback()
        return False, f'❌ Error seeding database: {e}'
