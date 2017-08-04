import os
import sys
import cherrypy
import sqlite3

from pathlib import Path

from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions

import gazee
from gazee.comicscan import ComicScanner

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
    Index Page, only needed to show the start page. From here, we'll use jquery calls to load in the rest of the application via the exposed methods.
    """
    @cherrypy.expose
    def index(self):
        return serve_template(templatename="index.html")

    """
    This returns the html template for the recents div.
    The recents div is by default the the last twenty comics added to the DB in the last 20 days.
    """
    #TODO
    # Make the amount of comics and time span user settable.
    # Optimize: New to all this, page loads a bit slow when being return for the first time. Images are already kept in their cache so how can we speed up the presentation of them? Gzip? Need to look into possibilities.
    @cherrypy.expose
    def recents(self):
        # Here we set the db file path.
        db = Path(os.path.join(gazee.DATA_DIR, gazee.DB_NAME))

        # Here we make the inital DB connection that we will be using throughout this function.
        connection = sqlite3.connect(str(db))
        c = connection.cursor()

        c.execute("SELECT * FROM {tn} WHERE DATE('now') - {it} <= 7 LIMIT 20".format(tn=gazee.ALL_COMICS, it=gazee.INSERT_DATE))
        # DB Always returns a tuple of lists. After fetching it, we then iterate over its various lists to assign their values to a dictionary.
        all_recent_comics_tup = c.fetchall()
        comics = []
        for f in all_recent_comics_tup:
            comics.append({"Key":                f[0],
                           "ComicName":          f[1],
                           "ComicImage":         f[2],
                           "ComicIssue":         f[3],
                           "ComicVolume":        f[4],
                           "ComicSummary":       f[5],
                           "ComicPath":          f[6],
                           "DateAdded":          f[7]})

        connection.commit()
        connection.close()

        return serve_template(templatename="recents.html", comics=comics)

    """
    This returns the library view starting with the root library directory.
    """
    # Library Page
    @cherrypy.expose
    def library(self, directory):
        dir_contents = []
        comics = []
        directories = []
        if directory == gazee.COMIC_PATH:
            dir_contents = os.list(gazee.COMIC_PATH)
        else:
            dir_contents = os.list(os.path.join(gazee.COMIC_PATH, directory))
        for i in dir_contents:
            if i.endswith((".cbz",".cbr")):
                comics.append

        return serve_template(templatename="recents.html", directory=directory, children=children)

    """
    This returns the reading view of the selected comic after being passed the comic path and forcing the default of starting at page 0.
    """
    # TODO
    # Good place to pass in a bookmark, how do we make them?
    @cherrypy.expose
    def readComic(self, comic_path, page_num=0):
        scanner = ComicScanner()
        scanner.unpackComic(comic_path)
        image_list = scanner.readingImages()
        num_pages = len(image_list)
        num_pages -= 1
        return serve_template(templatename="read.html", pages=image_list, current_page=page_num, np=1, lp=0)

    """
    This allows us to change pages and do some basic sanity checking.
    """
    #TODO 
    # Make this better. Should completely disable ability to cycle comic from first to last page in this manner as it causes some artifacting I can't account for at the moment.
    @cherrypy.expose
    def changePage(self, page_str):
        page_num = int(page_str)
        next_page = page_num + 1
        last_page = page_num - 1
        scanner = ComicScanner()
        image_list = scanner.readingImages()
        num_pages = len(image_list)
        if next_page > num_pages:
            page_num = 0
        if last_page < 0:
            page_num = num_pages - 1
        return serve_template(templatename="read.html", pages=image_list, current_page=page_num, np=next_page, lp=last_page, nop=num_pages)

    """
    This returns the settings page.
    """

    #Settings Page
    @cherrypy.expose
    def settings(self):
        #TODO
        scanner = ComicScanner()
        scanner.dbBuilder()
        return "Building"

    @cherrypy.expose
    def opds(self):
        #TODO
        return "not implemented yet"
