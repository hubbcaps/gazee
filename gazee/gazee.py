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

import json
import os
import re
import sys
import time
import subprocess
import cherrypy
import sqlite3
import configparser
import logging
import threading

from pathlib import Path

from mako.lookup import TemplateLookup
from mako import exceptions

import gazee
import gazee.versioning
from gazee.comicscan import ComicScanner

logging = logging.getLogger(__name__)

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
        cherrypy.session.load()
        if 'sizepref' not in cherrypy.session:
            cherrypy.session['sizepref'] = 'wide'
        logging.debug("Index Requested")
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

        c.execute("SELECT * FROM {tn} WHERE DATE('now') - {it} <= 7 ORDER BY date DESC, issue ASC LIMIT {nc} OFFSET {pn}".format(tn=gazee.ALL_COMICS, it=gazee.INSERT_DATE, cn=gazee.COMIC_NAME, ci=gazee.COMIC_NUMBER, nc=gazee.COMICS_PER_PAGE, pn=PAGE_OFFSET))
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
        user_level = gazee.authmech.get_user_level(user)

        logging.info("Index Served")

        return serve_template(templatename="index.html", comics=comics, num_of_pages=num_of_pages, current_page=int(page_num), user_level=user_level)

    @cherrypy.expose
    def search(self, page_num=1, search_string=''):
        cherrypy.session.load()
        if 'sizepref' not in cherrypy.session:
            cherrypy.session['sizepref'] = 'wide'
        logging.debug("Search Requested")
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
        user_level = gazee.authmech.get_user_level(user)

        logging.info("Search Served")

        return serve_template(templatename="search.html", comics=comics, num_of_pages=num_of_pages, current_page=int(page_num), user_level=user_level, search_string=search_string)

    """
    This returns the library view starting with the root library directory.
    """
    # Library Page
    @cherrypy.expose
    def library(self, parent, directory, page_num=1):
        cherrypy.session.load()
        if 'sizepref' not in cherrypy.session:
            cherrypy.session['sizepref'] = 'wide'
        logging.debug("Library Requested")
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

            for n in parent_key:
                c.execute("SELECT {fp} FROM {tn} WHERE {prk}=?".format(fp=gazee.FULL_DIR_PATH, tn=gazee.ALL_DIRS, prk=gazee.KEY), (n,))

                pdirinit = c.fetchall()
                parent_dir = [tup[0] for tup in pdirinit]

                if parent in parent_dir:
                    break

            full_dir = os.path.join(parent_dir[0], directory)

            c.execute("SELECT {prk} FROM {tn} WHERE {fp}=?".format(prk=gazee.KEY, tn=gazee.ALL_DIRS, fp=gazee.FULL_DIR_PATH), (full_dir,))

        pkinit = c.fetchall()
        pk = [tup[0] for tup in pkinit]

        # Select all the Nice Names from the Dir Names table.
        try:
            c.execute("SELECT {nn}, {di} FROM {tn} WHERE {ptk}=?".format(nn=gazee.NICE_NAME, di=gazee.DIR_IMAGE, tn=gazee.DIR_NAMES, ptk=gazee.PARENT_KEY), (pk[0],))

            dirsinit = c.fetchall()
            unsorted_directories = []
            for d in dirsinit:
                if d[1] is None:
                    unsorted_directories.append({"DirectoryName": d[0],
                                                 "DirectoryImage": "static/images/imgnotfound.png"})
                else:
                    unsorted_directories.append({"DirectoryName": d[0],
                                                 "DirectoryImage": d[1]})

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

            cp_split = os.path.split(gazee.COMIC_PATH)

            # Grinding the breadcrumb.
            if parent_dir == '':
                prd = ''
            else:
                parent_parts = os.path.split(parent_dir[0])
                prd = parent_parts[1]

            if prd == cp_split[1]:
                prd = ''

            # Sort and filter the directories
            new_dirs = sorted(unsorted_directories, key=lambda k: k['DirectoryName'])
            sorted_dirs = new_dirs
            directories = sorted_dirs

            filelist = []

            for d in sorted_dirs:
                if d['DirectoryName'].startswith('.'):
                    directories[:] = [r for r in directories if r.get('DirectoryName') != d['DirectoryName']]
                if parent_dir == '':
                    for root, dirs, files in os.walk(os.path.join(directory, d['DirectoryName'])):
                        filelist.extend(f for f in files)
                    if any(".cbz" in s for s in filelist):
                        filelist = []
                        continue
                    elif any(".cbr" in s for s in filelist):
                        filelist = []
                        continue
                    else:
                        filelist = []
                        directories[:] = [r for r in directories if r.get('DirectoryName') != d['DirectoryName']]
                else:
                    for root, dirs, files in os.walk(os.path.join(parent_dir[0], directory, d['DirectoryName'])):
                        filelist.extend(f for f in files)
                    if any(".cbz" in s for s in filelist):
                        filelist = []
                        continue
                    elif any(".cbr" in s for s in filelist):
                        filelist = []
                        continue
                    else:
                        filelist = []
                        directories[:] = [r for r in directories if r.get('DirectoryName') != d['DirectoryName']]

            connection.commit()
            connection.close()

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
        user_level = gazee.authmech.get_user_level(user)

        return serve_template(templatename="library.html", directories=directories, comics=comics, parent_dir=prd, num_of_pages=num_of_pages, current_page=int(page_num), current_dir=directory, user_level=user_level)

    @cherrypy.expose
    def download_comic(self, comic_path):
        return cherrypy.lib.static.serve_download(comic_path)

    """
    This returns the reading view of the selected comic after being passed the comic path and forcing the default of starting at page 0.
    """
    @cherrypy.expose
    def read_comic(self, comic_path, page_num=0):
        logging.debug("Reader Requested")

        cherrypy.session.load()
        username = cherrypy.request.login

        if 'sizepref' not in cherrypy.session:
            cherrypy.session['sizepref'] = 'wide'
        user_size_pref = cherrypy.session['sizepref']

        scanner = ComicScanner()
        scanner.user_unpack_comic(comic_path, username)
        image_list = scanner.reading_images(username)
        num_pages = len(image_list)

        if num_pages == 0:
            image_list = ['static/images/imgnotfound.png']

        cookie_comic = re.sub(r'\W+', '', comic_path)
        cookie_check = cherrypy.request.cookie
        if cookie_comic not in cookie_check:
            logging.debug("Cookie Creation")
            cookie_set = cherrypy.response.cookie
            cookie_set[cookie_comic] = 0
            cookie_set[cookie_comic]['path'] = '/'
            cookie_set[cookie_comic]['max-age'] = 2419200
            next_page = 1
            last_page = num_pages - 1
        else:
            logging.debug("Cookie Read")
            page_num = int(cookie_check[cookie_comic].value)
            logging.debug("Cookie Set To %d" % page_num)
            next_page = page_num + 1
            last_page = page_num - 1

        logging.info("Reader Served")
        return serve_template(templatename="read.html", pages=image_list, current_page=page_num, np=next_page, lp=last_page, nop=num_pages, size=user_size_pref, cc=cookie_comic)

    """
    This allows us to change pages and do some basic sanity checking.
    """
    @cherrypy.expose
    def change_page(self, page_str, cookie_comic):
        cherrypy.session.load()
        if 'sizepref' not in cherrypy.session:
            cherrypy.session['sizepref'] = 'wide'
        user_size_pref = cherrypy.session['sizepref']
        username = cherrypy.request.login
        page_num = int(page_str)
        next_page = page_num + 1
        last_page = page_num - 1
        scanner = ComicScanner()
        image_list = scanner.reading_images(username)
        num_pages = len(image_list)
        if page_num == -1:
            page_num = num_pages - 1
            next_page = 0
            last_page = num_pages - 2
        if page_num == num_pages:
            page_num = 0
            next_page = 1
            last_page = num_pages - 1

        cookie_set = cherrypy.response.cookie
        cookie_set[cookie_comic] = page_num
        cookie_set[cookie_comic]['path'] = '/'
        cookie_set[cookie_comic]['max-age'] = 2419200

        return serve_template(templatename="read.html", pages=image_list, current_page=page_num, np=next_page, lp=last_page, nop=num_pages, size=user_size_pref, cc=cookie_comic)

    @cherrypy.expose
    def up_size_pref(self, pref):
        cherrypy.session.load()
        cherrypy.session['sizepref'] = pref
        cherrypy.session.save()
        return
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
        # Grab Number of Comics in DB for display
        c.execute("SELECT COUNT(*) FROM {tn}".format(tn=gazee.ALL_COMICS))
        numcinit = c.fetchone()
        num_of_comics = numcinit[0]

        user = cherrypy.request.login
        user_level = gazee.authmech.get_user_level(user)

        # Grab all the users for display
        c.execute("SELECT * FROM {tn}".format(tn=gazee.USERS))
        usersinit = c.fetchall()
        users = []
        for f in usersinit:
            users.append({"User": f[0],
                          "Type": f[2]})

        # Generate time comic scan has been ongoing
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

        logo_paths = []
        for root, dirs, files in os.walk(os.path.join("public", "images", "logos")):
            logo_paths.extend(os.path.join(root, f) for f in files if '.png' in f)

        logos = []
        for f in logo_paths:
            logos.append(f.replace('public', 'static'))

        logdir = gazee.LOG_DIR
        logfiles = [i for i in os.listdir(logdir) if os.path.isfile(os.path.join(logdir, i)) and '.log' in i]

        logging.info("Settings Served")

        return serve_template(templatename="settings.html", user=user, user_level=user_level,
                              users=users, sip=scan_in_progress, noc=num_of_comics, logdir=logdir, logfiles=logfiles,
                              scantime=scantime, logos=logos, gazee_version=gazee.versioning.current_version(),
                              latest_version=gazee.versioning.latest_version(), python_version=sys.version_info)

    @cherrypy.expose
    @cherrypy.tools.accept(media='text/plain')
    def save_settings(self, scomicPath=None, scomicsPerPage=None, scomicScanInterval=None, smylarPath=None, ssslKey=None, ssslCert=None, sport=4242):
        # Set these here as they'll be used to assign the default values of the method arguments to the current values if they aren't updated when the method is called.
        config = configparser.ConfigParser()
        config.read(os.path.join(gazee.DATA_DIR, 'app.ini'))

        config['GLOBAL']['PORT'] = sport
        config['GLOBAL']['COMIC_PATH'] = scomicPath
        config['GLOBAL']['COMICS_PER_PAGE'] = scomicsPerPage
        config['GLOBAL']['COMIC_SCAN_INTERVAL'] = scomicScanInterval
        config['GLOBAL']['MYLAR_DB'] = smylarPath
        config['GLOBAL']['SSL_KEY'] = ssslKey
        config['GLOBAL']['SSL_CERT'] = ssslCert
        with open(os.path.join(gazee.DATA_DIR, 'app.ini'), 'w') as configfile:
            config.write(configfile)
        configfile.close()
        logging.info("Settings Saved")
        return

    @cherrypy.expose
    def change_theme(self, mainColor, accentColor, webTextColor, logo):
        # Set these here as they'll be used to assign the default values of the method arguments to the current values if they aren't updated when the method is called.
        config = configparser.ConfigParser()
        config.read(os.path.join(gazee.DATA_DIR, 'app.ini'))

        config['GLOBAL']['MAIN_COLOR'] = mainColor
        config['GLOBAL']['ACCENT_COLOR'] = accentColor
        config['GLOBAL']['WEB_TEXT_COLOR'] = webTextColor
        config['GLOBAL']['LOGO'] = logo
        with open(os.path.join(gazee.DATA_DIR, 'app.ini'), 'w') as configfile:
            config.write(configfile)
        configfile.close()

        with open('public/css/style.css', 'r+') as f:
            style = f.read()
            f.seek(0)
            style = style.replace(gazee.MAIN_COLOR, mainColor)
            style = style.replace(gazee.ACCENT_COLOR, accentColor)
            style = style.replace(gazee.WEB_TEXT_COLOR, webTextColor)
            f.write(style)
            f.truncate()

        gazee.MAIN_COLOR = mainColor
        gazee.ACCENT_COLOR = accentColor
        gazee.WEB_TEXT_COLOR = webTextColor
        gazee.LOGO = logo

        logging.info("Theme Saved")
        return

    @cherrypy.expose
    def get_log_text(self, logfile):
        logging.info('Dumping log file {} to text.'.format(logfile))

        with open(os.path.join(gazee.LOG_DIR, logfile), 'r') as f:
            log_text = ''.join(reversed(f.readlines()))

        return log_text

    @cherrypy.expose
    def change_password(self, user, password):
        gazee.authmech.change_pass(user, password)
        logging.info("Password Changed")
        return

    @cherrypy.expose
    def new_user(self, username, password, usertype):
        added = False
        if gazee.authmech.add_user(username, password, usertype):
            logging.info("New " + usertype.title() + " " + username + " Added")
            added = True
        return json.dumps({'added': added})

    @cherrypy.expose
    def del_user(self, username):
        db = Path(os.path.join(gazee.DATA_DIR, gazee.DB_NAME))
        connection = sqlite3.connect(str(db))
        c = connection.cursor()
        c.execute("DELETE FROM {tn} WHERE {cn}=?".format(tn=gazee.USERS, cn=gazee.USERNAME), (username,))
        connection.commit()
        connection.close()
        logging.info("User Deleted")
        return

    @cherrypy.expose
    def comic_scan(self):
        logging.info("DB Build Requested")
        scanner = ComicScanner()
        t1 = threading.Thread(target=scanner.db_builder)
        t1.start()
        return

    @cherrypy.expose
    def shutdown(self):
        cherrypy.engine.exit()
        if (os.path.exists(os.path.join(gazee.DATA_DIR, 'db.lock'))):
            os.remove(os.path.join(gazee.DATA_DIR, 'db.lock'))
        threading.Timer(1, lambda: os._exit(0)).start()
        print("Gazee is stopping")
        logging.info('Gazee is shutting down...')
        return

    @cherrypy.expose
    def restart(self):
        cherrypy.engine.exit()
        if (os.path.exists(os.path.join(gazee.DATA_DIR, 'db.lock'))):
            os.remove(os.path.join(gazee.DATA_DIR, 'db.lock'))
        popen_list = [sys.executable, gazee.FULL_PATH]
        popen_list += gazee.ARGS
        print("Gazee is restarting")
        logging.info('Restarting Gazee with ' + str(popen_list))
        if sys.platform == 'win32':
            subprocess.Popen(popen_list, cwd=os.getcwd())
            os._exit(0)
        else:
            os.execv(sys.executable, popen_list)
        logging.info('Gazee is restarting...')
        return

    @cherrypy.expose
    def update_gazee(self):
        updated = False
        if gazee.versioning.update_app():
            print("Gazee is restarting to update.")
            logging.info('Gazee is restarting to apply update.')
            if (os.path.exists(os.path.join(gazee.DATA_DIR, 'db.lock'))):
                os.remove(os.path.join(gazee.DATA_DIR, 'db.lock'))
            updated = True
        return json.dumps({'update': updated, 'current_version': gazee.versioning.current_version(),
                           'latest_version': gazee.versioning.latest_version()})

    @cherrypy.expose
    def opds(self):
        # TODO
        return "not implemented yet"
