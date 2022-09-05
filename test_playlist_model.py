"""User model tests."""

from models import db, User, Playlist, Song, PlaylistUser, PlaylistSong
from unittest import TestCase
import json

import os
os.environ['DATABASE_URL'] = "postgresql:///tabular-test"

from app import app


class PlaylistModelTestCase(TestCase):
    """Test user model"""

    def setUp(self):
        """add sample data."""

        db.drop_all()
        db.create_all()

        user1 = User.register(
            username='test1', email='test1@gmail.com', password='test1', first_name='testUser', last_name='One')
        user1id = 1000
        user1.id = user1id

        user2 = User.register(
            username='test2', email='test2@gmail.com', password='test2', first_name='otherTestUser', last_name=None)
        user2id = 2000
        user2.id = user2id

        user3 = User.register(
            username='test3', email='test3@gmail.com', password='test3', first_name='testUser', last_name='Three')
        user3id = 3000
        user3.id = user3id

        db.session.commit()

        playlist1 = Playlist(user_id=user1id, name='user1 Jams')
        p1id = 1111
        playlist1.id = p1id
        playlist2 = Playlist(user_id=user1id, name='user1 Favorites')
        p2id = 2222
        playlist2.id = p2id
        playlist3 = Playlist(user_id=user2id, name='user2 Jams')
        p3id = 3333
        playlist3.id = p3id

        pu1 = PlaylistUser(user_id=user1id, playlist_id=p1id)
        pu2 = PlaylistUser(user_id=user1id, playlist_id=p2id)
        pu3 = PlaylistUser(user_id=user2id, playlist_id=p3id)

        db.session.add_all([playlist1, playlist2, playlist3])
        db.session.commit()
        db.session.add_all([pu1, pu2, pu3])
        db.session.commit()

        song1 = Song(id=7777, artist="song1", title='song1', tab_url='song1')
        db.session.add(song1)
        db.session.commit()

        sp1 = PlaylistSong(song_id=7777, playlist_id=p2id)
        db.session.add(sp1)
        db.session.commit()

        self.user1 = User.query.get(user1id)
        self.user1id = user1id

        self.user2 = User.query.get(user2id)
        self.user2id = user2id

        self.user3 = User.query.get(user3id)
        self.user3id = user3id

        self.playlist1 = Playlist.query.get(p1id)
        self.playlist2 = Playlist.query.get(p2id)
        self.playlist3 = Playlist.query.get(p3id)

    def tearDown(self):
        super().tearDown()
        db.session.rollback()

    def test_playlist_model(self):
        """Does basic model work?"""

        p = Playlist(
            user_id=self.user3id,
            name='test'
        )

        db.session.add(p)
        db.session.commit()

        # Playlist should have no songs
        self.assertEqual(len(p.songs), 0)

    def test_repr(self):
        """Test for __repr__ method"""

        self.assertEqual(self.playlist1.__repr__(
        ), f"<Playlist {self.playlist1.name} created by {self.playlist1.user_id}>")

    def test_serialize(self):
        """Test that the serialize method works"""

        obj = {
            "id": self.playlist1.id,
            'user_id': self.playlist1.user_id,
            "name": self.playlist1.name,
        }

        self.assertEqual(self.playlist1.serialize(), json.dumps(obj))

    def test_creator(self):
        """Test creator relationship"""

        self.assertIsInstance(self.playlist1.creator, User)
        self.assertEqual(self.playlist1.creator.id, self.user1.id)

    def test_add_song(self):
        """Test that the add_song method works"""

        song = Song(id=1864, title='testSong',
                    artist='testArtist', tab_url='test')
        db.session.add(song)
        db.session.commit()

        self.assertEqual(len(self.playlist1.songs), 0)

        self.playlist1.add_song(1864)
        db.session.commit()
        self.assertEqual(len(self.playlist1.songs), 1)
        self.assertEqual(self.playlist1.songs[0].id, 1864)

    def test_add_user(self):
        """Test that the add_user method works"""

        self.assertEqual(len(self.playlist1.users), 1)

        self.playlist1.add_user(self.user2id)
        db.session.commit()

        self.assertEqual(len(self.playlist1.users), 2)

    def test_remove_song(self):
        """Test that the remove_song method works"""

        self.assertEqual(len(self.playlist2.songs), 1)

        self.playlist2.remove_song(self.playlist2.songs[0].id)
        db.session.commit()
        self.assertEqual(len(self.playlist2.songs), 0)
