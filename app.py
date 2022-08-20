

from hashlib import new
import os
from models import db, connect_db, User, Instrument, Playlist, Song, Like, PlaylistUser
from forms import EditUserForm, UserLoginForm, NewUserForm
from flask import Flask, render_template, redirect, request, flash, session, g, jsonify, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import requests
from json import loads


app = Flask(__name__)


CURR_USER_KEY = "curr_user"


app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///tabular'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")

toolbar = DebugToolbarExtension(app)

connect_db(app)

CURR_USER_KEY = 'curr_user'


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


def get_instrument_choices():
    """Get all instruments and construct instrument choice tuples to pass to select field"""

    choices = [(0, 'Select Your Instrument')]

    instruments = Instrument.query.all()

    for instrument in instruments:

        choices.append(
            (instrument.id, instrument.name))

    return choices


def add_song_if_new(**kwargs):
    """Add a song to the database"""

    if Song.query.filter_by(id=kwargs['id']).first():
        return None

    song = Song(**kwargs)
    db.session.add(song)
    db.session.commit()


@app.route('/')
@app.route('/index')
def index():
    """Direct user to the welcome page if not logged in, and landing page if logged in."""
    if g.user:

        return render_template('users/current/dashboard.html', user=g.user)

    else:
        return render_template('welcome.html')


# Routes for user authentication


@app.route('/register', methods=["GET", "POST"])
def register():
    """Handle user signup.

    Create new user and add to DB.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = NewUserForm()

    if form.validate_on_submit():
        try:
            user = User.register(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                first_name=form.first_name.data or None,
                last_name=form.last_name.data or None
            )
            db.session.commit()

        except IntegrityError:
            form.username.errors.append('Username already taken!')
            return render_template('users/register.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/register.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = UserLoginForm()

    if g.user:

        return redirect('/')

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        form.username.errors.append("Invalid credentials.")

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    return redirect('/')


@app.route('/search')
def search_page():
    """Display search page."""

    if not g.user:
        flash('Access Unauthorized! Please Login', 'danger')

        return redirect('/')

    return render_template('search.html', user=g.user)


# **************
# User routes
# **************

@app.route('/users/<int:user_id>/profile')
def user_profile(user_id):
    """Display user profile page given a user ID"""

    if not g.user:
        flash('Access Unauthorized! Please Login', 'danger')

        return redirect('/')

    # If the user ID is 0, display the user page for currently logged in user
    if user_id == 0:
        return render_template('users/current/my_profile.html', user=g.user)

    user = User.query.get(user_id)

    return render_template('users/profile.html', user=user)


@app.route('/users/profile/edit', methods=['GET', 'POST'])
def edit_my_profile():
    """Display page to edit current user's profile information"""

    if not g.user:
        flash('Access Unauthorized! Please Login', 'danger')

        return redirect('/')

    form = EditUserForm(obj=g.user)

    form.instrument_id.choices = get_instrument_choices()

    if form.validate_on_submit():

        try:
            for key, value in form.data.items():

                if key == 'instrument_id' and value == 0:
                    g.user.instrument = None
                else:
                    setattr(g.user, key, value)

        except IntegrityError:
            form.username.errors.append('Username already taken!')
            return render_template('users/current/edit_profile.html', user=g.user, form=form)

        db.session.add(g.user)
        db.session.commit()

        return redirect(request.referrer)

    return render_template('users/current/edit_profile.html', user=g.user, form=form)


@app.route('/users/likes', methods=['POST'])
def toggle_like():
    """Add or remove a song from a user's liked songs"""

    # Check that a user is logged in
    if not g.user:
        flash('Access Unauthorized! Please Login', 'danger')

        return redirect('/')

    # Get the song info and add the song to the database if it isn't in the database
    data = loads(request.json['json'])
    add_song_if_new(**data)

    # check if the song is in the user's likes
    liked_song = Like.query.filter(
        Like.song_id == data['id'], Like.user_id == g.user.id).first()

    # If it is in the likes, remove it
    if liked_song:
        db.session.delete(liked_song)
        db.session.commit()
        return 'Song successfully removed from your liked songs!'

    # If it is not in the likes, add it
    else:
        new_like = Like(user_id=g.user.id, song_id=data['id'])
        db.session.add(new_like)
        db.session.commit()
        return 'Song successfully added to your liked songs!'


