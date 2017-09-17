import logging
import logging.handlers
import os


def start(path, verboseon):

    if not os.path.exists(path):
        os.makedirs(path)

    logfile = os.path.join(path, 'gazee.log')
    number_of_logs = 5
    if verboseon:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO

    formatter = logging.Formatter('%(levelname)s %(asctime)s %(name)s.%(funcName)s: %(message)s')
    handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=5000000, backupCount=number_of_logs, encoding='utf-8')
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging_level)

    return
