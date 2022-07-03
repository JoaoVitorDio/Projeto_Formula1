import os
import pandas as pd
from sqlalchemy import create_engine, text
from flask import Flask, render_template, request

#Reading environment variables to get database name and password
database_name = os.environ['DatabaseName']
postgres_password = os.environ['PostgresPassword']

DATABASES = {
    'production':{
        'NAME': database_name,
        'USER': 'postgres',
        'PASSWORD': postgres_password,
        'HOST': '127.0.0.1',
        'PORT': 5432,
    },
}

# choose the database to use
db = DATABASES['production']
# construct an engine connection string
engine_string = "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}".format(
    user = db['USER'],
    password = db['PASSWORD'],
    host = db['HOST'],
    port = db['PORT'],
    database = db['NAME']
)

# create sqlalchemy engine
engine = create_engine(engine_string)
conn = engine.connect()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    login = request.form['login']
    password = request.form['password']
    
    # Inserting drivers already signed into users table
    sqlQuery = f'''SELECT * FROM users WHERE login = '{login}' and 
                           password = MD5(CONCAT('{password}',userID))'''
    df = pd.read_sql_query(sqlQuery,conn)
    
    if (len(df.index) > 0):
        return render_template('success.html', login = login, password = password) 
    else:
        return 'hm'
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)