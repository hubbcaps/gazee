import os, sys
import cherrypy
import string

from pathlib import Path

import gazee
from gazee import *

def main():
    conf = {
            '/' : {
                'tools.gzip.on': True,
                'tools.sessions.on': True,
                'tools.sessions.storage_class': cherrypy.lib.sessions.FileSession,
                'tools.sessions.storage_path': "data/sessions",
                'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'tools.digest_auth.on': True,
                'tools.digest_auth.realm': 'Gazee',
                'tools.digest_auth.users': gazee.authmech.getPassword
                },
            'global' : {
                'server.socket_host': '0.0.0.0',
                'server.socket_port': 4242
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

    return

if __name__ == '__main__':
    main()
