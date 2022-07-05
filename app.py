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
    name = session.get('username', None)

    if name:
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
    name = session.get('username', None)

    if name:
        return redirect(check_permission())
    else:
        return render_template('/login/login_form.html')


@app.route('/logout')
def logout():
    session.pop('username')
    return render_template('/login/login_form.html')


@app.route('/submit', methods=['POST'])
def submit():
    login = request.form['login']
    password = request.form['password']

    # Inserting driver already signed into users table
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
    if 'admin' != check_permission():
        return render_template('generic_error.html', message='User not allowed to see this content')

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
    if 'constructor' != check_permission():
        return render_template('generic_error.html', message='User not allowed to see this content')

    # getting constructor info
    name = session.get('username')
    constructor_ref = name[0:-2]

    # executing overview functions
    sql_query = f'''
    SELECT * FROM constructor_victories_count('{constructor_ref}'); 
                           '''
    count_victories = pd.read_sql_query(sql_query, conn)

    sql_query = f'''
    SELECT * FROM constructors_drivers_count('{constructor_ref}'); 
                           '''
    count_drivers = pd.read_sql_query(sql_query, conn)

    sql_query = f'''
    SELECT * FROM constructors_first_and_last_year('{constructor_ref}'); 
                           '''
    date_range = pd.read_sql_query(sql_query, conn)

    return render_template('constructors/overview.html',
                           name=name,
                           count_victories=count_victories.loc[0][0],
                           count_drivers=count_drivers.loc[0][0],
                           start_year=date_range.loc[0]['first_year'],
                           end_year=date_range.loc[0]['last_year'])


@app.route('/driver', methods=['GET'])
def driver_view():
    if 'driver' != check_permission():
        return render_template('generic_error.html', message='User not allowed to see this content')

    # getting driver info
    name = session.get('username')
    driver_ref = name[0:-2]
    sql_query = f'''
    SELECT * FROM driver where driverref = '{driver_ref}'; 
                           '''
    driver_info = pd.read_sql_query(sql_query, conn)
    driver_forename = driver_info.loc[0]['forename']
    driver_surname = driver_info.loc[0]['surname']

    # executing overview functions
    sql_query = f'''
    SELECT * FROM drivers_victories('{driver_forename}', '{driver_surname}')                   '''
    count_victories = pd.read_sql_query(sql_query, conn)

    sql_query = f'''
    SELECT * FROM drivers_first_and_last_year('{driver_forename}', '{driver_surname}')
                        '''
    date_range = pd.read_sql_query(sql_query, conn)

    return render_template('driver/overview.html',
                           name=name,
                           count_victories=count_victories.loc[0][0],
                           start_year=date_range.loc[0]['first_year'],
                           end_year=date_range.loc[0]['last_year'])


@app.route('/create-constructors', methods=['GET', 'POST'])
def create_constructors():
    if 'admin' != check_permission():
        return render_template('generic_error.html', message='User not allowed to see this content')
    else:
        if request.method == 'GET':
            return render_template('admin/create_constructors.html')
        else:
            constructor_ref = request.form['constructor_ref']
            constructorid = request.form['constructorid']
            name = request.form['name']
            nationality = request.form['nationality']
            url = request.form['url']

            sql_query = f'''
                INSERT INTO constructors (constructorid, constructorref, name, nationality, url)  VALUES ('{constructorid}', '{constructor_ref}','{name}','{nationality}','{url}');
            '''
            conn.execute(sql_query)

            # check user type and redirect to adequate page
            user_type = check_permission()
            return redirect(user_type)


@app.route('/create-drivers', methods=['GET', 'POST'])
def create_drivers():
    if 'admin' != check_permission():
        return render_template('generic_error.html', message='User not allowed to see this content')
    else:
        if request.method == 'GET':
            return render_template('admin/create_drivers.html')
        else:
            driverid = request.form['driverid']
            driverref = request.form['driver_ref']
            number = request.form['number']
            code = request.form['code']
            forename = request.form['forename']
            surname = request.form['surname']
            date_of_birth = request.form['date_of_birth']
            nationality = request.form['nationality']

            sql_query = f'''
                INSERT INTO driver (driverid, driverref, number, code, forename, surname, nationality, dob)  VALUES ('{driverid}', '{driverref}','{number}','{code}','{forename}', '{surname}', '{nationality}', '{date_of_birth}');
            '''
            conn.execute(sql_query)

            # check user type and redirect to adequate page
            user_type = check_permission()
            return redirect(user_type)


@app.route('/search-drivers', methods=['GET', 'POST'])
def search_drivers():
    if 'constructor' != check_permission():
        return render_template('generic_error.html', message='User not allowed to see this content')
    else:
        if request.method == 'GET':
            return render_template('constructors/search_driver.html')
        else:
            forename = request.form['forename']

            sql_query = f'''
                SELECT * FROM driver where forename = '{forename}'; 
            '''
            driver_info = pd.read_sql_query(sql_query, conn)
            # create a list of dict with search result
            list = driver_info.to_dict('records')

            name = session.get('username')
            constructor_ref = name[0:-2]

            sql_query = f'''
                SELECT DISTINCT driverid from results where constructorid = (select constructorid from constructors where constructorref = '{constructor_ref}')
            '''
            constructor_drivers_df = pd.read_sql_query(sql_query, conn)

            constructor_drivers = constructor_drivers_df.to_dict('list')

            result_set = [
                driver
                for driver
                in list
                if driver.get('driverid') in constructor_drivers['driverid']
            ]

            return render_template('/constructors/search_results.html', drivers=result_set)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
