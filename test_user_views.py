"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, Message, User, Playlist, PlaylistUser, Friend, Song, Like
import json

os.environ['DATABASE_URL'] = "postgresql:///tabular-test"

from app import app, CURR_USER_KEY
# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
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

        db.session.add_all([testuserp1, testuserp2, user2p1, user2p2])
        db.session.commit()

        # Add playlist/user relationship for created playlists
        pu1 = PlaylistUser(user_id=self.testuser_id, playlist_id=1111)
        pu2 = PlaylistUser(user_id=self.testuser_id, playlist_id=2222)
        pu3 = PlaylistUser(user_id=self.user2_id, playlist_id=3333)
        pu4 = PlaylistUser(user_id=self.user2_id, playlist_id=4444)
        db.session.add_all([pu1, pu2, pu3, pu4])

        # add one of user2's playlists to testuser's liked playlists
        liked_playlist = PlaylistUser(
            user_id=self.testuser_id, playlist_id=3333)
        db.session.add(liked_playlist)
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

        # Add a song to testuser's likes
        l1 = Like(user_id=self.testuser_id, song_id=4444)
        l2 = Like(user_id=self.user2_id, song_id=5555)
        db.session.add_all([l1, l2])
        db.session.commit()

        # add a friend request

        fr1 = Message(id=6758, author_id=self.nathan_id,
                      recipient_id=self.user3_id, content='', category='fr')
        fr2 = Message(id=6888, author_id=self.nathan_id,
                      recipient_id=self.user2_id, content='', category='fr')
        db.session.add_all([fr1, fr2])
        db.session.commit()

        self.testuser = User.query.get(8989)
        self.user2 = User.query.get(9546)
        self.user3 = User.query.get(6745)
        self.nathan = User.query.get(12647)
        self.song1 = Song.query.get(4444)
        self.song2 = Song.query.get(5555)
        self.song3 = Song.query.get(6666)

    def test_dashboard(self):
        """Does app show the dashboard if user is logged in?"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get('/')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('See What Your Friends Are Playing:', str(resp.data))

    def test_welcome(self):
        """Does app show the welcome page if user is not logged in?"""

        with self.client as c:

            resp = c.get('/')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Get Started', str(resp.data))

    def test_my_profile(self):
        """Test if user can view their profile page if logged in"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f'/users/{self.testuser.id}/profile')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Edit Profile', str(resp.data))

    def test_other_user_profile(self):
        """Test if user can view other user's profile if logged in"""

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f'/users/{self.user2.id}/profile')

            self.assertEqual(resp.status_code, 200)
            self.assertIn(
                f"@{self.user2.username}", str(resp.data))
            self.assertNotIn('Edit Profile', str(resp.data))

    def test_user_profile_unauthorized(self):
        """
        Can a user access a user profile page if not logged in?
        This test covers any route that includes a '@login_required' decorator
        """
        with self.client as c:

            resp = c.get(f'/users/{self.user2.id}/profile')

            self.assertEqual(resp.status_code, 302)

            resp = c.get(f'/users/{self.user2.id}/profile',
                         follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
        self.assertIn('Access Unauthorized!', str(resp.data))

    def test_edit_profile_page(self):
        """Can user access the edit profile page if logged in?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f'users/profile/edit')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Delete Profile', str(resp.data))

    def test_delete_profile(self):
        """Can user delete their profile if logged in?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f'users/profile/delete', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Get Started', str(resp.data))

            self.assertIsNone(User.query.filter_by(
                id=self.testuser.id).one_or_none())

    def test_add_like(self):
        """User should be able to like a song if logged in"""

        obj = {
            'id': self.song2.id,
            'title': self.song2.title,
            'artist': self.song2.artist,
            'tab_url': self.song2.tab_url
        }

        self.assertEqual(len(self.testuser.likes), 1)
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.post('/users/likes', json={"json": json.dumps(obj)})
            self.testuser = User.query.get(self.testuser_id)
            self.assertEqual(len(self.testuser.likes), 2)

    def test_remove_like(self):
        """User should be able to remove a like if logged in and song is already liked"""

        obj = {
            'id': self.song2.id,
            'title': self.song2.title,
            'artist': self.song2.artist,
            'tab_url': self.song2.tab_url
        }

        self.assertEqual(len(self.user2.likes), 1)
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id
            resp = c.post('/users/likes', json={"json": json.dumps(obj)})
            self.user2 = User.query.get(self.user2_id)
            self.assertEqual(len(self.user2.likes), 0)

    def test_my_playlists_page(self):
        """
        Is the user able to access their playlists page if logged in?
        Does it show the correct playlists?
        """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get(
                f'/users/{self.testuser.id}/playlists')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser Jams', str(resp.data))
            self.assertIn('testuser Favorites', str(resp.data))
            self.assertIn('user2 Jams', str(resp.data))
            self.assertNotIn('user2 Favorites', str(resp.data))
            self.assertIn('Create a New Playlist', str(resp.data))

    def test_friend_playlists_page(self):
        """Can user access another a friend's playlists page if logged in?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get(
                f'/users/{self.user2.id}/playlists')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('user2 Jams', str(resp.data))
            self.assertNotIn('testuser Jams', str(resp.data))
            self.assertNotIn('Create a New Playlist', str(resp.data))

    def test_non_friend_playlists_page(self):
        """
        User should not be able to access a user's playlists page
        if they are not friends
        """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get(
                f'/users/{self.nathan.id}/playlists', follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You must be friends', str(resp.data))
            self.assertIn('DASHBOARD', str(resp.data))

    def test_create_playlist(self):
        """User should be able to create a new playlist if logged in"""

        self.assertEqual(len(self.testuser.playlists), 3)
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.post(
                f'/users/{self.testuser.id}/playlists', data={'playlist-name': 'test playlist'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Playlist successfully', str(resp.data))
            self.assertIn('test playlist', str(resp.data))

            self.testuser = User.query.get(self.testuser_id)
            self.assertEqual(len(self.testuser.playlists), 4)

    def test_create_playlist_unauthorized(self):
        """User should not be able to create a playlist for another user"""

        self.assertEqual(len(self.user2.playlists), 2)
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.post(
                f'/users/{self.user2.id}/playlists', data={'playlist-name': 'test playlist'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You cannot create', str(resp.data))
            self.assertIn('DASHBOARD', str(resp.data))

            self.user2 = User.query.get(self.user2_id)
            self.assertEqual(len(self.user2.playlists), 2)

    def test_duplicate_playlist(self):
        """User should not be able to create a playlist with a duplicate name"""

        self.assertEqual(len(self.user2.playlists), 2)
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id
            resp = c.post(
                f'/users/{self.user2.id}/playlists', data={'playlist-name': 'user2 Jams'}, headers={
                    "Referer": f'/users/{self.user2.id}/playlists'
                }, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('PLAYLISTS', str(resp.data))
            self.user2 = User.query.get(self.user2_id)
            self.assertEqual(len(self.user2.playlists), 2)

    def test_send_friend_request(self):
        """User should be able to send a request to a user they are not friends with"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f'/users/request-friend/{self.nathan.id}', headers={
                          'Referer': f'/users/{self.nathan.id}/profile'}, follow_redirects=True)

            request = Message.query.filter(Message.author_id == self.testuser.id,
                                           Message.recipient_id == self.nathan.id).one_or_none()

            self.assertIsNotNone(request)
            self.assertEqual(request.category, 'fr')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Friend Request Pending', str(resp.data))

    def test_send_duplicate_request(self):
        """Users should not be able to send duplicate requests"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.nathan.id

            resp = c.post(f'/users/request-friend/{self.user3.id}', headers={
                          'Referer': f'/users/{self.user3.id}/profile'}, follow_redirects=True)

            request = Message.query.filter(Message.author_id == self.nathan.id,
                                           Message.recipient_id == self.user3.id).one_or_none()

            self.assertIsNotNone(request)
            self.assertEqual(request.category, 'fr')
            self.assertEqual(resp.status_code, 200)
            self.assertIn('There is already', str(resp.data))

    def test_already_friends(self):
        """Users should not be able to send a friend request to a user they are already friends with"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f'/users/request-friend/{self.user2.id}', headers={
                          'Referer': f'/users/{self.user2.id}/profile'}, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You are already friends!', str(resp.data))

    def test_accept_request(self):
        """Users should be able to accept a pending friend request"""
        request = Message.query.filter(
            Message.author_id == self.nathan.id, Message.recipient_id == self.user2.id).one_or_none()
        self.assertIsNotNone(request)
        self.assertEqual(len(self.user2.friends), 1)
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.id

            resp = c.post(f'/users/accept-request/{self.nathan.id}', headers={
                          'Referer': '/messages'}, follow_redirects=True)

            request = Message.query.filter(
                Message.author_id == self.nathan.id, Message.recipient_id == self.user2.id).one_or_none()
            self.assertIsNone(request)

            self.user2 = User.query.get(self.user2_id)
            self.assertEqual(len(self.user2.friends), 2)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You have successfully', str(resp.data))

    def test_deny_request(self):
        """Users should be able to deny a pending friend request"""

        request = Message.query.filter(
            Message.author_id == self.nathan.id, Message.recipient_id == self.user3.id).one_or_none()
        self.assertIsNotNone(request)
        self.assertEqual(len(self.user3.friends), 1)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user3.id

            resp = c.post(f'/users/deny-request/{self.nathan.id}', headers={
                          'Referer': '/messages'}, follow_redirects=True)

            request = Message.query.filter(
                Message.author_id == self.nathan.id, Message.recipient_id == self.user3.id).one_or_none()
            self.assertIsNone(request)

            self.user3 = User.query.get(self.user3_id)
            self.assertEqual(len(self.user3.friends), 1)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('MESSAGES', str(resp.data))

    def test_my_friends_page(self):
        """User should be able to view their friends page if logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get(
                f'/users/{self.testuser.id}/friends')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('user2', str(resp.data))
            self.assertIn('user3', str(resp.data))
            self.assertIn('MY FRIENDS', str(resp.data))
            self.assertNotIn('nathan', str(resp.data))

    def test_user_friends_page(self):
        """User should be able to view other users' friends page if logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            resp = c.get(
                f'/users/{self.user2.id}/friends')

            self.assertEqual(resp.status_code, 200)
            self.assertIn('testuser', str(resp.data))
            self.assertNotIn('user3', str(resp.data))
            self.assertNotIn('nathan', str(resp.data))

    def test_remove_friend(self):
        """
        User should be able to remove a friend if logged in and friends with user.
        """

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # test for a user that testuser is friends with
            self.assertEqual(len(self.testuser.friends), 2)
            resp = c.post(
                f'/users/remove-friend/{self.user2.id}')
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(len(self.testuser.friends), 1)
