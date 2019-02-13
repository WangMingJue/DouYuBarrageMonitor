# File Usage:
#
# Author: MingJue

import logging
import os.path
import time

global logger
logger = None


def get_logger():
    global logger
    if logger is None:
        # First, create a logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)  # Log level master switch

        # Second, create a handler, write information to log file
        rq = time.strftime('%Y%m%d', time.localtime(time.time()))
        log_path = os.path.split(os.path.realpath(__file__))[0]
        log_name = "{0}/{1}.log".format(log_path, rq)
        logfile = log_name
        fh = logging.FileHandler(logfile, mode='a+')
        fh.setLevel(logging.DEBUG)  # Log level switch for output to file

        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)  # Log level switch for output to console

        # Third, define the output format for the handler
        formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
        fh.setFormatter(formatter)

        # Fourth, add logger to handler
        logger.addHandler(fh)
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    return logger


if __name__ == '__main__':
    # logger example
    logger.debug('this is a logger debug message')
    logger.info('this is a logger info message')
    logger.warning('this is a logger warning message')
    logger.error('this is a logger error message')
    logger.critical('this is a logger critical message')
