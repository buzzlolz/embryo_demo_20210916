
import cv2
import numpy as np
import matplotlib.pyplot as plt

import statsmodels.api as sm
from scipy.stats import linregress

from scipy.signal import find_peaks
from yolo import YOLO
from PIL import Image

#import statsmodels.api as sm
# import imutils
import dlib

(major_ver, minor_ver, subminor_ver) = (cv2.__version__).split('.')



def detect_scipy_find_peaks(x,y):
    lowess = sm.nonparametric.lowess(y, x, frac=0.1)

    plt.plot(x, y)
    # print(lowess[:, 0])
    # plt.plot(lowess[:, 0], lowess[:, 1])


    peaks, _ = find_peaks(lowess[:, 1], height=0)
    inv_data= 1/lowess[:, 1]
    inv_peaks, _ = find_peaks(inv_data, height=0)
    plt.plot(lowess[:, 1])
    plt.plot(peaks, lowess[:, 1][peaks], "o")
    plt.plot(inv_peaks, lowess[:, 1][inv_peaks], "o")
    # print(inv_peaks)

    plt.show()


def emb_location(image):

    image=Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB))
    img,top,left,bottom, right=yolo_ini.detect_image(image)
    
    return top,left,bottom, right
    # cv2.waitKey(10)


def show_peaks_location(l_point,peaks,inv_peaks,video_name):


    num_list=np.arange(len(l_point))
    x=num_list
    y=l_point
    new_list_peaks = []
    new_list_invp=[]

    lowess = sm.nonparametric.lowess(y, x, frac=0.08)

    plt.figure()
    plt.plot(x, y)
    while -1 in peaks:
        peaks.remove(-1)
    while -1 in inv_peaks:
        inv_peaks.remove(-1)
    # print(peaks)
    # print(len(l_point))
    for i in peaks:
        new_list_peaks.append(l_point[i])
    for i in inv_peaks:
        new_list_invp.append(l_point[i])
    
    
    print(new_list_peaks)

    plt.plot(peaks,new_list_peaks,'o')
    plt.plot(inv_peaks,new_list_invp,'x')
    # plt.savefig('./result_frame_count/'+video_name+'.jpg')#儲存圖片
    plt.show()


# def detect_center()



def detect_slope(l_point,slope_thd,frame_num,window_size):
    min_point=min(l_point)
    max_point = max(l_point)
    np_l_point=np.array(l_point)
    # print("del:",max_point-min_point)
    #print("max:",max_point)
    if max_point-min_point>slope_thd:

        # print("min:",min_point,np.argmin(np_l_point)+frame_num)
        # print("max:",max_point,np.argmax(np_l_point)+frame_num)
        # print("RRRRRRRRRRRRRRRRRR")
        if np.argmax(np_l_point)>np.argmin(np_l_point):
            return (np.argmax(np_l_point)+frame_num-window_size),(np.argmin(np_l_point)+frame_num-window_size)
       
        else :
            return -1,-1
    else :
            return -1,-1


def detect_peaks(emb_count):
    num_list=np.arange(len(emb_count))
    x=num_list
    y=emb_pt_list
    lowess = sm.nonparametric.lowess(y, x, frac=0.15)

    plt.plot(x, y)
    # print(lowess[:, 0])
    # plt.plot(lowess[:, 0], lowess[:, 1])


    peaks, _ = find_peaks(lowess[:, 1], height=0)
    inv_data= 1/lowess[:, 1]
    inv_peaks, _ = find_peaks(inv_data, height=0)
    plt.plot(lowess[:, 1])
    plt.plot(peaks, lowess[:, 1][peaks], "o")
    plt.plot(inv_peaks, lowess[:, 1][inv_peaks], "x")
    # print(inv_peaks)
    return(inv_peaks)






