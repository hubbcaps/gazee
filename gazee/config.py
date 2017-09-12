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

    config = configparser.ConfigParser()
    config.read(os.path.join(gazee.DATA_DIR, 'app.ini'))
    
    config_errors = []
    try:
        gazee.PORT = int(config['GLOBAL']['PORT'])
    except:
        config_errors.append("port = 4242")

    try:
        gazee.COMIC_PATH = config['GLOBAL']['COMIC_PATH']
    except:
        config_errors.append("comic_path =")
        
    try:
        gazee.COMIC_SCAN_INTERVAL = config['GLOBAL']['COMIC_SCAN_INTERVAL']
    except:
        config_errors.append("comic_scan_interval = 60")

    try:
        gazee.COMICS_PER_PAGE = int(config['GLOBAL']['COMICS_PER_PAGE'])
    except:
        config_errors.append("comics_per_page = 15")

    try:
        gazee.MYLAR_DB = config['GLOBAL']['MYLAR_DB']
    except:
        config_errors.append("mylar_db =")

    try:
        gazee.SSL_KEY = config['GLOBAL']['SSL_KEY']
    except:
        config_errors.append("ssl_key =")

    try:
        gazee.SSL_CERT = config['GLOBAL']['SSL_CERT']
    except:
         config_errors.append("ssl_cert =")

    try:
        gazee.WEB_TEXT_COLOR = config['GLOBAL']['WEB_TEXT_COLOR']
    except:
        config_errors.append("web_text_color = FFFFFF")

    try:
        gazee.MAIN_COLOR = config['GLOBAL']['MAIN_COLOR']
    except:
        config_errors.append("main_color = 757575")

    try:
        gazee.ACCENT_COLOR = config['GLOBAL']['ACCENT_COLOR']
    except:
        config_errors.append("accent_color = BDBDBD")

    try:
        gazee.LOGO = config['GLOBAL']['LOGO']
    except:
        config_errors.append("logo = static/images/logos/red/logo-red-yellow.png")
    
    if len(config_errors) > 0:
        with open(os.path.join(gazee.DATA_DIR, 'app.ini'), 'a') as cf:
            cf.write("\n".join(config_errors) + "\n")

    return
