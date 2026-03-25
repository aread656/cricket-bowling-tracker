import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

def read_in_video():
    vid1 = cv.VideoCapture("data/07_02_26_1.mov")
    if not vid1.isOpened():
        print("Error: Video failed to open")
        exit()
    return vid1

