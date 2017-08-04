import os, sys, shutil
import sqlite3
import string
import cherrypy

from pathlib import Path
from gazee.gazee import Gazee
from gazee.comicscan import ComicScanner

__version__ = '0.0.1'
__all__ = ['Gazee', 'ComicScanner']

DB_NAME = "gazee.db"
DATA_DIR = "data"
TEMP_DIR = "tmp"
PORT = 4242
COMIC_PATH = "data/comics"

# Declare DB variables, such as table names and field names
# This is mostly so the names are in a central area for later reference.

# Directories table, and the only field in it.
ALL_DIRS = "all_directories"
PARENT_DIR = "parent_dir"
CHILD_DIR = "child_dir"

# Comics table and various attributes we associate with them.
ALL_COMICS = "all_comics"
COMIC_IMAGE = "image"
COMIC_NAME = "name"
COMIC_NUMBER = "issue"
COMIC_VOLUME = "volume"
COMIC_SUMMARY = "summary"
COMIC_FULL_PATH = "path"
INSERT_DATE = "date"
KEY = "key"

# Users Table and various attributes.
USERS = "USERS"
USERNAME = "username"
PASSWORD = "password"
TYPE = "type"

# Create DB if it doesn't already exist.
db = Path(os.path.join(DATA_DIR, DB_NAME))
if not db.is_file():
    connection = sqlite3.connect(str(db))
    c = connection.cursor()
    # Create the Directory table.
    c.execute('CREATE TABLE {tn} ({nf} {ft})'.format(tn=ALL_DIRS, nf=PARENT_DIR, ft="TEXT"))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=ALL_DIRS, cn=CHILD_DIR, ft="TEXT"))

    # Create Comics table and necessary columns.
    c.execute('CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)'.format(tn=ALL_COMICS, nf=KEY, ft="INTEGER"))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=ALL_COMICS, cn=COMIC_NAME, ft="TEXT"))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=ALL_COMICS, cn=COMIC_IMAGE, ft="TEXT"))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=ALL_COMICS, cn=COMIC_NUMBER, ft="TEXT"))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=ALL_COMICS, cn=COMIC_VOLUME, ft="TEXT"))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=ALL_COMICS, cn=COMIC_SUMMARY, ft="TEXT"))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=ALL_COMICS, cn=COMIC_FULL_PATH, ft="TEXT"))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}'".format(tn=ALL_COMICS, cn=INSERT_DATE))

    # Create Users colume and necessary columns.
    c.execute('CREATE TABLE {tn} ({nf} {ft})'.format(tn=USERS, nf=USERNAME, ft="TEXT"))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=USERS, cn=PASSWORD, ft="TEXT"))
    c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=USERS, cn=TYPE, ft="TEXT"))

    connection.commit()
    connection.close()

# Insert Admin user into DB if they aren't already there.
connection = sqlite3.connect(str(db))
c = connection.cursor()

c.execute('SELECT ({cn}) FROM {tn}'.format(cn=USERNAME, tn=USERS))
all_users = c.fetchall()

# Since queries return lists of tuples, we have to iterate those. We can use list comprehension here to iterate through the items in the first element of each tuple in the list. If the adminCheck variable is larger than 0, the admin has already been created, or something has gone horribly wrong.
adminCheck = [tup[0] for tup in all_users]

if len(adminCheck) == 0:
    c.execute('INSERT INTO {tn} ({cn1}, {cn2}, {cn3}) VALUES ("admin", "gazee", "administrator")'.format(tn=USERS, cn1=USERNAME, cn2=PASSWORD, cn3=TYPE))

connection.commit()
connection.close()
