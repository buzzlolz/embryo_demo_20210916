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
# from mask_rcnn_inf import img_inference_cell,load_cell_mask_model,load_frag_model,img_inference_frag
import random
import efficientnet.keras
import yolo
from yolo import YOLO
import os
# import threading
import matplotlib.pyplot as plt

from PIL import Image 






def crop_img_write(crop_img,crop_img_path):

    crop_img=cv2.cvtColor(np.array(crop_img),cv2.COLOR_RGB2BGR)
    crop_img=cv2.resize(crop_img,(300,300))

    cv2.imwrite(crop_img_path,crop_img)
    
    


def emb_yolo_crop(yolo_ini,image):
    img,*_=yolo_ini.detect_image(image)
    return img
    # cv2.waitKey(10)







# folder_path='/home/n200/D-slot/3dcnn_sqlitedata_1119/8/'
folder_path='/home/n200/D-slot/3dcnn_8test/'



yolo_ini = YOLO()

for dirPath, dirNames, fileNames in os.walk(folder_path):
    
    for f in fileNames:
        img_path =  os.path.join(dirPath, f)


        if img_path.endswith('.jpg'):
    # print(img_path)
            # img_path=os.path.join(folder_path,img_name)
            
            print('img path yolo:',img_path)
            img = cv2.imread(str(img_path))
            #cv2.imshow('test',img)
            #cv2.waitKey(0)
            #cv2.destroyAllWindows()

            if img is not None:
                img= cv2.resize(img,(300,300))
            image_yolo = Image.fromarray(cv2.cvtColor(img,cv2.COLOR_BGR2RGB))
            crop_img=emb_yolo_crop(yolo_ini,image_yolo)
            print("img yolo path:",img_path)
        #         # print("RRRRRRRR img_path :",img_path)
        #         t2= time.time()
        #         print("time ----yolocrop--------:",t2-t1)
        #         total_time+=t2-t1
        #         total_yolo_list.append(t2-t1)
            
            crop_img_write(crop_img,img_path)

            