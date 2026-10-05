"""
Marker Detector — Computer Vision Recruitment Task

Implement the MarkerDetector class and the utility functions below.
See README.md for full task description.
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple
from math import atan2

class MarkerDetector:
    """
    Detects colored markers in images using classical computer vision techniques.

    Each detection is a dictionary with the following fields:
        - 'color':  str           — one of 'red', 'green', 'blue', 'yellow'
        - 'bbox':   (x, y, w, h) — bounding rectangle of the detected contour
        - 'center': (cx, cy)     — center coordinates of the bounding box
        - 'area':   float        — area of the detected contour

    Optionally, if you attempt the bonus task:
        - 'shape':  str          — one of 'circle', 'triangle', 'rectangle'
    """

    # Define HSV color ranges for each target color.
    # Each entry maps a color name to a list of (lower_bound, upper_bound) tuples.
    # Use np.array([H, S, V]) for bounds. OpenCV uses H: 0-179, S: 0-255, V: 0-255.
    #
    # Hint: Red wraps around the hue spectrum (both ~0-10 and ~170-179 are red),
    # so you will likely need TWO ranges for red.
    COLOR_TH = 50
    HUE_RANGES = {
        # Hue in HSV
        # Both extremes included
        "blue":   [100, 130],
        "green":  [40, 80],
        "red1":   [170, 179],
        "red2":   [0, 10],
        "yellow": [25, 35]
    }

    
    # Minimum contour area to consider (filters noise)
    min_area = 500

    def inHueRange(self, image, hue_str):
        # image is GBR, we convert it to HVS
        image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        hsv_low = lambda l: np.array([l, 100, 100])
        hsv_high = lambda h: np.array([h, 255, 255])

        if hue_str == "red":
            res1 = cv2.inRange(image, hsv_low(self.HUE_RANGES["red1"][0]), hsv_high(self.HUE_RANGES["red1"][1]))
            res2 = cv2.inRange(image, hsv_low(self.HUE_RANGES["red2"][0]), hsv_high(self.HUE_RANGES["red2"][1]))
            return cv2.bitwise_or(res1, res2)
        
        return cv2.inRange(image, hsv_low(self.HUE_RANGES[hue_str][0]), hsv_high(self.HUE_RANGES[hue_str][1]))

    def getShapeName(self, perimeter) -> str:
        # Either rectangle, triangle or circle
        #perimeter = np.concatenate([perimeter, perimeter[:2]], axis=0)
        n = len(perimeter)
        win = 5
        path = []
        for i in range(n):
            curr_p = perimeter[i][0]
            next_p = perimeter[(i+win)%n][0]
            #print(f"p={curr_p}, np={next_p}")
            dy = next_p[1]-curr_p[1]
            dx = next_p[0]-curr_p[0]
            angle = atan2(dy, dx)
            path.append(angle)

        th = 0.2 
        angles = 0
        
        prev_delta = False
        for i in range(len(path)):
            delta = abs(path[(i+1)%n] - path[i])
            if prev_delta and delta - prev_delta > th:
                angles+=1

            prev_delta = delta
        #print(f"---\n---\n---")
        print("angles=", angles)
        return angles

    def getShapeInfo(self, perimeter) -> Dict:
        shape = dict()

        shape["area"] = cv2.contourArea(perimeter)
        if shape["area"] < self.min_area:
            return None 
        
        shape["bbox"] = cv2.boundingRect(perimeter)
        shape["center"] = [
            shape["bbox"][0] + shape["bbox"][2]//2, 
            shape["bbox"][1] + shape["bbox"][3]//2,
        ]

        self.getShapeName(perimeter)

        return shape

    def detect(self, image: np.ndarray) -> List[Dict]:
        """
        Detect colored markers in the given BGR image.

        Args:
            image: Input image in BGR format (as loaded by cv2.imread).

        Returns:
            A list of detection dictionaries, each containing:
            'color', 'bbox', 'center', and 'area' keys.
        """
        
        blue_img =   self.inHueRange(image, "blue")
        green_img =  self.inHueRange(image, "green")
        red_img =    self.inHueRange(image, "red")
        yellow_img = self.inHueRange(image, "yellow")
        
        #cv2.imwrite("tmp.png", blue_img)
        
        contour_categories = dict()
        get_contours = lambda img: cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        contour_categories["blue"], _   = get_contours(blue_img)
        contour_categories["green"], _  = get_contours(green_img)
        contour_categories["red"], _    = get_contours(red_img)
        contour_categories["yellow"], _ = get_contours(yellow_img)
        
        res = []
        for color, contours in contour_categories.items():
            for perimeter in contours:
                shape = self.getShapeInfo(perimeter)
                if shape != None:
                    shape["color"] = color
                    print(color)
                    res.append(shape)
                    #print(shape)

        return res

def intersect_ranges(range_a: Tuple, range_b: Tuple) -> Tuple:
    low = max(range_a[0], range_b[0])
    high = min(range_a[1], range_b[1])
    
    if low <= high:
        return (low, high)
    else:
        return None

def compute_iou(box_a: Tuple, box_b: Tuple) -> float:
    """
    Compute Intersection over Union (IoU) between two bounding boxes.

    Each box is represented as (x, y, w, h) where:
        - (x, y) is the top-left corner
        - (w, h) is the width and height

    Args:
        box_a: First bounding box as (x, y, w, h).
        box_b: Second bounding box as (x, y, w, h).

    Returns:
        IoU value as a float between 0.0 (no overlap) and 1.0 (perfect overlap).
    """

    inter_x = intersect_ranges(
        (box_a[0], box_a[0] + box_a[2] - 1), 
        (box_b[0], box_b[0] + box_b[2] - 1),
    )
    inter_y = intersect_ranges(
        (box_a[1], box_a[1] + box_a[3] - 1), 
        (box_b[1], box_b[1] + box_b[3] - 1),
    )
    if inter_x == None or inter_y == None:
        intersection = 0
    else:
        # print(box_a, box_b, inter_x)
        intersection = (inter_x[1] - inter_x[0] + 1) * (inter_y[1] - inter_y[0] + 1)
    
    area_a = box_a[2] * box_a[3]
    area_b = box_b[2] * box_b[3]

    # unione esclusione
    union = area_a + area_b - intersection

    return intersection / union

def filter_detections(detections: List[Dict], iou_threshold: float = 0.5) -> List[Dict]:
    """
    Filter overlapping detections using Non-Maximum Suppression (NMS).

    When two detections overlap (IoU > iou_threshold), keep the one with the
    larger area and discard the other.

    Args:
        detections: List of detection dictionaries (each must have 'bbox' and 'area').
        iou_threshold: IoU threshold above which two detections are considered overlapping.

    Returns:
        Filtered list of detections with overlapping duplicates removed.
    """
    filtered = []
    mask = [True]*len(detections)

    for i, shape_i in enumerate(detections):
        if mask[i]:
            for j, shape_j in enumerate(detections[i+1:], start=i+1):
                if mask[j]:
                    iou = compute_iou(shape_i["bbox"], shape_j["bbox"])
                    if iou > iou_threshold:
                        if shape_i["area"] >= shape_j["area"]:
                            mask[j] = False
                        else:
                            mask[i] = False

    filtered = []
    for shape, ok in zip(detections, mask):
        if ok:
            filtered.append(shape)

    return filtered
