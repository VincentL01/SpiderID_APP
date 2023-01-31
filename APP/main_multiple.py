import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image
import time
from utils.utils import EVALUATION_V7 as eval
import os
import sys

def resource_path(relative_path):
    ### Get absolute path to resource, works for dev and for PyInstaller
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

landing_photo_path = resource_path('bin/landing_photo.jpg')

#[TODO] make a log file, where it stores img_name, weight used and result, so next time the same image is loaded, it will not run detection again

IMAGE_LOADED = False
MULTIPLE_IMG = False

def open_img():
    global img_path
    global img
    global img_label
    img_path = filedialog.askopenfilenames() # this is a tuple
    if len(img_path) = 0:
        pass
    elif len(img_path) = 1:
        img = ImageTk.PhotoImage(Image.open(img_path))
        img_label.config(image=img)
        IMAGE_LOADED = True
        button_process.config(state='normal')
    else:
        MULTIPLE_IMG = True
        IMAGE_LOADED = True
        button_process.config(state='normal')


def process_img():
    # this notify_label would replace the old notify_label
    if IMAGE_LOADED:
        notify_label.config(text='Image processing!', fg='red', font = notify_font)
    else:
        notify_label.config(text='No image selected!', fg='red', font= notify_font)

    # create a new window to display result
    result_window = tk.Toplevel(root)
    result_window.title('Result')
    result_window.geometry('400x400')
    result_label = tk.Label(result_window)
    result_label.config(font=('Arial', 20))
    result_label.pack()

    # create a new window to display image with bounding box
    bb_window = tk.Toplevel(root)
    bb_window.title('Image with bounding box')
    # geometry = img size + 50
    bb_window.geometry(f'{img.width()+50}x{img.height()+50}')
    bb_label = tk.Label(bb_window)
    bb_label.pack()

    # run detection
    runner = eval(img_path)
    try:
        genus_list, gender_list, confidence_list, img_withbb_path = runner.get_info()
        #[TODO] display img_name and which weight file is used
        display_text = ''
        for i in range(len(genus_list)):
            display_text += '\nGenus: {}\nGender: {}\nConfidence: {}\n'.format(genus_list[i], gender_list[i], confidence_list[i])
        result_label.config(text=display_text)
        bb_img = ImageTk.PhotoImage(Image.open(img_withbb_path))
        bb_label.config(image=bb_img)
        bb_label.image = bb_img
    except:
        result_label.config(text='No result')

    # # save result
    # result_label = tk.Label(result_window, text='Saving result...')
    # result_label.pack()

    notify_label.config(text='Image processed!', fg='green', font= notify_font)

    # if other buttons are clicked, result_window will be destroyed
    result_window.protocol("WM_DELETE_WINDOW", result_window.destroy)

root = tk.Tk()
root.title('Image Processing')

canvas = tk.Canvas(root, width=700, height=700, bg='lightsteelblue2', relief='raised')
canvas.pack()

notify_font = ('Arial', 12, 'bold', 'italic')
notify_label = tk.Label(root, text='Please select an image for detection!', fg='red', font=notify_font)
notify_label.pack()

img_label = tk.Label(canvas)
# load initial photo
img = ImageTk.PhotoImage(Image.open(landing_photo_path))
img_label.config(image=img)
# give it a thin black border
img_label.config(borderwidth=2, relief='solid')
img_label.pack()


browse_text = 'Select an image'
weight_text = 'Select weight file'
process_text = 'Process image'
quit_text = 'Quit'

button_width = max(len(browse_text), len(weight_text), len(process_text), len(quit_text))
button_fg = 'white'
button_bg = 'green'
button_font = ('helvetica', 12, 'bold')

# BUTTON to select image
button_browse = tk.Button(root, text=browse_text, padx = 10, pady = 5, command=open_img,
                        fg = button_fg, bg = button_bg, width = button_width, font = button_font)
button_browse.pack()

# BUTTON to select WEIGHT FILE
button_weight = tk.Button(root, text=weight_text, padx = 10, pady = 5,
                        fg = button_fg, bg = button_bg, width = button_width, font = button_font)
button_weight.pack()

# BUTTON to process image
button_process = tk.Button(root, text=process_text, padx = 10, pady = 5, command=process_img,
                        fg = button_fg, bg = button_bg,  width = button_width, font = button_font)
button_process.pack()

# if img has not been loaded, this button will be disabled
if IMAGE_LOADED == False:
    button_process.config(state='disabled')
else:
    button_process.config(state='normal')

# BUTTON to quit
button_quit = tk.Button(root, text=quit_text, padx = 10, pady = 5, command=root.quit,
                        fg = button_fg, bg = button_bg,  width = button_width, font = button_font)
button_quit.pack()

# define button size that fit the longest text
button_width = max(len(browse_text), len(weight_text), len(process_text), len(quit_text))



root.mainloop()

# Path: APP\main.py

## OLD VERSION ##


## GREEN VERSION ##
# # BUTTON to select image
# browse_button = tk.Button(root, text=browse_text, command=open_img, 
#                             bg=button_bg, fg=button_fg, font=('helvetica', 12, 'bold'))
# root.create_window(150, 150, window=browse_button, width=button_width*10)

# # BUTTON to select weight file
# weight_button = tk.Button(root, text=weight_text,
#                             bg=button_bg, fg=button_fg, font=('helvetica', 12, 'bold'))
# root.create_window(150, 250, window=weight_button, width=button_width*10)

# # BUTTON to process image
# process_button = tk.Button(root, text=process_text, command=process_img, 
#                             bg=button_bg, fg=button_fg, font=('helvetica', 12, 'bold'))
# root.create_window(150, 350, window=process_button, width=button_width*10)

# # BUTTON to quit
# quit_button = tk.Button(root, text=quit_text, command=root.destroy,
#                         bg='brown', fg=button_fg, font=('helvetica', 12, 'bold'))
# root.create_window(150, 450, window=quit_button, width=button_width*10)