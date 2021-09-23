import os
import pandas as pd
import sqlite3
import numpy as np
import math
from PIL import Image
import io
from io import BytesIO
import threading
from Logger import Logger
from UnixSocketClient import UnixSocketClient
import logging
import cv2
import sys

from pathlib import Path

logging.basicConfig(level=logging.DEBUG)



class Extract_Sqlite():
    def __init__(self,sqlite_folder_path,cham_id,socket_client):
        self.sqlite_folder_path=sqlite_folder_path
        self.cham_id=cham_id
        self.b_stop=False
        self.socket_client= socket_client

        # self.sqlite_folder_path,self.cham_id,self.socket_client




    def send_socket(self,cham_id, schedule_percent, socket_client):       
        msg = {'chamber_id':cham_id,"percentage":int(schedule_percent)}        
        rsp = socket_client.Send(msg)  
        # socket_thread=threading.Thread(target=UnixSocketClient(chamber_well_path))
    
    




    def make_database_csv(self,sqlite_folder_path):
        df =pd.DataFrame()   
        
        
        if os.path.isdir(sqlite_folder_path):
            sql_list = os.listdir(sqlite_folder_path)
            if len(sql_list)>0:
                sqlite_folder_name = [x for x in sql_list if x.find('FP')==-1][0]
                # sqlite_folder_name = sql
                print('sqlite_folder_name:',sqlite_folder_name)

                sqlite_db_path  = os.path.join(sqlite_folder_path,sqlite_folder_name)
                print('sqlite_db_path:',sqlite_db_path)

                # if os.path.isfile(sqlite_db_path):
                #     write_folder_path = os.path.join(write_path,folder_name)
                #     print('write_folder_path',write_folder_path)
                #     if not os.path.isdir(write_folder_path):
                #         os.mkdir(write_folder_path)


                
                # print(sqlite_db_path)
                with sqlite3.connect(sqlite_db_path) as con:
                    
                    df=pd.read_sql_query("SELECT * FROM Images ",con)
                    
                    
                    return df
            else:
                return df
                    



    def sqlite2video_7FP(self,df,socket_client):
        schedule_percent=0
        save_datafolder_path='./data/ori_img/cham'+str(self.cham_id)
        # save_folder_root= './sql_extract_data'
        video_folder_root = './video/'

        folder_name = os.path.basename(self.sqlite_folder_path)

       
        
        
        # save_folder_path='./data/ori_img/cham'+str(save_cham_id)
        sql_list = os.listdir(self.sqlite_folder_path)
        if len(sql_list)>0:
            for sql in sql_list:
                if self.b_stop:
                    print(self.b_stop)
                    break
                if sql.find('FP')!=-1 and sql.find('.sqlite')!=-1:

                    print(sql)
                    # if sql.find('05')!=-1:
                    sql_path = os.path.join(self.sqlite_folder_path,sql)
                    sql_fpnum = int(sql[sql.find('.')-1])

                    with sqlite3.connect(sql_path) as con:

                        data = con.cursor()
                        data.execute("SELECT Content FROM ImageData ")


                        dataid = con.cursor()
                        dataid.execute("SELECT ImageId FROM ImageData ")
                        
                        Id_data = dataid.fetchall()

                        image = data.fetchall()
                        # print(len(image))
                        # print(Id_data[0])

                        dishId_list = list(set(df['DishPositionId']))

                        number_img = len(image)

                        image = np.array(image)

                        # fp_path = os.path.join(csvfolder_path,fp_name)
                        # if  not os.path.isdir(fp_path):
                        #     os.mkdir(fp_path)

                        each_image_schedule_percent = 100/len(image)/7
                        

                        
                        # for j in range(len(set(df['DishPositionId']))):
                        #     dish_path = os.path.join(save_folder_path,'dish'+str(dishId_list[j]))
                        #     if not os.path.isdir(dish_path):
                        #         os.mkdir(dish_path)
                        Id_data_list = []

                        for i in range(len(Id_data)):
                            Id_data_list.append(Id_data[i][0])
                        
                    
                        DishPositionId_list = set(df['DishPositionId'].values)

                        
                        for dish in DishPositionId_list:
                            # print(self.b_stop)
                            if self.b_stop:
                                print(self.b_stop)
                                break
                                # sys.exit('bstop ==True')

                            ImageId_list = df['ImageId'][(df['DishPositionId'] == dish)&(df['FocalPlaneIndex'] == sql_fpnum)].values
                            # print(len(ImageId_list))
                            dish_img_index=[]
                            for img_id in ImageId_list:
                                
                                dish_img_index.append(Id_data_list.index(img_id))
                            # print(dish_img_index)

                            #every fp video write------------------------------

                            fps = 6  
                            video_id_path =os.path.join(video_folder_root,folder_name)
                            if not os.path.isdir(video_id_path):
                                os.mkdir(video_id_path)
                            video_cham_path = os.path.join(video_id_path,'cham'+str(self.cham_id))
                            if not os.path.isdir(video_cham_path):
                                os.mkdir(video_cham_path)
                            video_dish_path =os.path.join(video_cham_path,'dish'+str(dish))
                            if not os.path.isdir(video_dish_path):
                                os.mkdir(video_dish_path)
                            save_video_name = folder_name+'_cham'+str(self.cham_id)+'_dish'+str(dish)+'_FP'+str(sql_fpnum)+'.avi'
                            save_video_path = os.path.join(video_dish_path,save_video_name)
                            print('save_video_path :',save_video_path)
            
                            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
                            videoWriter = cv2.VideoWriter(save_video_path,fourcc,fps,(900,900))


                            #every fp video write------------------------------




                            for count_frame,index in enumerate(dish_img_index):
                                
                                if self.b_stop:
                                    print(self.b_stop)
                                    break

                                roiImg = Image.open(BytesIO(image[index]))  
                                roiImg_=cv2.cvtColor(np.asarray(roiImg),cv2.COLOR_RGB2BGR)  

                            #     print(Id_data[i][0])
                                filename=df['Filename'][df['ImageId']==Id_data[index][0]].values[0]
                                dish = df['DishPositionId'][df['Filename']==filename].values[0]
                                # print('dish',dish)


                                #----------------write 7fp all img to folder
                        
                                # save_img_path = os.path.join(save_folder_path,'FP0'+str(sql_fpnum))
                                # save_img_path = os.path.join(save_img_path,'dish'+str(dish))
                                # save_img_path = os.path.join(save_img_path,filename)
                                # print(save_img_path)
                                # roiImg.save(save_img_path)

                                roiImg_video=cv2.resize(roiImg_,(900,900))
                                cv2.putText(roiImg_video,str(format(count_frame/6, '.2f'))+'hr' , (650, 820), cv2.FONT_HERSHEY_SIMPLEX,2, (0, 0, 255), 3, cv2.LINE_AA)

                                videoWriter.write(roiImg_video)
                                
                                
                                if sql_fpnum==5:
                                    save_datafolder_img_path = os.path.join(save_datafolder_path,'dish'+str(dish))
                                    save_datafolder_img_path = os.path.join(save_datafolder_img_path,filename)
                                    roiImg.save(save_datafolder_img_path)
                                
                                schedule_percent+=each_image_schedule_percent
                            
                                if count_frame %20==0:
                                    socket_thread=threading.Thread(target=self.send_socket(self.cham_id,schedule_percent, socket_client))
                                    socket_thread.start()
                                    print('schedule percent:',schedule_percent)
                                    print('socket send')
                                    # socket_thread=threading.Thread(target=send_socket(schedule_percent))
                                    # socket_thread.start()
                            videoWriter.release()

                        
        if not self.b_stop:                    
            schedule_percent=100
            print('schedule percent:',schedule_percent)
            socket_thread=threading.Thread(target=self.send_socket(self.cham_id,schedule_percent, socket_client))
            socket_thread.start()
                        

                        


                        


    



    def start_extract(self):
        # self.sqlite_folder_path=sqlite_folder_path
        df=self.make_database_csv(self.sqlite_folder_path)
        print('df:',df)
        if not df.empty:
            # self.cham_id = cham_id
            # sqlite2img(df,sqlite_folder_path,save_cham_id)
            self.sqlite2video_7FP(df, self.socket_client)
    

    def stop(self):
        self.b_stop = True
        
    
    




if __name__ == "__main__":
        
    logger = Logger('test').logger
    logger.setLevel(logging.INFO)

    socket_client = UnixSocketClient('bind_test', logger)   
    # socket_client=UnixSocketClient()
    sqlite_folder_path='/media/n200/Transcend/Embryo_data/sql_data/MTL-0245-13A1-9874'
    save_cham_id='8'

    es = Extract_Sqlite(sqlite_folder_path,save_cham_id,socket_client)
    
    th=threading.Thread(target=es.start_extract)
    es.stop()


    
    
    
   