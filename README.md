# music-streaming-app
This is a Music Streaming App project developed using Flask, a Python web framework. It allows users to discover, stream, and organize their favorite songs and albums. Users can create playlists, rate songs, and explore a wide range of music content.

## Features
- User Registration and Login: Users can create accounts, log in, and enjoy a personalized experience.
- Song and Album Management: Users can browse a vast collection of songs and albums, view details, and stream their favorite music.
- Playlist Creation: Users can create and manage playlists to organize their favorite songs.
- User Profiles: User profiles provide information about their playlists, ratings, and favorite songs.
- Song Rating: Users can rate songs, and the app calculates the average rating for each song.
- Search Functionality: Search for songs, albums, and artists by name or genre.
- Creator Profiles: Creators have profiles showcasing their bio, songs, and ratings.
- Admin Panel: Admins have access to advanced features like user management, song management, and more.

## Technologies Used
- **Flask**: Used for the backend implementation.
- **Flask-SQLAlchemy**: Manages the application's database.
- **Jinja2**: Template engine for rendering HTML content.
- **Flask-Login**: Implements user login functionality.
- **Bootstrap**: Integrated to enhance the application's visual design.
- **SQLite**: Selected as the database management system, ensuring data storage and retrieval
- **Flask-Restful**: Creates RESTful APIs for user, songs, and albums.

## Database Schema
The database schema includes tables for users, songs, albums, playlists, and ratings. It defines relationships between entities.

## API Design
The project includes APIs for managing users, songs, and albums. It allows creating, updating, and deleting records using RESTful endpoints.

### User API
- `/api/user`: CRUD operations for user profiles.
- `/api/user/<int:user_id>`: Get, update, or delete user details.

### Song API
- `/api/song`: CRUD operations for songs.
- `/api/song/<int:song_id>`: Get, update, or delete song details.

### Album API
- `/api/album`: CRUD operations for albums.
- `/api/album/<int:album_id>`: Get, update, or delete album details.

## Project Structure
- `app.py`: Contains the main application logic and routes.
- `templates/`: HTML templates for rendering pages.
- `static/`: CSS and image files.
- `models.py`: Defines the database models.
- `api.py`: Defines the RESTful APIs.


