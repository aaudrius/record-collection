# Record Collection App

This is a web application made for record collectors who would like to have their record collection stored, managed and shared with other users within one app. 
This app allows users to search for records, add them to their collection, and view details about each record.
It also allows users to listen to certain records if it is available.
It integrates with the Discogs and Spotify APIs to fetch record information and cover images and to listen to the records if they are available on Spotify.
The app also allows users to browse the collections of other users and follw them.

## Features
- User registration and authentication
- Search for records by artist, album, format or barcode
- Add records to your collection
- View, edit, and delete records in your collection
- View details of each record
- Listen to record if it is available on Spotify
- Follow other users and view their collections
- Calculate the total value of your collection or collections of users you follw based on the price of each record

## Tech Stack
- Flask
- SQLAlchemy (with SQLite)
- Flask-Migrate
- Flask-Login
- Discogs API
- Spotify API
- Bootstrap (for UI)

## Installation

### Prerequisites
- Python 3.x
- Virtual environment (recommended)

### Clone the Repository
```bash
git clone https://github.com/yourusername/record-collection-app.git
cd record-collection-app
```

### Set Up Virtual Environment
It is recommended to create a virtual environment to isolate the project dependencies.
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

### Install Dependencies
Install the necessary dependencies using pip:
```bash
pip install -r requirements.txt
```

### Environment Variables
Create a .env file in the root directory and add the following environment variables. These variables are necessary for the integration with the Discogs and Spotify APIs:
```
DISCOGS_KEY=your_discogs_api_key
DISCOGS_SECRET=your_discogs_api_secret
FLASK_APP=app.py
FLASK_ENV=development
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SECRET_KEY=your_flask_secret_key
```

### Initialize Database
Run the following command to migrate the database schema:
```
flask db upgrade
```

### Run the Application
Start the Flask development server using:
```
flask run
```
The application should now be running on `http://127.0.0.1:5000`.

### Project Structure
```
record-collection-app/
│
├── app.py                  # Main Flask application file
├── models.py               # Database models
├── helpers.py              # Helper functions (Spotify client, search functions)
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables
├── migrations/             # Database migrations
├── templates/
│   ├── base.html           # Base template
│   ├── index.html          # Home page template, collection of current user
│   ├── login.html          # Login page template
│   ├── register.html       # Registration page template
│   ├── search_artist_album.html  # Search results template
│   ├── user_collection.html  # User collection template
│   ├── users.html            # All registered users list template
│   ├── followees.html        # Users follwed by current user list template
│   └── item_details.html     # Collection item details (album/release) template
└── static/                 # Images
    ├── css/                # CSS files
    └── js/                 # JavaScript files
```

## Usage
### User Registration and Login
1. **Register:** Create a new account by providing a username and password on the registration page.
2. **Login:** Log in with your credentials to access the app.

### Searching for Records
#### Album search
- **Artist:** Enter an artist's name to find all records and releases by that artist (field mandatory).
- **Album:** Enter an album title to find specific albums and releases.
- **Format:** Select a format (e.g., Vynil, CD, Cassette, etc.) from the dropdown menu to filter the search.
#### Barcode search
- **Barcode:** Enter or scan a barcode of your release to find it in discogs database.

### Adding records to your collection
1. **Search:** Perform a search using the form on the search page (album search or barcode search).
2. **Select:** From search results select the label of your release and click "Add to Collection".
3. **View Collection:** Go to the home page to see all the records in your collection.

### Viewing and managigng your collection
- **Home Page:** View all records in your collection. Click any item to view it's details.
- **Total value:** See the total value of your collection based on the price of each item.
- **Delete:** Delete records from your collection.

### Following other users
1. **Users page:** View the list of the users registered to the app.
2. **View Users' Collections:** Click on a user to view their collection (only the list of albums, without item details and value of collection).
3. **Follow Users:** Follow users to sstay updated to their collection additions, view details of their records and value of their collection.

## API integration
### Discogs API
The app uses the discogs API to search for the records and fetch detailed info about them. You need to register for a Discogs API key and secret. This can be done [here](https://www.discogs.com/developers)

### Spotify API
The app uses Spotify API to provide the possibility to listen to certain albums when viewing album details if certain album is available on Spotify. You need to register for a Spotify API client ID and secret, which could be done [here](https://developer.spotify.com/documentation/web-api)

## ACKNOWLEGMENTS
- **[Flask](https://flask.palletsprojects.com/en/3.0.x/)**
- **[Discogs API](https://www.discogs.com/developers)**
- **[Spotify API](https://developer.spotify.com/documentation/web-api)**
- **[Bootstrap](https://getbootstrap.com/)**
