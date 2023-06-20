<!-- Put the logo of I-Shou university and ChungYuan University on the same line -->

# __SpiderID_APP__

![alt text](https://github.com/ThangLC304/SpiderID_APP/blob/main/bin/support/universities.png?raw=true)


# __Authorship__

## __Author:__

Luong Cao Thang  
PhD candidate, I-Shou University, Kaohsiung, Taiwan.  
Email: [thang.luongcao@gmail.com](mailto:thang.luongcao@gmail.com)  

## __Correspondence:__

Prof. Chih-Hsin Hung  
Laboratory of Biotechnology, I-Shou University, Kaohsiung, Taiwan.  
Email: [chhung@isu.edu.tw](mailto:chhung@isu.edu.tw)  

Prof. Chung-Der Hsiao  
Laboratory of Biotechnology, ChungYuan Christian University, Taoyuan, Taiwan.  
Email: [cdhsiao@cycu.edu.tw](mailto:cdhsiao@cycu.edu.tw)  


# __Spider Identification App__
Implement YOLO-based models, the state-of-the-art object detection models, as a solution for spider recognition.
The first version have been trained on Taiwan spiders dataset.


## __Overview__
Our app uses a YOLO-based Convolutional Neural Network (CNN) trained on open-access data to accurately identify spiders native to Taiwan. With its user-friendly interface, simply upload an image of a spider and the app will return a prediction of its genus in short amount of time. 


## __Features__
- Real-time spider identification
- YOLO-based CNN trained on open-access data
- User-friendly interface


## __INSTALLATION GUIDE__

### __For Non-coding Users:__

1. **DOWNLOAD** application zip file by **LEFT CLICK** on the **CODE** box in the repository above, and choose ```Download ZIP``` (~162Mb):

    ![tutorial_img_00](https://github.com/ThangLC304/SpiderID_APP/blob/main/bin/support/downloadsetup00.png?raw=true)


2. **EXTRACT** downloaded file at a location of your choice


3. **RIGHT CLICK** ```setup.bat``` file and choose **Run as Administrator**

    ![tutorial_img_01](https://github.com/ThangLC304/SpiderID_APP/blob/main/bin/support/downloadsetup01.png?raw=true)

    The setup will run automatically, it would take several minutes.


4. **RUN** the app by **DOUBLE CLICK** on ```run.bat``` in the installed folder.

    ![tutorial_img_02](https://github.com/ThangLC304/SpiderID_APP/blob/main/bin/support/downloadsetup02.png?raw=true)

5. If in any step of running setup.bat or run.bat there is the window of Window Protection, please use the following steps:

    **LEFT CLICK** ```"More info"```

    ![window_protect_image_00](https://github.com/ThangLC304/SpiderID_APP/blob/main/bin/support/ifwindowprotect00.png?raw=true)

    **LEFT CLICK** ```Run anyway```

    ![window_protect_image_01](https://github.com/ThangLC304/SpiderID_APP/blob/main/bin/support/ifwindowprotect01.png?raw=true)

<br>

### __For Users who are familiar with coding:__

__1. Clone to your computer using git__

    git clone https://github.com/ThangLC304/SpiderID_APP

__2. Install dependencies from SpiderID_APP/requirements.txt__

    pip install -r requirements.txt

__3. Run app by__

    python main.py


## __APP INSTRUCTION__

![APP_GUI_00](https://github.com/ThangLC304/SpiderID_APP/blob/main/bin/support/app_gui00.png?raw=true)

1. **Weight selection:**

    The default loaded weight is v7_WG which will identify image(s)/video and give you Genus & Gender of the Spider

    To use default weight, simply skip this Weight selection step.

    You can use Weight selection to select v7_NG to identify image(s)/video and give you Genus as the result only. This may increase the accuracy and confidence of the model while sacrificing the ability to identify gender.

2. **Image processing:**

    If one image is selected, the result would be displayed on the screen (new window is opened)
        If you want to see the result again, go to SpiderID_APP/runs/detect, the lastest identification would have the highest number in exp{num} format

    If several images are selected, the result would be saved at path: SpiderID_APP/result/exp{num}/result.csv
        Lastest detection would have the highest num

    Accepted image formats are:
    ```['bmp', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'dng', 'webp', 'mpo']```

3. **Video processing:**

    Simply select the video to detect

    Accepted video formats are:
    ```['mov', 'avi', 'mp4', 'mpg', 'mpeg', 'm4v', 'wmv', 'mkv']```

4. **History View:**

    ![APP_GUI_01](https://github.com/ThangLC304/SpiderID_APP/blob/main/bin/support/app_gui01.png?raw=true)

    In this feature, Users can view the identified images.

    1. User can retrieve list of images were identified by selecting the ```Weight```.
    2. **DOUBLE CLICK** on image name to load its history
    3. The bounding boxes and identification results are displayed using the lowest Confidence threshold, 
    adjusting the ```Threshold slider``` can filter out the lower confidence results.
    4. If an image is identified multiple times, select different ```Instances```



## __Help protect biodiversity__
Join the fight against biodiversity loss and enhance your spider knowledge with our Spider Identification App!
