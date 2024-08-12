import cv2
import numpy as np

def detect_objects(image):
    # Placeholder for your object detection model
    # This should return a list of detected objects and their classes
    # For this example, we'll simulate detection
    return [{"class": "non-ev", "confidence": 0.95}]

def process_frame(frame):
    objects = detect_objects(frame)
    for obj in objects:
        if obj["class"] == "non-ev":
            return True
    return False