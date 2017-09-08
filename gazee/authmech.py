#  This file is part of Gazee.
#
#  Gazee is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Gazee is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Gazee.  If not, see <http://www.gnu.org/licenses/>.

import os
import sqlite3
import hashlib
import logging

from pathlib import Path

import gazee


# This is the function called when a user logs in, it's given a realm (Gazee) and the user inputted username and password
# We get the hashed password from the DB for username and then check that against the hashed version of the inputted password
def check_password(realm, username, password):

    userstring = str(username)

    # Here we set the db file path.
    db = Path(os.path.join(gazee.DATA_DIR, gazee.DB_NAME))

    # Here we make the inital DB connection that we will be using throughout this function.
    connection = sqlite3.connect(str(db))
    c = connection.cursor()

    c.execute('SELECT {pw} FROM {tn} WHERE {un}=?'.format(pw=gazee.PASSWORD, tn=gazee.USERS, un=gazee.USERNAME), (userstring,))
    passinit = c.fetchone()
    if passinit is None:
        return False

    db_password = passinit[0]
    connection.commit()
    connection.close()

    return db_password == hash_pass(password)


def get_user_level(username):

    db = Path(os.path.join(gazee.DATA_DIR, gazee.DB_NAME))

    # Here we make the inital DB connection that we will be using throughout this function.
    connection = sqlite3.connect(str(db))
    c = connection.cursor()

    c.execute('SELECT {ut} FROM {tn} WHERE {un}=?'.format(ut=gazee.TYPE, tn=gazee.USERS, un=gazee.USERNAME), (username,))
    levelinit = c.fetchone()

    if levelinit is not None:
        userlevel = levelinit[0]
    else:
        userlevel = 'user'

    connection.commit()
    connection.close()

    return userlevel


def hash_pass(password):
    hashed_pass = hashlib.sha256(bytes(password, encoding='utf-8')).hexdigest()
    return hashed_pass


# This simply updates the currently logged in users password in the DB to their set and hashed password.
def change_pass(user, password):
    hashed_pass = hash_pass(password)

    # Here we set the db file path.
    db = Path(os.path.join(gazee.DATA_DIR, gazee.DB_NAME))

    # Here we make the inital DB connection that we will be using throughout this function.
    connection = sqlite3.connect(str(db))
    c = connection.cursor()

    c.execute('UPDATE {tn} SET {pw}=? WHERE {un}=?'.format(tn=gazee.USERS, pw=gazee.PASSWORD, un=gazee.USERNAME), (hashed_pass, user,))

    connection.commit()
    connection.close()

    logging.basicConfig(level=gazee.LOG_LEVEL, filename=os.path.join(gazee.DATA_DIR, 'gazee.log'))
    logger = logging.getLogger(__name__)
    logger.info("Password Updated")
    return


def add_user(user, password, ut):
    logging.basicConfig(level=gazee.LOG_LEVEL, filename=os.path.join(gazee.DATA_DIR, 'gazee.log'))
    logger = logging.getLogger(__name__)
    hashed_pass = hash_pass(password)

    # Here we set the db file path.
    db = Path(os.path.join(gazee.DATA_DIR, gazee.DB_NAME))

    # Here we make the inital DB connection that we will be using throughout this function.
    connection = sqlite3.connect(str(db))
    c = connection.cursor()
    try:
        c.execute('INSERT INTO {tn} ({un}, {pw}, {ut}) VALUES (?,?,?)'.format(tn=gazee.USERS, un=gazee.USERNAME, pw=gazee.PASSWORD, ut=gazee.TYPE), (user, hashed_pass, ut,))
    except sqlite3.IntegrityError:
        logger.info("User %s Already Exists" % user)
        return False
    finally:
        connection.commit()
        connection.close()

    logger.info("User %s Added" % (user))
    return True