@app.route('/users/<int:user_id>/playlists', methods=['GET', 'POST'])
def user_playlists(user_id):
    """
    GET request: display a list of the user's playlists, given a user id

    POST request: create a new playlist, given the user id matches the currently logged in user
    """

    # Check that a user is logged in
    if not g.user:
        flash('Access Unauthorized! Please Login', 'danger')

        return redirect('/')

    # Check for POST request

    if request.method == 'POST':

        # Check that the user id is the same as the currently logged in user.
        # Users cannot create a playlist for another user
        if user_id == g.user.id:

            name = request.form['playlist-name']

            # Do not allow user to create a playlist with a duplicate name
            is_duplicate = Playlist.query.filter(
                Playlist.user_id == g.user.id, Playlist.name == name).one_or_none()

            if is_duplicate:
                return 'this is a duplicate!'
            else:
                # Create a new playlist and add a playlist user
                new_playlist = Playlist(name=name, user_id=g.user.id)
                db.session.add(new_playlist)
                db.session.commit()
                playlist_user = PlaylistUser(
                    playlist_id=new_playlist.id, user_id=g.user.id)
                db.session.add(playlist_user)
                db.session.commit()

                return redirect(url_for('user_playlists', user_id=0))

    if user_id == 0:
        # If user id is 0, direct to logged in user's playlists
        return render_template('users/current/my_playlists.html', user=g.user)

    user = User.query.get_or_404(user_id)

    return render_template('playlists/playlists.html', user=user)

# *************
# Routes for playlists
# *************


@app.route('/playlists/<int:playlist_id>')
def show_playlist(playlist_id):
    """Display page for a playlist, given a playlist id"""

    if not g.user:
        flash('Access Unauthorized! Please Login', 'danger')

        return redirect('/')

    if playlist_id == 0:
        return render_template('playlists/likes.html', user=g.user)

    playlist = Playlist.query.get_or_404(playlist_id)

    return render_template('playlists/playlist.html', playlist=playlist, user=g.user)


@app.route('/playlists/<int:playlist_id>/delete', methods=["POST"])
def delete_playlist(playlist_id):
    """Delete a playlist from the database if the currently logged in user is the creator 
    of the playlist
    """

    playlist = Playlist.query.get_or_404(playlist_id)

    if not g.user:
        flash('Access Unauthorized! Please Login', 'danger')

        return redirect('/')

    if g.user.id != playlist.creator.id:
        flash("You may not delete another user's playlist!")
        return redirect('/')

    db.session.delete(playlist)
    db.session.commit()
    return redirect(url_for('user_playlists', user_id=0))


@app.route('/playlists/add-song', methods=["POST"])
def add_song_to_playlist():

    if not g.user:
        flash('Access Unauthorized! Please Login', 'danger')

        return redirect('/')

    data = loads(request.json['json'])
    songInfo = data['songInfo']
    add_song_if_new(**songInfo)

    playlists = [playlist['id'] for playlist in data['playlists']]
    playlists = Playlist.query.filter(Playlist.id.in_(playlists)).all()
    print(playlists)

    for playlist in playlists:

        if playlist.user_id != g.user.id:
            flash("You may not add a song to another user's playlist")
            return redirect('/')

        playlist.add_song(songInfo['id'])

    db.session.commit()

    return redirect(request.referrer)


# *****************
# API ENDPOINTS
# ****************


@app.route('/api/likes')
def get_liked_songs():
    """Returns a list of song ID's for all liked songs in the database"""

    if not g.user:
        liked_songs = []

    liked_songs = [song.id for song in g.user.likes]

    return jsonify(liked_songs)


@app.route('/api/users')
def get_users():
    """Returns a list of users' info from the database"""

    query = request.args.get('query')

    # If a query is provided, search the database using the query. Otherwise get all users
    if query:
        users = User.query.filter(User.username.ilike(f'%{query}%')).all()
    else:
        users = User.query.all()

    # Remove currently logged in user from the list of users
    if g.user in users:
        idx = users.index(g.user)
        users.pop(idx)

    if users:
        users = [user.serialize() for user in users]

    else:
        users = []

    return jsonify(users)
