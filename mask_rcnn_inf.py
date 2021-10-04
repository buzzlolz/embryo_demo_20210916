import os
import sys
import random
import math
import re
import time
import numpy as np
import cv2
import matplotlib
import matplotlib.pyplot as plt
import tensorflow as tf
import yaml
import skimage.io
import time
import matplotlib.pyplot as plt
from datetime import datetime 

from mrcnn.config import Config
#import utils
from mrcnn import model as modellib,utils
from mrcnn import visualize
import yaml
from mrcnn.model import log
from PIL import Image


# want to add mask rcnn pn detect
#os.environ["CUDA_VISIBLE_DEVICES"] = "0"
# Root directory of the project
ROOT_DIR = os.getcwd()

#ROOT_DIR = os.path.abspath("../")
# Directory to save logs and trained model
MODEL_DIR = ROOT_DIR

# class InferenceConfig(ShapesConfig):
#     GPU_COUNT = 1
#     IMAGES_PER_GPU = 1


class ShapesConfig_frag_model(Config):
    """Configuration for training on the toy shapes dataset.
    Derives from the base Config class and overrides values specific
    to the toy shapes dataset.
    """
    # Give the configuration a recognizable name
    NAME = "shapes"

    # Train on 1 GPU and 8 images per GPU. We can put multiple images on each
    # GPU because the images are small. Batch size is 8 (GPUs * images/GPU).
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

    # Number of classes (including background)
    NUM_CLASSES = 1 + 1  # background + ears

    # Use small images for faster training. Set the limits of the small side
    # the large side, and that determines the image shape.
    IMAGE_MIN_DIM = 512
    IMAGE_MAX_DIM = 512

    # Use smaller anchors because our image and objects are small
#     RPN_ANCHOR_SCALES = (8*6, 16*6, 32*6, 64*6, 128*6)  # anchor side in pixels
    RPN_ANCHOR_SCALES = (4*6, 8*6, 16*6, 32*6, 64*6)  # anchor side in pixels

    # Reduce training ROIs per image because the images are small and have
    # few objects. Aim to allow ROI sampling to pick 33% positive ROIs.
    TRAIN_ROIS_PER_IMAGE = 32

    # Use a small epoch since the data is simple
    STEPS_PER_EPOCH = 32

    # use small validation steps since the epoch is small
    VALIDATION_STEPS = 16
    
    # Accoring to CSDN 79140840 defin a global val iter_num
    # iter_num = 0
    
# config = ShapesConfig()
# config.display()

class ShapesConfig_pn_model(Config):
    """Configuration for training on the toy shapes dataset.
    Derives from the base Config class and overrides values specific
    to the toy shapes dataset.
    """
    # Give the configuration a recognizable name
    NAME = "shapes"

    # Train on 1 GPU and 8 images per GPU. We can put multiple images on each
    # GPU because the images are small. Batch size is 8 (GPUs * images/GPU).
    GPU_COUNT = 1
    IMAGES_PER_GPU = 1

    # Number of classes (including background)
    NUM_CLASSES = 1 + 3  # background + ears

    # Use small images for faster training. Set the limits of the small side
    # the large side, and that determines the image shape.
    IMAGE_MIN_DIM = 512
    IMAGE_MAX_DIM = 512

    # Use smaller anchors because our image and objects are small
#     RPN_ANCHOR_SCALES = (8*6, 16*6, 32*6, 64*6, 128*6)  # anchor side in pixels
    RPN_ANCHOR_SCALES = (4*6, 8*6, 16*6, 32*6, 64*6)  # anchor side in pixels

    # Reduce training ROIs per image because the images are small and have
    # few objects. Aim to allow ROI sampling to pick 33% positive ROIs.
    TRAIN_ROIS_PER_IMAGE = 32

    # Use a small epoch since the data is simple
    STEPS_PER_EPOCH = 32

    # use small validation steps since the epoch is small
    VALIDATION_STEPS = 16
    
    # Accoring to CSDN 79140840 defin a global val iter_num
    # iter_num = 0



def load_cell_mask_model():

    inference_config = InferenceConfig()

    # Recreate the model in inference mode
    model = modellib.MaskRCNN(mode="inference", 
                            config=inference_config,
                            model_dir=MODEL_DIR)


    # Get path to saved weights
    # Either set a specific path or find last trained weights
    # model_path = os.path.join(ROOT_DIR, ".h5 file name here")
    #model_path = model.find_last()
    # model_path='./logs/shapes20200407T1436/mask_rcnn_shapes_0025.h5'
    model_path='./model_data/cell_count_model/mask_rcnn_shapes_0100.h5'

    # Load trained weights
    print("Loading weights from ", model_path)
    model.load_weights(model_path, by_name=True)

    return model


def load_frag_model():
    # config = ShapesConfig()
    # config.display()

    inference_config = ShapesConfig_frag_model()

    # Recreate the model in inference mode
    model = modellib.MaskRCNN(mode="inference", 
                            config=inference_config,
                            model_dir=MODEL_DIR)


    # Get path to saved weights
    # Either set a specific path or find last trained weights
    # model_path = os.path.join(ROOT_DIR, ".h5 file name here")
    #model_path = model.find_last()
    # model_path='./logs/shapes20200407T1436/mask_rcnn_shapes_0025.h5'
    model_path='./model_data/cell_fragment_model/fragment_1029.h5'

    # Load trained weights
    print("Loading weights from ", model_path)
    model.load_weights(model_path, by_name=True)

    return model





