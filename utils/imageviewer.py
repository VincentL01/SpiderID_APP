import tkinter as tk
from tkinter import filedialog, ttk, Toplevel
from PIL import ImageTk, Image, ImageDraw
import os
import json
from pathlib import Path
import numpy as np

import logging
from colorlog import ColoredFormatter

from utils.misc import *

logger = logging.getLogger(__name__)

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HISTORY_PATH = os.path.join(ROOT_DIR, 'bin', 'history.json')
WEIGHTS_PATH = os.path.join(ROOT_DIR, 'bin', 'weights')
PROCESSED_DIR = os.path.join(ROOT_DIR, 'processed')
CLASS_LISTS = {
    'WG': 'genera_list_WG.csv',
    'NG': 'genera_list_NG.csv'
}

BBOX_COLORS = ['red', 'blue', 'green', 'yellow', 'orange', 'purple', 'pink', 'cyan', 'magenta', 'brown', 'black']

class ResultFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

    def add_label(self, text, color):
        label = ttk.Label(self, text=text)
        # set text color
        label.config(foreground=color)
        label.pack(side='top', fill='x')
    
    def delete_all(self):
        for widget in self.winfo_children():
            widget.destroy()


class ImageViewer(tk.Toplevel):
    def __init__(self):
        super().__init__()

        logger.info('Initializing ImageViewer...')

        print("ROOT_DIR: ", ROOT_DIR)
        print("HISTORY_PATH: ", HISTORY_PATH)
        print("WEIGHTS_PATH: ", WEIGHTS_PATH)
        print("PROCESSED_DIR: ", PROCESSED_DIR)

        self.title("Image Viewer")
        self.geometry("500x500")

        self.top = None  # Toplevel window

        # Frame for Listbox
        self.frame = ttk.Frame(self)
        # self.frame.place(x=10, y=10, width=200, height=200)
        self.frame.grid(row=0, rowspan=2, column=0, padx=10, pady=10, sticky='nsew')

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.frame)
        self.scrollbar.pack(side='right', fill='y')

        # Listbox
        self.listbox = tk.Listbox(self.frame, 
                                  width=50, 
                                  yscrollcommand=self.scrollbar.set)
        self.listbox.pack(side='left', fill='both')
        self.listbox.bind("<Double-Button-1>", self.display_info)
        self.scrollbar.config(command=self.listbox.yview)

        # Slider
        self.slider_frame = ttk.Frame(self)
        self.slider_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

        self.sliderlabel = ttk.Label(self.slider_frame, text='Confidence Threshold')
        self.sliderlabel.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')

        self.slidervalue = ttk.Label(self.slider_frame)
        self.slidervalue.grid(row=1, column=1, padx=10, pady=10, sticky='nsew')

        self.slider = ttk.Scale(self.slider_frame, 
                                from_=0.03, 
                                to=0.95, 
                                orient='horizontal',
                                command=self.on_slider_change)
        # self.slider.place(x=220, y=10, width=270, height=200)
        self.slider.grid(row=2, column=1, padx=10, pady=10, sticky='nsew')
        
        self.slider.set(0.03)
        self.slidervalue.config(text=round(float(self.slider.get()),4))

        # Results info
        
        self.result_frame = ResultFrame(self)
        self.result_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')


        # Weight types
        weight_types = os.listdir(WEIGHTS_PATH)
        weight_types = [Path(weight_type).stem for weight_type in weight_types if weight_type.endswith('.pt')]
        self.weight_frame = ttk.Frame(self)
        self.weight_frame.grid(row=3, column=0, padx=10, pady=10, sticky='nsew')
        
        self.weightLabel = ttk.Label(self.weight_frame, text='Weight Type')
        self.weightLabel.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.weightDropDown = ttk.Combobox(self.weight_frame, values=weight_types)
        # self.weightDropDown.place(x=120, y=430, width=100, height=30)
        self.weightDropDown.grid(row=1, column=0, padx = 10, pady = 10, sticky='nsew')
        self.weightDropDown.current(0)


        # Analyze instances
        instance_frame = ttk.Frame(self)
        instance_frame.grid(row=3, column=1, padx=10, pady=10, sticky='nsew')

        self.instancelabel = ttk.Label(instance_frame, text='Analyzed Instances')
        self.instancelabel.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        self.instanceDropDown = ttk.Combobox(instance_frame)
        self.instanceDropDown.grid(row=1, column=0, padx = 10, pady = 10, sticky='nsew')


        # INIT LOAD
        self.load_from_history()



    def load_from_history(self):
        # get weight_name from self.weightDropDown
        self.weight_name = self.weightDropDown.get()
        logger.debug(f"Loading history for weight: {self.weight_name}")
        if self.weight_name == '':
            logger.debug("No weight selected")
            return

        # load history
        with open(HISTORY_PATH, 'r') as f:
            history = json.load(f)

        self.images_history = history[self.weight_name]
        logger.debug(f"Images analyzed using weight {self.weight_name}: {len(self.images_history)}")
        
        self.image_files = list(self.images_history.keys())
        logger.debug(f"Image files: {self.image_files}")

        for file in self.image_files:
            self.listbox.insert(tk.END, file)


    def update_instance(self, event=None):
        # count number of instances
        index = self.listbox.curselection()[0]
        image_file = self.image_files[index]
        instances = [i for i in range(len(self.images_history[image_file]))]
        self.instanceDropDown.config(values=instances)
        # set to last
        self.instanceDropDown.current(len(instances)-1)

        #bind the selection event to self.display_info with initload = value of instanceDropdown
        self.instanceDropDown.bind("<<ComboboxSelected>>", self.display_info)


    def load_images(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            self.image_files = os.listdir(self.folder_path)
            self.listbox.delete(0, tk.END)
            for file in self.image_files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                    self.listbox.insert(tk.END, file)


    def spawn_top_widget(self, title='Image Viewer'):
        self.top = Toplevel(self)
        self.top.title(title)
        self.top.geometry("+%d+%d" % (self.winfo_x() + 500, self.winfo_y()))
        self.panel = ttk.Label(self.top)
        self.panel.pack()


    def info_reader(self, img_info_path):

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

        with open(img_info_path, 'r') as f:
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
            confidence = round(float(line[-1]),4)

            yolo_coords = [float(coord) for coord in line[1:5]]

            info_list.append((genus, gender, yolo_coords, confidence))
            # sort info_list by confidence, from high to low
            info_list = sorted(info_list, key=lambda x: x[3], reverse=True)

        return info_list
    

    def bbox_drawer(self, input_info_list):
        
        yolo_coords = []
        for info in input_info_list:
            yolo_coords.append(info[2])

        xyxy_coords = [yolo_to_xyxy(coord, self.dw, self.dh) for coord in yolo_coords]

        # draw bbox on image in self.panel
        img = self.img.copy()
        draw = ImageDraw.Draw(img)
        for i, bbox in enumerate(xyxy_coords):
            draw.rectangle(bbox, outline=BBOX_COLORS[i], width=2)  # Adjust color and width as needed

        img = ImageTk.PhotoImage(img)
        self.panel.config(image=img)
        self.panel.image = img


    def update_result_label(self, input_info_list, conf_threshold):
        # filter info_list by confidence threshold
        filtered_info_list = info_filter(input_info_list, conf_threshold)
        logger.debug(f"Filtered info list: {filtered_info_list}")

        self.result_frame.delete_all()

        for i in range(len(filtered_info_list)):
            display_text = ''
            display_text += '\nGenus: {}'.format(filtered_info_list[i][0])
            display_text += '\nGender: {}'.format(filtered_info_list[i][1])
            display_text += '\nConfidence: {}%'.format(filtered_info_list[i][3]*100)
            self.result_frame.add_label(display_text, color = BBOX_COLORS[i])


        self.bbox_drawer(filtered_info_list)
        logger.debug(f"Draw bbox to fit conf threshold of {conf_threshold}")


    def display_info(self, event=None):
        if self.listbox.curselection():
            index = self.listbox.curselection()[0]
            image_file = self.image_files[index]

            # get init_load from instanceDropDown
            try:
                init_load = int(self.instanceDropDown.get())
            except:
                init_load = -1

            self.update_instance()

            exp_path, analyze_time_formatted = self.images_history[image_file][init_load]

            analyze_time = convert_to_datetime(analyze_time_formatted)
            logger.debug(f"Image {image_file} analyzed at {analyze_time}")
            title = f"Image Viewer - {image_file} - {analyze_time_formatted}"

            img_path = os.path.join(PROCESSED_DIR, image_file)
            img_info_path = os.path.join(exp_path, 'labels', image_file.split('.')[0] + '.txt')

            self.img = Image.open(img_path)
            # resize image to fit in the window
            self.img, self.dw, self.dh = resize_to_fit(self.img, 500, 500) # self.dw = display width, self.dh = display height
            logger.debug(f"Image size: {self.img.size}")
            img = ImageTk.PhotoImage(self.img)
            if not self.top:
                self.spawn_top_widget(title)
            try:
                self.panel.config(image=img)
            except:
                self.spawn_top_widget(title)
                self.panel.config(image=img)
            # self.panel.image = img

            self.info_list = self.info_reader(img_info_path)
            logger.debug(f"Info list: {self.info_list}")

            # get confidence threshold value from slider
            confidence_threshold = float(self.slider.get())
            logger.debug(f"Confidence threshold: {confidence_threshold}")

            # filter info_list by confidence threshold
            filtered_info_list = info_filter(self.info_list, confidence_threshold)
            logger.debug(f"Filtered info list: {filtered_info_list}")

            # # draw bounding boxes
            # self.bbox_drawer(filtered_info_list)

            # update result label
            self.update_result_label(self.info_list, confidence_threshold)


    def clear_image(self):
        if self.top:
            self.panel.config(image='')


    def on_slider_change(self, value):
        logger.debug(f"Slider value changed: {value}")
        self.slidervalue.config(text=round(float(self.slider.get()),4))
        # self.bbox_drawer(self.info_list)
        # logger.debug(f"Drawn bounding boxes with Confidence threshold = {value}")
        try:
            self.update_result_label(self.info_list, value)
            logger.debug(f"Displayed results with Confidence threshold = {value}")
        except:
            pass

if __name__ == "__main__":
    app = ImageViewer()
    app.mainloop()
