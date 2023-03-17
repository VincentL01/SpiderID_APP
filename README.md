# SpiderID_APP
 
# Spider Identification App
Implement YOLO-based models, the state-of-the-art object detection models, as a solution for spider species recognition.
The first version have been trained on Taiwan spiders dataset.

## Overview
Our app uses a YOLO-based Convolutional Neural Network (CNN) trained on open-access data to accurately identify spiders native to Taiwan. With its user-friendly interface, simply upload an image of a spider and the app will return a prediction of its species in real-time. 

## Features
- Real-time spider species identification
- YOLO-based CNN trained on open-access data
- User-friendly interface

## How to use
1. Install the requirements listed in the `requirements.txt` file
```
pip install -r requirements.txt
```
2. Run the app and choose spider image/images for identification
    If one image is selected, the result would be displayed on the screen (new window is opened)
    If several images are selected, the result would be saved at path: APP/result/exp{num}/result.csv
3. Video processing would take a lot of time if using CPU (>400ms per frame)

## Help protect biodiversity
Join the fight against biodiversity loss and enhance your spider knowledge with our Taiwan Spider Identification App!
