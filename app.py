import os
import pandas as pd
from flask.cli import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from flask import Flask, render_template, request, redirect, session
import datetime

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


def check_permission():
    user = session.get('user', None)

    if user:
        if user['type'] == 'Escuderia':
            return 'constructor'
        elif user['type'] == 'Piloto':
            return 'driver'
        else:
            return 'admin'

    else:
        return render_template('generic_error.html', message='User not logged in. Please go to login page.')


@app.route('/')
def index():
    user = session.get('user', None)

    if user:
        return redirect(check_permission())
    else:
        return render_template('/login/login_form.html')


@app.route('/logout')
def logout():
    session.pop('user')
    return render_template('/login/login_form.html')


@app.route('/submit', methods=['POST'])
def submit():
    login = request.form['login']
    password = request.form['password']

    # Inserting driver already signed into users table
    sqlQuery = f'''
    SELECT userid, login, tipo, idoriginal, tipo FROM users WHERE login = '{login}' and 
                           password = MD5(CONCAT('{password}',userID))
                    '''
    df = pd.read_sql_query(sqlQuery, conn)

    if len(df.index) > 0:
        user_list = df.to_dict('record')
        # saves username into session

        session['user'] = {
            'id': user_list[0]['idoriginal'],
            'username': user_list[0]['login'],
            'user_ref': login[0:-2],
            'type': user_list[0]['tipo']
        }
        # check user type and redirect to adequate page
        user_type = check_permission()


        sql_query = f'''
            INSERT INTO log_table VALUES (DEFAULT,{df.loc[0].userid}, '{datetime.datetime.now()}');
                        '''
        conn.execute(sql_query)
        
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
    user = session.get('user')
    constructor_ref = user['user_ref']

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
                           name=user['username'],
                           count_victories=count_victories.loc[0][0],
                           count_drivers=count_drivers.loc[0][0],
                           start_year=date_range.loc[0]['first_year'],
                           end_year=date_range.loc[0]['last_year'])


