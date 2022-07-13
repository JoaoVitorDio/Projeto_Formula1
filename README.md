# Final project - Databases Laboratory (Bachelor of Information Systems - ICMC USP)
 
### The objective of the project is to practice the knowledge studied during the discipline with the creation of a prototype that is able to manipulate data and generate reports through a good usability interface. The project uses data related to the Formula 1 sport.

Repository link: https://github.com/JoaoVitorDio/Projeto_Formula1

### How to run
#### Prerequisites
* PostgreSQL and PgAdmin4;
* Set the three environment variables needed by the project in a copy of the .env.sample file (name this copy ".env"):
* DATABASE_NAME = 'name_of_database_created_in_postgres'
* DATABASE_PASSWORD = 'user_password_on_database_server'
* DATABASE_USERNAME = 'postgres_user'
* Python programming language installed, as well as some package manager (pip or conda, for example);

#### Step by step
* Run the following command in the project directory: `pip install -r requirements.txt`;
* In the `Project_Formula1/CreateDatabaseAndLoad)/CreateTablesAndLoad` directory, follow the instructions in the Load.txt file and run it completely in PgAdmin4, to create the tables and insert the data contained in `CreateTablesAndLoad/data`;
* Go to the `Project_Formula1/CreateDatabaseAndLoad)/CreateUsersTableAndLoad` directory and execute the commands from the `CreateUsersTable.txt` file in PgAdmin4;
* Run all the `CreateUsersTableAndLoad.py` code.
* Run files in the `Setup` directory that contain creation of functions, tables, views or triggers in PgAdmin4.
* Go back to the main directory and run the `app.py` file.
* Open the browser to the following `URL: Localhost:5000`.
