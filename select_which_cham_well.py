import csv
import os
import pandas as pd
from pathlib import Path

from ReadSqlDataHistoryPath  import ReadSqlInfoPath
import shutil
# patient_folder = './patient_id_save/'

def create_csv(patient_id,chamber_id,dish_id):
    patient_folder = './patient_id_save/'
    csv_path = os.path.join(patient_folder,patient_id+'.csv')
    if os.path.exists(csv_path):
        df=pd.read_csv(csv_path)
        df=df.append({'chamber':chamber_id,'dish':dish_id},ignore_index=True)
        
        df.to_csv(csv_path,index=0)
        # pass
    else:
        dic ={'chamber':[],'dish':[]}
        df = pd.DataFrame(dic)
        
        df=df.append({'chamber':chamber_id,'dish':dish_id},ignore_index=True)
        df.to_csv(csv_path,index=0)


def read_csv_get_chamber(patient_id):
    patient_folder = './patient_id_save/'
    csv_path = os.path.join(patient_folder,patient_id+'.csv')
    if os.path.exists(csv_path):
        df=pd.read_csv(csv_path)
        print("df len:",len(df['chamber']))
        for i in range(len(df['chamber'])):
            print("chamber :  {}  dish: {} ".format(df['chamber'][i],df['dish'][i]))



def make_empty_folder(patient_his_folder):
    

    for chamber in range(1,13):
        chamber_folder_path = os.path.join(patient_his_folder,'cham'+str(chamber))
        if not Path(chamber_folder_path).exists():
            os.mkdir(chamber_folder_path)
            for dish in range(1,16):
                dish_folder_path = os.path.join(chamber_folder_path,'dish'+str(dish))
                if not Path(dish_folder_path).exists():
                    # print('mkdir','./data/ori_img/cham'+str(chamber)+'/dish'+str(dish))
                    os.mkdir(dish_folder_path)

def move_select_cham_dish_folder(patient_id,time):
    

    _,his_folder_path= ReadSqlInfoPath()
    patient_csv_folder='./patient_id_save/'
    ori_img_folder = './data/crop_img/'
    # img_dir = './data/crop_img/'
    



    chamber_idlist = []
    chamber_id =-1
    # dish_idlist=[]

    #mkdir  patiend id folder
    patient_his_folder = os.path.join(his_folder_path,patient_id)
    if not os.path.isdir(patient_his_folder):
        os.mkdir(patient_his_folder)
    #mkdir time stamp folder
    patient_his_time_folder=os.path.join(patient_his_folder,time)
    if not os.path.isdir(patient_his_time_folder):
        os.mkdir(patient_his_time_folder)
    

    #get which chamber need to copy 
    csv_path = os.path.join(patient_csv_folder,patient_id+'.csv')
    if os.path.exists(csv_path):
        df=pd.read_csv(csv_path)

        chamber_id=df['chamber'][0]

    
    ori_chamber_path = os.path.join(ori_img_folder,"cham"+str(chamber_id))
    # print(' ori_chamber_path:',ori_chamber_path)
    backup_path = os.path.join(patient_his_time_folder,"cham"+str(chamber_id))
    shutil.copytree(ori_chamber_path,backup_path)

    

    # if os.path.exists(csv_path):
    #     df=pd.read_csv(csv_path)
    #     for i in range(len(df['chamber'])):
    #         chamber_idlist.append(df['chamber'][i])
    #         dish_idlist.append(df['dish'][i])
    #         print("chamber :  {}  dish: {} ".format(df['chamber'][i],df['dish'][i]))
    # print("chamber_idlist:",chamber_idlist)
    # print("dish_idlist:",dish_idlist)

    # make_empty_folder(patient_his_folder)


    # for i in range(len(chamber_idlist)):
    #     chamber_id=chamber_idlist[i]
    #     dish_id=dish_idlist[i]
    #     folder_path ='cham'+str(chamber_id)+'/dish'+str(dish_id)
    #     img_folder_dir= os.path.join(ori_img_folder,folder_path)
    #     hist_folder_dir = os.path.join(patient_his_folder,folder_path)
    #     if os.path.exists(hist_folder_dir):
    #         shutil.rmtree(hist_folder_dir)
    #     shutil.copytree(img_folder_dir,hist_folder_dir)






if __name__ == "__main__":
    # create_csv("A12345",1,2)
    # create_csv("A12345",1,1)
    # read_csv_get_chamber("A12345")
    move_select_cham_dish_folder("A12345",'20201010')
    