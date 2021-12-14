from configparser import RawConfigParser
import os

def ReadSqlInfoPath():
    path = './config/config_sqlite_path.ini'
    # print('ini path',path)
    
    if not os.path.exists(path): 
        print('Not found file=' + path) 
        
                       
    else:
        cfg = RawConfigParser()   
        cfg.read(path)
        sql_data_path = cfg.get('Path','sql_data_path')
        history_path = cfg.get('Path','history_path')       
       
        return sql_data_path,history_path