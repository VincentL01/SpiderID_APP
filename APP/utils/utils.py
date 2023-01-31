import os
import pandas as pd

import sys

# def resource_path(relative_path):
#     ### Get absolute path to resource, works for dev and for PyInstaller
#     try:
#         base_path = sys._MEIPASS
#     except Exception:
#         base_path = os.path.abspath(".")
    
#     return os.path.join(base_path, relative_path)

# ROOT_DIR is the directory up 1 level from this file directory
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

YOLOV7_DIR = os.path.join(ROOT_DIR, 'bin', 'yolov7')
RUN_DIR = os.path.join(ROOT_DIR, 'runs', 'detect')

DETECT_PATH_V7 = os.path.join(YOLOV7_DIR, 'detect.py')

CLASS_LISTS = {
    'WG': 'genera_list_WG.csv',
    'NG': 'genera_list_NG.csv'
}


RESULT_DIR = os.path.join(ROOT_DIR, 'result')
if not os.path.exists(RESULT_DIR):
    os.mkdir(RESULT_DIR)

WEIGHT_PATH_DEFAULT = os.path.join(ROOT_DIR, 'bin', 'weights', 'Genus_WG.pt')
GENERA_LIST_PATH_DEFAULT = os.path.join(ROOT_DIR, 'bin', CLASS_LISTS['WG'])




class EVALUATION_V7():

    def __init__(self, img_path, weight_path = WEIGHT_PATH_DEFAULT):

        self.img_path = img_path
        self.img_name = os.path.basename(img_path).split('.')[0]

        self.result_path = os.path.join(RESULT_DIR, 'detection_{}'.format(len(os.listdir(RESULT_DIR)) + 1))
        if not os.path.exists(self.result_path):
            os.mkdir(self.result_path)

        self.run_result = os.path.join(self.result_path, 'result.txt')

        self.weight_path = weight_path

        weight_name = os.path.basename(weight_path)
        weight_type = weight_name.split('.')[0].split('_')[-1]
        if weight_type not in ['WG', 'NG']:
            print('WRONG WEIGHT NAME FORMAT !')
            print('Weight name must end with _NG (no gender) or _WG (with gender)')
            exit()
        genera_list_path = os.path.join(ROOT_DIR, 'bin', CLASS_LISTS[weight_type])
        with open(genera_list_path, 'r') as f:
            self.genera_list = f.read().strip().split(',')
    
    def get_info(self):
        if len(os.listdir(RUN_DIR)) == 0:
            run_num = 'exp'
        else:
            run_num = 'exp'+str(len(os.listdir(RUN_DIR))+1)
        
        command = f'python {DETECT_PATH_V7} --source {self.img_path} --weights {self.weight_path} --save-txt --save-conf'
        os.system(command)

        # return genus, confidence
        label_path = os.path.join(RUN_DIR, run_num, 'labels', self.img_name + '.txt')
        img_withbb_path = os.path.join(RUN_DIR, run_num, self.img_name + '.jpg')
        with open(label_path, 'r') as f:
            lines = f.readlines()
        
        genus_list = []
        gender_list = []
        confidence_list = []

        for i, line in enumerate(lines):
            line = line.split()
            genus_code = line[0]
            genus_compact = self.genera_list[int(genus_code)]
            genus = genus_compact.split('_')[1]
            gender = genus_compact.split('_')[0]
            confidence = round(float(line[-1]),4)*100

            genus_list.append(genus)
            gender_list.append(gender)
            confidence_list.append(confidence)

        # self.genus = genus
        # self.gender = gender
        # self.confidence = confidence

        return genus_list, gender_list, confidence_list, img_withbb_path