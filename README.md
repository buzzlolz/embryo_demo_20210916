# embryo system

embryo analysis system -classification mask-rcnn yolo


## environment

- python=3.6.7
- keras =2.24 
- tensorflow-gpu=1.12
- cuda=9.2
- cudnn=7.6.5


## conda install env

`conda env create -f embryo_env.yaml -n emb_env`


## inference

`python main.py`

## Code Introduction

- Calandar.py:日曆按鈕功能
- Chamber_inference_Class:胚胎偵測主程式(yolo,stage classification,mask rcnn)
- Class_Extract_Sqlite.py:將sqlite 檔解開，讀取index檔並將timelapse影像影片寫入硬碟
- EmbryoBoxInfo.py :系統內所有表格細節
- ImportSqliteDialog.py:確認sqlite檔案已經解析完畢信號
- main.py:系統啟動程式
- mask_rcnn_inf.py:所有segmentation(mask rcnn )架構宣告
- ReadSqlInfoPath:讀取ini檔取得sqlite檔案path 和 hisory儲存位置
- SelectCellDish.py :Chamber select頁面圓形dish按鈕觸發事件與相關狀態

- TabEmbryoResults.py:Embryo Viewer 頁面pyqt 版面設定及相關功能
- TabHistoryChamber.py : History頁面pyqt 版面設定及相關功能
- TabMachineSelection.py:Machine Selection頁面pyqt 版面設定及相關功能
- TabSelectChamber.py:Chamber select頁面pyqt 版面設定及相關功能
- UI_Function.py:各系統頁面功能function
- Yolo.py :yolo相關功能

