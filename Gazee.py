import os
import sys
import cherrypy
import string

import gazee
from gazee import *

def main():
    # Set the server config.
    cherrypy.config.update("data/server.conf")
    # Start the server.
    cherrypy.quickstart(Gazee(), '/', 'data/server.conf')

    return

if __name__ == '__main__':
    main()
