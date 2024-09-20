from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, UserCollection, init_db
from helpers import get_spotify_client, search_spotify_album
import requests
import json
import re
import time


app = Flask(__name__)
app.secret_key = 'yoursecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///record_collection.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

DISCOGS_KEY = 'SCtzOnNEsRmZdJCNXPdw'
DISCOGS_SECRET = 'MrThSnTxABZdKmUguaAYQsWJvTfqIuqa'
MAX_RETRIES = 5

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def fetch_with_retry(url, params, retries=MAX_RETRIES):
    while retries > 0:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            if response.text.strip():  # Ensure response is not empty
                return response
            else:
                print("Error: Received empty response")
                return None
        elif response.status_code == 429:
            print("Rate limited. Retrying...")
            time.sleep(2 ** (MAX_RETRIES - retries))  # Exponential backoff
            retries -= 1
        else:
            print(f"HTTP error: {response.status_code} {response.text}")
            return None
    return None

@app.route('/')
@login_required
def index():
    collections = current_user.collections
    return render_template('index.html', collections=collections)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        if User.query.filter_by(username=username).first():
            flash('Username already exists.')
            return redirect(url_for('register'))

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        artist = request.form.get('artist', '').strip()
        album = request.form.get('album', '').strip()
        format = request.form.get('format', '').strip()
        barcode = request.form.get('barcode', '').strip()

        url = 'https://api.discogs.com/database/search'
        params = {
            'key': DISCOGS_KEY,
            'secret': DISCOGS_SECRET,
        }

        if barcode:
            params['barcode'] = barcode
            
        if artist and not album and not format:
            params['q'] = artist
            params['type'] = 'artist'
        elif album and not artist and not format:
            params['release_title'] = album
            params['type'] = 'release'
        elif artist and album and not format:
            params['q'] = artist
            params['release_title'] = album
            params['type'] = 'release'
        elif artist and format and not album:
            params['q'] = artist
            params['format'] = format
            params['type'] = 'release'
        elif format and album and not artist:
            params['release_title'] = album
            params['format'] = format
            params['type'] = 'release'
        elif format and not artist and not album:
            params['format'] = format
        elif artist and album and format:
            params['q'] = artist
            params['release_title'] = album
            params['format'] = format
            params['type'] = 'release'

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            search_results = response.json().get('results', [])
        except requests.exceptions.RequestException as e:
            flash(f"An error occurred: {e}")
            return redirect(url_for('search'))


        for result in search_results:
            result['year'] = result.get('year', 'N/A')
            result['country'] = result.get('country', 'N/A')
            result['labels'] = result.get('label', [])
            result['format'] = result.get('format', 'N/A')
            result['cover_image'] = result.get('cover_image', 'https://via.placeholder.com/150')

            if 'label' in result and isinstance(result['label'], list):
                result['labels'] = result['label']
            else:
                result['labels'] = []

            if 'format' in result and isinstance(result['format'], list):
                result['formats'] = result['format']
            else:
                result['formats'] = []

        return render_template('search_artist_album.html', search_results=search_results)
    return render_template('search_artist_album.html')

@app.route('/add_to_collection', methods=['POST'])
@login_required
def add_to_collection():
    try:
        release_data = json.loads(request.form['release_data'])
        selected_label = request.form['selected_label']
        selected_format = request.form['selected_format']
        artist_album = re.split(' - ', release_data['title'])
        artist = artist_album[0]
        album = artist_album[1]


        spotify_client = get_spotify_client()
        spotify_album_id = search_spotify_album(spotify_client, album, artist)

        new_record = UserCollection(
            user_id=current_user.id,
            release_id=release_data['id'],
            title=release_data['title'],
            cover_image=release_data.get('cover_image', ''),
            year=release_data.get('year', 'N/A'),
            country=release_data.get('country', 'N/A'),
            selected_label=selected_label,
            selected_format=selected_format,
            spotify_album_id=spotify_album_id
        )
        db.session.add(new_record)
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        print("Error:", str(e))
        return redirect(url_for('search'))

