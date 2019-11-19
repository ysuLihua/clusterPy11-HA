#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%m/%d/%Y %H:%M:%S %p"
logging.basicConfig(filename='installManager.log', level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)
def info(msg):
    logging.info(msg)
def warn(msg):
    logging.warn(msg)
def error(msg):
    logging.error(msg)