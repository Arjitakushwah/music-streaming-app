from flask import Flask, render_template, request, url_for, redirect
from models import db, Song, Album,User,Playlist,Creator,Rating
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import os
from werkzeug.utils import secure_filename
from sqlalchemy import func
from flask_restful import Api
from api import SongAPI,AlbumAPI
from sqlalchemy import or_

app = Flask(__name__)
app.static_folder = 'static'
app.config['SECRET_KEY'] = '1234'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///music_streaming.sqlite3"
db.init_app(app)
api = Api(app)
app.app_context().push()
login_manager = LoginManager(app)
login_manager.login_view = 'login'
app.config['UPLOAD_FOLDER'] = 'static/songs'
app.config['ALLOWED_EXTENSIONS'] = {'mp3'} 
 
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

#home page
@app.route('/')
def home():
    return render_template('home.html')
#go back
@app.route('/go_back', methods=['GET'])
def go_back():
    return redirect(request.referrer or url_for('home'))
#logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

#LOGIN AND REGISTRATION
#register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':        
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            return render_template('register.html', user_exists=True)
        else:
            name = request.form.get('name')
            if not username or not password or not email or not name:
                message="All fields are required"
                return render_template('invalid.html', message=message)
            new_user = User(username=username, password=password, email=email, name=name)
            db.session.add(new_user)
            db.session.commit()
            return render_template('confirmation.html', upload = False)
    return render_template('register.html', user_exists = False)
#user login
@app.route('/login' , methods=['GET', 'POST'])
def login():
    if request.method == 'POST':        
        username = request.form.get('username')
        password = request.form.get('password')
        user_exists = User.query.filter_by(username=username, password=password).first()
        if user_exists:
            login_user(user_exists)
            return redirect(url_for('user_dashboard'))
        else:
            message= "invalid credentials or user doesn't exist"
            return render_template('invalid.html', message=message)
    return render_template('login.html')
#admin login
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':       
        username = request.form.get('username')
        password = request.form.get('password')
        admin_exists = User.query.filter_by(username=username, password=password, role ="admin").first()
        if admin_exists:
            login_user(admin_exists)
            return redirect(url_for('admin_dashboard'))
        else:
            message ="invalid credentials or admin doesn't exist please login as a user"
            return render_template('invalid.html', message=message)
    return render_template('admin_login.html')

#USER MANAGEMENT
#user dashboard
@app.route('/user_dashboard')
@login_required
def user_dashboard():
    songs = Song.query.all()  
    albums = Album.query.all()
    user = current_user
    creator = Creator.query.all()
    playlist = Playlist.query.filter_by(user_id=user.id).all()
    return render_template('user_dashboard.html',songs=songs,albums=albums,playlists=playlist, creators=creator) 
#display the list of Songs, Albums or Cretors
@app.route('/display_content')
@login_required
def display_content():
    is_type = request.args.get('type')
    songs = Song.query.all()  
    albums = Album.query.all()
    creators = Creator.query.all()
    if is_type == 'song':
        return render_template('content.html', song=songs)
    elif is_type == 'creator':
        return render_template('content.html',creator=creators)
    else:
        return render_template('content.html', album=albums)
#user profile
@app.route('/profile')
@login_required
def user_profile():
    user = current_user
    playlists = Playlist.query.filter_by(user_id=user.id).all()
    return render_template('user_profile.html', user=user, playlists=playlists)
