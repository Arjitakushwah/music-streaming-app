#apis
from flask_restful import Api, Resource, reqparse, fields, marshal_with
from models import db, Song, Album
api = Api()

# song API
output_song = {
    "id": fields.Integer,
    "Song_name": fields.String,
    "singer": fields.String,
    "lyrics": fields.String,
    "duration": fields.Integer,
    "album_id": fields.Integer,
    "creator_id": fields.Integer,
}

song_parser = reqparse.RequestParser()
song_parser.add_argument("Song_name")
song_parser.add_argument("singer")
song_parser.add_argument("lyrics")
song_parser.add_argument("duration")
song_parser.add_argument("album_id")
song_parser.add_argument("creator_id")

class SongAPI(Resource):
    @marshal_with(output_song)
    def get(self, song_id):
        song = Song.query.get(int(song_id))
        if song:
            return song
        return {"message": "Song not found"}, 404

    @marshal_with(output_song)
    def put(self, song_id):
        args = song_parser.parse_args()
        song = Song.query.get(int(song_id))
        if song:
            for key, value in args.items():
                if value is not None:
                    setattr(song, key, value)
            db.session.commit()
            return song, 200
        return {"message": "Song not found"}, 404

    def delete(self, song_id):
        song = Song.query.get(int(song_id))
        if song:
            db.session.delete(song)
            db.session.commit()
            return {"message": "Song Deleted Successfully"}, 204
        return {"message": "Song not found"}, 404

    @marshal_with(output_song)
    def post(self):
        args = song_parser.parse_args()
        song = Song(**args)
        db.session.add(song)
        db.session.commit()
        return song, 201

# album API
output_album = {
    "id": fields.Integer,
    "album_name": fields.String,
    "artist": fields.String,
    "date_created": fields.DateTime,
}

# Request parser for album data
album_parser = reqparse.RequestParser()
album_parser.add_argument("album_name")
album_parser.add_argument("artist")

class AlbumAPI(Resource):
    @marshal_with(output_album)
    def get(self, album_id):
        album = Album.query.get(int(album_id))
        if album:
            return album
        return "", 404

    @marshal_with(output_album)
    def put(self, album_id):
        args = album_parser.parse_args()
        album = Album.query.get(int(album_id))
        if album:
            for key, value in args.items():
                if value is not None:
                    setattr(album, key, value)
            db.session.commit()
            return album, 200
        return {"message": "Album not found"}, 404

    def delete(self, album_id):
        album = Album.query.get(int(album_id))
        if album:
            db.session.delete(album)
            db.session.commit()
            return "", 204
        return {"message": "Album not found"}, 404

    @marshal_with(output_album)
    def post(self):
        args = album_parser.parse_args()
        album = Album(**args)
        db.session.add(album)
        db.session.commit()
        return album, 201

