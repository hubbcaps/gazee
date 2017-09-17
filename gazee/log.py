import logging
import logging.handlers
import os


def start(path, verboseon):

    if not os.path.exists(path):
        os.makedirs(path)

    logfile = os.path.join(path, 'gazee.log')
    backup_days = 8
    if verboseon:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO

    formatter = logging.Formatter('%(levelname)s %(asctime)s %(name)s.%(funcName)s: %(message)s')
    handler = logging.handlers.TimedRotatingFileHandler(logfile, when="D", interval=1, backupCount=backup_days, encoding='utf-8')
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging_level)

    return
