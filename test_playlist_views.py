"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, Message, User, Playlist, PlaylistUser, Friend, Song, Like, PlaylistSong
import json

os.environ['DATABASE_URL'] = "postgresql:///tabular-test"

from app import app, CURR_USER_KEY
# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class PlaylistViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        # Add sample users

        testuser = User.register(username="testuser",
                                 email="test@test.com",
                                 password="testuser",
                                 first_name='testuser',
                                 last_name=None)
        testuser.id = 8989
        self.testuser_id = 8989

        user2 = User.register(username="user2",
                              email="user2@test.com",
                              password="testuser",
                              first_name='user2',
                              last_name=None)
        user2.id = 9546
        self.user2_id = 9546

        user3 = User.register(username="user3",
                              email="user3@test.com",
                              password="testuser",
                              first_name='user3',
                              last_name=None)
        user3.id = 6745
        self.user3_id = 6745

        user4 = User.register(username="user4",
                              email="user4@test.com",
                              password="testuser",
                              first_name='user4',
                              last_name=None)
        user4.id = 76845
        self.user4_id = 76845

        nathan = User.register(username='nathan', email='nathan@test.com',
                               password='nathan', first_name='nathan', last_name=None)
        nathan.id = 12647
        self.nathan_id = 12647

        db.session.commit()

        # add user created playlists

        testuserp1 = Playlist(id=1111, name='testuser Jams',
                              user_id=self.testuser_id)
        testuserp2 = Playlist(
            id=2222, name='testuser Favorites', user_id=self.testuser_id)

        user2p1 = Playlist(id=3333, name='user2 Jams', user_id=self.user2_id)
        user2p2 = Playlist(id=4444, name='user2 Favorites',
                           user_id=self.user2_id)

        user3p1 = Playlist(id=5555, name='user3 Jams', user_id=self.user3_id)

        db.session.add_all([testuserp1, testuserp2, user2p1, user2p2, user3p1])
        db.session.commit()

        # Add playlist/user relationship for created playlists
        pu1 = PlaylistUser(user_id=self.testuser_id, playlist_id=1111)
        pu2 = PlaylistUser(user_id=self.testuser_id, playlist_id=2222)
        pu3 = PlaylistUser(user_id=self.user2_id, playlist_id=3333)
        pu4 = PlaylistUser(user_id=self.user2_id, playlist_id=4444)
        pu5 = PlaylistUser(user_id=self.user3_id, playlist_id=5555)
        db.session.add_all([pu1, pu2, pu3, pu4, pu5])
        db.session.commit()

        # add some iked playlists
        liked_playlist1 = PlaylistUser(
            user_id=self.testuser_id, playlist_id=3333)
        liked_playlist2 = PlaylistUser(
            user_id=self.nathan_id, playlist_id=5555)
        db.session.add_all([liked_playlist1, liked_playlist2])
        db.session.commit()

        # Add friend relationships
        f1 = Friend(user_1=self.testuser_id, user_2=self.user2_id)
        f2 = Friend(user_1=self.testuser_id, user_2=self.user3_id)

        db.session.add_all([f1, f2])
        db.session.commit()

        # Add a few songs

        s1 = Song(id=4444, title='Jammin',
                  artist='Bob Marley', tab_url='placeholder')
        s2 = Song(id=5555, title='Rock and Roll',
                  artist='Led Zeppelin', tab_url='placeholder')
        s3 = Song(id=6666, title='Angie',
                  artist='The Rolling Stones', tab_url='placeholder')
        db.session.add_all([s1, s2, s3])
        db.session.commit()

        # Add some songs to testuser's likes
        l1 = Like(user_id=self.testuser_id, song_id=4444)
        l2 = Like(user_id=self.testuser_id, song_id=5555)
        db.session.add_all([l1, l2])
        db.session.commit()

        # Add some songs to playlists
        ps1 = PlaylistSong(song_id=4444, playlist_id=1111)
        ps2 = PlaylistSong(song_id=5555, playlist_id=1111)
        ps3 = PlaylistSong(song_id=6666, playlist_id=3333)
        ps4 = PlaylistSong(song_id=4444, playlist_id=5555)
        db.session.add_all([ps1, ps2, ps3, ps4])
        db.session.commit()

        self.testuser = User.query.get(8989)
        self.user2 = User.query.get(9546)
        self.user3 = User.query.get(6745)
        self.user4 = User.query.get(76845)
        self.nathan = User.query.get(12647)
        self.testuserp1 = Playlist.query.get(1111)
        self.testuserp2 = Playlist.query.get(2222)
        self.user2p1 = Playlist.query.get(3333)
        self.user2p2 = Playlist.query.get(4444)
        self.user3p1 = Playlist.query.get(5555)
        self.song1 = Song.query.get(4444)
        self.song2 = Song.query.get(5555)
        self.song3 = Song.query.get(6666)

    def test_own_playlist_page(self):
        """
        Test that a user can view their own playlist page if logged in,
        with options to add or remove songs, or delete playlist
        """

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f'/playlists/{self.testuserp1.id}')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Jammin', str(resp.data))
            self.assertIn('Rock and Roll', str(resp.data))
            self.assertNotIn('Angie', str(resp.data))
            self.assertIn('Delete Playlist', str(resp.data))
            self.assertIn('Add Songs', str(resp.data))
            self.assertIn('Remove From Playlist', str(resp.data))

    def test_other_playlist_page(self):
        """
        Test that a user can view another user's playlist page if logged in,
        but does not have the option to add songs or delete playlist
        """

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f'/playlists/{self.user2p1.id}')

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('Jammin', str(resp.data))
            self.assertNotIn('Rock and Roll', str(resp.data))
            self.assertIn('Angie', str(resp.data))
            self.assertNotIn('Delete Playlist', str(resp.data))
            self.assertNotIn('Add Songs', str(resp.data))
            self.assertNotIn('Remove From Playlist', str(resp.data))

    def test_nonexistent_playlist_page(self):
        """
        Test that a 404 is returned if a user tries to view the page
        for a playlist that does not exist
        """
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get('/playlists/12548')

            self.assertEqual(resp.status_code, 404)
            self.assertIn(
                'The resource or page you are looking for', str(resp.data))

    def test_likes_page(self):
        """Test that a user can view their liked songs page if logged in"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get('/playlists/0')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Jammin', str(resp.data))
            self.assertIn('Rock and Roll', str(resp.data))
            self.assertNotIn('Angie', str(resp.data))

    def test_delete_own_playlist(self):
        """Test that the user can delete their own playlist if logged in"""
        self.assertEqual(len(self.testuser.playlists), 3)
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(
                f'/playlists/{self.testuserp1.id}/delete', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.testuser = User.query.get(self.testuser_id)
            self.assertEqual(len(self.testuser.playlists), 2)
            self.assertIn('MY PLAYLISTS', str(resp.data))

    def test_delete_other_user_playlist(self):
        """Test that the user cannot delete another user's playlist"""
        self.assertEqual(len(self.user2.playlists), 2)
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(
                f'/playlists/{self.user2p1.id}/delete', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.user2 = User.query.get(self.user2_id)
            self.assertEqual(len(self.user2.playlists), 2)
            self.assertIn('You may not delete', str(resp.data))
            self.assertIn('DASHBOARD', str(resp.data))

    def test_delete_nonexistent_playlist(self):
        """
        Test that a 404 is returned if a user tries to delete
        a playlist that does not exist
        """
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post('/playlists/12548/delete')

            self.assertEqual(resp.status_code, 404)
            self.assertIn(
                'The resource or page you are looking for', str(resp.data))

    def test_add_song_to_own_playlist(self):
        """Test if user can add a song to their own playlist"""

        self.assertEqual(len(self.testuserp2.songs), 0)
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            obj = {'songInfo': {
                'id': self.song1.id,
                'title': self.song1.title,
                'artist': self.song1.artist,
                'tab_url': self.song1.tab_url
            }, 'playlists': [{"id": self.testuserp2.id, "user_id": self.testuser.id, "name": self.testuserp2.name}]

            }

            resp = c.post('/playlists/add-song',
                          json={"json": json.dumps(obj)}, headers={
                              "Referer": '/playlists/2222'
                          }, follow_redirects=True)
            self.testuserp2 = Playlist.query.get(2222)
            self.assertEqual(len(self.testuserp2.songs), 1)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(self.testuserp2.name, str(resp.data))
            self.assertIn(self.song1.title, str(resp.data))

    def test_add_song_to_other_user_playlist(self):
        """Test that user cannot add a song to another user's playlist"""

        self.assertEqual(len(self.user2p2.songs), 0)
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            obj = {'songInfo': {
                'id': self.song1.id,
                'title': self.song1.title,
                'artist': self.song1.artist,
                'tab_url': self.song1.tab_url
            }, 'playlists': [{"id": self.user2p2.id, "user_id": self.user2.id, "name": self.user2p2.name}]

            }

            resp = c.post('/playlists/add-song',
                          json={"json": json.dumps(obj)}, follow_redirects=True)
            self.user2p2 = Playlist.query.get(4444)
            self.assertEqual(len(self.user2p2.songs), 0)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('DASHBOARD', str(resp.data))
            self.assertIn('You may not', str(resp.data))

    def test_remove_song_from_own_playlist(self):
        """Test if user can remove a song from one of their own playlists"""

        self.assertEqual(len(self.user2p1.songs), 1)
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id

            obj = {
                'id': self.song3.id,
                'title': self.song3.title,
                'artist': self.song3.artist,
                'tab_url': self.song3.tab_url
            }

            resp = c.post(f'/playlists/{self.user2p1.id}/remove-song', json={"json": json.dumps(obj)}, headers={
                "Referer": f'/playlists/{self.user2p1.id}'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.user2p1 = Playlist.query.get(3333)
            self.assertIn(
                self.user2p1.name, str(resp.data))
            self.assertNotIn(self.song3.title, str(resp.data))
            self.assertEqual(len(self.user2p1.songs), 0)

    def test_remove_song_from_other_user_playlist(self):
        """Test that the user cannot remove a song from another user's playlist"""

        self.assertEqual(len(self.user3p1.songs), 1)
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            obj = {
                'id': self.song1.id,
                'title': self.song1.title,
                'artist': self.song1.artist,
                'tab_url': self.song1.tab_url
            }

            resp = c.post(f'/playlists/{self.user3p1.id}/remove-song',
                          json={"json": json.dumps(obj)}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.user3p1 = Playlist.query.get(5555)
            self.assertIn('DASHBOARD', str(resp.data))
            self.assertIn('You may not remove', str(resp.data))
            self.assertEqual(len(self.user3p1.songs), 1)

    def test_remove_from_nonexistent_playlist(self):
        """
        Test that a 404 is returned if a user tries to remove a song
        from a playlist that does not exist
        """
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            obj = {
                'id': self.song1.id,
                'title': self.song1.title,
                'artist': self.song1.artist,
                'tab_url': self.song1.tab_url
            }

            resp = c.post('/playlists/12548/remove-song',
                          json={"json": json.dumps(obj)})

            self.assertEqual(resp.status_code, 404)
            self.assertIn(
                'The resource or page you are looking for', str(resp.data))

    def test_like_playlist(self):
        """Test that a user can like another user's playlist"""

        self.assertEqual(len(self.user3.playlists), 1)
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user3.id

            resp = c.post(f'/playlists/{self.user2p1.id}/like', headers={
                          'Referer': f'/users/{self.user3.id}/playlists'}, follow_redirects=True)

            self.user3 = User.query.get(self.user3.id)
            self.assertEqual(len(self.user3.playlists), 2)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Playlist successfully added', str(resp.data))
            self.assertIn(self.user2p1.name, str(resp.data))

    def test_like_own_playlist(self):
        """Test that a user cannot like their own playlist"""

        self.assertEqual(len(self.user2.playlists), 2)
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id

            resp = c.post(f'/playlists/{self.user2p1.id}/like', headers={
                          'Referer': f'/users/{self.user2.id}/playlists'}, follow_redirects=True)

            self.user2 = User.query.get(self.user2.id)
            self.assertEqual(len(self.user2.playlists), 2)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('You cannot like', str(resp.data))
            self.assertIn(self.user2p1.name, str(resp.data))
            self.assertIn(self.user2p2.name, str(resp.data))

    def test_like_already_liked_playlist(self):
        """Test that a user cannot like a playlist that they have already liked"""

        self.assertEqual(len(self.nathan.playlists), 1)
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.nathan.id

            resp = c.post(f'/playlists/{self.user3p1.id}/like', headers={
                          'Referer': f'/users/{self.nathan.id}/playlists'}, follow_redirects=True)

            self.nathan = User.query.get(self.nathan.id)
            self.assertEqual(len(self.nathan.playlists), 1)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('You already like', str(resp.data))
            self.assertIn(self.user3p1.name, str(resp.data))

    def test_like_nonexistent_playlist(self):
        """Test that a 404 is returned if a user tries to like a playlist that does not exist"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f'playlists/837364/like')

            self.assertEqual(resp.status_code, 404)

    def test_unlike_playlist(self):
        """Test that a user can unlike a liked playlist"""

        self.assertEqual(len(self.nathan.playlists), 1)
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.nathan.id

            resp = c.post(f'/playlists/{self.user3p1.id}/unlike', headers={
                          'Referer': f'/users/{self.nathan.id}/playlists'}, follow_redirects=True)

            self.nathan = User.query.get(self.nathan.id)
            self.assertEqual(len(self.nathan.playlists), 0)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Playlist successfully removed', str(resp.data))
            self.assertNotIn(self.user3p1.name, str(resp.data))

    def test_unlike_playlist_not_liked(self):
        """
        Test that a user cannot unlike a playlist that is not in 
        their liked playlists
        """
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user4.id

            resp = c.post(f'/playlists/{self.user3p1.id}/unlike', headers={
                          'Referer': f'/users/{self.user4.id}/playlists'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('This playlist is not', str(resp.data))
            self.assertIn('MY PLAYLISTS', str(resp.data))

    def test_unlike_nonexistent_playlist(self):
        """Test that a 404 is returned if a user tries to unlike a playlist that does not exist"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f'playlists/837364/unlike')

            self.assertEqual(resp.status_code, 404)