@app.route('/driver', methods=['GET'])
def driver_view():
    if 'driver' != check_permission():
        return render_template('generic_error.html', message='User not allowed to see this content')

    # getting driver info
    user = session.get('user')
    driver_ref = user['user_ref']

    sql_query = f'''
    SELECT * FROM driver where driverref = '{driver_ref}'; 
                    '''

    driver_info = pd.read_sql_query(sql_query, conn)
    driver_forename = driver_info.loc[0]['forename']
    driver_surname = driver_info.loc[0]['surname']

    # executing overview functions
    sql_query = f'''
    SELECT * FROM drivers_victories('{driver_forename}', '{driver_surname}')                   
                    '''
    count_victories = pd.read_sql_query(sql_query, conn)

    sql_query = f'''
    SELECT * FROM drivers_first_and_last_year('{driver_forename}', '{driver_surname}')
                        '''
    date_range = pd.read_sql_query(sql_query, conn)

    return render_template('driver/overview.html',
                           name=user['username'],
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

            # determine driver_id
            sql_query = f'''
                SELECT MAX(constructorid) FROM constructors;
                            '''
            id_result = pd.read_sql_query(sql_query, conn)

            constructorid = id_result.loc[0]['max'] + 1
            constructor_ref = request.form['constructor_ref']
            name = request.form['name']
            nationality = request.form['nationality']
            url = request.form['url']

            try: 
                sql_query = f'''
                    INSERT INTO constructors (constructorid, constructorref, name, nationality, url)  VALUES ('{constructorid}', '{constructor_ref}','{name}','{nationality}','{url}');
                                '''
                conn.execute(sql_query)
                
            except SQLAlchemyError as e:
                error = str(e.__dict__['orig'])
                return render_template('generic_error.html', message=error)
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
            # determine driver_id
            sql_query = f'''
                SELECT MAX(driverid) FROM driver;
                            '''
            id_result = pd.read_sql_query(sql_query, conn)

            driverid = id_result.loc[0]['max'] + 1
            driverref = request.form['driver_ref']
            number = request.form['number']
            code = request.form['code']
            forename = request.form['forename']
            surname = request.form['surname']
            date_of_birth = request.form['date_of_birth']
            nationality = request.form['nationality']
            
            try: 
                sql_query = f'''
                    INSERT INTO driver (driverid, driverref, number, code, forename, surname, nationality, dob)  VALUES ('{driverid}', '{driverref}','{number}','{code}','{forename}', '{surname}', '{nationality}', '{date_of_birth}');
                                '''
                conn.execute(sql_query)
            except SQLAlchemyError as e:
                error = str(e.__dict__['orig'])
                return render_template('generic_error.html', message=error)

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

            user = session.get('user')
            constructor_ref = user['user_ref']

            sql_query = f'''
                SELECT DISTINCT driverid from results where constructorid = {user['id']}
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


@app.route('/admin/reports', methods=['GET', 'POST'])
def admin_reports():
    if request.method == 'POST':
        city_name = request.form['city_name']
        return redirect(f'/admin/reports/report-02?city_name={city_name}')

    return render_template('/admin/dashboard_reports.html', name='Admin')


@app.route('/admin/reports/report-01')
def report_one():
    if 'admin' != check_permission():
        return render_template('generic_error.html', message='User not allowed to see this content')

    sql_query = f'''
    select
        s.status, count(*)
    from results
        join status s on results.statusid = s.statusid
    group by grouping sets (s.status)
    order by (s.status)
                    '''
    report_result = pd.read_sql_query(sql_query, conn)
    html = report_result.to_html(border=0, classes='')

    return render_template('generic_report.html', html=html)


@app.route('/admin/reports/report-02')
def report_two():
    if 'admin' != check_permission():
        return render_template('generic_error.html', message='User not allowed to see this content')

    city_name = request.args.get('city_name', None)
    sql_query = f'''
    SELECT *
        FROM (
            SELECT *, ROW_NUMBER() OVER (PARTITION BY nome_aeroporto ORDER BY earth_distance) as RN 
            FROM (
                SELECT A.nome_aeroporto, A.tipo_aeroporto, A.name_cidade as cidade_aeroporto, A.IATA_code,
                A.name_pais, A.continente_pais, C.name as name_cidade, earth_distance (ll_to_earth(A.latitude, A.longitude), ll_to_earth(C.lat , C.long)),
                    C.population, C.geonameid as id_geografico_cidade
                    FROM aeroportos_brasileiros		AS A
                    INNER JOIN geocities15k 		AS C
                    ON (earth_distance (ll_to_earth(A.latitude, A.longitude), ll_to_earth(C.lat , C.long))) < 100000
                    where C.name = '{city_name}'
            ) AS A
        ) AS A
        ORDER BY id_geografico_cidade, nome_aeroporto
                    '''
    report_result = pd.read_sql_query(sql_query, conn)
    html = report_result.to_html(border=0, classes='')

    return render_template('generic_report.html', html=html)


@app.route('/constructor/reports', methods=['GET'])
def constructor_reports():
    user = session.get('user')
    return render_template('/constructors/dashboard_reports.html', name=user['username'])


@app.route('/constructor/reports/report-03')
def report_three():
    if 'constructor' != check_permission():
        return render_template('generic_error.html', message='User not allowed to see this content')

    user = session.get('user')
    constructor_ref = user['user_ref']

    sql_query = f'''
        SELECT * FROM constructor_list_drivers('{constructor_ref}');
                    '''
    report_result = pd.read_sql_query(sql_query, conn)
    html = report_result.to_html(border=0, classes='')

    return render_template('generic_report.html', html=html)


@app.route('/constructor/reports/report-04')
def report_four():
    if 'constructor' != check_permission():
        return render_template('generic_error.html', message='User not allowed to see this content')

    user = session.get('user')
    constructor_ref = user['user_ref']

    sql_query = f'''
                SELECT s.status as status, count(*) as count from results r
                    inner join status s on r.statusid = s.statusid
                    -- o constructorid deve ser o originalid cadastrado na tabela 
                    -- user para o usuario que for do type 'Escuderia'
                    where r.constructorid = (SELECT constructorid FROM constructors WHERE constructorref = '{constructor_ref}')
                    group by s.status    
                    '''
    report_result = pd.read_sql_query(sql_query, conn)
    html = report_result.to_html(border=0, classes='')

    return render_template('generic_report.html', html=html)


@app.route('/driver/reports', methods=['GET'])
def driver_reports():
    user = session.get('user')
    return render_template('/driver/dashboard_reports.html', name=user['username'])


@app.route('/driver/reports/report-05')
def report_five():
    if 'driver' != check_permission():
        return render_template('generic_error.html', message='User not allowed to see this content')

    user = session.get('user')
    driver_ref = user['user_ref']

    sql_query = f'''
                SELECT ra.name, EXTRACT(YEAR FROM ra.date) AS race_year, COUNT(r.position) as vitorias 
                FROM driver d JOIN results r
                ON r.driverid = d.driverid
                JOIN races ra ON r.raceid = ra.raceid
                WHERE r.position = 1 AND d.driverref = '{driver_ref}'
                GROUP BY ROLLUP(race_year, ra.name)
                ORDER BY race_year;    
                    '''

    report_result = pd.read_sql_query(sql_query, conn)
    html = report_result.to_html(border=0, classes='')

    return render_template('generic_report.html', html=html)


@app.route('/driver/reports/report-06')
def report_six():
    if 'driver' != check_permission():
        return render_template('generic_error.html', message='User not allowed to see this content')

    user = session.get('user')
    driver_ref = user['user_ref']

    sql_query = f'''
            SELECT s.status as status, count(*) as count from results r
                inner join status s on r.statusid = s.statusid
                -- o driverid deve ser o originalid cadastrado na tabela 
                -- user para o usuario que for do type 'Piloto'
                where r.driverid =  (SELECT driverid FROM driver WHERE driverref = '{driver_ref}')
                group by s.status
                    '''

    report_result = pd.read_sql_query(sql_query, conn)
    html = report_result.to_html(border=0, classes='')

    return render_template('generic_report.html', html=html)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
