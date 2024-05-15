# # flask --app main --debug run
from flask import Flask, render_template, request, session, redirect, url_for
import pymysql
import bcrypt
import requests
# import json 

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

async def execute_sql(sql, params):
    connection = pymysql.connect(
        host="z5zm8hebixwywy9d.cbetxkdyhwsb.us-east-1.rds.amazonaws.com",
        user="mhrea84z1b2h34f8",
        password="r8q2hd2wo276ny8z",
        database="f0bxmsv6e0srffqw",
        cursorclass=pymysql.cursors.DictCursor
    )

    try:
        with connection.cursor() as cursor:
            await cursor.execute(sql, params)
            result = cursor.fetchall()
            return result
    finally:
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


@app.route('/logout')
def logout():
    session.clear()
    return render_template('login.html', errorMessage='Error!!!')
    

@app.route('/searchInfo',methods=['GET', 'POST'])
def search_info():
    if not is_authenticated():
        return redirect(url_for('login'))
    return render_template('searchInfo.html', movieData=None)


@app.route('/search', methods=['POST'])
def search():
    if not is_authenticated():
        return redirect(url_for('login'))
    movie_title = request.form['title']
    print(movie_title)
    api_key = 'f3b20a94'
    response = requests.get(f'http://www.omdbapi.com/?apikey={api_key}&t={movie_title}')
    movie_data = response.json()
    return render_template('search.html', movieData=movie_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/newUser')
def new_user():
    return render_template('newUser.html')

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
                # SQL query to insert username and hashed password into the table
                sql = "INSERT INTO p_admin (username, password) VALUES (%s, %s)"
                # Execute the query with username and hashed password as parameters
                cursor.execute(sql, (username, hashed_password))
                connection.commit()
        except Exception as e:
            # If an error occurs
            connection.rollback()
            # Handle the error
            print("Error:", e)
        finally:
            # Close database connection
            connection.close()

        # Redirect to success page
        return redirect(url_for('new_user_success', username=username))
    return render_template('newUser.html')


@app.route('/newUserSuccess/<username>')
def new_user_success(username):
    return render_template('newUserSuccess.html', username=username)

# if __name__ == '__main__':
#     app.run(debug=True)

