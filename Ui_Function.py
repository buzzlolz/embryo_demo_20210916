
import os, math
import pandas as pd
import csv
import random
import cv2
import shutil
import numpy as np
import pickle
# from scipy import stats
import logging
import copy
import sqlite3

logging.basicConfig(level=logging.WARNING)



#load timelapse image and save as a video
# def img_to_video(chamber_id,well_id):
#     csv_dir = './csv/'
#     img_dir = './data/crop_img/'
#     video_folder_dir = './video/'
#     folder_path ='cham'+str(chamber_id)+'/dish'+str(well_id)
#     # folder_path =chamber_well_path

#     img_folder_path = os.path.join(img_dir,folder_path)

#     filename_list = os.listdir(img_folder_path)
#     filename_list.sort()
#     save_video_path=os.path.join(video_folder_dir,'cham'+str(chamber_id)+'_'+'dish'+str(well_id)+'.avi')
#     # save_video_path='./video/cham'+str(chamber_id)+'_'+'dish'+str(well_id)+'.avi'
#     fps = 6  
    
#     fourcc = cv2.VideoWriter_fourcc(*'MJPG')
#     videoWriter = cv2.VideoWriter(save_video_path,fourcc,fps,(320,240))

#     for filename in filename_list:
#         img_path = os.path.join(img_folder_path,filename)
#         if os.path.isfile(str(img_path)):
#             #print( img_path)
#             img = cv2.imread(img_path)
#             # print(img)
#             img=cv2.resize(img,(320,240))
#             videoWriter.write(img)
#     videoWriter.release()      
# 
#    

# get time lapse video path
def load_video_path_with_7fp(patient_id,chamber_id,dish_id,fp_id):
    video_path=''
    video_folder_path = './video/'+str(patient_id)+'/cham'+str(chamber_id)+'/dish'+str(dish_id)
    print('video folder path',video_folder_path)
    if os.path.isdir(video_folder_path):
        video_list = os.listdir(video_folder_path)
        if len(video_list)!=0:
            for video_name in video_list:
                print('video_name',video_name)
                if video_name[video_name.find('.avi')-1]==str(fp_id):
                    video_path=os.path.join(video_folder_path,video_name)
                


    # path = os.path.abspath('./video/cham'+str(chamber_id)+'_'+'dish'+str(well_id)+'.avi')
    #path = os.path.abspath('./video/video2.mp4')
    print(video_path)
    return video_path


def get_history_patient_id_list():
    history_dir = '/mnt/2ecae85e-98a6-47ff-8547-bd79e071bd91/history'
    history_patient_id_list= os.listdir(history_dir)

    return history_patient_id_list


def move_video_to_history(patient_his_time_folder,patient_id):


    # history_dir = './history'

    history_video_dir =os.path.join(patient_his_time_folder,'video')
    video_dir = './video'
    

    for video_patient_id in os.listdir(video_dir):
        if video_patient_id==patient_id:
            video_patient_id_path =os.path.join(video_dir,video_patient_id)
            cham_list = os.listdir(video_patient_id_path)
            # print(cham_list)
            if len(cham_list)!=0:
                for cham_folder in cham_list:
                    cham_folder_path =os.path.join(video_patient_id_path,cham_folder)
                    if os.path.isdir(cham_folder_path):
                        shutil.move(cham_folder_path,history_video_dir)
                    # print('remove dir:----------------',video_patient_id_path)


            if os.path.isdir(video_patient_id_path):
                    # print('remove dir:',video_patient_id_path)
                    shutil.rmtree(video_patient_id_path)        









#return embryo viewer imformation each stage (show image path,time,fragment percentage)


def get_xlsx_predict_division_time(folder_name,chamber_id,dish_id):


    stage_dic=dict()
    timespend_dic=dict()
    percent_dic=dict()
    filename_dic=dict()
    xlsx_predict_division_time_dic = {}
    dict_list_return=['pn','t2','t3','t4','t5','t6','t7','t8','morula','blas']

    xlsx_predict_division_time_dic['Xlsx']=dict([(k,float('nan')) for k in dict_list_return])
    xlsx_predict_division_time_dic['Predict']=dict([(k,float('nan')) for k in dict_list_return])
    xlsx_predict_division_time_dic['Fragment']=dict([(k,float('nan')) for k in dict_list_return])
    xlsx_predict_division_time_dic['Cham_id']=str(chamber_id)
    xlsx_predict_division_time_dic['Dish_id']=str(dish_id)
    xlsx_predict_division_time_dic['Patient_id']=str(folder_name)
    xlsx_predict_division_time_dic['Dict_key']=dict_list_return
    # print("xlsx dic:",xlsx_predict_division_time_dic['Xlsx'])
    csv_dir = './csv/'
    img_dir = './data/crop_img/'
    folder_path ='cham'+str(chamber_id)+'/dish'+str(dish_id)
    csv_name = 'cham'+str(chamber_id)+'_'+'dish'+str(dish_id)+'.csv'

    csv_path = os.path.join(csv_dir,folder_path)
    csv_path = os.path.join(csv_path,csv_name)
    # print("get stage csv path:",csv_path)

    if os.path.isfile(csv_path):
        predict_division_dic=get_t2t8_dur_time(csv_path)
        write_analy_csv_t2_t8(chamber_id)


        
        xlsx_division_dic = search_embryologist_xlsx(folder_name,dish_id)
        frag_dic = get_avg_fragment_percent(csv_path)

        # print('predict_division_dic:',predict_division_dic)
        # print('xlsx_division_dic:',xlsx_division_dic)

        xlsx_predict_division_time_dic['Xlsx']=xlsx_division_dic
        xlsx_predict_division_time_dic['Predict']=predict_division_dic
        xlsx_predict_division_time_dic['Fragment']=frag_dic

    # print( len(xlsx_predict_division_time_dic['Xlsx']))
    # print(xlsx_predict_division_time_dic)



    



    
    return xlsx_predict_division_time_dic





# def get_each_stage_result(chamber_id,well_id):


#     stage_dic=dict()
#     timespend_dic=dict()
#     percent_dic=dict()
#     filename_dic=dict()
#     dict_key=['pn','2','3','4','5','6','7','8','morula','blas']

#     csv_dir = './csv/'
#     img_dir = './data/crop_img/'
#     folder_path ='cham'+str(chamber_id)+'/dish'+str(well_id)
#     csv_name = 'cham'+str(chamber_id)+'_'+'dish'+str(well_id)+'.csv'

#     csv_path = os.path.join(csv_dir,folder_path)
#     csv_path = os.path.join(csv_path,csv_name)
#     # psrint("get stage csv path:",csv_path)
#     img_folder_dir= os.path.join(img_dir,folder_path)
#     each_stage_list=[]
#     each_img_list=[]
#     each_percent_list=[]

#     if os.path.isfile(csv_path):
#         # csv_path =Path( Path("./csv/")/(str(emb_folder_sel)+'.csv'))
#         df = pd.read_csv(str(csv_path),encoding='utf-8')
#         df = df.sort_values(by='file_name')

        
#         # img_dir = str(Path('./data/crop_img/')/str(emb_folder_sel))       
#         for i in range(len(dict_key)):
#             lenth=len(df.file_name[df['cell_stage']==i+1].values)
#             if lenth!=0:
#                 # select_num = random.randint(0,lenth-1)
#                 print(len(df.file_name[df['cell_stage']==i+1].values))
#                 print()
#                 select_num = len(df.file_name[df['cell_stage']==i+1].values)//2
#                 print(select_num)
#                 select_img = sorted(df.file_name[df['cell_stage']==i+1].values)[select_num]
#                 # print("df.file_name[df['cell_stage']==i+1].values[random.randint(0,lenth-1)]:",df.file_name[df['cell_stage']==i+1].values[random.randint(0,lenth-1)])
#                 img_path = os.path.join(img_folder_dir,select_img)
#                 # new_img_path = str(Path(img_dir)/select_img)
#                 percentage = df.frag_percentage[df['file_name']==str(select_img)].values[0]
#                 stage = df.cell_stage[df['file_name']==str(select_img)].values[0]
#                 each_img_list.append(img_path)
#                 each_percent_list.append(str(percentage))
#                 each_stage_list.append(stage)
                
