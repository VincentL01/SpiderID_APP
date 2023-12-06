import os
# os.system('pip install -r requirements.txt')

import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from PIL import ImageTk, Image
import time
import sys
from googletrans import Translator
import pinyin
from pathlib import Path
import threading

from utils.utils import EVALUATION_V7 as eval
from utils.imageviewer import ImageViewer

import logging
from colorlog import ColoredFormatter

logger = logging.getLogger(__name__)

# save log to Log/log.txt
Path('Log').mkdir(parents=True, exist_ok=True)

# Configure the logging module
log_file = 'Log/log.txt'

# Define the log format with colors
log_format = "%(asctime)s %(log_color)s%(levelname)-8s%(reset)s %(message)s"

# Create a formatter with colored output
formatter = ColoredFormatter(log_format)

# Create a file handler to save logs to the file
file_handler = logging.FileHandler(log_file, mode='a')  # Set the mode to 'a' for append
file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(message)s"))

# Create a stream handler to display logs on the console with colored output
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

# Get the root logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(stream_handler)


def resource_path(relative_path):
    ### Get absolute path to resource, works for dev and for PyInstaller
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

landing_photo_path = resource_path('bin/support/landing_photo.png')

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WEIGHT_DIR = os.path.join(ROOT_PATH, 'bin', 'weights')

PROCESSED_DIR = os.path.join(ROOT_PATH, 'processed')
if not os.path.isdir(PROCESSED_DIR):
    os.mkdir(PROCESSED_DIR)

#[TODO] make a log file, where it stores img_name, weight used and result, so next time the same image is loaded, it will not run detection again

DEFAULT_WEIGHT = True

def inChinese(file_name):
    if any(u'\u4e00' <= char <= u'\u9fff' for char in file_name):
        return True
    else:
        return False

def pinyinize(file_name):
    # replace chinese characters with pinyin
    for char in file_name:
        if u'\u4e00' <= char <= u'\u9fff':
            file_name = file_name.replace(char, pinyin.get(char, format='strip', delimiter='_'))
    return file_name

def translated(chinese_name):
    # use googletrans to translate Chinese to English
    translator = Translator()
    translated_name = translator.translate(chinese_name, dest='en').text
    translated_name = translated_name.replace(' ', '_')
    if inChinese(translated_name):
        #replace chinese characters with their pinyin
        translated_name = pinyinize(translated_name)
    return translated_name

def available_name(file_dir, file_name):
    i = 0
    while os.path.exists(os.path.join(file_dir, file_name)):
        i += 1
        file_name = file_name.split('.')[0] + '_' + str(i) + '.jpg'

    return file_name

def choose_weight():
    global weight_path
    global DEFAULT_WEIGHT

    weight_path = filedialog.askopenfilename(initialdir=DEFAULT_WEIGHT_DIR, title="Select weight file", filetypes=(("weights files", "*.pt"), ("all files", "*.*")))
    if weight_path:
        weight_label.config(text='Weight file selected: {}'.format(os.path.basename(weight_path)))
        DEFAULT_WEIGHT = False
        logger.info("Weight file selected: {}".format(os.path.basename(weight_path)))
    else:
        logger.info("No weight file selected, using default weight")
        pass

def image_resizer(input_img, size_limit):
    if input_img.width > size_limit or input_img.height > size_limit:
        if input_img.width > input_img.height:
            input_img = input_img.resize((size_limit, int(input_img.height*size_limit/input_img.width)), Image.Resampling.ANTIALIAS)
        else:
            input_img = input_img.resize((int(input_img.width*size_limit/input_img.height), size_limit), Image.Resampling.ANTIALIAS)
    return input_img
    

