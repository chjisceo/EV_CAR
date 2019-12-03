# Call packages

import os
from flask import Flask, request, render_template, send_from_directory, send_file, make_response
import cv2
import functions as func
from feature_matching import FeatureMatching
from template_matching import TemplateMatching
import time
### remove cache
from functools import wraps,update_wrapper
from datetime import datetime

def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-control'] = 'no-store, no-cache, must-revalidate, post-check=0,pre-check =0, max-age =0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response
    return update_wrapper(no_cache,view)
###
__author__ = 'HarryCho'

app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/index")
def home():
    return render_template("index.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/testing", methods=["GET"])
def upload_get():
    return render_template("upload.html")


@app.route("/testing", methods=["POST"])
@nocache
def testing():
    target = os.path.join(APP_ROOT, 'images/')
    print(target)
    if not os.path.isdir(target):
        os.mkdir(target)
    else:
        print("Couldn't create upload directory: {}".format(target))
        print(request.files.getlist("file"))

    for upload in request.files.getlist("file"):
        print(upload)
        print("{} is the file name".format(upload.filename))
        filename = upload.filename
        destination = "/".join([target, filename])
        print ("Accept incoming file:", filename)
        print ("Save it to:", destination)
        upload.save(destination)

    start = datetime.now()
    start_time_data = time.strftime("%Y/%m/%d %H:%M:%S")

    # image_path = 'images/taxi2.jpg'
    image_path = 'images/' + filename
    img = cv2.imread(image_path)
    single_template = cv2.imread('static/img/template-img/single.png')
    double_template = cv2.imread('static/img/template-img/double.png')
    feature_template = cv2.imread('static/img/template-img/feature.png')
    is_ev_car = 0
    is_general_car = 0
    cropped_plate_img = None

    with open(image_path, 'rb') as binary_image:
        cropped_plate_img = func.crop_plate_img(binary_image.read(), img)

    if cropped_plate_img is None:
        print('Error while cropping plate img')
        return
    #gray_plate_img = cv2.cvtColor(cropped_plate_img, cv2.COLOR_BGR2GRAY)

    # Template Matching plate with one small evcar shape image
    single_template_matching = TemplateMatching(cropped_plate_img, single_template)
    single_template_matching.find_position()

    # Template Matching plate with special EV mark from left part of plate
    double_template_matching = TemplateMatching(cropped_plate_img, double_template)
    double_template_matching.find_position()

    # check position of 2 logos.
    if func.check_position_of_logos(single_template_matching, double_template_matching) is False:
        is_general_car += 1
        print('no EV car (logos not matching)')
    else:
        is_ev_car += 1

    # draw rectangle in Original image
    first_img = single_template_matching.draw_rectangle()
    second_img = double_template_matching.draw_rectangle(first_img)

    # Feature matching by 3 logos template.
    feature_template_matching = FeatureMatching(cropped_plate_img, feature_template)

    # if there is no points of feature matching.plus 1 point(is_general_car)
    if feature_template_matching.find_points() < 1:
        is_general_car += 1
        print('no EV car (no feature matching detected)')
    else:
        is_ev_car += 1 # if there are some points, plus 1 point

    # Detect which color of plate
    # if it is True : is_ev_car, else is_general_car
    color_of_plate = func.detect_plate_color(cropped_plate_img)
    if color_of_plate is not True:
        is_general_car += 1
    else:
        is_ev_car += 1

    print("is_general_car : {}\nis_ev_car : {}".format(is_general_car, is_ev_car))
    if is_ev_car >= 2:
        car_type = 'Electronic Vehicle'
        feature_point_img = feature_template_matching.draw_feature_points()

        # Set image as max width and same height
        combined_h = second_img.shape[0]
        combined_w = max(second_img.shape[1], feature_point_img.shape[1])
        new_size = (combined_w, combined_h)

        # Draw feature matching points on original image
        second_img = cv2.resize(second_img, new_size)
        feature_point_img = cv2.resize(feature_point_img, new_size)
        # Rectangle template image + feature matching image as vertical way
        result_plate_img = cv2.vconcat([second_img, feature_point_img])
    else:
        car_type = 'General Vehicle'
        result_plate_img = cropped_plate_img

    cv2.imwrite('static/results/saved.jpg',result_plate_img)
    processing = datetime.now() - start
    end_time_data = time.strftime("%Y/%m/%d %H:%M:%S")
    print(processing)

    return render_template("complete.html", image_name=filename, car=car_type, processing=processing, result_img=result_plate_img, start_time_data=start_time_data, end_time_data=end_time_data)

    # cv2.imshow('Original Image', img)
    # cv2.imshow('output', result_plate_img)
    # cv2.waitKey()

@app.route('/testing/<filename>')
def send_image(filename):
    return send_from_directory("images", filename)


if __name__ == "__main__":
    app.run(port=4555, debug=True)