@app.route('/delete_from_collection/<int:collection_id>', methods=['POST'])
@login_required
def delete_from_collection(collection_id):
    try:
        record = UserCollection.query.get_or_404(collection_id)
        if record.user_id != current_user.id:
            flash('You do not have permission to delete this item.')
            return redirect(url_for('index'))

        db.session.delete(record)
        db.session.commit()
        return redirect(url_for('index'))
    except Exception as e:
        print("Error:", str(e))
        return redirect(url_for('index'))

@app.route('/item_details/<int:collection_id>')
@login_required
def item_details(collection_id):
    record = UserCollection.query.get_or_404(collection_id)
    if record.user_id != current_user.id:
        flash('You do not have permission to view this item.')
        return redirect(url_for('index'))

    release_url = f"https://api.discogs.com/releases/{record.release_id}"
    master_url = f"https://api.discogs.com/masters/{record.release_id}"
    response_release = requests.get(release_url)
    response_master = requests.get(master_url)

    release_data = response_release.json()
    master_data = response_master.json()

    if not release_data or not master_data:
        flash('Something is wrong with this release')
        return render_template('search_artist_album.html')

    return render_template('item_details.html', record=record, release_data=release_data, master_data=master_data)

@app.route('/artist/<int:artist_id>/albums')
@login_required
def artist_albums(artist_id):
    url = f'https://api.discogs.com/artists/{artist_id}/releases'
    params = {
        'sort': 'year',
        'sort_order': 'desc',
        'key': DISCOGS_KEY,
        'secret': DISCOGS_SECRET,
    }
    response = requests.get(url, params=params)

    releases_response = fetch_with_retry(url, params)
    if not releases_response:
        flash('Failed to fetch artist releases')
        return redirect(url_for('index'))

    try:
        releases = releases_response.json().get('releases', [])
    except ValueError as e:
        print(f"Error parsing JSON response: {str(e)}")
        print("Response content:", releases_response.text)
        flash('Error parsing artist releases data')
        return redirect(url_for('index'))

    detailed_releases = []

    for release in releases:
        try:
            if release.get('type') == 'master':
                release_url = f"https://api.discogs.com/masters/{release['id']}"
            else:
                release_url = f"https://api.discogs.com/releases/{release['id']}"

            release_response = fetch_with_retry(release_url, params)
            if not release_response:
                continue



            if release_response.text.strip():
                detailed_release = release_response.json()
                detailed_release['year'] = detailed_release.get('year', 'N/A')
                detailed_release['country'] = detailed_release.get('country', 'N/A')
                detailed_release['labels'] = detailed_release.get('labels', [])
                detailed_release['formats'] = detailed_release.get('formats', [])
                detailed_release['images'] = detailed_release.get('images', [])
                detailed_releases.append(detailed_release)
            else:
                print("Error: Received empty release response")

        except ValueError as e:
                print(f"Error parsing JSON response: {str(e)}")
                print("Response content:", release_response.text)
                continue

    return render_template('artist_albums.html', releases=detailed_releases)

@app.route('/users')
@login_required
def users():
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('users.html', users=users)

@app.route('/user/<int:user_id>/collection')
@login_required
def user_collection(user_id):
    user = User.query.get_or_404(user_id)
    collections = user.collections
    is_followee = user in current_user.followees
    return render_template('user_collection.html', user=user, collections=collections, is_followee=is_followee)

@app.route('/add_friend/<int:user_id>', methods=['POST'])
@login_required
def follow(user_id):
    user = User.query.get_or_404(user_id)
    try:
        if user not in current_user.followees:
            current_user.followees.append(user)
            db.session.commit()
            flash('You now follow this user!')
        else:
            flash('You already follow this user.')
    except Exception as e:
        print(f"Error: {str(e)}")
        flash('An error occurred while adding friend.')
    return redirect(url_for('user_collection', user_id=user_id))

@app.route('/followees')
@login_required
def followees():
    followees = current_user.followees.all()
    return render_template('followees.html', followees=followees)

if __name__ == '__main__':
    app.run(debug=True)