def process_img():
    SINGLE_IMG = True

    img_path = filedialog.askopenfilenames(parent=root, title='Select images', filetypes=(("jpg files", "*.jpg"), ("all files", "*.*")))

    # if only one image is selected
    if len(img_path) == 0:
        return
    elif len(img_path) == 1:
        if not os.path.isdir('processed'):
            os.mkdir('processed')
        print('Loaded single image, path: {}'.format(img_path))
        img_path = img_path[0]
        # convert all images to jpg
        img_name = os.path.basename(img_path).split('.')[0]
        # replace all spaces with _
        img_name = img_name.replace(' ', '_')
        if inChinese(img_name):
            img_name = available_name('processed', translated(img_name))
        img = Image.open(img_path)
        img = img.convert('RGB')
        img.save('processed/{}.jpg'.format(img_name))
        img_path = 'processed/{}.jpg'.format(img_name)

        # # resize image to the highest dimension of 500, while keeping the aspect ratio
        # w, h = img.size
        # if w > h:
        #     display_img = img.resize((500, int(h / w * 500)))
        # else:
        #     display_img = img.resize((int(w / h * 500), 500))
        # display_img = ImageTk.PhotoImage(display_img)
        # img_label.config(image=display_img)

        img = ImageTk.PhotoImage(Image.open(img_path))
        IMAGE_LOADED = True
        button_process.config(state='normal')
    else:
        print('Loaded multiple images..')
        SINGLE_IMG = False
        # if multiple images are selected
        # copy all selected images to a temporary folder 
        temp_dir = os.path.join(ROOT_PATH, 'temp')
        if not os.path.exists(temp_dir):
            os.mkdir(temp_dir)
        else:
            for file in os.listdir(temp_dir):
                os.remove(os.path.join(temp_dir, file))
        #     for file in os.listdir(temp_dir):
        #         # move all files in temp_dir to processed folder
        #         try:
        #             os.rename(os.path.join(temp_dir, file), os.path.join('processed', file))
        #         except FileExistsError:
        #             os.remove(os.path.join('processed', file))
        #             os.rename(os.path.join(temp_dir, file), os.path.join('processed', file))
        for im_path in img_path:
            img_name = os.path.basename(im_path).split('.')[0]
            # replace all spaces with _
            img_name = img_name.replace(' ', '_')
            if inChinese(img_name):
                img_name = available_name(temp_dir, translated(img_name))
            img = Image.open(im_path)
            img = img.convert('RGB')
            img.save(os.path.join(temp_dir, '{}.jpg'.format(img_name)))

        print('All images are copied to temp folder: {}'.format(temp_dir))
        notify_label.config(text = 'Multple images selected!', fg='red', font = notify_font)
        IMAGE_LOADED = True
        button_process.config(state='normal')
        img_path = temp_dir

    # this notify_label would replace the old notify_label
    if img_path:
        notify_label.config(text='Image processing!', fg='red', font = notify_font)
    else:
        notify_label.config(text='No image selected!', fg='red', font= notify_font)

    # create a new window to display result
    result_window = tk.Toplevel(root)
    result_window.title('Result')
    result_label = tk.Label(result_window)
    result_label.config(font=('Arial', 20))
    result_label.pack()

    # create a new window to display image with bounding box
    bb_window = tk.Toplevel(root)
    bb_window.title('Image with bounding box')
    # geometry = img size + 50
    bb_label = tk.Label(bb_window)
    bb_label.pack()

    # run detection
    if DEFAULT_WEIGHT == False:
        logger.debug("Using custom weight file: {}".format(weight_path))
        runner = eval(img_path, weight_path)
    else:
        logger.debug("Using default weight file")
        runner = eval(img_path)
    if SINGLE_IMG:
        logger.info('Running detection on single image: {}'.format(img_path))

        _, info_list, img_withbb_path = runner.get_info_single()

        # if no bounding box is detected, show the original image
        if info_list == []:
            logger.debug('No bounding box detected!')
            img_withbb_path = img_path
        #[TODO] display img_name and which weight file is used
        
        logger.info('Display image saved to: {}'.format(img_withbb_path))

        bb_img = Image.open(img_withbb_path)
        bb_img = bb_img.convert('RGB')
        # if the image is too big, resize it, highest dimension = 800, keep aspect ratio
        bb_img = image_resizer(bb_img, 800)
        # if bb_img.width > 800 or bb_img.height > 800:
        #     if bb_img.width > bb_img.height:
        #         bb_img = bb_img.resize((800, int(bb_img.height*800/bb_img.width)), Image.ANTIALIAS)
        #     else:
        #         bb_img = bb_img.resize((int(bb_img.width*800/bb_img.height), 800), Image.ANTIALIAS)
        bb_img = ImageTk.PhotoImage(bb_img)
        bb_window.geometry(f'{bb_img.width()+50}x{bb_img.height()+50}')
        bb_label.config(image=bb_img)
        bb_label.image = bb_img

        display_text = ''
        if runner.weight_type == 'WG':
            for i in range(len(info_list)):
                logger.debug(f"Genus:{info_list[i][0]}, type = {type(info_list[i][0])}")
                logger.debug(f"Gender:{info_list[i][1]}, type = {type(info_list[i][1])}")
                logger.debug(f"Confidence:{info_list[i][2]}, type = {type(info_list[i][2])}")
                display_text += '\nGenus: {}\nGender: {}\nConfidence: {}\n'.format(info_list[i][0], info_list[i][1], round(info_list[i][2],2))
        elif runner.weight_type == 'NG':
            for i in range(len(info_list)):
                logger.debug(f"Genus:{info_list[i][0]}, type = {type(info_list[i][0])}")
                logger.debug(f"Gender:{info_list[i][1]}, type = {type(info_list[i][1])}")
                logger.debug(f"Confidence:{info_list[i][2]}, type = {type(info_list[i][2])}")
                display_text += '\nGenus: {}\nConfidence: {}\n'.format(info_list[i][0], round(info_list[i][2],2))
        # adjust the height of result_label to match the height if bb_window
        result_window.geometry(f'400x{bb_img.height()+50}')
        result_label.config(text=display_text)

    else:
        logger.info("Multiple images detected")
        csv_out, _ = runner.get_info_multiple()
        display_text = 'Multiple images detected \n'
        display_text += 'Result saved to {}'.format(csv_out)
        result_label.config(text=display_text)
        logger.info("Result saved to {}".format(csv_out))

    # except Exception as e:
    #     result_label.config(text='Error occured: {}'.format(e))

    # # save result
    # result_label = tk.Label(result_window, text='Saving result...')
    # result_label.pack()

    for file in os.listdir(temp_dir):
        # move all files in temp_dir to processed folder
        try:
            os.rename(os.path.join(temp_dir, file), os.path.join('processed', file))
        except FileExistsError:
            os.remove(os.path.join('processed', file))
            os.rename(os.path.join(temp_dir, file), os.path.join('processed', file))

    notify_label.config(text='Image processed!', fg='green', font= notify_font)

    # if other buttons are clicked, result_window will be destroyed
    result_window.protocol("WM_DELETE_WINDOW", result_window.destroy)

