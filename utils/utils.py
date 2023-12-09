import os
import pandas as pd
from pathlib import Path
import tkinter
from tkinter import ttk
import shutil
import json
import sys
from datetime import datetime
from pathlib import Path

import logging

logger = logging.getLogger(__name__)

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
RUN_DIR = os.path.join(ROOT_DIR, 'runs')
if not os.path.exists(RUN_DIR):
    os.mkdir(RUN_DIR)
DETECT_DIR = os.path.join(RUN_DIR, 'detect')
PROCESSED_DIR = os.path.join(ROOT_DIR, 'processed')


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

HISTORY_PATH = os.path.join(ROOT_DIR, 'bin', 'history.json')

img_formats = ['bmp', 'jpg', 'jpeg', 'png', 'tif', 'tiff', 'dng', 'webp', 'mpo']  # acceptable image suffixes
vid_formats = ['mov', 'avi', 'mp4', 'mpg', 'mpeg', 'm4v', 'wmv', 'mkv']  # acceptable video suffixes


class EVALUATION_V7():

    def __init__(self, media_path, weight_path = WEIGHT_PATH_DEFAULT):

        self.media_path = media_path
        
        self.weight_path = weight_path

        self.weight_name = Path(self.weight_path).stem
        if 'wg' in self.weight_name.lower():
            self.weight_type = 'WG'
        elif 'ng' in self.weight_name.lower():
            self.weight_type = 'NG'
        else:
            message = 'WRONG WEIGHT NAME FORMAT !'            
            message += '\nWeight name must end with _NG (no gender) or _WG (with gender)'
            raise Exception(message)

        genera_list_path = os.path.join(ROOT_DIR, 'bin', CLASS_LISTS[self.weight_type])
        with open(genera_list_path, 'r') as f:
            self.genera_list = f.read().strip().split(',')

        self.run_num = self.run_detection()
    


    def run_detection(self):

        if not os.path.exists(DETECT_DIR):
            os.mkdir(DETECT_DIR)
        if len(os.listdir(DETECT_DIR)) == 0:
            run_num = 'exp'
        else:
            run_num = 'exp'+str(len(os.listdir(DETECT_DIR))+1)

        command = "python"

        file_name = Path(self.media_path).name
        save_path = os.path.join(DETECT_DIR, run_num)

        if self.processed_before(file_name):
            logger.info(f"File {file_name} has been processed before. Analyze again?")
            #display message box using tkinter, ask user if they want to overwrite
            choice = tkinter.messagebox.askyesno(title="Duplication", message="File already exists. Analyze again?")
            if choice == False:
                logger.debug("User chose not to continue analysis")
                return
            else:
                logger.debug("User chose to continue analysis")
                pass
                # while True:
                #     try:
                #         shutil.rmtree(save_path)
                #         break
                #     except:
                #         choice = ttk.messagebox.askyesno(title="File in use", message="File is open. Close file and try again.")
                #         if choice == False:
                #             return
                #         else:
                #             continue

        default_args = [
            f'"{DETECT_PATH_V7}"',
            f'--source "{self.media_path}"',
            f'--weights "{self.weight_path}"',
            "--conf-thres 0.03",
            "--iou-thres 0.5",
            "--save-txt",
            "--save-conf",
            "--augment",
            "--no-trace",
            "--img-size 512",
        ]
        
        # if media file ends with img_formats, run detection on single image
        if self.media_path.split('.')[-1] in vid_formats:
            args = default_args + [f"--view-img"]
        else:
            args = default_args

        for arg in args:
            command += " " + arg

        os.system(command)

        logger.info(f"Detection completed for {self.media_path}")

        # save to history
        self.write_to_history(file_name, save_path)

        return run_num


    def processed_before(self, file_name):
        try:
            with open(HISTORY_PATH, 'r') as f:
                history = json.load(f)
        except FileNotFoundError:
            logger.debug("History file not found")
            # create history file
            with open(HISTORY_PATH, 'w') as f:
                json.dump({}, f)
            logger.debug("Created blank history file!")
            return False
        
        if self.weight_name not in history:
            logger.debug(f"Weight {self.weight_name} has not been processed before")
            history[self.weight_name] = {}
            with open(HISTORY_PATH, 'w') as f:
                json.dump(history, f)
            logger.debug(f"Added weight {self.weight_name} with blank dict to history file")
            return False

        if file_name in history[self.weight_name]:
            logger.debug(f"File {file_name} has been processed before")
            return True
        else:
            logger.debug(f"File {file_name} has not been processed before")
            return False


    def write_to_history(self, file_name, save_path):
        
        with open(HISTORY_PATH, 'r') as f:
            history = json.load(f)

        if (history == {}) or (history is None) or (history == "") or (self.weight_name not in history):
            history[self.weight_name] = {}
            logger.debug(f"History file of weight {self.weight_name} is empty. Created blank dictionary")

        # Get the current date and time
        current_time = datetime.now()

        # Format the current date and time
        formatted_time = current_time.strftime("%Y%m%d-%H%M%S")

        if file_name == "temp":
            # use pathlib and glob to find all .jpg in save_path
            file_names = [p.name for p in Path(save_path).glob('*.jpg')]

            for file_name in file_names:
                if file_name not in history[self.weight_name]:
                    history[self.weight_name][file_name] = [(save_path, formatted_time)]
                    logger.debug(f"History file of weight {self.weight_name} is empty. Created new entry")
                else:
                    history[self.weight_name][file_name].append((save_path, formatted_time))
                    logger.debug(f"History file of weight {self.weight_name} is not empty. Appended to existing entry")
        else:
            if file_name not in history[self.weight_name]:
                history[self.weight_name][file_name] = [(save_path, formatted_time)]
                logger.debug(f"History file of weight {self.weight_name} is empty. Created new entry")
            else:
                history[self.weight_name][file_name].append((save_path, formatted_time))
                logger.debug(f"History file of weight {self.weight_name} is not empty. Appended to existing entry")

        with open(HISTORY_PATH, 'w') as f:
            json.dump(history, f)
        logger.debug(f"Saved to history file")

    
    def get_save_paths(self, file_name):

        with open(HISTORY_PATH, 'r') as f:
            history = json.load(f)

        save_paths = history[self.weight_name][file_name]

        return save_paths


    def get_info_single(self, custom_label_path = 'Default', mode='last'):
        
        if custom_label_path == 'Default':
            img_name = Path(self.media_path).name
            img_stem = Path(self.media_path).stem
            save_paths = self.get_save_paths(img_name)
            if mode == 'last':
                label_path = os.path.join(save_paths[-1][0], 'labels', img_stem + '.txt')
        else:
            img_name = Path(self.media_path).name
            label_path = custom_label_path

        img_withbb_path = os.path.join(DETECT_DIR, self.run_num, img_name)
        # img_wobb_path = os.path.join(PROCESSED_DIR, img_name)
        with open(label_path, 'r') as f:
            lines = f.readlines()
        
        info_list = []

        for line in lines:
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

            # # keep top 2 results
            # if len(info_list) > 2:
            #     info_list = info_list[:2]

        return img_name, info_list, img_withbb_path



    def get_info_multiple(self):

        csv_out_dir = os.path.join(RESULT_DIR, self.run_num)
        if not os.path.exists(csv_out_dir):
            os.mkdir(csv_out_dir)
        csv_out_path = os.path.join(csv_out_dir, 'result.csv')

        # interfered images path
        labels_dir = os.path.join(DETECT_DIR, self.run_num, 'labels')
        labels = os.listdir(labels_dir)
        labels = [label for label in labels if label.endswith('.txt')]

        columns = ['image', 'genus_1', 'gender_1', 'confidence_1', 'genus_2', 'gender_2', 'confidence_2', 'img_withbb_path']
        df = pd.DataFrame(columns=columns)

        # 13 0.569351 0.567 0.727069 0.754 0.953831

        for label in labels:
            label_path = os.path.join(labels_dir, label)
            print('Working with label path', label_path)
            img_name, info_list, img_withbb_path = self.get_info_single(custom_label_path = label_path)
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

        return csv_out_path, df
    


    def get_info_video(self):
        csv_out_path, _ = self.get_info_multiple()

        df = pd.read_csv(csv_out_path)

        if self.weight_type == 'WG':
            has_gender = True
        else:
            has_gender = False

        def add_to_dict(row, g_num, result_dict, has_gender = True):
            if not pd.isna(row[f'genus_{g_num}']):
                if has_gender == True:
                    key = (row[f'genus_{g_num}'], row[f'gender_{g_num}'])
                else:
                    key = row[f'genus_{g_num}', 'NA']
                if key not in result_dict:
                    result_dict[key] = {}
                    result_dict[key]['count'] = 1
                    result_dict[key]['confidence'] = row[f'confidence_{g_num}']
                else:
                    result_dict[key]['count'] += 1
                    result_dict[key]['confidence'] += row[f'confidence_{g_num}']
        
        result_dict = {}
        for idx, row in df.iterrows():
            add_to_dict(row, 1, result_dict, has_gender = has_gender)
            add_to_dict(row, 2, result_dict, has_gender = has_gender)

        result_dict[('others', 'NA')] = {}
        result_dict[('others', 'NA')]['count'] = 0
        result_dict[('others', 'NA')]['confidence'] = 0

        threshold = int(0.1*len(df))
        unuse_keys = []
        for key, value in result_dict.items():
            if value['count'] < threshold:
                # add to a key name 'others'
                result_dict[('others', 'NA')]['count'] += value['count']
                result_dict[('others', 'NA')]['confidence'] += value['confidence']
                unuse_keys.append(key)
        
        for key in unuse_keys:
            del result_dict[key]

        for key, value in result_dict.items():
            value['confidence'] = value['confidence'] / value['count']
        
        return result_dict, len(df)
