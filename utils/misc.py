from datetime import datetime
from PIL import Image, ImageTk

def convert_to_datetime(time_str):
    return datetime.strptime(time_str, "%Y%m%d-%H%M%S")

def yolo_to_xyxy(yolo_coords, img_width, img_height):
    x, y, w, h = yolo_coords
    x1 = int((x - w/2) * img_width)
    y1 = int((y - h/2) * img_height)
    x2 = int((x + w/2) * img_width)
    y2 = int((y + h/2) * img_height)
    return (x1, y1, x2, y2)

def resize_to_fit(img, max_width, max_height):
    img_width, img_height = img.size
    
    # resize image so that the longest side fit in the window, while keeping the aspect ratio
    if img_width > img_height:
        ratio = max_width / img_width
    else:
        ratio = max_height / img_height

    new_width = int(img_width * ratio)
    new_height = int(img_height * ratio)

    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    return img, new_width, new_height

def info_filter(info_list, conf_threshold):

    conf_threshold = float(conf_threshold)
    
    filtered_info_list = []
    for info in info_list:
        if info[3] >= conf_threshold:
            filtered_info_list.append(info)
    return filtered_info_list