#                 filename_dic[dict_key[i]]=img_path
#                 stage_dic[dict_key[i]]=stage
#                 percent_dic[dict_key[i]]=percentage
                
#                 df['file_name']=sorted(df['file_name'])
#                 time = df['file_name'][df['file_name']==select_img].index.tolist()[0]
#                 print('filename',select_img)
#                 print("time",time)
#                 time = (time+1)*10
#                 hour = time//60
#                 minute = time %60
#                 print("{}  hour  {}  minute".format(hour,minute))

#                 timespend_dic[dict_key[i]]=(hour,minute)
                

#         #add stage_8 morula blas filename in filename_dic
#         lenth_8stage=len(df.file_name[df['cell_stage']==8].values)
#         print('len 8stage:',lenth_8stage)
#         if lenth_8stage!=0:
#             stage_8select_img = sorted(df.file_name[df['cell_stage']==8].values)[0]
#             # print("df.file_name[df['cell_stage']==i+1].values[random.randint(0,lenth-1)]:",df.file_name[df['cell_stage']==i+1].values[random.randint(0,lenth-1)])
#             stage_8_img_path = os.path.join(img_folder_dir,stage_8select_img)
#             filename_dic['8']=stage_8_img_path

#             morula_select_img = sorted(df.file_name[df['cell_stage']==8].values)[lenth_8stage//2]
#             # print("df.file_name[df['cell_stage']==i+1].values[random.randint(0,lenth-1)]:",df.file_name[df['cell_stage']==i+1].values[random.randint(0,lenth-1)])
#             morula_img_path = os.path.join(img_folder_dir,morula_select_img)
#             filename_dic['morula']=morula_img_path

#             blas_select_img = sorted(df.file_name[df['cell_stage']==8].values)[-1]
#             # print("df.file_name[df['cell_stage']==i+1].values[random.randint(0,lenth-1)]:",df.file_name[df['cell_stage']==i+1].values[random.randint(0,lenth-1)])
#             blas_img_path = os.path.join(img_folder_dir,blas_select_img)
#             filename_dic['blas']=blas_img_path







#         print(filename_dic)
#         # print(timespend_dic['2pn'][0])
#         # print(filename_dic)  
#         # print(stage_dic)   
#         # print(percent_dic)
#     return dict_key,filename_dic,timespend_dic,percent_dic




# def get_csv_history(chamber_id,well_id):
#     # stage_dic=dict()
#     precent_dic=dict()
#     dict_key=['2pn','2','3','4','5','6','7','8','blas']

#     csv_dir = './csv/'
#     img_dir = './data/crop_img/'
#     folder_path ='cham'+str(chamber_id)+'/dish'+str(well_id)
#     csv_name = 'cham'+str(chamber_id)+'_'+'dish'+str(well_id)+'.csv'

#     csv_path = os.path.join(csv_dir,folder_path)
#     csv_path = os.path.join(csv_path,csv_name)
#     # print("get stage csv path:",csv_path)
#     img_folder_dir= os.path.join(img_dir,folder_path)    
    
#     each_percent_list=[]    
#     if os.path.isfile(csv_path):
#         # csv_path =Path( Path("./csv/")/(str(emb_folder_sel)+'.csv'))
#         df = pd.read_csv(str(csv_path),encoding='utf-8')        
#         # img_dir = str(Path('./data/crop_img/')/str(emb_folder_sel))
#         temp=[]
#         for i in range(8):
#             lenth=len(df.file_name[df['cell_stage']==i+1].values)
#             # print("lenth:",lenth)
#             percentage=0
#             if lenth!=0:
#                 select_img = list(df.file_name[df['cell_stage']==i+1])
#                 # print("select_img:",select_img)
#                 for j in range(lenth):
#                     # img_path = os.path.join(img_folder_dir,select_img[j])
#                     percentage = percentage+df.frag_percentage[df['file_name']==str(select_img[j])].values[0]
#                 percentage=round(percentage/lenth,2)
#                 each_percent_list.append((percentage))

#                 precent_dic[dict_key[i]]=percentage
#         # print("each_percent_list",each_percent_list)
#         #print('percent dict:',precent_dic)       
#     return precent_dic
    
# def create_patient_record_csv(patient_id,chamber_id,dish_id,time):
#     patient_folder = './patient_id_save/'
#     if not os.path.isdir(patient_folder):
#         os.mkdir(patient_folder)
#     csv_path = os.path.join(patient_folder,patient_id+'_'+str(time)+'.csv')
#     if os.path.exists(csv_path):
#         df=pd.read_csv(csv_path)
#         df=df.append({'chamber':str(chamber_id),'dish':str(dish_id)},ignore_index=True)
        
#         df.to_csv(csv_path,index=0)
#         # pass
#     else:
#         dic ={'chamber':[],'dish':[],'start_time':[]}
#         df = pd.DataFrame(dic)
        
#         df=df.append({'chamber':str(chamber_id),'dish':str(dish_id),'start_time':str(time)},ignore_index=True)
#         df.to_csv(csv_path,index=0)

def clear_cham_dish_data_csv(cham_id):
    oriimg_root_folder_path ='./data/ori_img'
    cropimg_root_folder_path = './data/crop_img'
    csv_folder_path = './csv/'

    ori_folder_needdel=os.path.join(oriimg_root_folder_path,'cham'+str(cham_id))
    crop_folder_needdel=os.path.join(cropimg_root_folder_path,'cham'+str(cham_id))
    csv_folder_needdel=os.path.join(csv_folder_path,'cham'+str(cham_id))


    for root,folders,files in os.walk(ori_folder_needdel):
        for name in files:
            if name.endswith('.jpg'):
                file_path = os.path.join(root, name)
                os.remove(file_path) 
                print("remove :",file_path)
    
    for root,folders,files in os.walk(crop_folder_needdel):
        for name in files:
            if name.endswith('.jpg'):
                file_path = os.path.join(root, name)
                os.remove(file_path) 
                print("remove :",file_path)

    for root,folders,files in os.walk(csv_folder_needdel):
        for name in files:
            if name.endswith('.csv'):
                file_path = os.path.join(root, name)
                os.remove(file_path) 
                print("remove :",file_path)


#back up chamber dish imformation
# def move_select_cham_dish_folder(patient_id,time):
#     his_folder_path = './history/'
#     patient_csv_folder='./patient_id_save/'
#     ori_img_folder = './data/crop_img/'
#     csv_dir='./csv/'
#     # img_dir = './data/crop_img/'
#     chamber_idlist = []
#     chamber_id =-1
#     # dish_idlist=[]

#     #mkdir  patiend id folder
#     patient_his_folder = os.path.join(his_folder_path,patient_id)
#     if not os.path.isdir(patient_his_folder):
#         os.mkdir(patient_his_folder)
#     #mkdir time stamp folder
#     patient_his_time_folder=os.path.join(patient_his_folder,time)
#     if not os.path.isdir(patient_his_time_folder):
#         os.mkdir(patient_his_time_folder)
#     patient_his_time_data_folder=os.path.join(patient_his_time_folder,"data")
#     if not os.path.isdir(patient_his_time_data_folder):
#         os.mkdir(patient_his_time_data_folder)
#     patient_his_time_csv_folder=os.path.join(patient_his_time_folder,"csv")
#     if not os.path.isdir(patient_his_time_csv_folder):
#         os.mkdir(patient_his_time_csv_folder)

