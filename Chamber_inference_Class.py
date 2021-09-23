import keras
from keras.models import load_model
import numpy as np
import sys
from pathlib import Path
import glob
import time
import cv2
import argparse
import pandas as pd
import csv
from mask_rcnn_inf import img_inference_cell,load_cell_mask_model,load_frag_model,img_inference_frag

from keras.applications.inception_v3 import InceptionV3, preprocess_input

import random
import efficientnet.keras
import yolo
from yolo import YOLO
import os
import threading
import matplotlib.pyplot as plt
import Logger
from PyQt5 import QtCore

from Logger import Logger
from UnixSocketClient import UnixSocketClient
import logging

from PIL import Image 

import queue
import tensorflow as tf
logging.basicConfig(level=logging.DEBUG)

class Chamber_Inference(QtCore.QThread):
    finished = QtCore.pyqtSignal(int)
    def __init__(self, socket_client, logger, parent=None):        
        super(self.__class__, self).__init__(parent=parent)
        
        self.queue_chamber_id = queue.Queue(maxsize=6)
        self.socket_client = socket_client
        self.logger = logger
        self.b_stop = False
        self.o_stop = False
        self.cancel_chamber_ids = []
        self.current_analysis_chamber_id = 0
        
        self.load_models()

        # global cell_mask_model 
        # global yolo_ini
        # global frag_model

        # global sqlite_model

    def run(self):
        print('Inference start')
        while not self.b_stop:
            #print('while start')
            self.o_stop = False
            if not self.queue_chamber_id.empty():            
                cham_id = self.queue_chamber_id.get()
                if str(cham_id) in self.cancel_chamber_ids:
                     self.cancel_chamber_ids.remove(str(cham_id))
                     self.logger.info('Cancel chamber id=' + str(cham_id))
                     continue
                print('run anlysis chamid=' + cham_id)
                self.logger.info('Run chamber id=' + str(cham_id))
                self.current_analysis_chamber_id = cham_id                
                self.one_chamber_run(cham_id)
                print('run anlysis status=' + str(self.o_stop))
                
                self.finished.emit(int(cham_id))
                self.logger.info('Finish run chamber id=' + str(cham_id))                
                self.current_analysis_chamber_id = 0
                
                continue
            
            time.sleep(1)
            
        print('Break analysis loop')    
        self.logger.warning('Break analysis loop')

    def StopAnalysisChamberID(self, chamber_id):
        #Current run
        if str(self.current_analysis_chamber_id) == str(chamber_id):
            self.o_stop = True            
            return
            
        #if str(chamber_id) in list(self.queue_chamber_id.queue):
        #Add to cancel list               
        if str(chamber_id) not in self.cancel_chamber_ids:
            self.cancel_chamber_ids.append(str(chamber_id))    
        
    def Stop(self):
        self.b_stop = True
        
    def PutChamberID(self, chamber_id):
        #if not self.queue_chamber_id.full():
        if str(chamber_id) in self.cancel_chamber_ids:
            self.cancel_chamber_ids.remove(str(chamber_id))
            
        thread = threading.Thread(target=self.put_chamberID, kwargs={'chamber_id': chamber_id}) 
        thread.daemon = True
        thread.start()
        
    def CancelAnalysisChamberID(self, chamber_id):
        self.cancel_chamber_ids.append(str(chamber_id))
    
    def put_chamberID(self, chamber_id):
        if chamber_id not in list(self.queue_chamber_id.queue):
            self.queue_chamber_id.put(chamber_id)

    def load_sqlite_model(self):
        # net = load_model('./model_data/20201212_inception_stage1-8.hdf5',compile=False)
        net = load_model('./model_data/20201102_incv3_sqlite_013-0.036.hdf5',compile=False)
        return net

    def load_stage_pn_morula_blas_model(self):
        # net = load_model('./model_data/20201212_inception_stage1-8.hdf5',compile=False)
        net = load_model('./model_data/20210111_stage_pn_morula_blas.hdf5',compile=False)
        return net



    def predict_sqlitemodel_bak(self,model, img):
        """Run model prediction on image
        Args:
            model: keras model
            img: PIL format image
            target_size: (w,h) tuple
        Returns:
            list of predicted labels and their probabilities
        """

        label_to_pred_value= {'0': '2', '1': '3', '2': '4', '3': '5', '4': '6', '5': '7', '6': '8', '7': 'blas', '8': 'morula', '9': 'pn'}
        

        #   x = image.img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = preprocess_input(img)
        preds = model.predict(img)
        ayay=np.array(preds[0])
        pred_label = label_to_pred_value[str(np.argmax(ayay))]

        return pred_label


    def predict_sqlitemodel(self,model, img):
        """Run model prediction on image
        Args:
            model: keras model
            img: PIL format image
            target_size: (w,h) tuple
        Returns:
            list of predicted labels and their probabilities
        """
    

        #   x = image.img_to_array(img)
        img = np.expand_dims(img, axis=0)
        img = preprocess_input(img)
        preds = model.predict(img)
        ayay=np.array(preds[0])
        return str(np.argmax(ayay)+1)




    def sqlite_cell_classification_getcell(self,net,img_path):

        # net = sqlite_model
        img = cv2.imread(str(img_path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
        if img is not None:
            img= cv2.resize(img,(299,299))
            # res=predict_sqlitemodel(net,img)
            res=self.predict_sqlitemodel_bak(net,img)
        return res
            





    def check_env_folder(self):
        
        if not Path("./csv").exists():
            os.mkdir("./csv")
        if not Path('./video').exists():
            os.mkdir('./video')

        if not Path("./data/").exists():
            os.mkdir("./data/")
        if not Path('./data/ori_img').exists():
            os.mkdir('./data/ori_img')
        if not Path('./data/crop_img').exists():
            os.mkdir('./data/crop_img')
        if not Path('./history/').exists():
            os.mkdir('./history/')
        



        
        for chamber in range(1,13):
            if not Path('./data/ori_img/cham'+str(chamber)).exists():
                os.mkdir('./data/ori_img/cham'+str(chamber))
                for dish in range(1,16):
                    if not Path('./data/ori_img/cham'+str(chamber)+'/dish'+str(dish)).exists():
                        # print('mkdir','./data/ori_img/cham'+str(chamber)+'/dish'+str(dish))
                        os.mkdir('./data/ori_img/cham'+str(chamber)+'/dish'+str(dish))
        for chamber in range(1,13):
            if not Path('./data/crop_img/cham'+str(chamber)).exists():
                os.mkdir('./data/crop_img/cham'+str(chamber))
                for dish in range(1,16):
                    if not Path('./data/crop_img/cham'+str(chamber)+'/dish'+str(dish)).exists():
                        # print('mkdir','./data/ori_img/cham'+str(chamber)+'/dish'+str(dish))
                        os.mkdir('./data/crop_img/cham'+str(chamber)+'/dish'+str(dish))
        for chamber in range(1,13):
            if not Path('./csv/cham'+str(chamber)).exists():
                os.mkdir('./csv/cham'+str(chamber))
                for dish in range(1,16):
                    if not Path('./csv/cham'+str(chamber)+'/dish'+str(dish)).exists():
                        # print('mkdir','./data/ori_img/cham'+str(chamber)+'/dish'+str(dish))
                        os.mkdir('./csv/cham'+str(chamber)+'/dish'+str(dish))
            
        # if not Path("csv/data_img/").exists():
        #     os.mkdir("csv/data_img/")
        # if not Path("csv/stage_result/").exists():
        #     os.mkdir("csv/stage_result/")



    def load_data_folder(self,folder_dir):
        cham_list=os.listdir(folder_dir)
        dish_path_list=[]
        for cham in cham_list:
            cham_dir = os.path.join(folder_dir,cham)
            dish_list = os.listdir(cham_dir)
            for dish in dish_list:
                dish_path_list.append(os.path.join(cham_dir,dish))
        return dish_path_list
        


    def emb_yolo_crop(self,yolo_ini,image):
        img,top,left,bottom,right=yolo_ini.detect_image_with_stable_bbox(image)
        return img,top,left,bottom,right
        # cv2.waitKey(10)


    def check_emb_isboundary(self,yolo_shape,top,left,bottom,right):
        CenterX = (left+right)/2
        CenterY = (top+bottom)/2
        print("CenterX:",CenterX)
        print("CenterY:",CenterY)
        if CenterX<yolo_shape[0]/3 or CenterX>(yolo_shape[0]/3)*2 or CenterY<yolo_shape[1]/3 or CenterY>(yolo_shape[1]/3)*2:
            print('out of boundary')
        
            return True
        else:
            return False




    def read_from_video(self,video_dir):
        cap = cv2.VideoCapture(video_dir)
        while True:
            ret,frame = cap.read()
            if not ret:
                break
            
            #frame = cv2.resize(frame,(300,300))
            yield frame

    def read_dir_img_list(self,image_dir):
        for img_path in Path(image_dir).glob("*.*"):
            yield img_path


    def read_from_img(self,image_dir):

        image_dir = Path(image_dir)

        for img_path in image_dir.glob("*.*"):

            print(img_path)
            img = cv2.imread(str(img_path))
            #cv2.imshow('test',img)
            #cv2.waitKey(0)
            #cv2.destroyAllWindows()

            if img is not None:
                img= cv2.resize(img,(300,300))
        
                yield img,img_path

    def read_img_from_list(self,img_list,folder_path):


        for img_name in img_list:

            # print(img_path)
            img_path=os.path.join(folder_path,img_name)
            
            print('img path yolo:',img_path)
            img = cv2.imread(str(img_path))
            #cv2.imshow('test',img)
            #cv2.waitKey(0)
            #cv2.destroyAllWindows()

            if img is not None:
                img= cv2.resize(img,(300,300))
        
                yield img,img_path
                

    # def status_res_to_csv(filename,status):
    #     with open("./csv_record/test.csv",'a+',newline='') as csvfile:
    #         writer=csv.writer(csvfile)
    #         with open("./csv_record/test.csv",'r',newline='') as f:
    #             reader = csv.reader(f)
    #             if not[row for row in reader]:
    #                 writer .writerow(["file_name","status",'stage'])
    #                 writer.writerow([filename,str(status)])
    #             else :
    #                 writer.writerow([filename,str(status)])


    def check_undo_img_csv(self,filename,csv_path):
        

        if os.path.exists(csv_path):
            df=pd.read_csv(csv_path)
            

            if filename not in df["file_name"].values:
                df=df.append({'file_name':filename,"check":'F'},ignore_index=True)
                # print("filename:",filename)

                # print('new one')
            else :
                df.loc[df['file_name'].values==str(filename),'check']="T"
                # print("filename:",filename)

            df.to_csv(csv_path,index=0)
        else:
            dic = {
                'file_name':[],
                'check':[],
                'status':[],
                'cell_stage':[],
                'frag_percentage':[]
            }
            df = pd.DataFrame(dic)
            df=df.append({'file_name':filename,"check":'F'},ignore_index=True)
            df.to_csv(csv_path,index=0)

    def emb_status_csvwrite(self,img_path,status,csv_path):
        filename = os.path.basename(img_path)





        # filename = str(filename).split('\\')[-1]
        # csv_path = str(Path(csv_dir)/folder_name)+'.csv'
        # print("csv_path:",csv_path)
        # filename = str(img_path).split('/')[-1]

        if os.path.exists(csv_path):
            df=pd.read_csv(csv_path)
            

            
            df.loc[df['file_name'].values==str(filename),'status']=status
            # print("filename:",filename)

            df.to_csv(csv_path,index=0)

    def cell_stage_csvwrite(self,img_path,cell_stage,csv_path):
        # filename = str(filename).split('\\')[-1]
        filename = os.path.basename(img_path)
        # csv_path = str(Path(csv_dir)/folder_name)+'.csv'
        # # print("csv_path:",csv_path)
        # filename = str(img_path).split('/')[-1]

        if os.path.exists(csv_path):
            df=pd.read_csv(csv_path)
            

            
            df.loc[df['file_name'].values==str(filename),'cell_stage']=cell_stage
            # print("filename:",filename)

            df.to_csv(csv_path,index=0)

    def frag_percentage_csvwrite(self,img_path,frag_percentage,csv_path):
        # # filename = str(filename).split('\\')[-1]
        # csv_path = str(Path(csv_dir)/folder_name)+'.csv'
        # # print("csv_path:",csv_path)
        # filename = str(img_path).split('/')[-1]

        filename = os.path.basename(img_path)

        if os.path.exists(csv_path):
            df=pd.read_csv(csv_path)
            

            
            df.loc[df['file_name'].values==str(filename),'frag_percentage']=str(frag_percentage)

            print("frag_precentage :",frag_percentage)
            # print("filename:",filename)

            df.to_csv(csv_path,index=0)
        
    def get_undo_img_list(self,csv_path):
        img_list = []
        # csv_path = str(Path(csv_dir)/folder_name)+'.csv'
        print("csv_path:",csv_path)
        df=pd.read_csv(csv_path)
        print(df)

        if os.path.exists(csv_path):
            df=pd.read_csv(csv_path)
            # print(df.cell_stage[df['cell_stage']==None])
            img_list=df.file_name[df['cell_stage'].isna()]
            
            # img_list=df.file_name[df['check']=='F']
            print("img_list",img_list)
            return img_list
            

    def crop_img_write(self,crop_img,crop_img_path):

        crop_img=cv2.cvtColor(np.array(crop_img),cv2.COLOR_RGB2BGR)
        crop_img=cv2.resize(crop_img,(300,300))

        cv2.imwrite(crop_img_path,crop_img)
        
        # if not Path(Path(crop_folder_path)/folder_name).exists():
        #     print("mkdir :",str(Path(Path(crop_folder_path)/folder_name)))
        #     os.mkdir(str(Path(crop_folder_path)/folder_name))
        # crop_img=cv2.cvtColor(np.array(crop_img),cv2.COLOR_RGB2BGR)
        # crop_img=cv2.resize(crop_img,(300,300))
        # crop_img_name=str(Path(crop_img_path)).split('/')[-1]
        # new_crop_img_path = Path(Path(crop_folder_path)/folder_name)/crop_img_name
        # # crop_img_path=Path(crop_img_dir)/folder_name
        
        # # print(str(Path(crop_img_path)/crop_img_name))
        # # cv2.imwrite(str(Path(crop_img_path)/crop_img_name),crop_img)
        # cv2.imwrite(str(new_crop_img_path),crop_img)
        # # crop_img_path = str(Path(crop_img_path)/crop_img_name)
        # print("str(new_crop_img_path):",str(new_crop_img_path))
        # return str(new_crop_img_path)



    def stage_res_to_csv(self,filename,stage):
        
        df=pd.read_csv("./csv_record/test.csv",encoding='utf-8')
        df.stage[df['file_name'].values==str(filename)]=stage
        # print(df)
        df.to_csv("./csv_record/test.csv",index=0)



    def get_emb_res_img(self,img_dir):
        img_name_list = []
        img_dir=Path(img_dir)
        for img_path in img_dir.glob('*.*'):
            img_name_list.append(str(img_path))
        return img_name_list




        
    # def get_csv_history(self,chamber_id,well_id):


    #     # stage_dic=dict()
    #     precent_dic=dict()
    #     dict_key=['2pn','2','3','4','5','6','7','8','blas']

    #     csv_dir = './csv/'
    #     img_dir = './data/crop_img/'
    #     folder_path ='cham'+str(chamber_id)+'/dish'+str(well_id)
    #     csv_name = 'cham'+str(chamber_id)+'_'+'dish'+str(well_id)+'.csv'

    #     csv_path = os.path.join(csv_dir,folder_path)
    #     csv_path = os.path.join(csv_path,csv_name)
    #     print("get stage csv path:",csv_path)
    #     img_folder_dir= os.path.join(img_dir,folder_path)
        
    #     each_percent_list=[]

    #     if os.path.isfile(csv_path):
    #         # csv_path =Path( Path("./csv/")/(str(emb_folder_sel)+'.csv'))
    #         df = pd.read_csv(str(csv_path),encoding='utf-8')
            
    #         # img_dir = str(Path('./data/crop_img/')/str(emb_folder_sel))

    #         temp=[]
    #         for i in range(8):
    #             lenth=len(df.file_name[df['cell_stage']==i+1].values)
    #             print("lenth:",lenth)
    #             percentage=0
    #             if lenth!=0:
    #                 select_img = list(df.file_name[df['cell_stage']==i+1])
    #                 print("select_img:",select_img)
    #                 for j in range(lenth):
    #                     # img_path = os.path.join(img_folder_dir,select_img[j])
    #                     percentage = percentage+df.frag_percentage[df['file_name']==str(select_img[j])].values[0]
    #                 percentage=round(percentage/lenth,2)
    #                 each_percent_list.append((percentage))

    #                 precent_dic[dict_key[i]]=percentage
    #         print("each_percent_list",each_percent_list)
    #         print('percent dict:',precent_dic)
            

                    
    #                 # print("df.file_name[df['cell_stage']==i+1].values[random.randint(0,lenth-1)]:",df.file_name[df['cell_stage']==i+1].values[random.randint(0,lenth-1)])
    #                 # img_path = os.path.join(img_folder_dir,select_img)
    #                 # # new_img_path = str(Path(img_dir)/select_img)
    #                 # percentage = df.frag_percentage[df['file_name']==str(select_img)].values[0]
    #                 # stage = df.cell_stage[df['file_name']==str(select_img)].values[0]
    #                 # each_img_list.append(img_path)
    #                 # each_precent_list.append(str(percentage))
    #                 # each_stage_list.append(stage)

    #                 # stage_dic[stage_index[i]]=stage
    #                 # precent_dic[stage_index[i]]=percentage
                    

        


    #         # print(stage_dic)   
    #         # print(precent_dic)
    #     return each_stage_list,each_img_list,each_precent_list




    def get_each_stage_result(self,chamber_id,well_id):


        stage_dic=dict()
        precent_dic=dict()
        filename_dic=dict()
        dict_key=['2pn','2','3','4','5','6','7','8','blas']

        csv_dir = './csv/'
        img_dir = './data/crop_img/'
        folder_path ='cham'+str(chamber_id)+'/dish'+str(well_id)
        csv_name = 'cham'+str(chamber_id)+'_'+'dish'+str(well_id)+'.csv'

        csv_path = os.path.join(csv_dir,folder_path)
        csv_path = os.path.join(csv_path,csv_name)
        print("get stage csv path:",csv_path)
        img_folder_dir= os.path.join(img_dir,folder_path)
        each_stage_list=[]
        each_img_list=[]
        each_precent_list=[]

        if os.path.isfile(csv_path):
            # csv_path =Path( Path("./csv/")/(str(emb_folder_sel)+'.csv'))
            df = pd.read_csv(str(csv_path),encoding='utf-8')
            
            # img_dir = str(Path('./data/crop_img/')/str(emb_folder_sel))

            temp=[]
            for i in range(8):
                lenth=len(df.file_name[df['cell_stage']==i+1].values)
                if lenth!=0:
                    select_img = df.file_name[df['cell_stage']==i+1].values[random.randint(0,lenth-1)]
                    # print("df.file_name[df['cell_stage']==i+1].values[random.randint(0,lenth-1)]:",df.file_name[df['cell_stage']==i+1].values[random.randint(0,lenth-1)])
                    img_path = os.path.join(img_folder_dir,select_img)
                    # new_img_path = str(Path(img_dir)/select_img)
                    percentage = df.frag_percentage[df['file_name']==str(select_img)].values[0]
                    stage = df.cell_stage[df['file_name']==str(select_img)].values[0]
                    each_img_list.append(img_path)
                    each_precent_list.append(str(percentage))
                    each_stage_list.append(stage)
                    
                    filename_dic[dict_key[i]]=img_path
                    stage_dic[dict_key[i]]=stage
                    precent_dic[dict_key[i]]=percentage
                    

        

            print(filename_dic)  
            print(stage_dic)   
            print(precent_dic)
        return dict_key,each_img_list,each_stage_list,each_precent_list


    # def img_to_video_bak(self,chamber_id,well_id):


    #     csv_dir = './csv/'
    #     img_dir = './data/crop_img/'
    #     folder_path ='cham'+str(chamber_id)+'/dish'+str(well_id)
    #     csv_name = 'cham'+str(chamber_id)+'_'+'dish'+str(well_id)+'.csv'

    #     csv_path = os.path.join(csv_dir,folder_path)
    #     csv_path = os.path.join(csv_path,csv_name)
    #     print("get stage csv path:",csv_path)

    #     folder_path = './data/crop_img/cham'+str(chamber_id)+'/dish'+str(well_id)
    #     save_video_path='./video/cham'+str(chamber_id)+'_'+'dish'+str(well_id)+'.avi'
    #     fps = 6  
        
    #     fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    #     videoWriter = cv2.VideoWriter(save_video_path,fourcc,fps,(300,300))
        
    #     if os.path.isfile(str(csv_path)):

    #         df = pd.read_csv(str(csv_path),encoding='utf-8')
    #         filename_list = df['file_name'].sort_values()
    #         print(filename_list)
    #         for filename in filename_list:
    #             img_path = os.path.join(folder_path,filename)
    #             if os.path.isfile(str(img_path)):
    #                 img = cv2.imread(img_path)
    #                 # print(img)
    #                 img=cv2.resize(img,(300,300))
    #                 videoWriter.write(img)
    #         videoWriter.release()



    # def img_to_video(self,chamber_well_path):


    #     csv_dir = './csv/'
    #     img_dir = './data/crop_img/'
    #     folder_path =chamber_well_path
    #     n_chamber_well_path=''
    #     if chamber_well_path.find('/')!=-1:

    #         n_chamber_well_path = chamber_well_path.replace('/','_')
    #         csv_name = n_chamber_well_path+'.csv'

    #     elif chamber_well_path.find('\\')!=-1:

    #         n_chamber_well_path = chamber_well_path.replace('\\','_')
    #         csv_name = n_chamber_well_path+'.csv'
        

    #     csv_path = os.path.join(csv_dir,folder_path)
    #     csv_path = os.path.join(csv_path,csv_name)
    #     print("get stage csv path:",csv_path)

    #     folder_path = os.path.join(img_dir,chamber_well_path)
    #     save_video_path=os.path.join('./video',n_chamber_well_path+'.avi')
    #     # save_video_path='./video/cham'+str(chamber_id)+'_'+'dish'+str(well_id)+'.avi'
    #     fps = 6  
        
    #     fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    #     videoWriter = cv2.VideoWriter(save_video_path,fourcc,fps,(300,300))
        
    #     if os.path.isfile(str(csv_path)):

    #         df = pd.read_csv(str(csv_path),encoding='utf-8')
    #         filename_list = df['file_name'].sort_values()
    #         print(filename_list)
    #         for filename in filename_list:
    #             img_path = os.path.join(folder_path,filename)
    #             if os.path.isfile(str(img_path)):
    #                 img = cv2.imread(img_path)
    #                 # print(img)
    #                 img=cv2.resize(img,(300,300))
    #                 videoWriter.write(img)
    #         videoWriter.release()


    def send_cham_dish_percent_socket(self, chamber_id, dish_id,schedule_percentage):
          
        msg = {"chamber_id":chamber_id, "dish_id":dish_id,'percentage':schedule_percentage}        
        rsp = self.socket_client.Send(msg)  
        # socket_thread=threading.Thread(target=UnixSocketClient(chamber_well_path))
    

    def send_socket(self,chamber_id,dish_id,check_boundary):
            
        msg = {"chamber_id":chamber_id,"dish_id":dish_id,'check_isboundary':check_boundary}        
        rsp = self.socket_client.Send(msg)  
        # socket_thread=threading.Thread(target=UnixSocketClient(chamber_well_path))
        if check_boundary:
            print('out of boundary')
        else:
            print('normal')




    def make_queue_list_boundary_status(self,image_dir):

        queue_list= []

        chamber_list = os.listdir(image_dir)
        for chamber_folder in chamber_list:

            chamber_path = os.path.join(image_dir,chamber_folder)
            dish_list = os.listdir(chamber_path)
            for dish_folder in dish_list:
                queue_list.append(chamber_folder+'_'+dish_folder)
        

        return queue_list



    def load_models(self):
        

        # global cell_mask_model 
        # global yolo_ini
        # global frag_model

        # global sqlite_model


        
        # blas_cd_model = load_model(model_path,compile=False) # model -> blas none blas classification
        self.graph_list =[]


        self.yolo_ini = YOLO()
        
        self.sqlite_model = self.load_stage_pn_morula_blas_model()
        # self.sqlite_model._make_predict_function()
        self.graph_list.append(tf.get_default_graph())
        
        # self.cell_mask_model = load_cell_mask_model()
        # self.cell_mask_model._make_predict_function()
        # self.graph_list.append(tf.get_default_graph())


        self.frag_model = load_frag_model()
        # self.frag_model._make_predict_function()
        self.graph_list.append(tf.get_default_graph())
        
        # sqlite_model=load_sqlite_model()
        # return blas_cd_model,yolo_ini,cell_mask_model


    def one_chamber_run(self,cham_id):


        

        # global cell_mask_model 
        # global yolo_ini
        # global frag_model

        # global sqlite_model

        self.check_env_folder()
        image_dir = './data/ori_img/'
        crop_image_dir = './data/crop_img/'
        # video_dir='./emb_video_0512/MTL-0245-11E9-4C5B-P10-FP3.avi'
        # label_list = ['blas','cd']
        # crop_folder_path = './data/crop_img/'
        csv_dir='./csv/'
        
        queue_make_list =self.make_queue_list_boundary_status(image_dir)
        # print('queue_make_list:',queue_make_list)
        
        record_emb_outboundary_status =[]

        for i in range(len(queue_make_list)):
            record_emb_outboundary_status.append(queue.Queue(3))

        


        img_folder_path = os.path.join(image_dir,'cham'+str(cham_id))
        dish_folder_path_list =[]
        # print(img_folder_path)

        for d_id in range(1,16):
            dish_folder_path_list.append(os.path.join(img_folder_path,'dish'+str(d_id)))


        # dish_folder_list = os.listdir(img_folder_path)
        


        # for dish_folder_name in dish_folder_list:
        #     dish_folder_path_list.append(os.path.join(img_folder_path,dish_folder_name))
        # print('RRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRRR')
        print(logging.debug('dish_folder_path_list: %s'%(dish_folder_path_list)))
        # print('dish_folder_path_list',dish_folder_path_list)

        
        
        # print('each schedule percent:',each_schedule_percent)


        for index,dish_folder_path in enumerate(dish_folder_path_list):
            chamber_id = dish_folder_path[dish_folder_path.find('cham')+4:dish_folder_path.find('dish')-1]
            dish_id = dish_folder_path[dish_folder_path.find('dish')+4:]


            #add stop 
            if self.o_stop:
                break

            print('dish_folder_path',dish_folder_path)

            if len(os.listdir(dish_folder_path))!=0:
                schedule_percentage=0
                # each_schedule_percent=int(100/len(dish_folder_path))
                logging.debug('dish_folder_len :  %a'%(len(os.listdir(dish_folder_path))))
                # print('dish_folder_len',len(os.listdir(dish_folder_path)))
                each_img_schedule_percent = 100/len(os.listdir(dish_folder_path))
                
                # folder_path = Path(image_dir)/folder_name
                logging.debug('folder_path : %s'%(dish_folder_path))
                
                # print('folder_path',dish_folder_path)
                image_path_genereator = self.read_dir_img_list(dish_folder_path)
                csv_path=''
                
                for img_path in image_path_genereator:
                    # print('img_path',img_path)
                    image_name =os.path.basename(img_path)
                    csv_dir_path = dish_folder_path.replace(image_dir,csv_dir)
                    # print("csv_dir  path ",csv_dir_path)
                    csv_name = csv_dir_path.split('/')[-2]+'_'+csv_dir_path.split('/')[-1]+'.csv'
                    # print('csv_name:',csv_name)
                    csv_path = os.path.join(csv_dir_path,csv_name)
                    self.check_undo_img_csv(image_name,csv_path)

                    

                
                img_list_todo = self.get_undo_img_list(csv_path)
                print('img_list_todo',img_list_todo)
                logging.debug("list to do : %s"%(img_list_todo))
                

                # print("list to do :",img_list_todo)
                logging.debug('chamber_id dish_id: %s , %s '%(chamber_id,dish_id))
                

                
                # print('chamber_id dish_id: ',chamber_id,dish_id)


                # if img_list_todo is not None:
                #     if not img_list_todo.empty :
                #         chamber_well_path = dish_folder_path.replace(image_dir,'')
                #         video_thread  = threading.Thread(target=self.img_to_video(chamber_well_path))
                #         video_thread.start()
                yolo_img_generator=self.read_img_from_list(img_list_todo,dish_folder_path)
                out_boundary_send=False
                status=''
                img_count=0
                if img_list_todo is not None:
                    for img,img_path in yolo_img_generator:

                        #add stop 
                        if self.o_stop:
                            break


                        image_yolo = Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
                        crop_img,top,left,bottom,right=self.emb_yolo_crop(self.yolo_ini,image_yolo)


                        # #check outof boundary number is bigger than 3
                        # t1=time.time()
                        # out_boundary_check=check_emb_isboundary(image_yolo.size,top,left,bottom,right)
                        # if record_emb_outboundary_status[int(chamber_id)*15+int(dish_id)-1].full():
                        #     record_emb_outboundary_status[int(chamber_id)*15+int(dish_id)-1].get()
                        #     record_emb_outboundary_status[int(chamber_id)*15+int(dish_id)-1].put(out_boundary_check)
                        # else:
                        #     record_emb_outboundary_status[int(chamber_id)*15+int(dish_id)-1].put(out_boundary_check)
                        # # print(list(record_emb_outboundary_status[int(chamber_id)*15+int(dish_id)-1].queue))
                        # previous_queue= list(record_emb_outboundary_status[int(chamber_id)*15+int(dish_id)-1].queue)

                        # # if False in previous_queue:
                        # #     out_boundary_send=False
                        # print('previous_queue',previous_queue)

                        # if record_emb_outboundary_status[int(chamber_id)*15+int(dish_id)-1].full() and False not in previous_queue and status!=True:
                        #     print("need to transmission------------------------")
                        #     status=True
                        #     # out_boundary_send=True
                        #     socket_thread=threading.Thread(target=send_socket(chamber_id,dish_id,True))
                        #     socket_thread.start()
                        # if record_emb_outboundary_status[int(chamber_id)*15+int(dish_id)-1].full() and True not in previous_queue and status!=False:
                        #     # out_boundary_send=False
                        #     print('normal-------------------------------')
                        #     status=False
                        #     socket_thread=threading.Thread(target=send_socket(chamber_id,dish_id,False))
                        #     socket_thread.start()
                        # t2=time.time()
                        # print('time q spend:',t2-t1)

                        

                        # print("img yolo path:",img_path)
                        # print('yolo box:',top,left,bottom,right)

                        crop_img_path = img_path.replace(image_dir,crop_image_dir)
                        self.crop_img_write(crop_img,crop_img_path)

                        with self.graph_list[0].as_default():
                            
            
                            cell_number=self.sqlite_cell_classification_getcell(self.sqlite_model,crop_img_path)
                            self.cell_stage_csvwrite(crop_img_path,cell_number,csv_path)

                        with self.graph_list[1].as_default():
    
                            frag_percentage=img_inference_frag(self.frag_model,crop_img_path)
                            self.frag_percentage_csvwrite(crop_img_path,frag_percentage,csv_path)

                        schedule_percentage+=each_img_schedule_percent
                        # print('schedule percent:',schedule_percentage)
                        logging.debug('schedule percent: %s'%(schedule_percentage))


                        if img_count%10==0:
                            socket_thread=threading.Thread(target=self.send_cham_dish_percent_socket(cham_id, dish_id,int(schedule_percentage)))
                            socket_thread.start()
                        img_count+=1
                        
            if not self.o_stop:
                socket_thread=threading.Thread(target=self.send_cham_dish_percent_socket(cham_id, dish_id,100))
                socket_thread.start()

            

    #def start(self, cham_id):
    #   self.one_chamber_run(cham_id)

                        

            
            



            



    


if __name__ == '__main__':
    logger = Logger('test').logger
    logger.setLevel(logging.INFO)

    socket_client = UnixSocketClient('bind_test', logger)
    inf_class = Chamber_Inference(socket_client,logger)
    inf_class.start(8)
    
    # get_each_stage_img()
   