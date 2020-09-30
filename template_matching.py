# template_matching.py

import cv2
import imutils
import numpy as np


class TemplateMatching:

    def __init__(self, plate_image, template):
        self.plate_image = plate_image.copy()
        self.template = template
        self.gray_plate_img = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
        self.info = None
        self.drew_img = None


    def find_position(self):
        # template will be single or double
        template_gray = cv2.cvtColor(self.template, cv2.COLOR_BGR2GRAY)
        template_canny = cv2.Canny(template_gray, 50, 200)
        (tH, tW) = template_canny.shape[:2]
        gray = self.gray_plate_img
        info = None

        # loop over the scales of the image ( multiply 2 ~ 0.1 on plate image)
        for scale in np.linspace(0.1, 2.0, 50)[::-1] :

            # resize the image according to the scale, and keep track
            # of the ratio of the resizing
            resized = imutils.resize(gray, width=int(gray.shape[1] * scale))
            r = gray.shape[1] / float(resized.shape[1])

            # if the resized image is smaller than the template, then break
            # from the loop
            if resized.shape[0] < tH or resized.shape[1] < tW:
                break
            
            # detect edges in the resized, grayscale image and apply template
            # matching to find the template in the image
            edged = cv2.Canny(resized, 50, 200)
            result = cv2.matchTemplate(edged, template_canny, cv2.TM_CCOEFF)
            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

            # if we have found a new maximum correlation value, then update
            # the bookkeeping variable
            if info is None or maxVal > info[0]:
                info = (maxVal, maxLoc, r, scale, tW, tH)

        self.info = info
        return info

    def get_start_pos(self):
        _, maxLoc, r, _, tW, tH  = self.info
        return ( int(maxLoc[0] * r) ), ( int(maxLoc[1] * r) )

    def get_end_pos(self):
        _, maxLoc, r, _, tW, tH  = self.info
        return ( int((maxLoc[0] + tW) * r) , int((maxLoc[1] + tH) * r))


    def draw_rectangle(self, image=None, rectangle_color=(0, 0, 255), thickness=2):
        if image is None:
            image = self.plate_image
        
        _, maxLoc, r, scale, tW, tH  = self.info

        (startX, startY) = self.get_start_pos()
        (endX, endY) = self.get_end_pos()

        self.drew_img = cv2.rectangle(image,(startX, startY), (endX,endY), rectangle_color, thickness )
        return self.drew_img
