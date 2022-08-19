from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
import json


bcrypt = Bcrypt()
db = SQLAlchemy()


class Friend(db.Model):

    """Relationship between two users that are friends"""

    __tablename__ = 'friends'

    user_1 = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'), primary_key=True)

    user_2 = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'), primary_key=True)


class Like(db.Model):

    """Mapping a song to a user for likes"""

    __tablename__ = 'likes'

    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'), primary_key=True)

    song_id = db.Column(db.Integer, db.ForeignKey(
        'songs.id', ondelete='cascade'), primary_key=True)


class PlaylistSong(db.Model):

    """Mapping a song to a playlist"""

    __tablename__ = 'playlists_songs'

    playlist_id = db.Column(db.Integer, db.ForeignKey(
        'playlists.id', ondelete='cascade'), primary_key=True)

    song_id = db.Column(db.Integer, db.ForeignKey(
        'songs.id', ondelete='cascade'), primary_key=True)


class BandMember(db.Model):

    """Relationship for members of a band"""

    __tablename__ = 'bands_members'

    band_id = db.Column(db.Integer, db.ForeignKey(
        'bands.id', ondelete='cascade'), primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'), primary_key=True)


class BandPlaylist(db.Model):

    """Relationship for playlists that belong to a band"""

    __tablename__ = 'bands_playlists'

    band_id = db.Column(db.Integer, db.ForeignKey(
        'bands.id', ondelete='cascade'), primary_key=True)

    playlist_id = db.Column(db.Integer, db.ForeignKey(
        'playlists.id', ondelete='cascade'), primary_key=True)


class User(db.Model):

    """A User in the application"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    username = db.Column(db.String(30), nullable=False, unique=True)

    email = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

    first_name = db.Column(db.String(20), nullable=False)

    last_name = db.Column(db.String(30), nullable=True)

    profile_pic = db.Column(
        db.Text, nullable=True, default='https://www.kindpng.com/picc/m/451-4517876_default-profile-hd-png-download.png')

    cover_pic = db.Column(
        db.Text, nullable=True, default='https://facebooktimelinephotos.files.wordpress.com/2012/01/grass-landscape.png')

    instrument_id = db.Column(db.Integer, db.ForeignKey(
        'instruments.id'), nullable=True, default=None)

    bio = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow())

    instrument = db.relationship('Instrument')

    likes = db.relationship('Song', secondary='likes')

    my_playlists = db.relationship('Playlist', backref='creator')

    all_playlists = db.relationship(
        'Playlist', secondary='playlists_users', backref='users')

    friends = db.relationship('User', secondary='friends', primaryjoin=(Friend.user_1 == id),
                              secondaryjoin=(Friend.user_2 == id))

    @property
    def full_name(self):

        return self.first_name + ' ' + self.last_name

    def __repr__(self):

        return f"<User #{self.id}, username: {self.username}, email: {self.email}>"

    @classmethod
    def register(cls, username, email, password, first_name, last_name):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            first_name=first_name,
            last_name=last_name
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

    def serialize(self):
        """return a JSON object with basic user info"""

        obj = {
            'id': self.id,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.first_name,
            'profile_pic': self.profile_pic
        }

        return json.dumps(obj)


class Instrument(db.Model):

    """Available instruments for user profile"""

    __tablename__ = 'instruments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(50), nullable=False)

    icon = db.Column(db.Text, nullable=False)

    def __repr__(self):

        return f"<Instrument: {self.name}>"


class Song(db.Model):

    """An individual song with its tabs"""

    __tablename__ = 'songs'

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.Text, nullable=False)

    artist = db.Column(db.Text, nullable=False)

    tab_url = db.Column(db.Text, nullable=False)

    def __repr__(self):

        return f"<{self.title} by {self.artist}>"

    def serialize(self):

        obj = {
            "id": self.id,
            "title": self.title,
            "artist": self.artist,
            "tab_url": f'https://www.songsterr.com/a/wa/song?id=${self.id}'}

        return json.dumps(obj)


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

    def __repr__(self):

        return f"<Playlist {self.name} created by {self.user_id}>"


class PlaylistUser(db.Model):

    """Mapping users to playlists (to keep track of each user's created playlists, saved public playlists, and shared private playlists)"""

    __tablename__ = 'playlists_users'

    playlist_id = db.Column(db.Integer, db.ForeignKey(
        'playlists.id', ondelete='cascade'), primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'), primary_key=True)


class Band(db.Model):

    """Model for a 'band' or group of users in the system"""

    __tablename__ = 'bands'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    name = db.Column(db.String(50), nullable=False, unique=True)

    genre = db.Column(db.String(30), nullable=True)

    description = db.Column(db.Text, nullable=True)

    band_pic = db.Column(db.Text, nullable=True,
                         default='https://www.pngitem.com/pimgs/m/19-195664_rock-band-clip-art-musical-ensemble-silhouette-vector.png')

    playlists = db.relationship('Playlist', secondary='bands_playlists')

    members = db.relationship(
        'User', secondary='bands_members', backref='bands')

    messages = db.relationship('Message')

    def __repr__(self):

        return f"<Band {self.name}>"


class Message(db.Model):

    """Model for messages in the system, either between users or within a band"""

    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    author_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=False)

    content = db.Column(db.Text, nullable=False)

    category = db.Column(db.Text, nullable=False, default='dm')

    recipient_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=True)

    band_id = db.Column(db.Integer, db.ForeignKey('bands.id'), nullable=True)

    time_sent = db.Column(db.DateTime, nullable=False,
                          default=datetime.utcnow())


def connect_db(app):
    """
    Connect this database to provided Flask app.
    """

    db.app = app
    db.init_app(app)
