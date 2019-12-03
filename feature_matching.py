# feature_matching.py

import cv2
import numpy as np

class FeatureMatching:

    def __init__(self, plate_img, template):
        self.plate_img = plate_img.copy()
        self.template = template.copy()
        self.matching_points = None
        self.sift_image = cv2.xfeatures2d.SIFT_create()
        self.drew_image = None

    
    def compute_image(self, image):
        # find the keypoints and descriptors with SIFT
        return self.sift_image.detectAndCompute(image, None)



    def find_points(self, threshold=0.6):
        template_img = self.template
        plate_img = self.plate_img
        
        # find the keypoints and descriptors with SIFT
        _, des1 = self.compute_image(template_img)
        _, des2 = self.compute_image(plate_img)

        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)

        # store all the good matches as per Lowe's ratio test.
        self.matching_points = []
        for m, n in matches:
            if m.distance < threshold * n.distance: # 0.6 is 
                self.matching_points.append(m)

        print(len(self.matching_points))
        return len(self.matching_points)


    def draw_feature_points(self, image=None, color=(0,255,0)):
        if image is None:
            image = self.plate_img
        
        # find the keypoints and descriptors with SIFT
        kp1,_ = self.compute_image(self.template)
        kp2,_ = self.compute_image(image)

        src_pts = np.float32([ kp1[m.queryIdx].pt for m in self.matching_points ]).reshape(-1, 1, 2)
        dst_pts = np.float32([ kp2[m.trainIdx].pt for m in self.matching_points ]).reshape(-1, 1, 2)
        M, mask = cv2.findHomography(src_pts, dst_pts)

        matchesMask = None

        h, w, d = self.template.shape
        pts = np.float32([ [0, 0], [0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
        dst = cv2.perspectiveTransform(pts, M)

        polyline_image = cv2.polylines(image, [np.int32(dst)], False, 255, 3, cv2.LINE_AA)

        draw_params = dict(matchColor = color, # draw matches in green color
                       singlePointColor= None, # draw only inliers
                       flags= 0)
        self.drew_image = cv2.drawMatches(self.template, kp1, polyline_image, kp2, self.matching_points, None, **draw_params)
        
        return self.drew_image