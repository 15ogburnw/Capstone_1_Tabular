from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

bcrypt = Bcrypt()
db = SQLAlchemy()


class User(db.Model):

    """A User in the application"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String(30), nullable=False, unique=True)

    email = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.String(50), nullable=False)

    first_name = db.Column(db.String(30), nullable=False)

    last_name = db.Column(db.String(50), nullable=True)

    profile_pic = db.Column(
        db.Text, nullable=True, default='https://www.kindpng.com/picc/m/451-4517876_default-profile-hd-png-download.png')

    instrument_id = db.Column(db.Integer, db.ForeignKey(
        'instruments.id'), nullable=True, default=None)

    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow())

    instrument = db.relationship('Instrument')

    likes = db.relationship('Song', secondary='likes')

    my_playlists = db.relationship('Playlist', backref='creator')

    all_playlists = db.relationship(
        'Playlist', secondary='playlists_users', backref='users')

    friends = db.relationship('User', secondary='friends')


class Friend(db.Model):

    __tablename__ = 'friends'

    user_1 = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'), primary_key=True)

    user_2 = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'), primary_key=True)


class Instrument(db.Model):

    """Available instruments for user profile"""

    __tablename__ = 'instruments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(50), nullable=False)

    icon = db.Column(db.Text, nullable=False)


class Song(db.Model):

    """An individual song with its tabs"""

    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.Text, nullable=False)

    artist = db.Column(db.Text, nullable=False)

    tab_url = db.Column(db.Text, nullable=False)


class Like(db.Model):

    """Mapping a song to a user for likes"""

    __tablename__ = 'likes'

    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'), primary_key=True)

    song_id = db.Column(db.Integer, db.ForeignKey(
        'songs.id', ondelete='cascade'), primary_key=True)


class Playlist(db.Model):

    """An individual playlist"""

    __tablename__ = 'playlists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'), nullable=False)

    name = db.Column(db.String(50), nullable=False)

    is_private = db.Column(db.Boolean, nullable=False, default=False)

    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow())

    updated_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow())

    songs = db.relationship('Song', secondary='playlists_songs')


class PlaylistSong(db.Model):

    """Mapping a song to a playlist"""

    __tablename__ = 'playlists_songs'

    playlist_id = db.Column(db.Integer, db.ForeignKey(
        'playlists.id', ondelete='cascade'), primary_key=True)

    song_id = db.Column(db.Integer, db.ForeignKey(
        'songs.id', ondelete='cascade'), primary_key=True)


class PlaylistUser(db.Model):

    """Mapping users to playlists (to show which users can access the playlist)"""

    __tablename__ = 'playlists_users'

    playlist_id = db.Column(db.Integer, db.ForeignKey(
        'playlists.id', ondelete='cascade'), primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'), primary_key=True)


class Band(db.Model):

    __tablename__ = 'bands'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(50), nullable=False)

    genre = db.Column(db.String(30), nullable=True)

    description = db.Column(db.Text, nullable=True)

    band_pic = db.Column(db.Text, nullable=True,
                         default='https://www.pngitem.com/pimgs/m/19-195664_rock-band-clip-art-musical-ensemble-silhouette-vector.png')

    playlists = db.relationship('Playlist', secondary='bands_playlists')

    members = db.relationship(
        'User', secondary='bands_members', backref='bands')

    messages = db.relationship('Message')


class BandMember(db.Model):

    __tablename__ = 'bands_members'

    band_id = db.Column(db.Integer, db.ForeignKey(
        'bands.id', ondelete='cascade'), primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'), primary_key=True)


class BandPlaylist(db.Model):

    __tablename__ = 'bands_playlists'

    band_id = db.Column(db.Integer, db.ForeignKey(
        'bands.id', ondelete='cascade'))

    playlist_id = db.Column(db.Integer, db.ForeignKey(
        'playlists.id', ondelete='cascade'))


class Message(db.Model):

    __tablename__ = 'messages'

    author_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)

    content = db.Column(db.Text, nullable=False)

    category = db.Column(db.Text, nullable=False, default='dm')

    recipient_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=True)

    band_id = db.Column(db.Integer, db.ForeignKey('bands.id'), nullable=True)

    time_sent = db.Column(db.DateTime, nullable=False,
                          default=datetime.utcnow())
