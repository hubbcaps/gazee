#!/usr/bin/env python3
#  This file is part of Gazee.
#
#  Gazee is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Gazee is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Gazee.  If not, see <http://www.gnu.org/licenses/>.

import os
import sys
import argparse
import logging

import cherrypy
from cherrypy.process.plugins import Daemonizer, PIDFile

import gazee
from gazee import Gazee, ComicScanner

logging = logging.getLogger(__name__)

gazee.FULL_PATH = os.path.abspath(__file__)
# Verify our app is working out of the install directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

if (sys.platform == 'win32' and sys.executable.split('\\')[-1] == 'pythonw.exe'):
    sys.stdout = open(os.devnull, "w")
    sys.stderr = open(os.devnull, "w")


def main():
    parser = argparse.ArgumentParser(description='Gazee - Open Comic Book Reader')

    parser.add_argument('-d', '--daemon', action='store_true', help='Run as a daemon')
    parser.add_argument('-c', '--datadir', help='Set data directory')
    parser.add_argument('-l', '--logdir', help='Set log directory')
    parser.add_argument('-v', '--verbose', action='store_true', help='Set log level to debug')

    args = parser.parse_args()

    if args.datadir:
        gazee.DATA_DIR = args.datadir
        gazee.TEMP_DIR = os.path.join(args.datadir, 'tmp')

    if not os.path.exists(gazee.DATA_DIR):
        os.makedirs(os.path.abspath(gazee.DATA_DIR))

    if not os.path.exists(os.path.join(gazee.DATA_DIR, 'sessions')):
        os.makedirs(os.path.abspath(os.path.join(gazee.DATA_DIR, 'sessions')))

    if not os.path.exists(gazee.TEMP_DIR):
        os.makedirs(os.path.abspath(gazee.TEMP_DIR))

    from gazee import log
    if args.logdir:
        gazee.LOG_DIR = args.logdir
        gazee.ARGS += ["-l", gazee.LOG_DIR]
    else:
        gazee.LOG_DIR = gazee.DATA_DIR
    if args.verbose:
        log.start(gazee.LOG_DIR, True)
        gazee.ARGS += ["-v"]
    else:
        log.start(gazee.LOG_DIR, False)
    cherrypy.log.error_log.propagate = True
    cherrypy.log.access_log.propagate = False

    gazee.db.db_creation()
    gazee.config.config_read()

    if args.daemon:
        if sys.platform == 'win32':
            logging.info("Daemonize not supported under Windows, starting normally")
        else:
            # If the pidfile already exists, Gazee may still be running, so exit
            if os.path.exists(gazee.PIDFILE):
                sys.exit("PID file '" + gazee.PIDFILE + "' already exists. Exiting.")

            # The pidfile is only useful in daemon mode, make sure we can write the file properly
            try:
                PIDFile(cherrypy.engine, gazee.PIDFILE).subscribe()
            except IOError as e:
                raise SystemExit("Unable to write PID file: %s [%d]" % (e.strerror, e.errno))
            if gazee.DATA_DIR is not 'data':
                gazee.ARGS += ["-c", gazee.DATA_DIR]
            gazee.ARGS += ["-d"]
            Daemonizer(cherrypy.engine).subscribe()

    # This verifies the color scheme stays between automated updates as what the user set.
    if os.path.exists('public/css/style.css'):
        with open('public/css/style.css') as f:
            style = f.read()

        with open('public/css/style.css', "w") as f:
            style = style.replace("757575", gazee.MAIN_COLOR)
            style = style.replace("BDBDBD", gazee.ACCENT_COLOR)
            style = style.replace("FFFFFF", gazee.WEB_TEXT_COLOR)
            f.write(style)

    if gazee.DATA_DIR is not 'data':
        conf = {
            '/': {
                'tools.gzip.on': True,
                'tools.gzip.mime_types': ['text/*', 'application/*', 'image/*'],
                'tools.sessions.on': True,
                'tools.sessions.timeout': 1440,
                'tools.sessions.storage_class': cherrypy.lib.sessions.FileSession,
                'tools.sessions.storage_path': os.path.join(gazee.DATA_DIR, "sessions"),
                'tools.auth_basic.on': True,
                'tools.auth_basic.realm': 'Gazee',
                'tools.auth_basic.checkpassword': gazee.authmech.check_password,
                'request.show_tracebacks': False
            },
            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'tools.staticdir.dir': "public"
            },
            '/data': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': gazee.DATA_DIR
            },
            '/tmp': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': gazee.TEMP_DIR
            },
            '/favicon.ico': {
                'tools.staticfile.on': True,
                'tools.staticfile.filename': os.path.join(os.getcwd(), "public/images/favicon.ico")
            }
        }
    else:
        conf = {
            '/': {
                'tools.gzip.on': True,
                'tools.gzip.mime_types': ['text/*', 'application/*', 'image/*'],
                'tools.staticdir.root': os.path.abspath(os.getcwd()),
                'tools.sessions.on': True,
                'tools.sessions.timeout': 1440,
                'tools.sessions.storage_class': cherrypy.lib.sessions.FileSession,
                'tools.sessions.storage_path': os.path.join(gazee.DATA_DIR, "sessions"),
                'tools.auth_basic.on': True,
                'tools.auth_basic.realm': 'Gazee',
                'tools.auth_basic.checkpassword': gazee.authmech.check_password,
                'request.show_tracebacks': False
            },
            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': "public"
            },
            '/data': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': gazee.DATA_DIR
            },
            '/tmp': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': gazee.TEMP_DIR
            },
            '/favicon.ico': {
                'tools.staticfile.on': True,
                'tools.staticfile.filename': os.path.join(os.getcwd(), "public/images/favicon.ico")
            }
        }

    if (gazee.SSL_KEY == '') and (gazee.SSL_CERT == ''):
        options_dict = {
            'server.socket_port': gazee.PORT,
            'server.socket_host': '0.0.0.0',
            'server.thread_pool': 30,
            'log.screen': False,
            'engine.autoreload.on': False,
        }
    else:
        options_dict = {
            'server.socket_port': gazee.PORT,
            'server.socket_host': '0.0.0.0',
            'server.thread_pool': 30,
            'server.ssl_module': 'builtin',
            'server.ssl_certificate': gazee.SSL_CERT,
            'server.ssl_private_key': gazee.SSL_KEY,
            'log.screen': False,
            'engine.autoreload.on': False,
        }

    cherrypy.config.update(options_dict)

    cherrypy.engine.timeout_monitor.unsubscribe()
    cherrypy.tree.mount(Gazee(), '/', config=conf)

    logging.info("Gazee Started")

    cherrypy.engine.start()
    print("Gazee has started")
    scanner = ComicScanner()
    scanner.rescan_db()
    cherrypy.engine.block()


if __name__ == '__main__':
    main()