def process_video():
    global video_path
    global DEFAULT_WEIGHT

    logger.info("Processing video...")

    # create a new window to display result
    result_window = tk.Toplevel(root)
    result_window.title('Result')

    result_label = ttk.Label(result_window)
    result_label.config(font=('Arial', 20))
    result_label.grid(row=0, column=0, sticky='ew')

    DEFAULT_VIDEO_DIR = resource_path('test')
    video_path = filedialog.askopenfilename(initialdir=DEFAULT_VIDEO_DIR, title="Select video file", filetypes=(("video files", "*.mp4"), ("all files", "*.*")))
    if video_path:
        notify_label.config(text='Video selected!', fg='red', font= notify_font)
        if DEFAULT_WEIGHT:
            logger.debug("Using custom weight file: {}".format(weight_path))
            print('Evaluating video with default weight file')
            video_runner = eval(video_path)
        else:
            logger.debug("Using default weight file")
            print('Evaluating video with weight file: {}'.format(weight_path))
            video_runner = eval(video_path, weight_path)

        result_dict, total_frame = video_runner.get_info_video()
        display_text = ''
        if video_runner.weight_type == 'WG':
            for key in result_dict:
                display_text += '\nGenus: {} - Gender: {}\nSensitivity: {}/{}\nConfidence: {}\n'.format(key[0], key[1], result_dict[key]['count'], total_frame, round(result_dict[key]['confidence'],2))
        elif video_runner.weight_type == 'NG':
            for key in result_dict:
                display_text += '\nGenus: {}\nSensitivity: {}/{}\nConfidence: {}\n'.format(key[0], result_dict[key]['count'], total_frame, round(result_dict[key]['confidence'],2))
        result_label.config(text=display_text)
        # expand the window to fit the text
        result_window.geometry(f'500x{result_label.winfo_height()+200}')
        # change the appear location of the window
        result_window.geometry("+{}+{}".format(root.winfo_x()+root.winfo_width(), root.winfo_y()))

        notify_label.config(text='Video processed!', fg='green', font= notify_font)