#     #get which chamber need to copy 
#     csv_path = os.path.join(patient_csv_folder,patient_id+"_"+time+'.csv')
#     if os.path.exists(csv_path):
#         df=pd.read_csv(csv_path)

#         chamber_id=df['chamber'][0]

#     #print(chamber_id)
#     ori_data_chamber_path = os.path.join(ori_img_folder,"cham"+str(chamber_id))
#     ori_csv_cahmber_path=os.path.join(csv_dir,"cham"+str(chamber_id))
#     #print("ori_csv_cahmber_path:",ori_csv_cahmber_path)

#     #print(' ori_chamber_path:',ori_data_chamber_path)
#     backup_data_path = os.path.join(patient_his_time_data_folder,"cham"+str(chamber_id))
#     backup_csv_path = os.path.join(patient_his_time_csv_folder,"cham"+str(chamber_id))
#     if not os.path.isdir(backup_data_path):
#         shutil.copytree(ori_data_chamber_path, backup_data_path)
#     if not os.path.isdir(backup_csv_path):
#         shutil.copytree(ori_csv_cahmber_path,backup_csv_path)



#return history page patient_id->save time list
def history_getid_timelist(patient_id):
    history_dir='/mnt/2ecae85e-98a6-47ff-8547-bd79e071bd91/history'

    id_list = os.listdir(history_dir)
    # print(id_list)
    if patient_id in id_list:
        patient_id_dir =os.path.join(history_dir,patient_id) 
        id_time_list =os.listdir(patient_id_dir)
        #print(id_time_list)
        return id_time_list



#return dic_key=['2pn','2','3','4','5','6','7','8','blas'] and each stage fragment percent

def get_avg_fragment_percent(csv_path):
    dict_key=['pn','2','3','4','5','6','7','8','morula','blas']
    write_dict_key=['pn','t2','t3','t4','t5','t6','t7','t8','morula','blas']
    # dict_key=['2pn','2','3','4','5','6','7','8','blas']
    percent_dic=dict()
    df = pd.read_csv(str(csv_path),encoding='utf-8')        
    # img_dir = str(Path('./data/crop_img/')/str(emb_folder_sel))
    for i,stage in enumerate(dict_key):
        lenth=len(df.file_name[df['cell_stage']==stage])
        # print(i+1)
        # print(df.frag_percentage[df['cell_stage']==i+1])
        frag_list = df.frag_percentage[df['cell_stage']==stage].values
        # print(frag_list.mean())
        mean_percentage=frag_list.mean()
        percent_dic[write_dict_key[i]]=mean_percentage

    #print(percent_dic)
    return percent_dic    


# #calculate each stage duration time

# def get_each_stage_division_time(csv_path):



#     dict_key=['2pn','2','3','4','5','6','7','8']

#     divid_dic=dict()
#     count = 0
#     range_inter=5

#     save_cellchange_list=list(np.zeros(8))

#     df = pd.read_csv(str(csv_path),encoding='utf-8')
#     df = df.sort_values(by='file_name')
#     cell_list = df['cell_stage'].values
#     print(cell_list)
#     save = 0
#     for i in range(len(cell_list)):
#         # print(i)
#         if cell_list[i] !=save and not math.isnan(cell_list[i]) and save<cell_list[i]:
#             save=int(cell_list[i])
#             print(save)
#             if cell_list[i]<len(save_cellchange_list)+1:
#                 save_cellchange_list[save-1]=i
    
#     print(save_cellchange_list)

#     #check list have zero or not
#     for i in range(len(save_cellchange_list)):
#         if i!=0 and save_cellchange_list[i]==0:
#             save_cellchange_list[i]=save_cellchange_list[i-1]

#     save_cellchange_list=np.array(save_cellchange_list)
#     time = (save_cellchange_list)*10
#     hour = time//60
#     minute = time %60
#     print("{}  hour  {}  minute".format(hour,minute))

#     for i in range(len(dict_key)):
#         divid_dic[dict_key[i]]=(hour[i],minute[i])

#     print(divid_dic)

#     return divid_dic


#return history page  dish_id,status,info,stage,duration_time

def search_history_csv(patient_id,patient_time):
    history_dir='/mnt/2ecae85e-98a6-47ff-8547-bd79e071bd91/history'
    id_dir = os.path.join(history_dir,patient_id)
    time_dir = os.path.join(id_dir,patient_time)
    time_dir = os.path.join(time_dir,'csv')
    DishList_dic = dict()
    
    
    total_DishList=[]

    chamber_list = os.listdir(time_dir)
    # print(id_list)
    for chamber in chamber_list:
        chamber_dir = os.path.join(time_dir,chamber)
        dish_list =os.listdir(chamber_dir)
        for dish_name in dish_list:
        # for i in range(len(dish_list)):
            dish_id = dish_name.replace('dish','')
            DishID_Stage_dic = dict()
            
            dish_dir = os.path.join(chamber_dir,dish_name)
            csv_namelist =os.listdir(dish_dir)
            # print(csv_name)
            all_element_dic=dict()


            if csv_namelist :
                csv_name=chamber+'_'+dish_name+'.csv'
                csv_path=os.path.join(dish_dir,csv_name)
                analy_csv_name=chamber+'_'+dish_name+'_analy.csv'
                analy_csv_path=os.path.join(dish_dir,analy_csv_name)
                if os.path.isfile(analy_csv_path):
                    df=pd.read_csv(analy_csv_path)
                    DishID_Stage_dic['DishId']=df['dish'].values[0]
                    dict_total_element=dict()
                    dict_total_element['Status']=df['Status'].values[0]
                    dict_total_element['t2']=df['t2'].values[0]
                    dict_total_element['t3']=df['t3'].values[0]
                    dict_total_element['t4']=df['t4'].values[0]
                    dict_total_element['t5']=df['t5'].values[0]
                    dict_total_element['t6']=df['t6'].values[0]
                    dict_total_element['t7']=df['t7'].values[0]
                    dict_total_element['t8']=df['t8'].values[0]
                    dict_total_element['Morula']=df['Morula'].values[0]
                    dict_total_element['Blas']=df['Blas'].values[0]
                    dict_total_element['comp']=df['comp'].values[0]
                    dict_total_element['PN_Fading']=df['PN_Fading'].values[0]
                    dict_total_element['ICM']=df['ICM'].values[0]
                    dict_total_element['TE']=df['TE'].values[0]
                    dict_total_element['PGS']=df['PGS'].values[0]
                    dict_total_element['Probility']=df['Probility'].values[0]

                    DishID_Stage_dic['Info']=dict_total_element





                if os.path.isfile(csv_path):
                    percent_dic=get_avg_fragment_percent(csv_path)
                    DishID_Stage_dic['Fragment']=percent_dic
                    # print('percent_dic',percent_dic)
                
                total_DishList.append(DishID_Stage_dic) 

                
                # for csv_name in csv_namelist:

                #     if csv_name.find('analy')==-1:
                #         csv_path = os.path.join(dish_dir,csv_name)
                #         print(csv_path)
                #         dict_key,percent_dic=get_avg_fragment_percent(csv_path)
                #         get_analycsv_all_element()
                #         # divid_dic = get_each_stage_division_time(csv_path)
                #         t2tot8_dic = get_t2t8_dur_time(csv_path)

                #         # print(percent_dic)
                #         DishID_Stage_dic['DishId']=dish_id
                #         DishID_Stage_dic['Stage']=percent_dic
                #         DishID_Stage_dic['Division']=t2tot8_dic
                #         print('t2tot8_dic:',t2tot8_dic)
                #         # print("RRRRRRRRR",DishID_Stage_dic)

                #         total_DishList.append(DishID_Stage_dic)
                #     else:
                #         analy_csv_path = os.path.join(dish_dir,csv_name)
                #         print('analy',analy_csv_path)
                #         # dict_key,percent_dic=get_avg_fragment_percent(analy_csv_path)

                #         # divid_dic = get_each_stage_division_time(analy_csv_path)

                #         df = pd.read_csv(analy_csv_path)
                #         print(df)
                #         status = df['Status'].values[0]
                #         print('status-------------------',status)
                #         DishID_Stage_dic['Status']=status
                #         # DishID_Stage_dic['Stage']=percent_dic
                #         # DishID_Stage_dic['Division']=divid_dic
                #         # print("RRRRRRRRR",DishID_Stage_dic)

                #         total_DishList.append(DishID_Stage_dic) 
                
                #     # total_DishList.append(DishID_Stage_dic)
            else :
                DishID_Stage_dic['DishId']=dish_id
                DishID_Stage_dic['Fragment']={}
                DishID_Stage_dic['Info']={}
                

                total_DishList.append(DishID_Stage_dic)
            
                # total_DishList.append(DishID_Stage_dic)
                # DishList_dic["DishList"]['DishId']={}
    # print(total_cham_percent_dic['11'])
   
    DishList_dic["DishList"]=total_DishList
    return DishList_dic




