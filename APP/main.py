import os
# os.system('pip install -r requirements.txt')

import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
import time
from utils.utils import EVALUATION_V7 as eval
import sys
from googletrans import Translator
import pinyin



def resource_path(relative_path):
    ### Get absolute path to resource, works for dev and for PyInstaller
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

landing_photo_path = resource_path('bin/landing_photo.jpg')

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
DEFAULT_WEIGHT_DIR = os.path.join(ROOT_PATH, 'bin', 'weights')

#[TODO] make a log file, where it stores img_name, weight used and result, so next time the same image is loaded, it will not run detection again

IMAGE_LOADED = False
DEFAULT_WEIGHT = True
SINGLE_IMG = True

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

def open_img():
    global img_path
    global img
    global img_label
    global display_img
    global SINGLE_IMG
    global IMAGE_LOADED

    img_path = filedialog.askopenfilenames(parent=root, title='Select images', filetypes=(("jpg files", "*.jpg"), ("all files", "*.*")))

    # if only one image is selected
    if len(img_path) == 0:
        pass
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

        # resize image to the highest dimension of 500, while keeping the aspect ratio
        w, h = img.size
        if w > h:
            display_img = img.resize((500, int(h / w * 500)))
        else:
            display_img = img.resize((int(w / h * 500), 500))
        display_img = ImageTk.PhotoImage(display_img)
        img_label.config(image=display_img)

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
                # move all files in temp_dir to processed folder
                try:
                    os.rename(os.path.join(temp_dir, file), os.path.join('processed', file))
                except FileExistsError:
                    os.remove(os.path.join('processed', file))
                    os.rename(os.path.join(temp_dir, file), os.path.join('processed', file))
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

def choose_weight():
    global weight_path
    global DEFAULT_WEIGHT

    weight_path = filedialog.askopenfilename(initialdir=DEFAULT_WEIGHT_DIR, title="Select weight file", filetypes=(("weights files", "*.pt"), ("all files", "*.*")))
    if weight_path:
        weight_label.config(text='Weight file selected: {}'.format(os.path.basename(weight_path)))
        DEFAULT_WEIGHT = False
    else:
        pass

def process_img():
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
        runner = eval(img_path, weight_path)
    else:
        runner = eval(img_path)
    if SINGLE_IMG:
        _, info_list, img_withbb_path = runner.get_info_single()

        # if no bounding box is detected, show the original image
        if info_list == []:
            img_withbb_path = img_path
        #[TODO] display img_name and which weight file is used
        
        bb_img = Image.open(img_withbb_path)
        bb_img = bb_img.convert('RGB')
        # if the image is too big, resize it, highest dimension = 800, keep aspect ratio
        if bb_img.width > 800 or bb_img.height > 800:
            if bb_img.width > bb_img.height:
                bb_img = bb_img.resize((800, int(bb_img.height*800/bb_img.width)), Image.ANTIALIAS)
            else:
                bb_img = bb_img.resize((int(bb_img.width*800/bb_img.height), 800), Image.ANTIALIAS)
        bb_img = ImageTk.PhotoImage(bb_img)
        bb_window.geometry(f'{bb_img.width()+50}x{bb_img.height()+50}')
        bb_label.config(image=bb_img)
        bb_label.image = bb_img

        display_text = ''
        for i in range(len(info_list)):
            display_text += '\nGenus: {}\nGender: {}\nConfidence: {}\n'.format(info_list[i][0], info_list[i][1], round(info_list[i][2],2))
        # adjust the height of result_label to match the height if bb_window
        result_window.geometry(f'400x{bb_img.height()+50}')
        result_label.config(text=display_text)

    else:
        csv_out, _ = runner.get_info_multiple()
        display_text = 'Multiple images detected \n'
        display_text += 'Result saved to {}'.format(csv_out)
        result_label.config(text=display_text)

    # except Exception as e:
    #     result_label.config(text='Error occured: {}'.format(e))

    # # save result
    # result_label = tk.Label(result_window, text='Saving result...')
    # result_label.pack()

    notify_label.config(text='Image processed!', fg='green', font= notify_font)

    # if other buttons are clicked, result_window will be destroyed
    result_window.protocol("WM_DELETE_WINDOW", result_window.destroy)

def process_video():
    global video_path
    global DEFAULT_WEIGHT

    # create a new window to display result
    result_window = tk.Toplevel(root)
    result_window.title('Result')
    result_label = tk.Label(result_window)
    result_label.config(font=('Arial', 20))
    result_label.pack()

    DEFAULT_VIDEO_DIR = resource_path('test')
    video_path = filedialog.askopenfilename(initialdir=DEFAULT_VIDEO_DIR, title="Select video file", filetypes=(("video files", "*.mp4"), ("all files", "*.*")))
    if video_path:
        notify_label.config(text='Video selected!', fg='red', font= notify_font)
        if DEFAULT_WEIGHT:
            print('Evaluating video with default weight file')
            video_runner = eval(video_path)
        else:
            print('Evaluating video with weight file: {}'.format(weight_path))
            video_runner = eval(video_path, weight_path)

        percentage, avg_confidence = video_runner.get_info_multiple()
        print('Percentage of correct detection: {}'.format(percentage))
        print('Average confidence: {}'.format(avg_confidence))


root = tk.Tk()
root.title('Image Processing')

canvas = tk.Canvas(root, width=700, height=700, bg='lightsteelblue2', relief='raised')
canvas.pack()

notify_font = ('Arial', 12, 'bold', 'italic')
notify_label = tk.Label(root, text='Please select an image for detection!', fg='red', font=notify_font)
notify_label.pack()

weight_label = tk.Label(root, text='Default weight file loaded, click Select weight to change', fg='black', font=('Arial', 12))
weight_label.pack()

img_label = tk.Label(canvas)
# load initial photo
img = ImageTk.PhotoImage(Image.open(landing_photo_path))
img_label.config(image=img)
# give it a thin black border
img_label.config(borderwidth=2, relief='solid')
img_label.pack()

texts = {
    'browse_text' : 'Select image(s)',
    'weight_text' : 'Select weight file',
    'process_text' : 'Process image',
    'video_text' : 'Process video',
    'video_text_local' : 'From playback files',
    'video_text_stream' : 'From live feed',
    'quit_text' : 'Quit'
}

button_width = max(len(texts['browse_text']), len(texts['weight_text']), len(texts['process_text']), len(texts['quit_text']))
button_fg = 'white'
button_bg = 'green'
button_font = ('helvetica', 12, 'bold')

# BUTTON to select image
button_browse = tk.Button(root, text=texts['browse_text'], padx = 10, pady = 5, command=open_img,
                        fg = button_fg, bg = button_bg, width = button_width, font = button_font)
button_browse.pack()

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

# if img has not been loaded, this button will be disabled
if IMAGE_LOADED == False:
    button_process.config(state='disabled')
else:
    button_process.config(state='normal')

# BUTTON to quit
button_quit = tk.Button(root, text=texts['quit_text'], padx = 10, pady = 5, command=root.quit,
                        fg = button_fg, bg = button_bg,  width = button_width, font = button_font)
button_quit.pack()



root.mainloop()
