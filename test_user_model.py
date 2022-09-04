"""User model tests."""

from models import db, User, Friend
from sqlalchemy import exc
from unittest import TestCase
import json

import os
os.environ['DATABASE_URL'] = "postgresql:///tabular-test"

from app import app


class UserModelTestCase(TestCase):
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

        self.user1 = User.query.get(user1id)
        self.user1id = user1id

        self.user2 = User.query.get(user2id)
        self.user2id = user2id

        self.user3 = User.query.get(user3id)
        self.user3id = user3id

    def tearDown(self):
        super().tearDown()
        db.session.rollback()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            first_name='test'
        )

        db.session.add(u)
        db.session.commit()

        # User should have no friends, messages, likes, or playlists
        self.assertEqual(len(u.friends), 0)
        self.assertEqual(len(u.sent_msgs), 0)
        self.assertEqual(len(u.received_msgs), 0)
        self.assertEqual(len(u.likes), 0)
        self.assertEqual(len(u.playlists), 0)

    def test_repr(self):
        """Test for __repr__ method"""

        self.assertEqual(self.user1.__repr__(
        ), f"<User #{self.user1.id}, username: {self.user1.username}, email: {self.user1.email}>")

    def test_add_friend(self):
        """Test that the friends property works"""

        friend = Friend(user_1=self.user1id, user_2=self.user2id)
        db.session.add(friend)
        db.session.commit()

        self.assertEqual(len(self.user1.friends), 1)
        self.assertEqual(len(self.user2.friends), 1)
        self.assertEqual(len(self.user3.friends), 0)

        self.assertEqual(self.user1.friends[0].id, self.user2.id)
        self.assertEqual(self.user2.friends[0].id, self.user1.id)

    def test_full_name(self):
        """Test full name property"""

        self.assertEqual(self.user1.full_name, 'testUser One')
        self.assertEqual(self.user2.full_name, 'otherTestUser')

    def test_check_if_friends(self):
        """Test that the check_if_friends method works"""

        friend = Friend(user_1=self.user1id, user_2=self.user2id)
        db.session.add(friend)
        db.session.commit()

        self.assertTrue(self.user1.check_if_friends(self.user2id))
        self.assertTrue(self.user2.check_if_friends(self.user1id))
        self.assertFalse(self.user1.check_if_friends(self.user1id))
        self.assertFalse(self.user2.check_if_friends(self.user2id))

    def test_serialize(self):
        """Test that the serialize method works"""

        obj = {
            'id': self.user1.id,
            'username': self.user1.username,
            'first_name': self.user1.first_name,
            'last_name': self.user1.last_name,
            'profile_pic': self.user1.profile_pic,
        }

        self.assertEqual(self.user1.serialize(), json.dumps(obj))

    def test_register(self):
        """Test that a the register method works with valid credentials"""

        new_user = User.register(
            username='test_user', email='test_user@gmail.com', password='test_user', first_name="test", last_name=None)
        new_user_id = 4000
        new_user.id = new_user_id

        db.session.commit()

        new_user = User.query.get(new_user_id)

        self.assertEqual(new_user.id, new_user_id)
        self.assertEqual(new_user.username, 'test_user')
        self.assertEqual(new_user.email, 'test_user@gmail.com')
        self.assertNotEqual(new_user.password, 'test_user')
        self.assertEqual(new_user.first_name, 'test')
        self.assertIsNone(new_user.last_name)
        self.assertEqual(new_user.profile_pic,
                         'images/default_profile_pic.png')
        self.assertEqual(new_user.cover_pic, 'images/default_cover_pic.jpg')

    def test_invalid_username(self):
        """Test that an error is raised when attempting to register with an invalid username"""

        User.register(None, 'invalid@gmail.com', 'invalid', 'invalid', None)

        with self.assertRaises(exc.IntegrityError):
            db.session.commit()

    def test_invalid_email(self):
        """Test that an error is raised when attempting to register with an invalid email"""

        User.register('invalid', None, 'invalid', 'invalid', None)

        with self.assertRaises(exc.IntegrityError):
            db.session.commit()

    def test_invalid_password(self):
        """Test that an error is raised when attempting to register with an invalid password"""

        with self.assertRaises(ValueError):
            User.register('invalid', 'invalid@gmail.com',
                          None, 'invalid', None)

    def test_no_first_name(self):
        """Test that an error is raised when attempting to register with a no first name"""
        User.register('invalid', 'invalid@gmail.com',
                      'invalid', None, None)
        with self.assertRaises(exc.IntegrityError):
            db.session.commit()

    def test_duplicate_username(self):
        """Test that an error is raised when attempting to register with a username that is already taken"""

        User.register('test1', 'invalid@gmail.com', 'invalid', 'invalid', None)

        with self.assertRaises(exc.IntegrityError):
            db.session.commit()

    def test_duplicate_email(self):
        """
        Test that an error is raised when attempting to register with an email that is already
        associated with an existing account
        """

        User.register('newtest', 'test1@gmail.com', 'invalid', 'invalid', None)

        with self.assertRaises(exc.IntegrityError):
            db.session.commit()

    # # Tests for user authentication method

    def test_valid_auth(self):
        """Test that a the correct user is returned when valid credentials are entered into the authenticate method"""

        self.assertEqual(User.authenticate(
            username='test1', password='test1'), self.user1)

    def test_invalid_username_auth(self):
        """Test that the authenticate method returns an error when an invalid username is entered"""

        self.assertFalse(User.authenticate('wrong', 'test1'))

    def test_invalid_password_auth(self):
        """Test that the authenticate method returns an error when an invalid password is entered"""

        self.assertFalse(User.authenticate('test1', 'wrong'))
