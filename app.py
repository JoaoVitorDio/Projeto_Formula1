import os
import pandas as pd
from flask.cli import load_dotenv
from pandas import read_sql_query
from sqlalchemy import create_engine, text
from flask import Flask, render_template, request, redirect, session

# Creating environment based on .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Reading environment variables to get database name and password
DATABASES = {
    'production': {
        'NAME': os.environ['DATABASE_NAME'],
        'USER': os.environ['DATABASE_USERNAME'],
        'PASSWORD': os.environ['DATABASE_PASSWORD'],
        'HOST': '127.0.0.1',
        'PORT': 5432,
    },
}

# choose the database to use
db = DATABASES['production']
# construct an engine connection string
engine_string = "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}".format(
    user=db['USER'],
    password=db['PASSWORD'],
    host=db['HOST'],
    port=db['PORT'],
    database=db['NAME']
)

# create sqlalchemy engine
engine = create_engine(engine_string)
conn = engine.connect()

app = Flask(__name__)
app.secret_key = 'super_secret'


def execute_sql_query_from_file(filename):
    sql = open(filename, 'r')
    df = read_sql_query(sql.read(), conn)
    sql.close()
    return df


def check_permission():
    if 'username' in session:
        name = session.get('username')

        if name.endswith('_c'):
            return 'constructor'
        elif name.endswith('_d'):
            return 'driver'
        else:
            return 'admin'
    else:
        return render_template('generic_error.html', message='User not logged in. Please go to login page.')


@app.route('/')
def index():
    return render_template('/login/login_form.html')


@app.route('/submit', methods=['POST'])
def submit():
    login = request.form['login']
    password = request.form['password']

    # Inserting drivers already signed into users table
    sqlQuery = f'''
    SELECT userid, login, tipo, idoriginal FROM users WHERE login = '{login}' and 
                           password = MD5(CONCAT('{password}',userID))
                           '''
    df = pd.read_sql_query(sqlQuery, conn)

    if len(df.index) > 0:
        # saves username into session
        session['username'] = login

        # check user type and redirect to adequate page
        user_type = check_permission()
        return redirect(user_type)

    else:
        return render_template('generic_error.html', message='Wrong username or password. Try again.')


@app.route('/admin', methods=['GET'])
def admin_view():
    sql_query = f'''
    SELECT DISTINCT COUNT(*) FROM driver; 
                           '''
    count_drivers = pd.read_sql_query(sql_query, conn)

    sql_query = f'''
    SELECT DISTINCT COUNT(*) FROM constructors; 
                           '''
    count_constructors = pd.read_sql_query(sql_query, conn)

    sql_query = f'''
    SELECT DISTINCT COUNT(*) FROM races; 
                           '''
    count_races = pd.read_sql_query(sql_query, conn)

    sql_query = f'''
    SELECT DISTINCT COUNT(*) FROM seasons; 
                           '''
    count_seasons = pd.read_sql_query(sql_query, conn)

    return render_template('/admin/overview.html',
                           name='Admin',
                           count_drivers=count_drivers.loc[0][0],
                           count_races=count_races.loc[0][0],
                           count_seasons=count_seasons.loc[0][0],
                           count_constructors=count_constructors.loc[0][0])


@app.route('/constructor', methods=['GET'])
def constructor_view():
    if 'username' in session:
        name = session.get('username')

    return render_template('constructors/overview.html', name=name)


@app.route('/driver', methods=['GET'])
def driver_view():
    if 'username' in session:
        name = session.get('username')

    return render_template('driver/overview.html', name=name)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
