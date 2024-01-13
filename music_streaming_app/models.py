from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()
# song model
class Song(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    Song_name = db.Column(db.String(20), nullable = False)
    singer = db.Column(db.String(255), nullable=False)
    lyrics = db.Column(db.Text, nullable = True)
    duration = db.Column(db.Integer, nullable=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp(), nullable=False) 
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable = False)
    creator_id = db.Column(db.Integer, db.ForeignKey('creator.id'), nullable=False)
    song_file = db.Column(db.String(255), nullable=True)
    album = db.relationship('Album', back_populates='songs')
    creator = db.relationship('Creator', back_populates='songs')
    playlists = db.relationship('Playlist', secondary='playlist_song', back_populates='songs')
    ratings = db.relationship('Rating', back_populates='songs', cascade='all, delete-orphan')

# album model
class Album(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    album_name = db.Column(db.String(20), nullable = False)
    artist = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    songs = db.relationship('Song', back_populates='album', cascade='all, delete-orphan')

#playlist model 
class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='playlists')
    songs = db.relationship('Song', secondary='playlist_song', back_populates='playlists')
    
class PlaylistSong(db.Model):
    __tablename__ = 'playlist_song'
    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)

#user model
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key =True)
    name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(40), nullable= False)
    password = db.Column(db.String(12), nullable=False)
    role = db.Column(db.String(30), default="normal user")
    creator = db.relationship('Creator', uselist=False, back_populates='user')
    playlists = db.relationship('Playlist', back_populates='user')
    ratings = db.relationship('Rating', back_populates ='user')

#creator model
class Creator(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False)
    bio = db.Column(db.Text, nullable=True)
    rating = db.Column(db.Float, default=0.0)
    flagged = db.Column(db.Boolean, default=False)
    user = db.relationship('User', back_populates='creator')
    songs = db.relationship('Song', back_populates='creator')

# rating
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    song_id = db.Column(db.Integer, db.ForeignKey('song.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    # __table_args__ = (db.UniqueConstraint('user_id', 'song_id'),)
    user = db.relationship('User', back_populates='ratings')
    songs = db.relationship('Song', back_populates='ratings')

