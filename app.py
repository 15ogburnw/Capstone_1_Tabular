import os

from flask import Flask, render_template, redirect, request, flash, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User
from forms import UserLoginForm, NewUserForm

CURR_USER_KEY = "curr_user"

app = Flask(__name__)


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


@app.route('/')
@app.route('/index')
def index():
    """Direct user to the welcome page if not logged in, and landing page if logged in."""
    if g.user:

        return render_template('users/dashboard.html', user=g.user)

    else:
        return render_template('welcome.html')


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


@app.route('/playlists')
def my_playlists():

    return 'testing url_for'