# def search_history_csv_bak(patient_id,patient_time):
#     history_dir='./history/'
#     id_dir = os.path.join(history_dir,patient_id)
#     time_dir = os.path.join(id_dir,patient_time)
#     time_dir = os.path.join(time_dir,'csv')
#     DishList_dic = dict()
    
    
#     total_DishList=[]

#     chamber_list = os.listdir(time_dir)
#     # print(id_list)
#     for chamber in chamber_list:
#         chamber_dir = os.path.join(time_dir,chamber)
#         dish_list =os.listdir(chamber_dir)
#         for dish_name in dish_list:
#         # for i in range(len(dish_list)):
#             dish_id = dish_name.replace('dish','')
#             DishID_Stage_dic = dict()
#             dish_dir = os.path.join(chamber_dir,dish_name)
#             csv_namelist =os.listdir(dish_dir)
#             # print(csv_name)
#             all_element_dic=dict()


#             if csv_namelist :
                
                
#                 for csv_name in csv_namelist:
#                     if csv_name.find('analy')==-1:
#                         csv_path = os.path.join(dish_dir,csv_name)
#                         print(csv_path)
#                         dict_key,percent_dic=get_avg_fragment_percent(csv_path)
#                         get_analycsv_all_element()
#                         # divid_dic = get_each_stage_division_time(csv_path)
#                         t2tot8_dic = get_t2t8_dur_time(csv_path)

#                         # print(percent_dic)
#                         DishID_Stage_dic['DishId']=dish_id
#                         DishID_Stage_dic['Stage']=percent_dic
#                         DishID_Stage_dic['Division']=t2tot8_dic
#                         print('t2tot8_dic:',t2tot8_dic)
#                         # print("RRRRRRRRR",DishID_Stage_dic)

#                         total_DishList.append(DishID_Stage_dic)
#                     else:
#                         analy_csv_path = os.path.join(dish_dir,csv_name)
#                         print('analy',analy_csv_path)
#                         # dict_key,percent_dic=get_avg_fragment_percent(analy_csv_path)

#                         # divid_dic = get_each_stage_division_time(analy_csv_path)

#                         df = pd.read_csv(analy_csv_path)
#                         print(df)
#                         status = df['Status'].values[0]
#                         print('status-------------------',status)
#                         DishID_Stage_dic['Status']=status
#                         DishID_Stage_dic['PGS']=df['PGS'].values[0]
#                         # DishID_Stage_dic['Stage']=percent_dic
#                         # DishID_Stage_dic['Division']=divid_dic
#                         # print("RRRRRRRRR",DishID_Stage_dic)

#                         total_DishList.append(DishID_Stage_dic) 
                
#                     # total_DishList.append(DishID_Stage_dic)
#             else :
#                 DishID_Stage_dic['DishId']=dish_id
#                 DishID_Stage_dic['Stage']={}
#                 DishID_Stage_dic['Division']={}
#                 DishID_Stage_dic['Status']={}
#                 DishID_Stage_dic['PGS']={}

#                 total_DishList.append(DishID_Stage_dic)
            
#                 # total_DishList.append(DishID_Stage_dic)
#                 # DishList_dic["DishList"]['DishId']={}
#     # print(total_cham_percent_dic['11'])
   
#     DishList_dic["DishList"]=total_DishList
#     return DishList_dic







# def search_history_csv(patient_id,patient_time):
#     history_dir='./history/'
#     id_dir = os.path.join(history_dir,patient_id)
#     time_dir = os.path.join(id_dir,patient_time)
#     time_dir = os.path.join(time_dir,'csv')
#     DishList_dic = dict()
    
    
#     total_DishList=[]

#     chamber_list = os.listdir(time_dir)
#     # print(id_list)
#     for chamber in chamber_list:
#         chamber_dir = os.path.join(time_dir,chamber)
#         dish_list =os.listdir(chamber_dir)
#         for dish_name in dish_list:
#         # for i in range(len(dish_list)):
#             dish_id = dish_name.replace('dish','')
#             DishID_Stage_dic = dict()
#             dish_dir = os.path.join(chamber_dir,dish_name)
#             csv_namelist =os.listdir(dish_dir)
#             # print(csv_name)


#             if csv_namelist :
                
#                 for csv_name in csv_namelist:
#                     if csv_name.find('analy')==-1:
#                         csv_path = os.path.join(dish_dir,csv_name)
#                         print(csv_path)
#                         dict_key,percent_dic=get_avg_fragment_percent(csv_path)

#                         divid_dic = get_each_stage_division_time(csv_path)

#                         # print(percent_dic)
#                         DishID_Stage_dic['DishId']=dish_id
#                         DishID_Stage_dic['Stage']=percent_dic
#                         DishID_Stage_dic['Division']=divid_dic
#                         # print("RRRRRRRRR",DishID_Stage_dic)

#                         total_DishList.append(DishID_Stage_dic)
#                     else:
#                         analy_csv_path = os.path.join(dish_dir,csv_name)
#                         print('analy',analy_csv_path)
#                         # dict_key,percent_dic=get_avg_fragment_percent(analy_csv_path)

#                         # divid_dic = get_each_stage_division_time(analy_csv_path)

#                         df = pd.read_csv(analy_csv_path)
#                         print(df)
#                         status = df['Status'].values[0]
#                         print('status-------------------',status)
#                         DishID_Stage_dic['Status']=status
#                         # DishID_Stage_dic['Stage']=percent_dic
#                         # DishID_Stage_dic['Division']=divid_dic
#                         # print("RRRRRRRRR",DishID_Stage_dic)

#                         total_DishList.append(DishID_Stage_dic) 
                
#                     # total_DishList.append(DishID_Stage_dic)
#             else :
#                 DishID_Stage_dic['DishId']=dish_id
#                 DishID_Stage_dic['Stage']={}
#                 DishID_Stage_dic['Division']={}
#                 DishID_Stage_dic['Status']={}

#                 total_DishList.append(DishID_Stage_dic)
            
#                 # total_DishList.append(DishID_Stage_dic)
#                 # DishList_dic["DishList"]['DishId']={}
#     # print(total_cham_percent_dic['11'])
   
#     DishList_dic["DishList"]=total_DishList
#     return DishList_dic