def load_pn_count_model():

    inference_config = ShapesConfig_pn_model()
    # Recreate the model in inference mode
    model = modellib.MaskRCNN(mode="inference", 
                            config=inference_config,
                            model_dir=MODEL_DIR)


    # Get path to saved weights
    # Either set a specific path or find last trained weights
    # model_path = os.path.join(ROOT_DIR, ".h5 file name here")
    #model_path = model.find_last()
    # model_path='./logs/shapes20200407T1436/mask_rcnn_shapes_0025.h5'
    model_path='./model_data/cell_pn_model/cell_pn_model_20210927.h5'

    # Load trained weights
    print("Loading weights from ", model_path)
    model.load_weights(model_path, by_name=True)

    return model


def img_inference_frag(frag_model,img_path):

    
    # Index of the class in the list is its ID. For example, to get ID of
    # the teddy bear class, use: class_names.index('teddy bear')
    class_names = ['BG', 'frag']
    # Load a random image from the images folder

    image = skimage.io.imread(img_path)


    #plt.show("./7_00000417_DISH1_1120000_00059.jpg")
    all_d_time=0



    # Run detection
    
    t_start=time.time()
    results = frag_model.detect([image], verbose=1)
    t_end = time.time()
    #print("mask rcnn result::",results['mask'])
    
    d_time=t_end-t_start
    all_d_time=all_d_time+d_time


        
  
    # Visualize results

    r = results[0]
    # print(r)
    # print(r['masks'])
    # print("class id",r['class_ids'])
    cell_count=len(r['scores'])
    # print("len r['scores']",len(r['scores']))

    # visualize.display_instances(image, r['rois'], r['masks'], r['class_ids'], 
    #                             class_names, r['scores'])
    percentage = visualize.frag_percentage_count(image,r['rois'], r['masks'], r['class_ids'], r['scores'],
                                class_names)
    print ("precentage:",percentage)
    return percentage
    





def img_inference_cell(mask_model,img_path):

    
    # Index of the class in the list is its ID. For example, to get ID of
    # the teddy bear class, use: class_names.index('teddy bear')
    class_names = ['BG', 'cell']
    # Load a random image from the images folder

    image = skimage.io.imread(img_path)


    #plt.show("./7_00000417_DISH1_1120000_00059.jpg")
    all_d_time=0
    a=datetime.now() 
    # Run detection
    
    t_start=time.time()
    results = mask_model.detect([image], verbose=1)
    t_end = time.time()
    #print("mask rcnn result::",results['mask'])
    
    d_time=t_end-t_start
    all_d_time=all_d_time+d_time


    print("duration time:",all_d_time/1)
        
    b=datetime.now() 
    # Visualize results
    print("shijian",(b-a).seconds)
    r = results[0]
    # print(r)
    # print(r['masks'])
    # print("class id",r['class_ids'])
    cell_count=len(r['scores'])
    # print("len r['scores']",len(r['scores']))


    #image save and show

    # image_name = img_path.split('/')[-1]
    # # visualize.save_mask_result(image, image_name,r['rois'], r['masks'], r['class_ids'], 
    # #                             class_names, r['scores'])
    # visualize.display_instances(image,image_name,r['rois'], r['masks'], r['class_ids'], r['scores'],
    #                             class_names)
    return cell_count
    



def img_inference_pn_count(mask_model,img_path):

    
    # Index of the class in the list is its ID. For example, to get ID of
    # the teddy bear class, use: class_names.index('teddy bear')
    class_names = ['BG', 'cytoplasm','pn','ZP']
    # Load a random image from the images folder

    image = skimage.io.imread(img_path)


    #plt.show("./7_00000417_DISH1_1120000_00059.jpg")
    all_d_time=0
    # a=datetime.now() 
    # Run detection
    
    # t_start=time.time()
    results = mask_model.detect([image], verbose=1)
    # t_end = time.time()
    #print("mask rcnn result::",results['mask'])
    
    # d_time=t_end-t_start
    # all_d_time=all_d_time+d_time


    # print("duration time:",all_d_time/1)
        
    # b=datetime.now() 
    # Visualize results
    # print("shijian",(b-a).seconds)
    r = results[0]
    # print(r)
    # print(r['masks'])
    # print("class id",r['class_ids'])
    cell_count=len(r['scores'])
    pn_count = (r['class_ids']==2).sum()
    print(pn_count)
    # print("len r['scores']",len(r['scores']))


    #image save and show

    # image_name = img_path.split('/')[-1]
    # # visualize.save_mask_result(image, image_name,r['rois'], r['masks'], r['class_ids'], 
    # #                             class_names, r['scores'])
    # visualize.display_instances(image,image_name,r['rois'], r['masks'], r['class_ids'], r['scores'],
    #                             class_names)



    return pn_count
    


if __name__=='__main__':
    
    img_path="C:/A70417/Mask_RCNN/data_0617/6_00000496_6_DISH7_1163000_00050.jpg"
    frag_models = load_frag_model()
    img_inference_frag(frag_models,img_path)