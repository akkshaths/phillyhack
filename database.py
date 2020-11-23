import psycopg2
from configparser import ConfigParser
import os
import datetime


def config(filename='C:/Users/akkie/Documents/GitHub/phillyhack/database2.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db

def select_emission_from_usertable (user):
    conn = None
    
    params = config()

    
    #print('Connecting to the PostgreSQL database...')
    conn = psycopg2.connect(**params)
    
    conn.autocommit = True
    cur = conn.cursor()
    postgreSQL_select_Query = "select * from users"

    cur.execute(postgreSQL_select_Query)
    user_records = cur.fetchall()

    total = []
    for row in user_records:
        if row[1] == user:
            total = [row[0], row[1], row[2], row[3], row[4]]

    cur.close()

    conn.close()
    #print('Database connection closed.')
    return total

def update_emission_from_users (user, newNum):
    conn = None
    
    params = config()

    
    #print('Connecting to the PostgreSQL database...')
    conn = psycopg2.connect(**params)
    
    conn.autocommit = True
    cur = conn.cursor()

    list1 = select_emission_from_usertable(user)

    update_post_description = f"""
    UPDATE
        users
    SET
        total = {newNum}
    WHERE
        id = {list1[0]}
    """

    execute_query(conn, update_post_description)
    cur.close()

    conn.close()
    

def addUser (newUserName, password):
    conn = None
    
    params = config()

    
    #print('Connecting to the PostgreSQL database...')
    conn = psycopg2.connect(**params)
    
    conn.autocommit = True
    cur = conn.cursor()

    postgreSQL_select_Query = "select * from users"

    cur.execute(postgreSQL_select_Query)
    user_records = cur.fetchall()

    for row in user_records:
        if row[1] == newUserName:
            return 0

    new = [(newUserName, password, datetime.date.today(), 0)]

    post_records = ", ".join(["%s"] * 1)

    insert_query = (
        f"INSERT INTO users (username, password, date, total) VALUES {post_records}"
    )

    cur.execute(insert_query, new)

    return 1

def checkUser (user, passw):
    list1 = select_emission_from_usertable(user)
    if len(list1) == 0:
        return 0
    elif passw == list1[2]:
        return 1
    else:
        return 0

def execute_query(connection, query):
    connection.autocommit = True
    cursor = connection.cursor()
    cursor.execute(query)
        #print("Query executed successfully")
    #except:

        #print(f"The error occurred")



def execute_read_query(connection, query):
    cursor = connection.cursor()
    result = None
    
    cursor.execute(query)
    result = cursor.fetchall()
    return result
    