def view_img():
    app = ImageViewer()
    app.mainloop()

def exit_program():
    root.destroy()


### GUI ###

root = tk.Tk()
root.title('SpiderID APP -- Version 1.0.2')

canvas = tk.Canvas(root, width=700, height=700, bg='lightsteelblue2', relief='raised')
canvas.pack()

notify_font = ('Arial', 12, 'bold', 'italic')
notify_label = tk.Label(root, text='Please select an image for detection!', fg='red', font=notify_font)
notify_label.pack()

weight_label = tk.Label(root, text='Default weight file loaded, click Select weight to change', fg='black', font=('Arial', 12))
weight_label.pack()

img_label = tk.Label(canvas)
# load initial photo
img = Image.open(landing_photo_path)
# resize image to make large dimension is 612, small dimension is scaled accordingly
try:
    if img.width > img.height:
        img = img.resize((612, int(img.height*612/img.width)), Image.ANTIALIAS)
    else:
        img = img.resize((int(img.width*612/img.height), 612), Image.ANTIALIAS)
except:
    logger.warning("Image ANTIALIAS failed, using LANCZOS instead")
    if img.width > img.height:
        img = img.resize((612, int(img.height * 612 / img.width)), Image.Resampling.LANCZOS)
    else:
        img = img.resize((int(img.width * 612 / img.height), 612), Image.Resampling.LANCZOS)
img = ImageTk.PhotoImage(img)
img_label.config(image=img)
# give it a thin black border
img_label.config(borderwidth=2, relief='solid')
img_label.pack()

texts = {
    'weight_text' : 'Select weight file',
    'process_text' : 'Process image(s)',
    'video_text' : 'Process video',
    'video_text_local' : 'From playback files',
    'video_text_stream' : 'From live feed',
    'view history' : 'View History',
    'quit_text' : 'Quit'
}

button_width = max(len(texts['weight_text']), len(texts['process_text']), len(texts['quit_text']))
button_fg = 'white'
button_bg = 'green'
button_font = ('helvetica', 12, 'bold')


# BUTTON to select WEIGHT FILE
button_weight = tk.Button(root, text=texts['weight_text'], padx = 10, pady = 5, command=choose_weight,
                        fg = button_fg, bg = button_bg, width = button_width, font = button_font)
button_weight.pack()

# BUTTON to process image
button_process = tk.Button(root, text=texts['process_text'], padx = 10, pady = 5, command=process_img,
                        fg = button_fg, bg = button_bg,  width = button_width, font = button_font)
button_process.pack()

# BUTTON to process video
button_video = tk.Button(root, text=texts['video_text'], padx = 10, pady = 5, command=process_video,
                        fg = button_fg, bg = button_bg,  width = button_width, font = button_font)
button_video.pack()

# BUTTON to view processed images
button_view = tk.Button(root, text=texts['view history'], padx = 10, pady = 5, command=view_img,
                        fg = button_fg, bg = button_bg,  width = button_width, font = button_font)
button_view.pack()


# BUTTON to quit
button_quit = tk.Button(root, text=texts['quit_text'], padx = 10, pady = 5, command=exit_program,
                        fg = button_fg, bg = button_bg,  width = button_width, font = button_font)
button_quit.pack()


root.mainloop()
