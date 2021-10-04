# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 09:19:56 2019

@author: minghung
"""
import os, sys, threading, time
import socket
import json
import logging
from Logger import Logger
from PyQt5 import QtCore


class UnixSocketServer(QtCore.QThread):    
    finished = QtCore.pyqtSignal(dict)
    def __init__(self, addr, logger, parent=None):
        super(UnixSocketServer, self).__init__(parent=parent) 
        #Server
        self.b_stop = False          
        self.logger = logger
        self.socket_addr = addr        
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            os.remove(self.socket_addr)
        except OSError:
            pass
        print('Server address:%s' %self.socket_addr)
        
    def run(self):                
        self.logger.info('Starting up server')        
        self.sock.bind(self.socket_addr)
        self.sock.listen(5)
        self.sock.settimeout(2)        
        while not self.b_stop:
            # print('waiting for a query')
            query = {}
            try:
                #Receive
                connection, client_addr = self.sock.accept()                
                data = connection.recv(1024)               
                query = json.loads(data.decode())
                print (str(query))
                self.logger.info('Socket recv=' + str(query))
                #Response
                rsp ={"response":"ok"}               
                connection.sendall(json.dumps(rsp).encode())                
            except:
                # print('[Warning]Unix socket server error msg=' +  str(sys.exc_info()[1]))
                if 'timed out' not in str(sys.exc_info()[1]):
                    self.logger.error('Socket error msg=' + str(sys.exc_info()[1]))    
            
            self.finished.emit(query)            
          
        self.logger.info('Stop server')        
                   
    def Stop(self):
        self.b_stop = True
       
            
if __name__ == '__main__':
    logger = Logger('test').logger
    logger.setLevel(logging.INFO)
    
    uds_server = UnixSocketServer('bind_test', logger)
    uds_server.run()
    time.sleep(5)
    uds_server.Stop()
    time.sleep(5)


           
