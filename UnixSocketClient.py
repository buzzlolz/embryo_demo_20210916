# -*- coding: utf-8 -*-
"""
Created on Fri Jun 28 10:56:54 2019

@author: minghung
"""

import os, sys
import socket
import json
import logging
from Logger import Logger


class UnixSocketClient:
    def __init__(self, addr, logger):
        self.socket_addr = addr
        self.logger = logger   
    
    def Send(self, request):        
        rsp_data = None
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.settimeout(5)        

        try:       
            #Send
            sock.connect(self.socket_addr)            
            sock.sendall(json.dumps(request).encode())            
            self.logger.info('Send msg=' + str(request))
            #Response
            rsp = sock.recv(1024).decode()           
            self.logger.info('Rsp=' + str(rsp))
            if rsp != '':
                print(str(rsp))
                rsp_data = json.loads(str(rsp))                           
        except:           
            print('[ERROR]Unix socket send error msg=' +  str(sys.exc_info()[1]))
            self.logger.error('Socket send error msg=' +  str(sys.exc_info()[1]))
        
        sock.close()
        return rsp_data
     
        
if __name__ == '__main__':
    logger = Logger('test').logger
    logger.setLevel(logging.INFO)

    socket_client = UnixSocketClient('bind_test', logger)    
    msg = {"chamber_id":'3',"dish_id":'2',"check_isboundary":True}     
    rsp = socket_client.Send(msg)  
    print ('Rsp message:' + str(rsp))  



