# from flask import Flask, render_template
# from flask_bootstrap import Bootstrap
# import random
# import os
# from PIL import Image

# app = Flask(__name__)
# bootstrap = Bootstrap(app) 

# @app.route('/')
# def home():
#     # # Generate a random number between 1 and 10
#     # random_number = random.randint(1, 10)

#     # # Example of passing data to the template
#     return render_template('index.html')

# # playlist = []

# # def store_song(my_song):
# #     playlist.append(dict(
# #         song = my_song,
# #         date = datetime.today()
# #     ))

# # @app.route('/', methods=('GET', 'POST'))
# # def index():
# #     form = Playlist()
# #     if form.validate_on_submit():
# #         store_song(form.song_title.data)
# #         return redirect('/view_playlist')
# #     return render_template('index.html', form=form)

# # flask --app main --debug run
from flask import Flask, render_template, request, session, redirect, url_for
import pymysql
import bcrypt
import requests

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Database connection
def db_connection():
    connection = pymysql.connect(
        host="z5zm8hebixwywy9d.cbetxkdyhwsb.us-east-1.rds.amazonaws.com",
        user="mhrea84z1b2h34f8",
        password="r8q2hd2wo276ny8z",
        database="f0bxmsv6e0srffqw",
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

# Check if user is authenticated
def is_authenticated():
    return 'authenticated' in session and session['authenticated']

# Home route
@app.route('/')
def home():
    if not is_authenticated():
        return redirect(url_for('login'))
    return render_template('index.html')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = db_connection()
        with connection.cursor() as cursor:
            sql = "SELECT * FROM p_admin WHERE username = %s"
            cursor.execute(sql, (username,))
            row = cursor.fetchone()
            if row:
                hashed_password = row['password']
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                    session['authenticated'] = True
                    return redirect(url_for('home'))
        return render_template('login.html', errorMessage="Wrong username/password!")
    return render_template('login.html', errorMessage="")

# Logout route
# @app.route('/logout')
# def logout():
#     session.pop('authenticated', None)
#     return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    return render_template('login.html', errorMessage='Error!!!')
    

@app.route('/searchInfo', methods=['GET'])
def search_info():
    if not is_authenticated():
        return redirect(url_for('login'))
    return render_template('searchInfo.html', movieData=None)


@app.route('/search', methods=['POST'])
def search():
    if not is_authenticated():
        return redirect(url_for('login'))
    movie_title = request.form['title']
    api_key = 'f3b20a94'
    response = requests.get(f'http://www.omdbapi.com/?apikey={api_key}&t={movie_title}')
    movie_data = response.json()
    return render_template('search.html', movieData=movie_data)


# @app.route('/newUser', methods=['POST'])
# def new_user():
#     # Extract username and password from the request
#     user = request.form['username']
#     passw = request.form['password']
    
#     # SQL query to insert new user
#     sql = "INSERT INTO p_admin (username, password) VALUES (?, ?)"
#     params = (user, passw)
    
#     # Execute SQL query
#     data = execute_sql(sql, params)
    
#     # Render login page after inserting user
#     return render_template('login.html')


# if __name__ == '__main__':
#     app.run(debug=True)

