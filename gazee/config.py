import os
import configparser
import logging

import gazee


def configRead():

    logging.basicConfig(level=logging.DEBUG, filename=os.path.join(gazee.DATA_DIR, 'gazee.log'))
    logger = logging.getLogger(__name__)

    if not os.path.exists(os.path.join(gazee.DATA_DIR, 'app.ini')):
        with open(os.path.join(gazee.DATA_DIR, 'app.ini'), 'a') as cf:
            cf.write("[GLOBAL]\n")
            cf.write("port = 4242\n")
            cf.write("comic_path =\n")
            cf.write("comic_scan_interval = 60\n")
            cf.write("comics_per_page = 15\n")
            cf.write("mylar_db =\n")
            cf.write("ssl_key =\n")
            cf.write("ssl_cert =\n")
            cf.write("web_text_color = FFFFFF\n")
            cf.write("main_color = 757575\n")
            cf.write("accent_color = bdbdbd\n")
        cf.close()

    config = configparser.ConfigParser()
    config.read(os.path.join(gazee.DATA_DIR, 'app.ini'))

    gazee.PORT = int(config['GLOBAL']['PORT'])
    gazee.COMIC_PATH = config['GLOBAL']['COMIC_PATH']
    gazee.COMIC_SCAN_INTERVAL = config['GLOBAL']['COMIC_SCAN_INTERVAL']
    gazee.COMICS_PER_PAGE = int(config['GLOBAL']['COMICS_PER_PAGE'])
    gazee.MYLAR_DB = config['GLOBAL']['MYLAR_DB']
    gazee.SSL_KEY = config['GLOBAL']['SSL_KEY']
    gazee.SSL_CERT = config['GLOBAL']['SSL_CERT']
    gazee.WEB_TEXT_COLOR = config['GLOBAL']['WEB_TEXT_COLOR']
    gazee.MAIN_COLOR = config['GLOBAL']['MAIN_COLOR']
    gazee.ACCENT_COLOR = config['GLOBAL']['ACCENT_COLOR']
    gazee.ARGS = []
    gazee.THUMB_SIZE = 400, 300
    return
