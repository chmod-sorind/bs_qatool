# bsLogger.py
import logging

logFile = 'logs\log.log'


def write(log_level, msg):
    logging.basicConfig(format='%(asctime)s(%(levelname)s) %(message)s',
                        datefmt='[%Y-%m-%dT%H:%M:%S]',
                        filename=logFile, level=logging.DEBUG)
    log_level(msg)