#edit user profile
@app.route('/profile/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':        
        username = request.form.get('username')
        name = request.form.get('name')
        email = request.form.get('email')
        current_user.username = username
        current_user.name = name
        current_user.email = email
        db.session.commit()
        return redirect(url_for('user_profile'))  
    return render_template('edit_profile.html', user=current_user, change_password = False)
# chane password
@app.route('/profile/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        if current_user.password == old_password:
            current_user.password = new_password
            db.session.commit()
            return render_template('confirmation.html', change_password=True)
        elif not current_user.password == old_password:
            return render_template('edit_profile.html',user=current_user,change_password=True, error = True)
    return render_template('edit_profile.html',user=current_user,change_password=True, error = False)

#ADMIN PANEL
#admin dashboard
@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    total_users = User.query.filter_by(role="normal user").count()
    total_creators = Creator.query.count()
    total_songs = Song.query.count()
    total_albums = Album.query.count()
    albums = Album.query.all()
    creators = Creator.query.all()
    return render_template('admin_dashboard.html', total_songs=total_songs, users=total_users, total_creators=total_creators, total_albums=total_albums, albums = albums, creators = creators )

#FLAG creators
# Admin flagging a creator
@app.route('/flag_creator/<int:creator_id>', methods=['POST'])
def flag_creator(creator_id):
    creator = Creator.query.get(creator_id)
    if creator:
        creator.flagged = True
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
# whitelist a creator
@app.route('/whitelist_creator/<int:creator_id>', methods=['POST'])
def whitelist_creator(creator_id):
    creator = Creator.query.get(creator_id)
    if creator:
        creator.flagged = False
        db.session.commit()
        return redirect(url_for('admin_dashboard'))

@app.route('/details')
@login_required
def details():
    is_type = request.args.get('type')
    type_id = request.args.get('type_id')
    if is_type == 'song':
        song = Song.query.get(type_id)
        return render_template('admin_content.html', song=song, album=None, creator=None)
    elif is_type == 'creator':
        creator = Creator.query.get(type_id)
        return render_template('admin_content.html', song=None, album=None, creator=creator)
    else:
        album = Album.query.get(type_id)
        return render_template('admin_content.html', song=None, album=album, creator = None)

#CREATOR MANAGEMENT
#Check creator account
@app.route('/check_creator_account')
@login_required
def check_creator_account():
    creator_exist = Creator.query.filter_by(user_id = current_user.id).first()    
    if creator_exist:
        return redirect(url_for('creator_dashboard'))
    return redirect(url_for('creator'))   
#creator
@app.route('/creator')
@login_required
def creator():
    return render_template('creator.html')
#creator register
@app.route('/creator/register', methods=['GET', 'POST'])
@login_required
def creator_register():  
    creator_exist = Creator.query.filter_by(user_id = current_user.id).first()
    user = User.query.filter_by(id = current_user.id).first()
    if request.method == 'POST':
        if not creator_exist:
            bio = request.form.get('bio')
            new_creator = Creator(user_id=current_user.id,bio=bio)
            db.session.add(new_creator)
            db.session.commit()
            user.role = "creator"
            db.session.commit()
            return redirect(url_for('creator_dashboard'))
    return render_template('creator_register.html')
#creator dashboard
@app.route('/creator_dashboard')
@login_required
def creator_dashboard():
    creator = Creator.query.filter_by(user_id=current_user.id).first()
    total_songs = Song.query.filter_by(creator_id=creator.id).count()
    total_albums = Album.query.filter_by(artist=creator.user.name).count()  
    albums = Album.query.filter_by(artist=creator.user.name).all()
    average_rating = creator.rating
    bio = creator.bio
    return render_template('creator_dashboard.html',creator = creator, creator_name=creator.user.name, total_songs=total_songs, total_albums=total_albums,albums=albums, average_rating=average_rating, bio = bio) 
# creator profile
@app.route('/creator_profile/<int:creator_id>', methods=['GET'])
@login_required
def creator_profile(creator_id):
    creator = Creator.query.get(creator_id)
    if creator:
        return render_template('creator_profile.html', creator=creator)
    else:
        message = "creator doesn't exist"
        return render_template('invalid.html', message=message)
    
#SONG MANAGEMENT
#upload song
@app.route('/upload_song', methods=['GET', 'POST'])
@login_required
def upload_song():
    if request.method == 'POST':
        song_name = request.form.get('songname')
        creator = request.form.get('artist')
        album_name = request.form.get('albumname')
        lyrics = request.form.get('lyrics')
        duration = request.form.get('duration')
        song_file = request.files['songFile']
        creator_id = current_user.creator.id
        album = Album.query.filter_by(album_name=album_name).first()
        if not album:
            album = Album(album_name=album_name, artist=current_user.name)
            db.session.add(album)
            db.session.commit()
        album_id = album.id
        if song_file:
            filename = secure_filename(song_file.filename)
            song_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_url = "songs/" + filename
            new_song = Song(Song_name=song_name, creator_id=creator_id, album_id=album_id,singer = creator, lyrics=lyrics, duration=duration, song_file=file_url)
            db.session.add(new_song)
            db.session.commit()
            return render_template('confirmation.html', upload = True)
    return render_template('upload_song.html')
# song page
@app.route('/song/<int:song_id>')
def song_page(song_id):
    song = Song.query.get(song_id)
    return render_template('song_page.html', song=song)
#album page
@app.route('/album/<int:album_id>')
def album_page(album_id):
    album = Album.query.get(album_id)
    return render_template('album_page.html', album=album)
#delete album
@app.route('/delete_album/<int:album_id>', methods=['GET'])
def delete_album(album_id):
    album = Album.query.get(album_id)
    if album:
        Song.query.filter_by(album_id=album_id).delete()
        db.session.delete(album)
        db.session.commit()
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('creator_dashboard'))   
# edit song
@app.route('/edit_song/<int:song_id>', methods=['GET', 'POST'])
def edit_song(song_id):
    song = Song.query.get(song_id)
    if request.method == 'POST':
        song_name = request.form.get('song_name')
        lyrics = request.form.get('lyrics')
        duration = request.form.get('duration')
        artist = request.form.get('artist_name')
        album = request.form.get('album_name')
        song.Song_name = song_name
        song.lyrics = lyrics
        song.duration = duration
        song.singer = artist
        song.album.album_name = album
        db.session.commit()
        return redirect(url_for('creator_dashboard'))  
    return render_template('edit_song.html', song=song)
# delete song
@app.route('/delete_song/<int:song_id>')
def delete_song(song_id):
    song = Song.query.get(song_id)
    db.session.delete(song)
    db.session.commit()
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('creator_dashboard'))
# rate song
@app.route('/rate_song/<int:song_id>', methods=['GET', 'POST'])
def rate_song(song_id):
    song = Song.query.get(song_id)
    user_id = current_user.id 
    if request.method == 'POST':
        rating = int(request.form.get('rating'))
        new_rating = Rating(rating=rating,user_id=user_id, song_id=song.id)
        db.session.add(new_rating)
        db.session.commit()
        creator_id = song.creator_id
        creator = Creator.query.filter_by(id=creator_id).first()
        ratings_for_creator = Rating.query.filter_by(user_id=creator.user.id).all()

        total_rating = sum(rating.rating for rating in ratings_for_creator)
        average_rating = total_rating / len(ratings_for_creator) if ratings_for_creator else 0.0
        creator.rating = average_rating
        db.session.commit()
        return redirect(url_for('song_page', song_id=song.id))
    return render_template('rate_song.html', song=song)