#move select chamber to history folder    
def move_select_cham_dish_folder(patient_id, time, chamber_id):
    history_dir = '/mnt/2ecae85e-98a6-47ff-8547-bd79e071bd91/history'
    patient_csv_folder='./patient_id_save/'
    ori_img_folder = './data/crop_img/'
    csv_dir='./csv/'
    # img_dir = './data/crop_img/'
    # chamber_idlist = []
    # chamber_id =-1
    # dish_idlist=[]

    # write_analy_csv_1248fragpercent(chamber_id)#write fragment 1 2 4 8 to csv first
    write_analy_csv_t2_t8(chamber_id)

    #mkdir  patiend id folder
    patient_his_folder = os.path.join(history_dir,patient_id)
    if not os.path.isdir(patient_his_folder):
        os.mkdir(patient_his_folder)
    #mkdir time stamp folder
    patient_his_time_folder=os.path.join(patient_his_folder,time)
    if not os.path.isdir(patient_his_time_folder):
        os.mkdir(patient_his_time_folder)
    patient_his_time_data_folder=os.path.join(patient_his_time_folder,"data")
    if not os.path.isdir(patient_his_time_data_folder):
        os.mkdir(patient_his_time_data_folder)
    patient_his_time_csv_folder=os.path.join(patient_his_time_folder,"csv")
    if not os.path.isdir(patient_his_time_csv_folder):
        os.mkdir(patient_his_time_csv_folder)

    patient_his_time_video_folder=os.path.join(patient_his_time_folder,"video")
    if not os.path.isdir(patient_his_time_video_folder):
        os.mkdir(patient_his_time_video_folder)

    #get which chamber need to copy 
    # csv_path = os.path.join(patient_csv_folder,patient_id+"_"+time+'.csv')
    # if os.path.exists(csv_path):
    #     df=pd.read_csv(csv_path)

    #     chamber_id=df['chamber'][0]

    move_video_to_history(patient_his_time_folder,patient_id)

    
    ori_data_chamber_path = os.path.join(ori_img_folder,"cham"+str(chamber_id))
    ori_csv_chamber_path=os.path.join(csv_dir,"cham"+str(chamber_id))
    # print("ori_csv_chamber_path:",ori_csv_chamber_path)

    # print(' ori_chamber_path:',ori_data_chamber_path)
    backup_data_path = os.path.join(patient_his_time_data_folder,"cham"+str(chamber_id))
    backup_csv_path = os.path.join(patient_his_time_csv_folder,"cham"+str(chamber_id))
    if not os.path.isdir(backup_data_path):
        shutil.copytree(ori_data_chamber_path,backup_data_path)
    if not os.path.isdir(backup_csv_path):
        shutil.copytree(ori_csv_chamber_path,backup_csv_path)
    

    # xgboost_inf_write(patient_id,time,chamber_id)
    for dish_folder in os.listdir(ori_data_chamber_path):
        dish_id = dish_folder.replace('dish','')
        xgboost_inf_write_blas_morula_pnfading(patient_id,time,chamber_id,dish_id)



#write history page change pgs status to history folder csv 
def write_his_status_pgs(patient_id,patient_time,dish_id,status=None,pgs=None):
    history_dir='/mnt/2ecae85e-98a6-47ff-8547-bd79e071bd91/history'
    id_dir = os.path.join(history_dir,patient_id)
    time_dir = os.path.join(id_dir,patient_time)
    time_dir = os.path.join(time_dir,'csv')
    DishList_dic = dict()
    
    
    total_DishList=[]

    chamber_list = os.listdir(time_dir)
    cham_id = 0
    # print(id_list)
    for chamber in chamber_list:
        chamber_dir = os.path.join(time_dir,chamber)
        # dish_list =os.listdir(chamber_dir)
        dish_path =os.path.join(chamber_dir,'dish'+str(dish_id))
        csv_analy = [x for x in os.listdir(dish_path) if x.find('analy')!=-1]
        print(csv_analy)
        if len(csv_analy)!=0:
            csv_analy = csv_analy[0]
            csv_analy_path =os.path.join(dish_path,csv_analy)
            if os.path.exists(csv_analy_path):
                df=pd.read_csv(csv_analy_path)

                if status!=None:
                
                    df['Status']=status
                if pgs!=None:
                    df['PGS']=pgs
                print(df)
            

                df.to_csv(csv_analy_path,index=0)
            else:
                dic = {
                        'chamber':[],
                        'dish':[],
                        'Status':[],

                        't2':[],
                        't3':[],
                        't4':[],
                        't5':[],
                        't6':[],
                        't7':[],
                        't8':[],
                        'Morula':[],
                        'Blas':[],
                        'comp':[],
                        'PN_Fading':[],

                        
                        'ICM':[],
                        'TE':[],
                        'PGS':[],
                        'Probility':[]
                    
                        

                }
                df = pd.DataFrame(dic)
                df=df.append({'chamber':cham_id,"dish":dish_id,'Status':status,'PGS':pgs},ignore_index=True)
                # df['PGS']=pgs
                print(df)
                df.to_csv(csv_analy_path,index=0)


#write history page info change to history csvfile

def write_his_all_element(patient_id,patient_time,dish_id,status=None,t2=None,t3=None,t4=None,t5=None,t6=None,t7=None,t8=None,morula=None,blas=None,comp=None,pn_fading=None,icm=None,te=None,pgs=None,prob=None):
    history_dir='/mnt/2ecae85e-98a6-47ff-8547-bd79e071bd91/history'
    id_dir = os.path.join(history_dir,patient_id)
    time_dir = os.path.join(id_dir,patient_time)
    time_dir = os.path.join(time_dir,'csv')
    DishList_dic = dict()
    
    
    total_DishList=[]
    if os.path.isdir(time_dir):

        chamber_list = os.listdir(time_dir)
        # print(id_list)
        for chamber in chamber_list:
            chamber_dir = os.path.join(time_dir,chamber)
            # dish_list =os.listdir(chamber_dir)
            dish_path =os.path.join(chamber_dir,'dish'+str(dish_id))
            if os.path.isdir(dish_path):
                csv_analy = [x for x in os.listdir(dish_path) if x.find('analy')!=-1]
                print(csv_analy)
                if len(csv_analy)!=0:
                    csv_analy = csv_analy[0]
                    csv_analy_path =os.path.join(dish_path,csv_analy)
                    if os.path.exists(csv_analy_path):
                        df=pd.read_csv(csv_analy_path)
                        df['Status']=status
                        df['t2']=t2
                        df['t3']=t3
                        df['t4']=t4
                        df['t5']=t5
                        df['t6']=t6
                        df['t7']=t7
                        df['t8']=t8
                        df['Morula']=morula
                        df['Blas']=blas
                        df['comp']=comp
                        df['PN_Fading']=pn_fading
                        
                        df['ICM']=icm
                        df['TE']=te
                        df['PGS']=pgs
                        df['Probility']=prob

                        
                        # if pgs!=None:
                        #     df['PGS']=pgs
                        print(df)
                    

                        df.to_csv(csv_analy_path,index=0)
                # else:
                #     csv_name = chamber+'_dish'+str(dish_id)+'_analy.csv'
                #     csv_analy_path=os.path.join(dish_path,csv_name)
                #     dic = {
                #         'chamber':[],
                #         'dish':[],
                #         'Status':[],

                #         't2':[],
                #         't3':[],
                #         't4':[],
                #         't5':[],
                #         't6':[],
                #         't7':[],
                #         't8':[],
                #         'Morula':[],
                #         'Blas':[],
                #         'comp':[],
                #         'PN_Fading':[],

                        
                #         'ICM':[],
                #         'TE':[],
                #         'PGS':[],
                #         'Probility':[]
                    
                        

                #     }
                #     # dic['Status']=status
                #     # dic['t2']=t2
                #     # dic['t3']=t3
                #     # dic['t4']=t4
                #     # dic['t5']=t5
                #     # dic['t6']=t6
                #     # dic['t7']=t7
                #     # dic['t8']=t8
                #     # dic['Morula']=morula
                #     # dic['Blas']=blas
                #     # dic['comp']=comp
                    
                #     # dic['ICM']=icm
                #     # dic['TE']=te
                #     # dic['PGS']=pgs

                #     # print('dic',dic)

                #     df = pd.DataFrame.from_dict(dic)
                    
                    

                #     df=df.append({"dish":dish_id,'Status':status,'t2':t2,'t3':t3,'t4':t4,'t5':t5,'t6':t6,'t7':t7,'t8':t8,'Morula':morula,'Blas':blas,'comp':comp,'PN_Fading':pn_fading,'ICM':icm,'TE':te,'PGS':pgs},ignore_index=True)
                #     # df['PGS']=pgs
                #     print(df)
                #     df.to_csv(csv_analy_path,index=0)


