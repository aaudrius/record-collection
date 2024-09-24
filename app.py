import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Users, UserCollections, init_db
from helpers import get_spotify_client, search_spotify_album
import requests
import json
import re
import time
from config import config

load_dotenv()

app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'default')])

init_db(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

DISCOGS_KEY = os.getenv('DISCOGS_KEY')
DISCOGS_SECRET = os.getenv('DISCOGS_SECRET')
MAX_RETRIES = 5

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

def fetch_with_retry(url, params, retries=MAX_RETRIES):
    while retries > 0:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            if response.text.strip():
                return response
            else:
                print("Error: Received empty response")
                return None
        elif response.status_code == 429:
            print("Rate limited. Retrying...")
            time.sleep(2 ** (MAX_RETRIES - retries))
            retries -= 1
        else:
            print(f"HTTP error: {response.status_code} {response.text}")
            return None
    return None

def fetch_detailed_release_info(result_id, result_type):
    if result_type == 'master':
        url = f"https://api.discogs.com/masters/{result_id}"
    else:
        url = f"https://api.discogs.com/releases/{result_id}"

    params = {
        'key': DISCOGS_KEY,
        'secret': DISCOGS_SECRET,
    }

    detailed_response = fetch_with_retry(url, params)
    if detailed_response:
        return detailed_response.json()
    return None

@app.route('/')
@login_required
def index():
    collections = current_user.collections
    total_value = sum(record.price for record in collections if record.price is not None)
    return render_template('index.html', collections=collections, total_value=total_value)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)

        if Users.query.filter_by(username=username).first():
            flash('Username already exists.')                        
            return redirect(url_for('register'))
                                                                                                                                                                                                                                                                                                                                                                                                                                              
        new_user = Users(username=username, password=hashed_password)
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
        user = Users.query.filter_by(username=username).first()

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
        barcode = request.form.get('barcode', '').strip()
        format = request.form.get('format', '').strip()
        search_type = request.form.get('search_type')

        url = 'https://api.discogs.com/database/search'
        params = {
            'key': DISCOGS_KEY,
            'secret': DISCOGS_SECRET,
        }

        if search_type == 'album_search':
            params['artist'] = artist
            params['release_title'] = album
            
        if search_type == 'barcode_search':
            params['barcode'] = barcode

        if format:
            params['format'] = format

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
            formats = result.get('format', [])
            result['format'] = formats[0] if formats else 'N/A'
            result['cover_image'] = result.get('cover_image', 'https://via.placeholder.com/150')

            if 'label' in result and isinstance(result['label'], list):
                result['labels'] = result['label']
            else:
                result['labels'] = []

        return render_template('search_artist_album.html', search_results=search_results)
    return render_template('search_artist_album.html')


@app.route('/add_to_collection', methods=['POST'])
@login_required
def add_to_collection():
    try:
        release_data = json.loads(request.form['release_data'])
        selected_label = request.form['selected_label']
        artist_album = re.split(' - ', release_data['title'])
        artist = artist_album[0]
        album = artist_album[1]

        detailed_info = fetch_detailed_release_info(release_data['id'], release_data['type'])
        lowest_price = detailed_info.get('lowest_price', None) if detailed_info else None

        spotify_client = get_spotify_client()
        spotify_album_id = search_spotify_album(spotify_client, album, artist)

        new_record = UserCollections(
            user_id=current_user.id,
            release_id=release_data['id'],
            title=release_data['title'],
            cover_image=release_data.get('cover_image', ''),
            year=release_data.get('year', 'N/A'),
            country=release_data.get('country', 'N/A'),
            format=release_data.get('format', 'N/A'),
            price=lowest_price,
            selected_label=selected_label,
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
        record = UserCollections.query.get_or_404(collection_id)
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
    record = UserCollections.query.get_or_404(collection_id)
    if record.user_id != current_user.id:
        user = Users.query.get_or_404(record.user_id)
        is_followee = True if user in current_user.followees else False
    else:
        is_followee = False
    if record.user_id == current_user.id or user in current_user.followees:

        release_url = f"https://api.discogs.com/releases/{record.release_id}"
        master_url = f"https://api.discogs.com/masters/{record.release_id}"
        response_release = requests.get(release_url)
        response_master = requests.get(master_url)
        release_data = response_release.json()
        master_data = response_master.json()

    else:
        print(current_user.followees.all(), record.user_id)
        flash('You do not have permission to view this item.')
        return redirect(url_for('index'))

    if not release_data or not master_data:
        flash('Something is wrong with this release')
        return render_template('search_artist_album.html')

    return render_template('item_details.html', record=record, release_data=release_data, master_data=master_data, is_followee=is_followee)

@app.route('/users')
@login_required
def users():
    users = Users.query.filter(Users.id != current_user.id).all()
    return render_template('users.html', users=users)

@app.route('/user/<int:user_id>/collection')
@login_required
def user_collection(user_id):
    user = Users.query.get_or_404(user_id)
    collections = user.collections
    total_value = sum(record.price for record in collections if record.price is not None)
    is_followee = user in current_user.followees
    return render_template('user_collection.html', user=user, collections=collections, is_followee=is_followee, total_value=total_value)

@app.route('/add_friend/<int:user_id>', methods=['POST'])
@login_required
def follow(user_id):
    user = Users.query.get_or_404(user_id)
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

@app.route('/unfollow/<int:user_id>', methods=['POST'])
@login_required
def unfollow(user_id):
    user = Users.query.get_or_404(user_id)

    try:
        if user in current_user.followees:
            current_user.followees.remove(user)
            db.session.commit()
            flash('You have unfollowed this user.')
        else:
            flash('You do not follow this user.')
    except Exception as e:
        print(f"Error: {str(e)}")
        flash('An error occurred while unfollowing the user.')
    
    return redirect(url_for('user_collection', user_id=user_id))

if __name__ == '__main__':
    app.run(debug=True)
