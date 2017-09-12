import os
import configparser

import gazee


def config_read():
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
            cf.write("accent_color = BDBDBD\n")
            cf.write("logo = static/images/logos/red/logo-red-yellow.png\n")
        cf.close()

    config = configparser.ConfigParser()
    config.read(os.path.join(gazee.DATA_DIR, 'app.ini'))

    try:
        gazee.PORT = int(config['GLOBAL']['PORT'])
    except:
        with open(os.path.join(gazee.DATA_DIR, 'app.ini'), 'a') as cf:
            cf.write("port = 4242\n")
        cf.close()
    try:
        gazee.COMIC_PATH = config['GLOBAL']['COMIC_PATH']
    except:
        with open(os.path.join(gazee.DATA_DIR, 'app.ini'), 'a') as cf:
            cf.write("comic_path =\n")
        cf.close()
    try:
        gazee.COMIC_SCAN_INTERVAL = config['GLOBAL']['COMIC_SCAN_INTERVAL']
    except:
        with open(os.path.join(gazee.DATA_DIR, 'app.ini'), 'a') as cf:
            cf.write("comic_scan_interval = 60\n")
        cf.close()
    try:
        gazee.COMICS_PER_PAGE = int(config['GLOBAL']['COMICS_PER_PAGE'])
    except:
        with open(os.path.join(gazee.DATA_DIR, 'app.ini'), 'a') as cf:
            cf.write("comics_per_page = 15\n")
        cf.close()
    try:
        gazee.MYLAR_DB = config['GLOBAL']['MYLAR_DB']
    except:
        with open(os.path.join(gazee.DATA_DIR, 'app.ini'), 'a') as cf:
            cf.write("mylar_db =\n")
        cf.close()
    try:
        gazee.SSL_KEY = config['GLOBAL']['SSL_KEY']
    except:
        with open(os.path.join(gazee.DATA_DIR, 'app.ini'), 'a') as cf:
            cf.write("ssl_key =\n")
        cf.close()
    try:
        gazee.SSL_CERT = config['GLOBAL']['SSL_CERT']
    except:
        with open(os.path.join(gazee.DATA_DIR, 'app.ini'), 'a') as cf:
            cf.write("ssl_cert =\n")
        cf.close()
    try:
        gazee.WEB_TEXT_COLOR = config['GLOBAL']['WEB_TEXT_COLOR']
    except:
        with open(os.path.join(gazee.DATA_DIR, 'app.ini'), 'a') as cf:
            cf.write("web_text_color = FFFFFF\n")
        cf.close()
    try:
        gazee.MAIN_COLOR = config['GLOBAL']['MAIN_COLOR']
    except:
        with open(os.path.join(gazee.DATA_DIR, 'app.ini'), 'a') as cf:
            cf.write("main_color = 757575\n")
        cf.close()
    try:
        gazee.ACCENT_COLOR = config['GLOBAL']['ACCENT_COLOR']
    except:
        with open(os.path.join(gazee.DATA_DIR, 'app.ini'), 'a') as cf:
            cf.write("accent_color = BDBDBD\n")
        cf.close()
    try:
        gazee.LOGO = config['GLOBAL']['LOGO']
    except:
        with open(os.path.join(gazee.DATA_DIR, 'app.ini'), 'a') as cf:
            cf.write("logo = static/images/logos/red/logo-red-yellow.png\n")
        cf.close()
    return