#embryo viewer load default icm te
def read_analy_csv_icm_te(cham_id, dish_id):
    csv_path ='./csv/cham'+str(cham_id)+'/dish'+str(dish_id)+'/'+'cham'+str(cham_id)+'_'+'dish'+str(dish_id)+'_analy.csv'
    # if os.path.exists(csv_path):
    # df=pd.read_csv(csv_path)    
    if os.path.exists(csv_path):
        df=pd.read_csv(csv_path)       
        return df['ICM'].to_string(), df['TE'].to_string()
    else:
        return '', ''

    
#embyro page icm te write to csv-cham-dish  csv 
def write_analy_csv_icm_te(cham_id,dish_id,icm=None,te=None):
    csv_path ='./csv/cham'+str(cham_id)+'/dish'+str(dish_id)+'/'+'cham'+str(cham_id)+'_'+'dish'+str(dish_id)+'_analy.csv'
    # if os.path.exists(csv_path):
    # df=pd.read_csv(csv_path)

    if os.path.exists(csv_path):
        df=pd.read_csv(csv_path)
        
        # df['PGS']=pgs
        if icm!=None:
            df['ICM']=icm
        if te!=None:
            df['TE']=te
        print(df)
        

        df.to_csv(csv_path,index=0)
    else:
        dic = {
                'chamber':[],
                'dish':[],
                'Status':[],

                't2':[],
                't3':[],
                't4':[],
                't5':[],
                't6':[],
                't7':[],
                't8':[],
                'Morula':[],
                'Blas':[],
                'comp':[],
                'PN_Fading':[],

                
                'ICM':[],
                'TE':[],
                'PGS':[],
                'Probility':[]
            
                

            }
        df = pd.DataFrame(dic)
        df=df.append({'chamber':cham_id,"dish":dish_id,'ICM':icm,'TE':te},ignore_index=True)
        # df['PGS']=pgs
        print(df)
        df.to_csv(csv_path,index=0)


   

    

    df.to_csv(csv_path,index=0)






def normalize_classify_stage(cell_stage_list):

    
    normalize_range=2
    for i,cell in enumerate(cell_stage_list):
        if cell_stage_list[i] in ['2','3','4','5','6','7','8']:
            #print('cellstage_ i :',cell_stage_list[i])
            cell_stage_list[i]=str(int(float(cell_stage_list[i])))
    
    old_cell_stage_list = copy.deepcopy(cell_stage_list)

    for i,cell in enumerate(cell_stage_list):
        if i >=normalize_range and i <len(cell_stage_list)-normalize_range:
            cell_stage_list[i]=max(old_cell_stage_list[i-normalize_range:i+normalize_range+1] ,key=list(old_cell_stage_list).count)

    return cell_stage_list


#return history page t2-t8 time list 
def get_t2t8_dur_time(csv_path):

    print('get t2 t8 oricsv path :',csv_path)

    df=pd.read_csv(csv_path,engine='python')
    df = df.sort_values(by='file_name')
    cell_stage_list = df['cell_stage'].values
    # print(cell_stage_list)
    dic_key = ['pn','t2','t3','t4','t5','t6','t7','t8','morula','blas','comp']
    class_list =['pn','2','3','4','5','6','7','8','morula','blas','comp']
    t2t8_dict=dict()
    save_t2t8_list = []
    print('csv path:',csv_path)
    

    new_cell_stage_list=normalize_classify_stage(cell_stage_list)
    # print(new_cell_stage_list)
    
    for class_ind in range(len(class_list)):
        stage = class_list[class_ind]
        # print('stage:',stage)
        each_stage_list=[i for i,v in enumerate(new_cell_stage_list) if v==stage]
        # print(each_stage_list)
        if not save_t2t8_list:
            if len(each_stage_list)!=0:
                save_t2t8_list.append(each_stage_list[0])
            else:
                save_t2t8_list.append(-1)
        else:
            if len(each_stage_list)!=0:
                if max(each_stage_list)<=max(save_t2t8_list):
                    # print('max(each_stage_list)',max(each_stage_list))
                    # print('max(save_t2t8_list)',max(save_t2t8_list))
                    save_t2t8_list.append(-1)
                    continue
                for num in range(len(each_stage_list)):
                    
                    if each_stage_list[num]<max(save_t2t8_list):
                        continue
                    else:
                        # print('save')
                        logging.debug('save')
                        save_t2t8_list.append(each_stage_list[num])
                        break
                

            else:
                save_t2t8_list.append(-1)
        # print('save_t2t8_list:',save_t2t8_list)
    
    logging.debug('save_t2t8_list : %s'%(save_t2t8_list))

    hours_t2t8_list = np.around(np.array(save_t2t8_list)/6,decimals=2)
    logging.debug('hours_t2t8_list : %s'%(hours_t2t8_list))
    
    for i in range(len(hours_t2t8_list)):
        if hours_t2t8_list[i]<0:
            hours_t2t8_list[i]=None

    # print(hours_t2t8_list)

    for i in range(len(hours_t2t8_list)):
        t2t8_dict[dic_key[i]]=hours_t2t8_list[i]
    
    # print('dic t2t8 list:',t2t8_dict)
    logging.info('dic t2t8 list : %s'%(t2t8_dict))

    
    
    return t2t8_dict



#write csv-cham-dish  analy csv t2-t8 time
def write_analy_csv_t2t8(cham_id,dish_id,t2t8_time_dic):
    csv_path ='./csv/cham'+str(cham_id)+'/dish'+str(dish_id)+'/'+'cham'+str(cham_id)+'_'+'dish'+str(dish_id)+'_analy.csv'
    # if os.path.exists(csv_path):
    # df=pd.read_csv(csv_path)

    if os.path.exists(csv_path):
        df=pd.read_csv(csv_path)
        
        df['PN_Fading']=t2t8_time_dic['pn']
        df['t2']=t2t8_time_dic['t2']
        df['t3']=t2t8_time_dic['t3']
        df['t4']=t2t8_time_dic['t4']
        df['t5']=t2t8_time_dic['t5']
        df['t6']=t2t8_time_dic['t6']
        df['t7']=t2t8_time_dic['t7']
        df['t8']=t2t8_time_dic['t8']
        df['Morula']=t2t8_time_dic['morula']
        df['Blas']=t2t8_time_dic['blas']
        df['comp']=t2t8_time_dic['comp']
       
        # print('rewirte df:',df)
        

        df.to_csv(csv_path,index=0)
    else:
        dic = {
                'chamber':[],
                'dish':[],
                'Status':[],
                't2':[],
                't3':[],
                't4':[],
                't5':[],
                't6':[],
                't7':[],
                't8':[],
                'Morula':[],
                'Blas':[],
                'comp':[],
                'PN_Fading':[],            
                'ICM':[],
                'TE':[],
                'PGS':[],
                'Probility':[]
            
                

            }
        print(t2t8_time_dic)
        # dic['chamber'].append(cham_id)
        # dic['dish'].append(dish_id)
        # dic['t2'].append(t2t8_time_list[0])
        # dic['t3'].append(t2t8_time_list[1])
        # dic['t4'].append(t2t8_time_list[2])
        # dic['t5'].append(t2t8_time_list[3])
        # dic['t6'].append(t2t8_time_list[4])
        # dic['t7'].append(t2t8_time_list[5])
        # dic['t8'].append(t2t8_time_list[6])

        df = pd.DataFrame(dic)
        df=df.append({'chamber':cham_id,"dish":dish_id,'PN_Fading':t2t8_time_dic['pn'],'t2':t2t8_time_dic['t2'],'t3':t2t8_time_dic['t3'],'t4':t2t8_time_dic['t4'],'t5':t2t8_time_dic['t5'],'t6':t2t8_time_dic['t6'],'t7':t2t8_time_dic['t7'],'t8':t2t8_time_dic['t8'],'Morula':t2t8_time_dic['morula'],'Blas':t2t8_time_dic['blas']},ignore_index=True)
        # df['PGS']=pgs
        print(df)
        df.to_csv(csv_path,index=0)


   

    

    # df.to_csv(csv_path,index=0)





