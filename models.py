from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_bcrypt import Bcrypt
from datetime import datetime
import json
from flask import g


bcrypt = Bcrypt()
db = SQLAlchemy()


# msg_categories = {
#     friend_request = 'fr',
#     direct_message = 'dm',
#     band-invite = 'bi'
# }


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


# ************ REVISIT LATER *************

# class BandMember(db.Model):

#     """Relationship for members of a band"""

#     __tablename__ = 'bands_members'

#     band_id = db.Column(db.Integer, db.ForeignKey(
#         'bands.id', ondelete='cascade'), primary_key=True)

#     user_id = db.Column(db.Integer, db.ForeignKey(
#         'users.id', ondelete='cascade'), primary_key=True)


# class BandPlaylist(db.Model):

#     """Relationship for playlists that belong to a band"""

#     __tablename__ = 'bands_playlists'

#     band_id = db.Column(db.Integer, db.ForeignKey(
#         'bands.id', ondelete='cascade'), primary_key=True)

#     playlist_id = db.Column(db.Integer, db.ForeignKey(
#         'playlists.id', ondelete='cascade'), primary_key=True)


class User(db.Model):

    """A User in the application"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, db.CheckConstraint('id>0'),
                   primary_key=True, autoincrement=True)

    username = db.Column(db.String(30), nullable=False, unique=True)

    email = db.Column(db.Text, nullable=False, unique=True)

    password = db.Column(db.Text, nullable=False)

    first_name = db.Column(db.String(20), nullable=False)

    last_name = db.Column(db.String(30), nullable=True)

    profile_pic = db.Column(
        db.Text, nullable=True, default='https://media.istockphoto.com/vectors/vector-guitar-logo-icon-vector-id1197682363?k=20&m=1197682363&s=170667a&w=0&h=x0Rfh6occzSzKRjar0zQqQhR15GhM_4UrSVwHgXhXto=')

    cover_pic = db.Column(
        db.Text, nullable=True, default='https://facebooktimelinephotos.files.wordpress.com/2012/01/grass-landscape.png')

    instrument_id = db.Column(db.Integer, db.ForeignKey(
        'instruments.id', ondelete='SET NULL'), nullable=True, default=None)

    bio = db.Column(db.Text, nullable=True)

    # To be used in future updates
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow())

    instrument = db.relationship('Instrument')

    likes = db.relationship('Song', secondary='likes')

    playlists = db.relationship(
        'Playlist', secondary='playlists_users', backref='users')

    @property
    def friends(self):
        f1_ids = db.session.query(Friend.user_2).filter(
            Friend.user_1 == self.id).all()
        f1 = User.query.filter(User.id.in_(f1_ids)).all()
        f2_ids = db.session.query(Friend.user_1).filter(
            Friend.user_2 == self.id).all()
        f2 = User.query.filter(User.id.in_(f2_ids)).all()

        return f1 + f2

    @property
    def full_name(self):
        if self.last_name:
            return self.first_name + ' ' + self.last_name
        else:
            return self.first_name

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
            'last_name': self.last_name,
            'profile_pic': self.profile_pic,
        }

        if self.instrument:
            obj['instrument_name'] = self.instrument.name
            obj['instrument_icon'] = self.instrument.icon

        return json.dumps(obj)

    def check_if_friends(self, user_id):

        user = User.query.get(user_id)

        if user in self.friends:
            return True
        else:
            return False

    def send_friend_request(self, recipient_id):

        new_request = Message(
            author_id=self.id, category='fr', content='', recipient_id=recipient_id)

        db.session.add(new_request)

    def accept_friend_request(self, friend_id):

        request = Message.query.filter(
            Message.author_id == friend_id, Message.recipient_id == self.id).one()
        db.session.delete(request)

        new_friend = Friend(user_1=self.id, user_2=friend_id)
        db.session.add(new_friend)

    def deny_friend_request(self, friend_id):

        request = Message.query.filter(
            Message.author_id == friend_id, Message.recipient_id == self.id, Message.category == 'fr').first()

        if request:
            db.session.delete(request)
            return True

    def check_pending_request(self, other_user_id):

        request1 = Message.query.filter(
            Message.author_id == other_user_id, Message.recipient_id == self.id, Message.category == 'fr').first()

        request2 = Message.query.filter(
            Message.author_id == self.id, Message.recipient_id == other_user_id, Message.category == 'fr').first()

        if request1 or request2:
            return True
        else:
            return False

    def remove_friend(self, user_id):

        f1 = Friend.query.filter(
            Friend.user_1 == self.id, Friend.user_2 == user_id).first()
        f2 = Friend.query.filter(
            Friend.user_2 == self.id, Friend.user_1 == user_id).first()

        if f1:
            db.session.delete(f1)
        if f2:
            db.session.delete(f2)


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

    # To be used in future updates
    created_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow())

    # to be used in future updates
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=datetime.utcnow())

    songs = db.relationship(
        'Song', secondary='playlists_songs', backref='playlists')

    creator = db.relationship('User')

    def __repr__(self):

        return f"<Playlist {self.name} created by {self.user_id}>"

    def serialize(self):

        obj = {
            "id": self.id,
            'user_id': self.user_id,
            "name": self.name,
        }

        return json.dumps(obj)

    def add_song(self, song_id):

        playlist_song = PlaylistSong(playlist_id=self.id, song_id=song_id)
        db.session.add(playlist_song)

    def remove_song(self, song_id):
        playlist_song = PlaylistSong.query.filter(
            PlaylistSong.playlist_id == self.id, PlaylistSong.song_id == song_id).one_or_none()
        db.session.delete(playlist_song)

    def add_user(self, user_id):

        playlist_user = PlaylistUser(playlist_id=self.id, user_id=user_id)
        db.session.add(playlist_user)


class PlaylistUser(db.Model):

    """Mapping users to playlists (to keep track of each user's created playlists, saved public playlists, and shared private playlists)"""

    __tablename__ = 'playlists_users'

    playlist_id = db.Column(db.Integer, db.ForeignKey(
        'playlists.id', ondelete='cascade'), primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id', ondelete='cascade'), primary_key=True)

# ************** REVISIT LATER *****************

# class Band(db.Model):

#     """Model for a 'band' or group of users in the system"""

#     __tablename__ = 'bands'

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)

#     name = db.Column(db.String(50), nullable=False, unique=True)

#     genre = db.Column(db.String(30), nullable=True)

#     description = db.Column(db.Text, nullable=True)

#     band_pic = db.Column(db.Text, nullable=True,
#                          default='https://www.pngitem.com/pimgs/m/19-195664_rock-band-clip-art-musical-ensemble-silhouette-vector.png')

#     playlists = db.relationship('Playlist', secondary='bands_playlists')

#     members = db.relationship(
#         'User', secondary='bands_members', backref='bands')

#     messages = db.relationship('Message')

#     def __repr__(self):

#         return f"<Band {self.name}>"


class Message(db.Model):

    """Model for messages in the system, either between users or within a band"""

    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    author_id = db.Column(
        db.Integer, db.ForeignKey('users.id', ondelete='cascade'), nullable=False)

    content = db.Column(db.Text, nullable=False)

    category = db.Column(db.Text, nullable=False, default='dm')

    recipient_id = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=True)

    # band_id = db.Column(db.Integer, db.ForeignKey(
    #     'bands.id', ondelete='cascade'), nullable=True)

    # To be used for future messaging features
    time_sent = db.Column(db.DateTime, nullable=False,
                          default=datetime.utcnow())

    author = db.relationship(
        'User', primaryjoin='Message.author_id == User.id', backref='sent_msgs')

    recipient = db.relationship(
        'User', primaryjoin='Message.recipient_id == User.id', backref='received_msgs')

# band = db.relationship('Band', primaryjoin='Message.band_id == Band.id')


def connect_db(app):
    """
    Connect this database to provided Flask app.
    """

    db.app = app
    db.init_app(app)
