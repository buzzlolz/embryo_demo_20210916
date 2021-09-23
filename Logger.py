# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 14:22:59 2019

@author: minghung
"""
import os
import errno
import logging
from time import strftime, localtime
from logging.handlers import RotatingFileHandler


class Logger():
    def __init__(self, name):
        #Set logger parameter
        try:
            os.makedirs(os.getcwd() + '/log')
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
        logFormatStr = '%(asctime)-14s [%(levelname)s] %(module)s:%(funcName)s: %(message)s'
        logging.basicConfig(format = logFormatStr, filename = './log/systemlog_' + name + '.log', level=logging.INFO)
        formatter = logging.Formatter(logFormatStr)
        sizeHandler = RotatingFileHandler('./log/systemlog_' + name + '.log', mode='a', maxBytes=5*1024*1024, backupCount=10, encoding=None, delay=0)
        sizeHandler.setLevel(logging.INFO)
        sizeHandler.setFormatter(formatter)
        
        self.logger = logging.getLogger(name)
        self.logger.propagate = False
        self.logger.addHandler(sizeHandler)
    