#call by move_select_cham_dish_folder ->write csv-cham-dish  analy csv t2-t8 time

def write_analy_csv_t2_t8(cham_id):
    chamber_path = './csv/cham'+str(cham_id)+'/'

    dish_folder_list = os.listdir(chamber_path)
    percent_dic =dict()

    for dish_folder in dish_folder_list:
        dish_folder_path = os.path.join(chamber_path,dish_folder)
        dish_id =dish_folder.replace('dish','')
        if os.path.isdir(dish_folder_path):
            # csv_list = os.listdir(dish_folder_path)

            ori_csvname = 'cham'+str(cham_id)+'_'+str(dish_folder)+'.csv'
            oricsv_path = os.path.join(dish_folder_path,ori_csvname)
            print('oricsvpath',oricsv_path)
            if os.path.isfile(oricsv_path):
                t2t8_time_dic=get_t2t8_dur_time(oricsv_path)
                print('t2t8timelist:',t2t8_time_dic)

                write_analy_csv_t2t8(cham_id,dish_id,t2t8_time_dic)




                


# #xgboost inf and write result to csv only t2-t8 time input

# def xgboost_inf_write(patient_id, patient_time, chamber_id):



    

#     history_dir='./history/'
#     xgboost_model_path = './model_data/xgboost_score/model_all_input1224_withoutblas_morula.pkl'
#     id_dir = os.path.join(history_dir,patient_id)
#     time_dir = os.path.join(id_dir,patient_time)
#     time_dir = os.path.join(time_dir,'csv')
#     DishList_dic = dict()
    
    
    

#     chamber_list = os.listdir(time_dir)
#     # print(id_list)
#     for chamber in chamber_list:
#         chamber_dir = os.path.join(time_dir,chamber)
#         dish_list =os.listdir(chamber_dir)
#         for dish_folder in dish_list:
#             dish_path =os.path.join(chamber_dir,dish_folder)
#             csv_analy = [x for x in os.listdir(dish_path) if x.find('analy')!=-1]
#             if len(csv_analy)!=0:
#                 csv_analy = csv_analy[0]
#                 csv_analy_path =os.path.join(dish_path,csv_analy)
#                 if os.path.exists(csv_analy_path):
#                     # df=pd.read_csv(csv_analy_path)

#                     dataset = pd.read_csv(csv_analy_path)
                    
#                     # df = pd.DataFrame(dataset)
#                     # print(dataset[['1_frag','2_frag','4_frag','8_frag']])
#                     # x_fortest = dataset[['1_frag','2_frag','4_frag','8_frag']]

#                     x_fortest=dataset[['t2','t3','t4','t5','t6','t7','t8']]

#                     # x_fortest = dataset.drop('Status', axis=1)
#                     # x_fortest=x_fortest.drop('chamber',axis=1)
#                     # x_fortest=x_fortest.drop('dish',axis=1)
#                     # x_fortest=x_fortest.drop('ICM',axis=1)
#                     # x_fortest=x_fortest.drop('TE',axis=1)
#                     # x_fortest=x_fortest.drop('PGS',axis=1)
#                     # x_fortest=x_fortest.drop('Morula',axis=1)
#                     # x_fortest=x_fortest.drop('Blas',axis=1)
#                     # x_fortest=x_fortest.drop('comp',axis=1)
#                     # x_fortest=x_fortest.drop('PN_Fading',axis=1)
#                     # x
#                     # print(dataset['1_frag'])
#                     x_test = pd.get_dummies(x_fortest)
#                     # #model = pickle.load(open("model.pkl", "rb"))
#                     model = pickle.load(open(xgboost_model_path, "rb"))
#                     # print(x_test)
#                     test_predictions = model.predict(x_test)[0]
#                     test_pre_prob = model.predict_proba(x_test)[0]
#                     print(test_pre_prob)
#                     dataset['Status']=test_predictions
#                     dataset['Probility']=max(test_pre_prob)
#                     dataset.to_csv(csv_analy_path,index=0)
#                     # print(test_pre_prob)
#                     print(test_predictions)   



# history page after change info do xgboost again ->write success percentage      
def xgboost_inf_write_blas_morula_pnfading(patient_id, patient_time, chamber_id,dish_id):



    history_dir='/mnt/2ecae85e-98a6-47ff-8547-bd79e071bd91/history'
    xgboost_model_path = './model_data/xgboost_score/model_all_input1223.pkl'
    id_dir = os.path.join(history_dir,patient_id)
    time_dir = os.path.join(id_dir,patient_time)
    time_dir = os.path.join(time_dir,'csv')
    DishList_dic = dict()


    chamber_dir=os.path.join(time_dir,'cham'+str(chamber_id))
    dish_path = os.path.join(chamber_dir,'dish'+str(dish_id))


    
    
    

    # chamber_list = os.listdir(time_dir)
    # # print(id_list)
    # for chamber in chamber_list:
    #     chamber_dir = os.path.join(time_dir,chamber)
    #     dish_list =os.listdir(chamber_dir)
    #     for dish_folder in dish_list:
    #         dish_path =os.path.join(chamber_dir,dish_folder)
    print('chamber_id dish_id',chamber_id,dish_id)
    csv_analy = [x for x in os.listdir(dish_path) if x.find('analy')!=-1]
    if len(csv_analy)!=0:
        csv_analy = csv_analy[0]
        csv_analy_path =os.path.join(dish_path,csv_analy)
        if os.path.exists(csv_analy_path):
            # df=pd.read_csv(csv_analy_path)

            dataset = pd.read_csv(csv_analy_path)
            print(dataset)
            # print(dataset['t2'])
            # print(dataset[['t2','t3','t4','t5','t6','t7','t8','Morula','Blas','comp','PN_Fading']])
            
            # df = pd.DataFrame(dataset)
            # print(dataset[['1_frag','2_frag','4_frag','8_frag']])
            # x_fortest = dataset[['1_frag','2_frag','4_frag','8_frag']]
            # x_fortest=dataset[['t2','t3','t4','t5','t6','t7','t8','Morula','Blas','comp','PN_Fading']]



            x_fortest = dataset.drop('Status', axis=1)
            x_fortest=x_fortest.drop('chamber',axis=1)
            x_fortest=x_fortest.drop('dish',axis=1)
            x_fortest=x_fortest.drop('ICM',axis=1)
            x_fortest=x_fortest.drop('TE',axis=1)
            x_fortest=x_fortest.drop('PGS',axis=1)
            x_fortest=x_fortest.drop('Probility',axis=1)

            # x_fortest=x_fortest.drop('Morula',axis=1)
            # x_fortest=x_fortest.drop('Blas',axis=1)
            # x_fortest=x_fortest.drop('comp',axis=1)
            # x_fortest=x_fortest.drop('PN_Fading',axis=1)
            # # x
            # print(dataset['1_frag'])
            x_test = pd.get_dummies(x_fortest)
            # #model = pickle.load(open("model.pkl", "rb"))
            model = pickle.load(open(xgboost_model_path, "rb"))
            # print(x_test)
            test_predictions = model.predict(x_test)[0]
            test_pre_prob = model.predict_proba(x_test)[0]
            print(test_pre_prob)
            dataset['Status']=test_predictions
            dataset['Probility']=test_pre_prob[1]
            # print('test probility transfer:',test_pre_prob[1])
            dataset.to_csv(csv_analy_path,index=0)
            # print(test_pre_prob)
            print(test_predictions)


