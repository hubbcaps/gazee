import os,sys
import sqlite3
import string
import hashlib
import logging

from pathlib import Path

import gazee

logging.basicConfig(level=logging.DEBUG,filename='data/gazee.log')
logger = logging.getLogger(__name__) 

# This is the function called when a user logs in, it returns their hashed password from the DB for checking by CherryPys auth mechanism.
def getPassword(username):

    userstring = str(username)

    # Here we set the db file path.
    db = Path(os.path.join(gazee.DATA_DIR, gazee.DB_NAME))

    # Here we make the inital DB connection that we will be using throughout this function.
    connection = sqlite3.connect(str(db))
    c = connection.cursor()

    c.execute('SELECT {pw} FROM {tn} WHERE {un}=?'.format(pw=gazee.PASSWORD,tn=gazee.USERS,un=gazee.USERNAME),(userstring,))
    passinit = c.fetchone()
    if not passinit is None:
        password = passinit[0]
    else:
        password = 'nil'

    connection.commit()
    connection.close()

    return password

def getUserLevel(username):

    db = Path(os.path.join(gazee.DATA_DIR, gazee.DB_NAME))

    # Here we make the inital DB connection that we will be using throughout this function.
    connection = sqlite3.connect(str(db))
    c = connection.cursor()

    c.execute('SELECT {ut} FROM {tn} WHERE {un}=?'.format(ut=gazee.TYPE,tn=gazee.USERS,un=gazee.USERNAME),(username,))
    levelinit = c.fetchone()

    if not levelinit is None:
        userlevel = typeinit[0]
    else:
        userlevel = 'user'

    connection.commit()
    connection.close()

    return userlevel

def hashPass(password):
    hashedPass = hashlib.sha256(bytes(password, encoding='utf-8')).hexdigest()
    return hashedPass

# This simply updates the currently logged in users password in the DB to their set and hashed password.
def changePass(user, password):
    hashedPass = hashPass(password)

    # Here we set the db file path.
    db = Path(os.path.join(gazee.DATA_DIR, gazee.DB_NAME))

    # Here we make the inital DB connection that we will be using throughout this function.
    connection = sqlite3.connect(str(db))
    c = connection.cursor()

    c.execute('UPDATE {tn} SET {pw}=? WHERE {un}=?'.format(tn=gazee.USERS,pw=gazee.PASSWORD,un=gazee.USERNAME),(hashedPass,user,))

    connection.commit()
    connection.close()
    logging.info("Password Updated")

    return

def addUser(user, password, ut):
    hashedPass = hashPass(password)

    # Here we set the db file path.
    db = Path(os.path.join(gazee.DATA_DIR, gazee.DB_NAME))

    # Here we make the inital DB connection that we will be using throughout this function.
    connection = sqlite3.connect(str(db))
    c = connection.cursor()

    c.execute('INSERT INTO {tn} ({un}, {pw}, {ut}) VALUES (?,?,?)'.format(tn=gazee.USERS, un=gazee.USERNAME, pw=gazee.PASSWORD, ut=gazee.TYPE), (user, hashedPass, ut,))

    connection.commit()
    connection.close()

    logging.info("User %s Added" % (user))
    return
