import os
import pandas as pd
from sqlalchemy import create_engine, text
from flask.cli import load_dotenv


#Reading environment variables to get database name and password
# Creating environment based on .env file
basedir = os.getcwd()
load_dotenv(os.path.join(basedir, '.env'))

DATABASES = {
    'production':{
        'NAME': os.environ['DATABASE_NAME'],
        'USER': os.environ['DATABASE_USERNAME'],
        'PASSWORD':  os.environ['DATABASE_PASSWORD'],
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


#Creating the systems admin
sql_text = text("INSERT INTO users VALUES (DEFAULT,'admin','admin','Administrador',NULL)")
result = conn.execute(sql_text)


# Inserting driver already signed into users table
df = pd.read_sql_query('''SELECT CONCAT(driverref,'_d') AS login, driverref as password, 
                       driverid as IdOriginal FROM driver''',conn)
df['tipo'] = 'Piloto'
df.to_sql('users', engine, if_exists='append', index=False)


# Inserting constructors already signed into users table
df = pd.read_sql_query('''SELECT CONCAT(constructorref,'_c') AS login, constructorref as password, 
                       constructorid as IdOriginal FROM constructors''',conn)
df['tipo'] = 'Escuderia'
df.to_sql('users', engine, if_exists='append', index=False)


# Encrypting passwords with md5 from postgres
sql_text = text('''UPDATE users SET password = MD5(CONCAT(Password, UserID))''')
result = conn.execute(sql_text)

conn.close()