def search_embryologist_xlsx(folder_name,dish_id):

    print('start dish_id',dish_id)
    sql_data_path ='/mnt/2ecae85e-98a6-47ff-8547-bd79e071bd91/sql_data'
    csv_path = './TimelapseAnnotations_20201218_1419.csv'
    dict_list =['PN Fading','t2','t3','t4','t5','t6','t7','t8','Morula','Blastocyst']
    dict_list_return=['pn','t2','t3','t4','t5','t6','t7','t8','morula','blas']
    time_dic={}

    sqlite_index_path =os.path.join(sql_data_path,folder_name)
    sqlite_index_path=os.path.join(sqlite_index_path,folder_name+'.sqlite')
    
    
    # print('sqlite_index_path:',sqlite_index_path)
    start_timelist = {}
    
    if os.path.isfile(sqlite_index_path):
        with sqlite3.connect(sqlite_index_path) as con:
                    
                    df_index=pd.read_sql_query("SELECT * FROM Images ",con)
                    # print(df_index['ElapsedTime'])
                    dish_number_list = set(df_index['DishPositionId'])
                    # print(set(df_index['DishPositionId']))
                    

                    for count,d_id in enumerate(dish_number_list):
                        start_timelist[str(d_id)]=format(df_index['ElapsedTime'].values[count]/3600,'.2f')




    # for i in range(dish_number):
    #     print(df['ElapsedTime'][df['ElapsedTime']==i].values)
    #     start_timelist['1']=format(df['ElapsedTime'][df['ElapsedTime']==i].values[0]/3600,'.2f')
    #     # start_timelist.append(format(df['ElapsedTime'][i]/3600, '.2f'))
    # print(start_timelist)





        df = pd.read_csv(csv_path)

        dish_start_time = float(start_timelist[str(dish_id)])
        # print(type(dish_start_time))

        
        # print(df['Dish position'])
        for i,key in enumerate(dict_list):

            stage_time = df[key][(df['Time-lapse #']==folder_name) &(df['Dish position'].values==int(dish_id)) ].values
            print('dish_id',dish_id)
            print("stage_time",stage_time)
            
            if len(stage_time)!=0:
                stage_time=float(stage_time[0])-dish_start_time
            else :
                stage_time = float('nan')
            # print(type(stage_time))
            time_dic[dict_list_return[i]]=stage_time
    else:
        print('error-----------------------------------------------------------')

    # print(t2)

    # print(time_dic)
    return time_dic






def write_embryo_viewer_timecsv(chamber_id,dish_id,status=None,t2=None,t3=None,t4=None,t5=None,t6=None,t7=None,t8=None,morula=None,blas=None,comp=None,pn_fading=None,icm=None,te=None,pgs=None,prob=None):
    csv_dir='./csv/'
    cham_dir =os.path.join(csv_dir,'cham'+str(chamber_id))
    dish_dir = os.path.join(cham_dir,'dish'+str(dish_id))
    timecsv_name = 'cham'+str(chamber_id)+'_dish'+str(dish_id)+'_analy.csv'
    timecsv_path =os.path.join(dish_dir,timecsv_name)
    print('analy_csv:',timecsv_path)
    if os.path.isfile(timecsv_path):
        print('exist')
        df = pd.read_csv(timecsv_path)
        print(df)
        df['Status']=status
        df['t2']=t2
        df['t3']=t3
        df['t4']=t4
        df['t5']=t5
        df['t6']=t6
        df['t7']=t7
        df['t8']=t8
        df['Morula']=morula
        df['Blas']=blas
        df['comp']=comp
        df['PN_Fading']=pn_fading
        
        df['ICM']=icm
        df['TE']=te
        df['PGS']=pgs
        df['Probility']=prob

        print(df)
                    

        df.to_csv(timecsv_path,index=0)
    else:


       
        dic = {
            'chamber':[],
            'dish':[],
            'Status':[],

            't2':[],
            't3':[],
            't4':[],
            't5':[],
            't6':[],
            't7':[],
            't8':[],
            'Morula':[],
            'Blas':[],
            'comp':[],
            'PN_Fading':[],

            
            'ICM':[],
            'TE':[],
            'PGS':[],
            'Probility':[]
        
            

        }
        

        df = pd.DataFrame.from_dict(dic)
        
        

        df=df.append({"dish":dish_id,'Status':status,'t2':t2,'t3':t3,'t4':t4,'t5':t5,'t6':t6,'t7':t7,'t8':t8,'Morula':morula,'Blas':blas,'comp':comp,'PN_Fading':pn_fading,'ICM':icm,'TE':te,'PGS':pgs},ignore_index=True)
        # df['PGS']=pgs
        print(df)
        df.to_csv(timecsv_path,index=0)







        

if __name__ == '__main__':
    
    # move_select_cham_dish_folder("MTL-0245-136E-3D95", '20211225', 8)
    # xgboost_inf_write_blas_morula_pnfading('MTL-0245-136E-3D95','20211225','8','1')
    # id_time_list = history_getid_timelist('A123456789')
    # get_dic=search_history_csv('A123456789',id_time_list[0])
    # print(get_dic)
    
    #_=get_csv_history(1,2)
    #id_time_list=history_getid_timelist("A12345")
    #print (id_time_list)
    # dict_key,filename_dic,timespend_dic,percent_dic=get_each_stage_result(3,)
    # print(dict_key,filename_dic,timespend_dic,percent_dic)
    # move_select_cham_dish_folder("A12345",'20201010')
    # img_to_video(1,1)
    # get_dic=search_history_csv('tst','20210118')
    # print(get_dic)
    # _=get_avg_fragment_percent('./history/A12345/20201010/csv/cham1/dish1/cham1_dish1.csv')
    # write_analy_csv_icm_te(3,1,te= 60)
    # write_analy_csv_1248fragpercent(1)
    # write_his_status_pgs("test", '20201217',1,pgs=10)
    # xgboost_inf_write("test", '20201217', 1)
    # get_each_stage_division_time('/home/n200/A70417/EmbryoGUI_0910/csv/cham5/dish8/cham5_dish8.csv')
    # write_his_all_element("test23", '20201217', 3,t2=33.2,t3=35.4,pgs=1,icm=10,morula=105)
    # get_t2t8_dur_time('/home/n200/A70417/EmbryoGUI_0910/csv/cham3/dish3/cham3_dish3.csv')

    # write_analy_csv_t2_t8()
    # xgboost_inf_write_blas_morula_pnfading("test2", '20201217', 3,5)
    # clear_cham_dish_data_csv(5)
    # get_t2t8_dur_time('/home/n200/A70417/EmbryoGUI_0910/csv/cham6/dish5/cham6_dish5.csv')
    # dic = get_xlsx_predict_division_time('MTL-0245-13A1-9874','6','5')
    # print(dic)
    dic=search_embryologist_xlsx('MTL-0245-11E9-4C5B','3')
    print(dic)
    # load_video_path_with_7fp('MTL-0245-13A1-9874',7,2,6)
    # write_embryo_viewer_timecsv(3,1,t2=3)
