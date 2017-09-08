import os
import logging
import sqlite3

import gazee

from pathlib import Path


def db_creation():

    logging.basicConfig(level=logging.DEBUG, filename=os.path.join(gazee.DATA_DIR, 'gazee.log'))
    logger = logging.getLogger(__name__)

    # Create DB if it doesn't already exist.
    db = Path(os.path.join(gazee.DATA_DIR, gazee.DB_NAME))
    if not db.is_file():
        connection = sqlite3.connect(str(db))
        c = connection.cursor()

        # Create the Directories table.
        c.execute('CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)'.format(tn=gazee.ALL_DIRS, nf=gazee.KEY, ft="INTEGER"))
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=gazee.ALL_DIRS, cn=gazee.FULL_DIR_PATH, ft="TEXT"))

        # Create the Directory table.
        c.execute('CREATE TABLE {tn} ({nf} {ft})'.format(tn=gazee.DIR_NAMES, nf=gazee.NICE_NAME, ft="TEXT"))
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=gazee.DIR_NAMES, cn=gazee.DIR_IMAGE, ft="TEXT"))
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=gazee.DIR_NAMES, cn=gazee.PARENT_KEY, ft="INTEGER"))

        # Create Comics table and necessary columns.
        c.execute('CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)'.format(tn=gazee.ALL_COMICS, nf=gazee.KEY, ft="INTEGER"))
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=gazee.ALL_COMICS, cn=gazee.COMIC_NAME, ft="TEXT"))
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=gazee.ALL_COMICS, cn=gazee.COMIC_IMAGE, ft="TEXT"))
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=gazee.ALL_COMICS, cn=gazee.COMIC_NUMBER, ft="INTEGER"))
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=gazee.ALL_COMICS, cn=gazee.COMIC_VOLUME, ft="INTEGER"))
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=gazee.ALL_COMICS, cn=gazee.COMIC_SUMMARY, ft="TEXT"))
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=gazee.ALL_COMICS, cn=gazee.COMIC_FULL_PATH, ft="TEXT"))
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=gazee.ALL_COMICS, cn=gazee.PARENT_KEY, ft="INTEGER"))
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}'".format(tn=gazee.ALL_COMICS, cn=gazee.INSERT_DATE))

        # Create Users colume and necessary columns.
        c.execute('CREATE TABLE {tn} ({nf} {ft} PRIMARY KEY)'.format(tn=gazee.USERS, nf=gazee.USERNAME, ft="TEXT"))
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=gazee.USERS, cn=gazee.PASSWORD, ft="TEXT"))
        c.execute("ALTER TABLE {tn} ADD COLUMN '{cn}' {ft}".format(tn=gazee.USERS, cn=gazee.TYPE, ft="TEXT"))

        connection.commit()
        connection.close()
        logging.info("DB Schema Created")

    # Insert Admin user into DB if they aren't already there.
    connection = sqlite3.connect(str(db))
    c = connection.cursor()

    c.execute('SELECT ({cn}) FROM {tn}'.format(cn=gazee.USERNAME, tn=gazee.USERS))
    all_users = c.fetchall()

    # Since queries return lists of tuples, we have to iterate those. We can use list comprehension here to iterate through the items in the first element of each tuple in the list. If the adminCheck variable is larger than 0, the admin has already been created, or something has gone horribly wrong.
    adminCheck = [tup[0] for tup in all_users]

    if len(adminCheck) == 0:
        c.execute('INSERT INTO {tn} ({cn1}, {cn2}, {cn3}) VALUES ("admin", "87f69abe62021d9ab8497e052c65ee79ca6705169916b930ea3e6979a0555c4d", "admin")'.format(tn=gazee.USERS, cn1=gazee.USERNAME, cn2=gazee.PASSWORD, cn3=gazee.TYPE))
        logger.info("Admin inserted into DB")

    connection.commit()
    connection.close()
    return
