

import os
from models import db, connect_db, User, Instrument, Playlist, Song, Like
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


# Routes for currently logged in user

@app.route('/users/profile')
def my_profile():
    """Display page for logged in user's profile"""

    if not g.user:
        flash('Access Unauthorized! Please Login', 'danger')

        return redirect('/')

    return render_template('/users/current/profile.html', user=g.user)


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

    if not g.user:
        flash('Access Unauthorized! Please Login', 'danger')

        return redirect('/')

    data = loads(request.json['json'])

    add_song_if_new(**data)

    liked_song = Like.query.filter(
        Like.song_id == data['id'], Like.user_id == g.user.id).first()

    if liked_song:
        db.session.delete(liked_song)
        db.session.commit()
        return 'Song successfully removed from your liked songs!'

    else:
        new_like = Like(user_id=g.user.id, song_id=data['id'])
        db.session.add(new_like)
        db.session.commit()
        return 'Song successfully added to your liked songs!'


@app.route('/users/playlists', methods=['GET', 'POST'])
def my_playlists():

    if not g.user:
        flash('Access Unauthorized! Please Login', 'danger')

        return redirect('/')

    if request.method == 'POST':

        name = request.form['playlist-name']

        is_duplicate = Playlist.query.filter(
            Playlist.user_id == g.user.id, Playlist.name == name).one_or_none()

        if is_duplicate:
            return 'this is a duplicate!'
        else:
            new_playlist = Playlist(name=name, user_id=g.user.id)
            db.session.add(new_playlist)
            db.session.commit()
            return redirect(url_for('my_playlists'))

    return render_template('playlists/my_playlists.html', user=g.user)


# Endpoints for other users' info

@app.route('/users/<int:user_id>/profile')
def user_profile(user_id):

    if not g.user:
        flash('Access Unauthorized! Please Login', 'danger')

        return redirect('/')

    user = User.query.get_or_404(user_id)

    return render_template('users/profile.html', user=user)


@app.route('/playlists/<int:playlist_id>')
def show_playlist(playlist_id):

    if not g.user:
        flash('Access Unauthorized! Please Login', 'danger')

        return redirect('/')

    if playlist_id == 0:
        return render_template('playlists/likes.html', user=g.user)

    playlist = Playlist.query.get_or_404(playlist_id)

    return render_template('playlists/playlist.html', playlist=playlist, user=g.user)


@app.route('/playlists/<int:playlist_id>/delete', methods=["POST"])
def delete_playlist(playlist_id):

    playlist = Playlist.query.get_or_404(playlist_id)

    if not g.user:
        flash('Access Unauthorized! Please Login', 'danger')

        return redirect('/')

    if g.user.id != playlist.creator.id:
        flash("You may not delete another user's playlist!")
        return redirect('/')

    db.session.delete(playlist)
    db.session.commit()
    return redirect(url_for('my_playlists'))


@app.route('/playlists/<int:playlist_id>/add', methods=["POST"])
def add_song_to_playlist(playlist_id):
    print('come_back')


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

    query = request.args.get('query')

    if query:
        users = User.query.filter(User.username.ilike(f'%{query}%')).all()
    else:
        users = User.query.all()

    if g.user in users:
        idx = users.index(g.user)
        users.pop(idx)

    if users:
        users = [user.serialize() for user in users]

    else:
        users = []

    return jsonify(users)
