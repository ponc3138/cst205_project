""""
Movie Website 
By: Fernando Ponce, Ethan Pimentel, Michael Tan, Noemhi Marquez
Abstract: Movie search engine that gives users information about movies. 
Date: 05/16/2024
Course: CST205

Github Link: https://github.com/ponc3138/cst205_project

APIs Used:
https://rapidapi.com/rapihub-rapihub-default/api/imdb-top-100-movies/
https://www.omdbapi.com/


Fernando and Ethan mainly worked on backend, while Michael and Noemhi mainly 
worked on front end. All helped each other when needed, and added to / changed different
files if deemed necessary. 
"""

from flask import Flask, render_template, request, session, redirect, url_for
import pymysql
import bcrypt
import requests
import random

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# https://www.geeksforgeeks.org/how-to-connect-python-with-sql-database/
# Helped with connecting to databse
def db_connection():
    connection = pymysql.connect(
        host="z5zm8hebixwywy9d.cbetxkdyhwsb.us-east-1.rds.amazonaws.com",
        user="mhrea84z1b2h34f8",
        password="r8q2hd2wo276ny8z",
        database="f0bxmsv6e0srffqw",
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection

# Executes sql queries using pymysql to connect with the SQL database
async def execute_sql(sql, params):
    # Database connection
    connection = pymysql.connect(
        host="z5zm8hebixwywy9d.cbetxkdyhwsb.us-east-1.rds.amazonaws.com",
        user="mhrea84z1b2h34f8",
        password="r8q2hd2wo276ny8z",
        database="f0bxmsv6e0srffqw",
        cursorclass=pymysql.cursors.DictCursor
    )

    # Executes SQL Query
    try:
        with connection.cursor() as cursor:
            await cursor.execute(sql, params)
            result = cursor.fetchall()
            return result
    finally:
        # Closes connection
        connection.close()

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
        # Gets username and password 
        username = request.form['username']
        password = request.form['password']
        connection = db_connection()
        # Executes SQL query to get username and password from database
        with connection.cursor() as cursor:
            sql = "SELECT * FROM p_admin WHERE username = %s"
            cursor.execute(sql, (username,))
            row = cursor.fetchone()
            # Verification for password
            if row:
                hashed_password = row['password']
                if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
                    session['authenticated'] = True
                    return redirect(url_for('home'))
        return render_template('login.html', errorMessage="Wrong username/password!")
    return render_template('login.html', errorMessage="")


# Logs user out
@app.route('/logout')
def logout():
    session.clear()
    return render_template('login.html', errorMessage='Error!!!')


# Variable to store top 100 movies
top_100_movies = []

# https://rapidapi.com/rapihub-rapihub-default/api/imdb-top-100-movies/
# Used  that API and code to get top 100 movies
def get_top_100_movies():
    url = "https://imdb-top-100-movies.p.rapidapi.com/"
    headers = {
        "X-RapidAPI-Key": "fd68b4fcb2mshd3c6bd86561d448p19fcb6jsna886e963e385",
        "X-RapidAPI-Host": "imdb-top-100-movies.p.rapidapi.com"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        return []

# Makes sure the variiable 'top_100_movies' is populated
def ensure_movies_loaded():
    global top_100_movies
    # Checks if it's empty 
    if not top_100_movies:
        # If it is empty, calls function to populate it
        top_100_movies = get_top_100_movies()


@app.route('/searchInfo', methods=['GET', 'POST'])
def search_info():
    # Ensure the movies are loaded
    ensure_movies_loaded()

    # Get 20 movies
    random_movies = random.sample(top_100_movies, 20)

    if not is_authenticated():
        return redirect(url_for('login'))
    # Passes the list 'random_movies' to the 'searchInfo.html' file
    return render_template('searchInfo.html', random_movies=random_movies)



# https://www.omdbapi.com/
# Used API to get movie information
@app.route('/search', methods=['POST'])
def search():
    if not is_authenticated():
        return redirect(url_for('login'))

    ensure_movies_loaded()

    # Checks if 'random' button is pressed in the search form
    if 'random' in request.form:
        # Gets movie title from list
        random_movie = random.choice(top_100_movies)
        movie_title = random_movie['title']
    # If not, gets movie title from user input
    else:
        movie_title = request.form['title']


    # Get movie data from API
    api_key = 'f3b20a94'
    response = requests.get(f'http://www.omdbapi.com/?apikey={api_key}&t={movie_title}')
    movie_data = response.json()
    # Renders 'search.html' template with the movie data 
    return render_template('search.html', movieData=movie_data)



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/newUser')
def new_user():
    return render_template('newUser.html')


# https://www.geeksforgeeks.org/sql-using-python/
# Used link to help us put user into database
@app.route('/newUser', methods=['GET', 'POST'])
def new_user_info():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  

        # Hash the password
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        connection = db_connection()
        
        try:
            with connection.cursor() as cursor:
                # SQL query to insert username and hashed password into the database
                sql = "INSERT INTO p_admin (username, password) VALUES (%s, %s)"
                # Execute query with username and hashed password 
                cursor.execute(sql, (username, hashed_password))
                connection.commit()
        except Exception as e:
            # If an error occurs
            connection.rollback()
            print("Error:", e)
        finally:
            # Close database connection
            connection.close()

        # Go to success page
        return redirect(url_for('new_user_success', username=username))
    return render_template('newUser.html')


@app.route('/newUserSuccess/<username>')
def new_user_success(username):
    return render_template('newUserSuccess.html', username=username)

# if __name__ == '__main__':
#     app.run(debug=True)

