import os,sys
import sqlite3
import string

from pathlib import Path

import gazee

def getPassword(username):

    userstring = str(username)

    # Here we set the db file path.
    db = Path(os.path.join(gazee.DATA_DIR, gazee.DB_NAME))

    # Here we make the inital DB connection that we will be using throughout this function.
    connection = sqlite3.connect(str(db))
    c = connection.cursor()

    # Here we define some variables we will use to check for existing directories and directories that need to be removed from the db.    
    c.execute('SELECT {pw} FROM {tn} WHERE {un}=?'.format(pw=gazee.PASSWORD,tn=gazee.USERS,un=gazee.USERNAME),(userstring,))
    passinit = c.fetchone()
    password = passinit[0]
    return password
