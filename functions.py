# Call packages

import requests
import base64
import os
import numpy as np
import cv2
import math

def crop_plate_img(binary_image,img):
    # Secret key from ALPR site
    SECRET_KEY = 'sk_3ad45d755d67600b8fcb0a78'

    # Encode image
    img_base64 = base64.b64encode(binary_image)

    # search on API from Photo
    url = 'https://api.openalpr.com/v2/recognize_bytes?recognize_vehicle=1&country=kor&secret_key=%s' % (SECRET_KEY)
    r = requests.post(url, data=img_base64)
    json_data = r.json()
    x1_co = json_data['results'][0]['coordinates'][0]['x']
    y1_co = json_data['results'][0]['coordinates'][0]['y']
    x2_co = json_data['results'][0]['coordinates'][2]['x']
    y2_co = json_data['results'][0]['coordinates'][2]['y']

    # Crop plate from Original Image
    # error point will be +- 20 by y-axis
    cropped_img = img[y1_co - 20:y2_co + 20, x1_co: x2_co]

    return cropped_img


def check_position_of_logos(first_logo, second_logo, threshold=20):
    (startX_1, startY_1) = first_logo.get_start_pos()
    (startX_2, startY_2) = second_logo.get_start_pos()
    x_dif = abs(startX_1 - startX_2)
    y_dif = abs(startY_1 - startY_2)

    if x_dif < threshold and y_dif < threshold:
        return True
    return False


def count_color(plate_image, hsv_img, min_range, max_range):
    color_mask = cv2.inRange(hsv_img, min_range, max_range)
    color = cv2.bitwise_and(plate_image, plate_image, mask=color_mask)
    color_count = np.count_nonzero(color)
    return color_count


def is_image_valid(image_path):
    KB = int(math.floor(os.path.getsize(image_path) / 1024))

    # if image size is smaller than 300KB, print this
    if KB < 30:
        result = "이미지 크기가 {}KB 입니다. 높은 화질의 이미지를 올려주세요.".format(KB)
        print(result)
        return False
    return True


def detect_plate_color(cropped_plate_img):
    plate = cropped_plate_img.copy()
    hsv_img = cv2.cvtColor(plate, cv2.COLOR_BGR2HSV)
    count_blue = count_color(plate, hsv_img, (85, 80, 20), (125, 255, 255))
    count_green = count_color(plate, hsv_img, (40, 80, 20), (80, 255, 255))
    count_white = count_color(plate, hsv_img, (0, 0, 170), (131, 255, 255))
    count_yellow = count_color(plate, hsv_img, (15, 80, 20), (35, 255, 255))

    value_list = [count_blue, count_green, count_white, count_yellow]  # each number of points will be list.

    max_value = max(value_list)  # Find max count in Value list
    index = value_list.index(max_value)  # Find Index in Value list
    if index is 0:
        return True
    return False

