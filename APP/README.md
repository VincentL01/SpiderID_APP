<!-- Put the logo of I-Shou university and ChungYuan University on the same line -->

# SpiderID_APP

![alt text](https://github.com/ThangLC304/SpiderID_APP/blob/main/bin/support/universities.png?raw=true)


# Authorship

## Author:

Luong Cao Thang  
PhD candidate, I-Shou University, Kaohsiung, Taiwan.  
Email: [thang.luongcao@gmail.com](mailto:thang.luongcao@gmail.com)  

## Correspondence:

Prof. Chih-Hsin Hung  
Laboratory of Biotechnology, I-Shou University, Kaohsiung, Taiwan.  
Email: [chhung@isu.edu.tw](mailto:chhung@isu.edu.tw)  

Prof. Chung-Der Hsiao  
Laboratory of Biotechnology, ChungYuan Christian University, Taoyuan, Taiwan.  
Email: [cdhsiao@cycu.edu.tw](mailto:cdhsiao@cycu.edu.tw)  


# Spider Identification App
Implement YOLO-based models, the state-of-the-art object detection models, as a solution for spider recognition.
The first version have been trained on Taiwan spiders dataset.


## Overview
Our app uses a YOLO-based Convolutional Neural Network (CNN) trained on open-access data to accurately identify spiders native to Taiwan. With its user-friendly interface, simply upload an image of a spider and the app will return a prediction of its genus in short amount of time. 


## Features
- Real-time spider identification
- YOLO-based CNN trained on open-access data
- User-friendly interface


## INSTALLATION GUIDE

### For Non-coding Users:

1. Download **ONLY** ```setup.bat``` file first:

    **RIGHT CLICK** on the ```setup.bat``` file in the repository above, and choose ```Open link in new tab```:

    ![alt text](https://github.com/ThangLC304/SpiderID_APP/blob/main/bin/support/downloadsetup00.png?raw=true)

    **LEFT CLICK** on the ```Raw``` button

    ![alt text](https://github.com/ThangLC304/SpiderID_APP/blob/main/bin/support/downloadsetup01.png?raw=true)

    **RIGHT CLICK** anywhere on the page, choose save as

    ![alt text](https://github.com/ThangLC304/SpiderID_APP/blob/main/bin/support/downloadsetup02.png?raw=true)

    **CHANGE** file type to **All Files**, make sure the File name is ```setup.bat```

    ![alt text](https://github.com/ThangLC304/SpiderID_APP/blob/main/bin/support/downloadsetup03.png?raw=true)

2. **RIGHT CLICK** and **Run as Administrator**, it will ask you if you want to change installation path from the default one, default installation path is ```C:\SpiderID```

![alt text](https://github.com/ThangLC304/SpiderID_APP/blob/main/bin/support/Installation.png?raw=true)

The setup will run automatically, it would take several minutes.

3. Run the app by double click on run.bat in the installed folder.

### For Users who are familiar with coding

__1. Clone to your computer using git__

    git clone https://github.com/ThangLC304/SpiderID_APP

__2. Install dependencies from SpiderID_APP/requirements.txt__

    pip install -r requirements.txt

__3. Run app by__

    python main.py


## APP INSTRUCTION

![alt text](https://github.com/ThangLC304/SpiderID_APP/blob/main/bin/support/APP.png?raw=true)

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


## Help protect biodiversity
Join the fight against biodiversity loss and enhance your spider knowledge with our Spider Identification App!
