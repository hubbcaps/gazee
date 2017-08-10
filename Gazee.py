import os, sys
import cherrypy
import string
import logging

from pathlib import Path

import gazee
from gazee import *

def main():
    logging.basicConfig(level=logging.DEBUG,filename='data/gazee.log')
    logger = logging.getLogger(__name__) 

    conf = {
            'global' : {
                'server.socket_host': '0.0.0.0',
                'server.socket_port': 4242
                },
            '/' : {
                'tools.gzip.on': True,
                'tools.sessions.on': True,
                'tools.sessions.storage_class': cherrypy.lib.sessions.FileSession,
                'tools.sessions.storage_path': "data/sessions",
                'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'tools.basic_auth.on': True,
                'tools.basic_auth.realm': 'Gazee',
                'tools.basic_auth.users': gazee.authmech.getPassword,
                'tools.basic_auth.encrypt': gazee.authmech.hashPass
                },
            '/static' : {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': "public"
                },
            '/data' : {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': "data"
                },
            '/tmp' : {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': "tmp"
                }
            }
    # Start the server.
    cherrypy.quickstart(Gazee(), '/', config=conf)
    logging.info("Gazee Started")

    return

if __name__ == '__main__':
    main()
