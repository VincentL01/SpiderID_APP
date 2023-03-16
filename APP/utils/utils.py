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

WEIGHT_PATH_DEFAULT = os.path.join(ROOT_DIR, 'bin', 'weights', 'v7_WG.pt')
GENERA_LIST_PATH_DEFAULT = os.path.join(ROOT_DIR, 'bin', CLASS_LISTS['WG'])


class EVALUATION_V7():

    def __init__(self, media_path, weight_path = WEIGHT_PATH_DEFAULT):

        self.media_path = media_path
        
        self.weight_path = weight_path

        weight_name = os.path.basename(weight_path)
        self.weight_type = weight_name.split('.')[0].split('_')[-1]
        if self.weight_type not in ['WG', 'NG']:
            print('WRONG WEIGHT NAME FORMAT !')
            print('Weight name must end with _NG (no gender) or _WG (with gender)')
            exit()
        genera_list_path = os.path.join(ROOT_DIR, 'bin', CLASS_LISTS[self.weight_type])
        with open(genera_list_path, 'r') as f:
            self.genera_list = f.read().strip().split(',')

        self.run_num = self.run_detection()
    
    def run_detection(self):
        if not os.path.exists(RUN_DIR):
            os.mkdir(RUN_DIR)
        if len(os.listdir(RUN_DIR)) == 0:
            run_num = 'exp'
        else:
            run_num = 'exp'+str(len(os.listdir(RUN_DIR))+1)
        
        command = f'python {DETECT_PATH_V7} --source {self.media_path} --weights {self.weight_path} --save-txt --save-conf'
        os.system(command)
        
        return run_num

    def get_info(self, custom_label_path = 'Default'):
        
        # return genus, confidence
        if custom_label_path == 'Default':
            img_name = os.path.basename(self.media_path).split('.')[0]
            label_path = os.path.join(RUN_DIR, self.run_num, 'labels', img_name + '.txt')
        else:
            img_name = os.path.basename(custom_label_path).split('.')[0]
            label_path = custom_label_path

        img_withbb_path = os.path.join(RUN_DIR, self.run_num, img_name + '.jpg')
        with open(label_path, 'r') as f:
            lines = f.readlines()
        
        info_list = []
        # genus_list = []
        # gender_list = []
        # confidence_list = []

        for i, line in enumerate(lines):
            line = line.split()
            genus_code = line[0]
            genus_compact = self.genera_list[int(genus_code)]
            if '_' in genus_compact:
                genus = genus_compact.split('_')[1]
                gender = genus_compact.split('_')[0]
            else:
                genus = genus_compact
                gender = 'NA'
            confidence = round(float(line[-1]),4)*100

            info_list.append((genus, gender, confidence))
            # sort info_list by confidence, from high to low
            info_list = sorted(info_list, key=lambda x: x[2], reverse=True)
            # keep top 2 results
            if len(info_list) > 2:
                info_list = info_list[:2]

            # genus_list.append(genus)
            # gender_list.append(gender)
            # confidence_list.append(confidence)

        return img_name, info_list, img_withbb_path

    def get_info_multiple(self):

        csv_out_dir = os.path.join(RESULT_DIR, self.run_num)
        if not os.path.exists(csv_out_dir):
            os.mkdir(csv_out_dir)
        csv_out_path = os.path.join(csv_out_dir, 'result.csv')

        # interfered images path
        labels_dir = os.path.join(RUN_DIR, self.run_num, 'labels')
        labels = os.listdir(labels_dir)
        labels = [label for label in labels if label.endswith('.txt')]

        columns = ['image', 'genus_1', 'gender_1', 'confidence_1', 'genus_2', 'gender_2', 'confidence_2', 'img_withbb_path']
        df = pd.DataFrame(columns=columns)

        # 13 0.569351 0.567 0.727069 0.754 0.953831

        for label in labels:
            label_path = os.path.join(labels_dir, label)
            print('Working with label path', label_path)
            img_name, info_list, img_withbb_path = self.get_info(custom_label_path = label_path)
            if len(info_list) == 0:
                # write a row with img_name, NA, NA, NA, NA, NA, NA, img_withbb_path
                # using pd.concat
                df = pd.concat([df, pd.DataFrame([[img_name, 'NA', 'NA', 'NA', 'NA', 'NA', 'NA', img_withbb_path]], columns=columns)], ignore_index=True)
            elif len(info_list) == 1:
                df = pd.concat([df, pd.DataFrame([[img_name, info_list[0][0], info_list[0][1], info_list[0][2], 'NA', 'NA', 'NA', img_withbb_path]], columns=columns)], ignore_index=True)
            elif len(info_list) == 2:
                df = pd.concat([df, pd.DataFrame([[img_name, info_list[0][0], info_list[0][1], info_list[0][2], info_list[1][0], info_list[1][1], info_list[1][2], img_withbb_path]], columns=columns)], ignore_index=True)
        
        df.to_csv(csv_out_path, index=False)
        print('Result saved to', csv_out_path)

        return csv_out_path