if __name__ == "__main__":
    
    
    yolo_ini = YOLO()


    # set image size
    width = 640 #1280
    height = 360 #720
    tracking_enable = False
    

    #tracker = dlib.correlation_tracker()

    # video_name_list=['MTL-0245-11B6-1CC4-P04-FP3',
    #     'MTL-0245-11B6-1CC4-P05-FP3',
    #     'MTL-0245-11B6-1CC4-P06-FP3',
    #     'MTL-0245-11B6-1CC4-P07-FP3',
    #     'MTL-0245-11B6-1CC4-P08-FP3',
    #     'MTL-0245-11B6-1CC4-P09-FP3',
    #     'MTL-0245-11B6-1CC4-P10-FP3',
    #     'MTL-0245-11B6-1CC4-P11-FP3',
    #     'MTL-0245-11E9-4C5B-P03-FP3',
    #     'MTL-0245-11E9-4C5B-P04-FP3',
    #     'MTL-0245-11E9-4C5B-P05-FP3',
    #     'MTL-0245-11E9-4C5B-P06-FP3',
    #     'MTL-0245-11E9-4C5B-P07-FP3',
    #     'MTL-0245-11E9-4C5B-P08-FP3',
    #     'MTL-0245-11E9-4C5B-P09-FP3',
    #     'MTL-0245-11E9-4C5B-P10-FP3']
    # for video_name in video_name_list:
        #cap = cv2.VideoCapture(0)
        #cap = cv2.VideoCapture('MTL-0245-11B6-1CC4-P04-FP3.avi')
    #video_name='MTL-0245-11E9-4C5B-P05-FP3'
    # video_name='MTL-0245-11E9-4C5B-P10-FP3'
    #video_name='MTL-0245-11B6-1CC4-P11-FP3'
    #video_name='MTL-0245-11E9-4C5B-P10-FP3'
    # video_name="MTL-0245-11B6-1CC4-P04-FP3.avi"
    video_name_list=["MTL-0245-11B6-1CC4-P04-FP3"]

    for video_name in video_name_list:

        cap = cv2.VideoCapture('./emb_video_0512/'+video_name+'.avi')

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('./result_0623/'+video_name+'.avi',fourcc, 15.0, (1280,720))

        #write result into txt file
        fp = open("./var/yolo_"+video_name+'_var_0604.txt', "w")

        area = width*height

        #ret, frame = cap.read()
        #avg = cv2.blur(frame, (4,4))
        #avg_float = np.float32(avg)

        frameNum = 0
        nzEmbryoRegionCount = 0
        nzWholeImageCount = 0
        peak_point=0
        inv_peak_point=0
        emb_pt_list =[]
        emb_loc_total_pt=[]
        peaks = [42,110,178,284,421,478,525]
        peaks_list=[]
        inv_peaks_list=[]
        pb = False
        stopNum = 0
        window_size=50
        EmbryoWidth = 0
        EmbryoHeight = 0
        pre_x=0
        pre_y=0

        while(cap.isOpened()):

            ret, frame = cap.read()

            if ret == False or frame is None:
                break
                
            


            top, left, bottom, right=emb_location(frame)
            CenterX = (left+right)/2
            CenterY = (top+bottom)/2
            # print("x : {x}   y: {y}".format(x=CenterX,y=CenterY))
            # print("left-right : {x} ".format(x=right-left))

            if frameNum!=0:
                if abs(pre_x -CenterX)>30 or abs(pre_y -CenterY)>30:
                    cv2.putText(frame, "alert by moving", (1000, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)
                if CenterX<400 or CenterX>880 or CenterY<200 or CenterY>520:
                    cv2.putText(frame, "alert by boundary", (1000, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)

            pre_x=CenterX
            pre_y=CenterY



            


            if frameNum == 1:
                EmbryoWidth = right-left+1
                EmbryoHeight = bottom-top+1


            if frameNum > 0:
                
                blur = cv2.blur(frame, (4,4))
                
                if frameNum == 1:
                    avg = blur.copy()
                    avg_float = np.float32(avg)

                diff = cv2.absdiff(avg, blur)
            
                
                # unpack the position object
                startX = int(CenterX - EmbryoWidth/2)
                startY = int(CenterY - EmbryoHeight/2)
                endX = int(CenterX + EmbryoWidth/2)
                endY = int(CenterY + EmbryoHeight/2)

                if startX < 170:
                    startX = 170
                if startY < 0:
                    startY = 0
                if endX > 1065: #1110
                    endX = 1065
                if endY > 720:
                    endY = 720

                    
                EmbryoRegion_gray = frame[startY:endY, startX:endX] 
                EmbryoArea = int(endX-startX+1) * int(endY-startY+1)
                var = np.var(EmbryoRegion_gray)
                    
        
                #ret, thresh = cv2.threshold(gray, 25, 255, cv2.THRESH_BINARY)
                #nzWholeImageCount = cv2.countNonZero(thresh)
                #EmbryoRegion_thresh = thresh[top:bottom, left:right] 
                #nzEmbryoRegionCount = cv2.countNonZero(EmbryoRegion_thresh)
                #emb_pt_list.append(nzEmbryoRegionCount)
                #emb_loc_total_pt.append(nzEmbryoRegionCount)
                
                
                emb_pt_list.append(var)
                emb_loc_total_pt.append(var)
                if frameNum%window_size==0:   # peak detect slope
                   peak_point,inv_peak_point=detect_slope(emb_pt_list,75,frameNum,window_size)
                #    print(inv_peak_point)
                   emb_pt_list.clear()
                   if peak_point not in peaks_list:
                       peaks_list.append(peak_point)
                   if inv_peak_point not in inv_peaks_list:
                       inv_peaks_list.append(inv_peak_point)
                # print (peak_point)    
                

                cv2.accumulateWeighted(blur, avg_float, 0.1)
                avg = cv2.convertScaleAbs(avg_float)
                
                
                #rgb = cv2.cvtColor(thresh,cv2.COLOR_GRAY2RGB)
                #text2 = 'threshold='+str(ret2)
                #text2 = 'threshold=25'
                #cv2.putText(rgb, text2, (1000, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 1, cv2.LINE_AA)
                #cv2.rectangle(rgb, (left, top), (right, bottom), (255, 255, 0), 2)

                text = str(frameNum)
                #cv2.putText(rgb, text, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)
                #cv2.putText(rgb, 'updateWeight=0.1', (10, 710), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)
                #cv2.putText(rgb, "nzCount(image)="+str(nzWholeImageCount), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 1, cv2.LINE_AA)
                #cv2.putText(rgb, "nzCount(Embryo)="+str(nzEmbryoRegionCount), (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 1, cv2.LINE_AA)
                
                cv2.putText(frame, text, (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)
                cv2.putText(frame, "variance(Embryo)="+str(var), (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)
                # fp.write(str(var)+","+str(frameNum)+"\n")
                cv2.putText(frame, "Area="+str(EmbryoArea), (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)

                
                #if frameNum in peaks:
                #    stopNum = frameNum + 6
                #    pb = True

                #if pb == True:
                #    cv2.putText(frame, 'cleavage', (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 1, cv2.LINE_AA)
                
                #if frameNum > stopNum:
                #    pb = False
                #if ok:
                #    cv2.rectangle(frame, (t_left, t_top), (t_right, t_bottom), (255, 255, 0), 2)
                if frameNum > 0:
                    cv2.rectangle(frame, (startX, startY), (endX, endY), (255, 255, 0), 2)
                out.write(frame)
                cv2.imshow('frame', frame)
                # fp.write(str(nzWholeImageCount)+","+str(nzEmbryoRegionCount)+","+str(frameNum)+"\n")
                
            frameNum = frameNum+1
            
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        # print("peaks_list:",peaks_list)

        # show_peaks_location(emb_loc_total_pt,peaks_list,inv_peaks_list,video_name) 

        # detect_scipy_find_peaks(np.arange(len(emb_loc_total_pt)),emb_loc_total_pt)

        #print(peaks_list)
        cap.release()
        out.release()
        fp.close()
        cv2.destroyAllWindows()



