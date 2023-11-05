import numpy as np
import cv2
from mss import mss
from screeninfo import get_monitors
import pytesseract
from pytesseract import Output
import time
import pyautogui as pagi

# import tesseract, download it from github and install it to this path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# this block of code gets the monitor info and formats it into a dictionary
formatted_info = {}
for m in get_monitors():
    monitor_info = str(m)
    monitor_info = monitor_info.replace('Monitor(', ' ')
    monitor_info = monitor_info.replace(')', '')
    monitor_info = monitor_info.replace('\\', '')
    monitor_info = monitor_info.replace('.', '')
    monitor_info = monitor_info.replace('=', ':')
    info = [i + '' for i in monitor_info.split(',')]
    for j in info:
        j = j.lstrip()
        formatted_info[j[0:j.index(':')]] = j[j.index(':') + 1:]
    for k in formatted_info:
        try:
            formatted_info[k] = int(formatted_info[k])
        except ValueError:
            continue
    # print(formatted_info)

# a function to help identify the screenshot bounds and other
# useful info like button placements if pytesseract doesn't work
get_screenshot_bounds = False  # comment to true
while get_screenshot_bounds:
    print(pagi.position())

# scalers to limit region of interest to perform OCR, useful when windows
# are snapped to be next to each other
scaler_width = 2
scaler_height = 1
# set parameters of screenshot to take, this can be customised too
screenshot_bounds = {'top': formatted_info['x'], 'left': formatted_info['y'],
                     'width': int(formatted_info['width'] / scaler_width),
                     'height': int(formatted_info['height'] / scaler_height)}

# using mss
sct = mss()
# these 2 params are to resize the cv2 window
window_width_resizer = 2
window_height_resizer = 1
# minimum confidence of detection
min_conf = 5
# initialise these bbox values
x, y, w, h = 0, 0, 0, 0
# boolean to toggle whether cv2 window is shown,
# note that it makes the programme run slower so use
# it for testing only
show_image = False
# loop sleep to control speed of detection loop
loop_sleep_time = 0
# have this delay in the loop to prevent mouse lock
click_sleep_time = 3

while True:
    # take a screenshot
    sct_img = sct.grab(screenshot_bounds)
    # convert it to image
    image = np.array(sct_img)
    # apply grayscale and other  image processing here
    gray = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
    # print('========================================')
    # use pytesseract to gather all data in screenshot
    data = pytesseract.image_to_data(gray, output_type=Output.DICT)
    n_boxes = len(data['level'])
    # print(data) # this is for debugging purposes
    for i in range(n_boxes):
        # check through the lists for words you want to detect
        if data['text'][i] == 'Skills' and data['conf'][i] > min_conf:
            # get the bbox data
            (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
            # print(x, y, w, h) # for debugging
            # adjust the position of where the cursor is going to click in the centre of the bbox
            xloc = (x + w / 2)
            yloc = (y + h / 2)
            # print(xloc, yloc)
            # move the cursor to perform a click or anything else
            try:
                pagi.moveTo(xloc, yloc, 0.3)
                pagi.leftClick()
                pagi.moveTo(xloc, yloc - 276, 0.3)
                pagi.leftClick()
                # have this delay in the loop to prevent mouse lock
                time.sleep(click_sleep_time)
            except:
                continue

    # this code is to check that the detection is doing its thing by
    # creating a window and showing the bbox around the text
    if show_image is True:
        cv2.rectangle(gray, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.namedWindow('screen', cv2.WINDOW_FREERATIO)
        cv2.resizeWindow('screen', int(formatted_info['width'] / window_width_resizer),
                         int(formatted_info['height'] / window_height_resizer))
        cv2.imshow('screen', gray)
        if (cv2.waitKey(1) & 0xFF) == ord('q'):
            cv2.destroyAllWindows()
            break

    time.sleep(loop_sleep_time)
