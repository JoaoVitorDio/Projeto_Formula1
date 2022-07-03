import os
import pandas as pd
from sqlalchemy import create_engine, text

#Reading environment variables to get database name and password
database_name = os.environ["DatabaseName"]
postgres_password = os.environ["PostgresPassword"]

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
db = DATABASES["production"]
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
sql_text = text("INSERT INTO USERS VALUES (DEFAULT,'admin','admin','Administrador',NULL)")
result = conn.execute(sql_text)


# Inserting drivers and constructors already signed into users table
# read a table from database into pandas dataframe
df = pd.read_sql_query("SELECT CONCAT(driverref,'_d') AS login, driverref as password FROM driver",conn)


conn.close()