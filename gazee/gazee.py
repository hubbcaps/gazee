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
#  along with Mylar.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import time
import cherrypy
import sqlite3
import configparser
import logging
import subprocess
import threading

from pathlib import Path

from mako.lookup import TemplateLookup
from mako import exceptions

import gazee
from gazee.comicscan import ComicScanner

DATA_DIR = 'data'
logging.basicConfig(level=logging.DEBUG, filename=os.path.join(DATA_DIR, 'gazee.log'))
logger = logging.getLogger(__name__)

"""
This initializes our mako template serving directory and allows us to return it's compiled embeded html pages rather than the default return of a static html page.
"""


def serve_template(templatename, **kwargs):
    html_dir = 'public/html/'
    _hplookup = TemplateLookup(directories=[html_dir])
    try:
        template = _hplookup.get_template(templatename)
        return template.render(**kwargs)
    except:
        return exceptions.html_error_template().render()


"""
Web Pages/Views methods that are exposed for API like url calling.
"""


class Gazee(object):

    """
    Index Page
    This returns the html template for the recents div.
    The recents div is by default the the last twenty comics added to the DB in the last 7 days.
    """
    @cherrypy.expose
    def index(self, page_num=1):
        logging.info("Index Requested")
        # Here we set the db file path.
        db = Path(os.path.join(gazee.DATA_DIR, gazee.DB_NAME))

        # Here we make the inital DB connection that we will be using throughout this function.
        connection = sqlite3.connect(str(db))
        c = connection.cursor()

        c.execute("SELECT COUNT(*) FROM {tn} WHERE DATE('now') - {it} <= 7".format(tn=gazee.ALL_COMICS, it=gazee.INSERT_DATE))
        numcinit = c.fetchone()
        num_of_comics = numcinit[0]
        num_of_pages = 0
        while num_of_comics >= 0:
            num_of_comics -= gazee.COMICS_PER_PAGE
            num_of_pages += 1

        if page_num == 1:
            PAGE_OFFSET = 0
        else:
            PAGE_OFFSET = gazee.COMICS_PER_PAGE * (int(page_num) - 1)

        c.execute("SELECT * FROM {tn} WHERE DATE('now') - {it} <= 7 ORDER BY {cn} ASC, {ci} ASC LIMIT {nc} OFFSET {pn}".format(tn=gazee.ALL_COMICS, it=gazee.INSERT_DATE, cn=gazee.COMIC_NAME, ci=gazee.COMIC_NUMBER, nc=gazee.COMICS_PER_PAGE, pn=PAGE_OFFSET))
        # DB Always returns a tuple of lists. After fetching it, we then iterate over its various lists to assign their values to a dictionary.
        all_recent_comics_tup = c.fetchall()
        comics = []
        for f in all_recent_comics_tup:
            comics.append({"Key": f[0],
                           "ComicName": f[1],
                           "ComicImage": f[2],
                           "ComicIssue": f[3],
                           "ComicVolume": f[4],
                           "ComicSummary": f[5],
                           "ComicPath": f[6],
                           "DateAdded": f[7]})

        connection.commit()
        connection.close()

        user = cherrypy.request.login
        user_level = gazee.authmech.getUserLevel(user)

        logging.info("Index Served")

        return serve_template(templatename="index.html", comics=comics, num_of_pages=num_of_pages, current_page=int(page_num), user_level=user_level)

    @cherrypy.expose
    def search(self, page_num=1, search_string=''):
        logging.info("Search Requested")
        # Here we set the db file path.
        db = Path(os.path.join(gazee.DATA_DIR, gazee.DB_NAME))

        # Here we make the inital DB connection that we will be using throughout this function.
        connection = sqlite3.connect(str(db))
        c = connection.cursor()

        c.execute("CREATE VIRTUAL TABLE ComicSearch USING fts4(key, name, image, issue, volume, summary, path, parent_key, date)")
        c.execute("INSERT INTO ComicSearch SELECT key, name, image, issue, volume, summary, path, parent_key, date from all_comics")

        c.execute("SELECT COUNT(*) FROM ComicSearch WHERE ComicSearch MATCH ?", (search_string,))
        numcinit = c.fetchone()
        num_of_comics = numcinit[0]
        num_of_pages = 0
        while num_of_comics >= 0:
            num_of_comics -= gazee.COMICS_PER_PAGE
            num_of_pages += 1

        if page_num == 1:
            PAGE_OFFSET = 0
        else:
            PAGE_OFFSET = gazee.COMICS_PER_PAGE * (int(page_num) - 1)

        c.execute("SELECT * FROM ComicSearch WHERE ComicSearch MATCH ? ORDER BY name ASC, issue ASC LIMIT {nc} OFFSET {pn}".format(nc=gazee.COMICS_PER_PAGE, pn=PAGE_OFFSET), (search_string,))
        # DB Always returns a tuple of lists. After fetching it, we then iterate over its various lists to assign their values to a dictionary.
        all_recent_comics_tup = c.fetchall()
        comics = []
        for f in all_recent_comics_tup:
            comics.append({"Key": f[0],
                           "ComicName": f[1],
                           "ComicImage": f[2],
                           "ComicIssue": f[3],
                           "ComicVolume": f[4],
                           "ComicSummary": f[5],
                           "ComicPath": f[6],
                           "DateAdded": f[7]})

        c.execute("DROP TABLE ComicSearch")
        connection.commit()
        connection.close()

        user = cherrypy.request.login
        user_level = gazee.authmech.getUserLevel(user)

        logging.info("Search Served")

        return serve_template(templatename="search.html", comics=comics, num_of_pages=num_of_pages, current_page=int(page_num), user_level=user_level, search_string=search_string)

    """
    This returns the library view starting with the root library directory.
    """
    # Library Page
    @cherrypy.expose
    def library(self, directory, page_num=1):
        logging.info("Library Requested")
        # Here we set the db file path.
        db = Path(os.path.join(gazee.DATA_DIR, gazee.DB_NAME))

        # Here we make the inital DB connection that we will be using throughout this function.
        connection = sqlite3.connect(str(db))
        c = connection.cursor()

        # Here we get the Primary Key of the selected directory
        if directory == gazee.COMIC_PATH:
            c.execute("SELECT {prk} FROM {tn} WHERE {fp}=?".format(prk=gazee.KEY, tn=gazee.ALL_DIRS, fp=gazee.FULL_DIR_PATH), (directory,))
            parent_dir = ''
        else:
            c.execute("SELECT {ptk} FROM {tn} WHERE {fp}=?".format(ptk=gazee.PARENT_KEY, tn=gazee.DIR_NAMES, fp=gazee.NICE_NAME), (directory,))
            ptkinit = c.fetchall()
            parent_key = [tup[0] for tup in ptkinit]

            c.execute("SELECT {fp} FROM {tn} WHERE {prk}=?".format(fp=gazee.FULL_DIR_PATH, tn=gazee.ALL_DIRS, prk=gazee.KEY), (parent_key[0],))

            pdirinit = c.fetchall()
            parent_dir = [tup[0] for tup in pdirinit]

            full_dir = os.path.join(parent_dir[0], directory)

            c.execute("SELECT {prk} FROM {tn} WHERE {fp}=?".format(prk=gazee.KEY, tn=gazee.ALL_DIRS, fp=gazee.FULL_DIR_PATH), (full_dir,))

        pkinit = c.fetchall()
        pk = [tup[0] for tup in pkinit]

        # Select all the Nice Names from the Dir Names table.
        try:
            c.execute("SELECT {nn} FROM {tn} WHERE {ptk}=?".format(nn=gazee.NICE_NAME, tn=gazee.DIR_NAMES, ptk=gazee.PARENT_KEY), (pk[0],))

            dirsinit = c.fetchall()
            directories = [tup[0] for tup in dirsinit]

            c.execute("SELECT COUNT(*) FROM {tn} WHERE {pk}=?".format(tn=gazee.ALL_COMICS, pk=gazee.PARENT_KEY), (pk[0],))
            numcinit = c.fetchone()
            num_of_comics = numcinit[0]
            num_of_pages = 0
            while num_of_comics >= 0:
                num_of_comics -= gazee.COMICS_PER_PAGE
                num_of_pages += 1

            if page_num == 1:
                PAGE_OFFSET = 0
            else:
                PAGE_OFFSET = gazee.COMICS_PER_PAGE * (int(page_num) - 1)

            # Select all of the comics associated with the parent dir as well.
            c.execute("SELECT * FROM {tn} WHERE {prk}=? ORDER BY {cn} ASC LIMIT {np} OFFSET {pn}".format(tn=gazee.ALL_COMICS, cn=gazee.COMIC_NUMBER, np=gazee.COMICS_PER_PAGE, prk=gazee.PARENT_KEY, pn=PAGE_OFFSET), (pk[0],))

            # DB Always returns a tuple of lists. After fetching it, we then iterate over its various lists to assign their values to a dictionary.
            comicsinit = c.fetchall()
            comics = []
            for f in comicsinit:
                comics.append({"Key": f[0],
                               "ComicName": f[1],
                               "ComicImage": f[2],
                               "ComicIssue": f[3],
                               "ComicVolume": f[4],
                               "ComicSummary": f[5],
                               "ComicPath": f[6],
                               "DateAdded": f[7]})

            connection.commit()
            connection.close()

            cp_split = os.path.split(gazee.COMIC_PATH)

            # End it all by grinding the breadcrumb.
            if parent_dir == '':
                prd = ''
            else:
                parent_parts = os.path.split(parent_dir[0])
                prd = parent_parts[1]

            if prd == cp_split[1]:
                prd = ''

            directories.sort()
            logging.info("Library Served")

        except IndexError:
            logging.warning("No Child Directories, Scan your comic path")
            directories = []
            comics = []
            prd = ''
            num_of_pages = 1
            page_num = 1
            directory = gazee.COMIC_PATH

        user = cherrypy.request.login
        user_level = gazee.authmech.getUserLevel(user)

        return serve_template(templatename="library.html", directories=directories, comics=comics, parent_dir=prd, num_of_pages=num_of_pages, current_page=int(page_num), current_dir=directory, user_level=user_level)

    @cherrypy.expose
    def downloadComic(self, comic_path):
        return cherrypy.lib.static.serve_download(comic_path)

    """
    This returns the reading view of the selected comic after being passed the comic path and forcing the default of starting at page 0.
    """
    # TODO
    # Good place to pass in a bookmark, how do we make them?
    @cherrypy.expose
    def readComic(self, comic_path, page_num=0):
        username = cherrypy.request.login
        logging.info("Reader Requested")
        scanner = ComicScanner()
        scanner.userUnpackComic(comic_path, username)
        image_list = scanner.readingImages(username)
        num_pages = len(image_list)
        if num_pages == 0:
            image_list = ['static/images/imgnotfound.png']
        logging.info("Reader Served")
        return serve_template(templatename="read.html", pages=image_list, current_page=page_num, np=1, lp=num_pages - 1, nop=num_pages)

    """
    This allows us to change pages and do some basic sanity checking.
    """
    @cherrypy.expose
    def changePage(self, page_str):
        username = cherrypy.request.login
        page_num = int(page_str)
        next_page = page_num + 1
        last_page = page_num - 1
        scanner = ComicScanner()
        image_list = scanner.readingImages(username)
        num_pages = len(image_list)
        if page_num == -1:
            page_num = num_pages - 1
            next_page = 0
            last_page = num_pages - 2
        if page_num == num_pages:
            page_num = 0
            next_page = 1
            last_page = num_pages - 1
        return serve_template(templatename="read.html", pages=image_list, current_page=page_num, np=next_page, lp=last_page, nop=num_pages)

    """
    This returns the settings page.
    """
    @cherrypy.expose
    def settings(self):

        # Here we set the db file path.
        db = Path(os.path.join(gazee.DATA_DIR, gazee.DB_NAME))

        # Here we make the inital DB connection that we will be using throughout this function.
        connection = sqlite3.connect(str(db))
        c = connection.cursor()
        c.execute("SELECT COUNT(*) FROM {tn}".format(tn=gazee.ALL_COMICS))
        numcinit = c.fetchone()
        num_of_comics = numcinit[0]

        user = cherrypy.request.login
        user_level = gazee.authmech.getUserLevel(user)

        if os.path.exists(os.path.join(gazee.DATA_DIR, "db.lock")):
            scan_in_progress = True
            made = os.path.getmtime(os.path.join(gazee.DATA_DIR, "db.lock"))
            now = time.time()
            since = now - made
            m, s = divmod(int(since), 60)
            h, m = divmod(m, 60)
            scantime = ("%d:%02d:%02d" % (h, m, s))
        else:
            scan_in_progress = False
            scantime = ("%d:%02d:%02d" % (0, 0, 0))

        logging.info("Settings Served")
        return serve_template(templatename="settings.html", user=user, user_level=user_level, sip=scan_in_progress, noc=num_of_comics, scantime=scantime)

    @cherrypy.expose
    @cherrypy.tools.accept(media='text/plain')
    def saveSettings(self, scomicPath=None, scomicsPerPage=None, scomicScanInterval=None, smylarPath=None, ssslKey=None, ssslCert=None, sport=4242):
        # Set these here as they'll be used to assign the default values of the method arguments to the current values if they aren't updated when the method is called.
        config = configparser.ConfigParser()
        config.read('data/app.ini')

        config['GLOBAL']['PORT'] = sport
        config['GLOBAL']['COMIC_PATH'] = scomicPath
        config['GLOBAL']['COMICS_PER_PAGE'] = scomicsPerPage
        config['GLOBAL']['COMIC_SCAN_INTERVAL'] = scomicScanInterval
        config['GLOBAL']['MYLAR_DB'] = smylarPath
        config['GLOBAL']['SSL_KEY'] = ssslKey
        config['GLOBAL']['SSL_CERT'] = ssslCert
        with open('data/app.ini', 'w') as configfile:
            config.write(configfile)
        configfile.close()
        logging.info("Settings Saved")
        self.restart()
        return

    @cherrypy.expose
    def changePassword(self, password):
        user = cherrypy.request.login
        gazee.authmech.changePass(user, password)
        logging.info("Password Changed")
        return

    @cherrypy.expose
    def newUser(self, username, password, usertype):
        gazee.authmech.addUser(username, password, usertype)
        logging.info("New User Added")
        return

    @cherrypy.expose
    def comicScan(self):
        logging.info("DB Build Requested")
        scanner = ComicScanner()
        scanner.dbBuilder()
        logging.info("DB Build Finished")
        return

    @cherrypy.expose
    def shutdown(self):
        cherrypy.engine.exit()
        threading.Timer(1, lambda: os._exit(0)).start()
        logger.info('Gazee is shutting down...')
        return

    @cherrypy.expose
    def restart(self):
        cherrypy.engine.exit()
        popen_list = [sys.executable, gazee.FULL_PATH]
        popen_list += gazee.ARGS
        logger.info('Restarting Gazee with ' + str(popen_list))
        subprocess.Popen(popen_list, cwd=os.getcwd())
        threading.Timer(1, lambda: os._exit(0)).start()
        logger.info('Gazee is restarting...')
        return

    @cherrypy.expose
    def opds(self):
        # TODO
        return "not implemented yet"