#PLAYLIST MANAGEMENT
# create playlist
@app.route('/create_playlist', methods=['GET','POST'])
@login_required
def create_playlist():
    if request.method == 'POST':
        name = request.form.get('playlist_name')
        user_id = current_user.id       
        new_playlist = Playlist(name=name, user_id=user_id)
        db.session.add(new_playlist)
        db.session.commit()
        return redirect(url_for('playlist', playlist_id=new_playlist.id))
    return render_template('create_playlist.html')
#display playlist
@app.route('/playlist/<int:playlist_id>', methods=['GET', 'POST'])
@login_required
def playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id) 
    return render_template('playlist.html', playlist=playlist)
# edit playlist
@app.route('/edit_playlist/<int:playlist_id>', methods=['GET', 'POST'])
@login_required  
def edit_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    if not playlist:
        return redirect(url_for('user_profile'))
    if request.method == 'POST':
        playlist_name = request.form.get('playlistName')
        playlist.name = playlist_name     
        selected_songs = request.form.getlist('selected_songs')
        if selected_songs:
            songs_to_add = Song.query.filter(Song.id.in_(selected_songs)).all()
            for song in songs_to_add:
                if song not in playlist.songs:
                    playlist.songs.append(song)
        db.session.commit()
        return redirect(url_for('user_profile'))
    all_songs = Song.query.all()
    return render_template('edit_playlist.html', playlist=playlist, all_songs=all_songs)
# delete song from playlist
@app.route('/remove_song_from_playlist/<int:playlist_id>/<int:song_id>', methods=['GET','POST'])
@login_required
def remove_song_from_playlist(playlist_id, song_id):
    playlist = Playlist.query.get(playlist_id)
    if not playlist:
        return redirect(url_for('user_profile'))
    song = Song.query.get(song_id)
    if not song:
        return redirect(url_for('user_profile'))
    if song in playlist.songs:
        playlist.songs.remove(song)
        db.session.commit()
    return redirect(url_for('user_profile'))
# delete playlist
@app.route('/delete_playlist/<int:playlist_id>', methods=['GET','POST'])
def delete_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    db.session.delete(playlist)
    db.session.commit()
    return redirect(url_for('user_profile'))

#SEARCH FUNCTIONALITY
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    songs = Song.query.filter(or_(
        Song.Song_name.ilike(f'%{query}%'),
        Song.singer.ilike(f'%{query}%')
    )).all()
    albums = Album.query.filter(or_(
        Album.album_name.ilike(f'%{query}%'),
        Album.artist.ilike(f'%{query}%')
    )).all()
    creators = Creator.query.join(User).filter(User.username.ilike(f'%{query}%')).all()
    return render_template('search.html', songs=songs, albums=albums, creators=creators)

#APIS
api.add_resource(AlbumAPI, "/api/album", "/api/album/<int:album_id>")
api.add_resource(SongAPI, "/api/song", "/api/song/<int:song_id>")

if __name__ == '__main__':
    app.debug = True
    app.run()