import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

def read_in_video():
    vid1 = cv.VideoCapture("data/07_02_26_1.mov")
    if not vid1.isOpened():
        print("Error: Video failed to open")
        exit()
    return vid1

def process_video(vid):
    while True:
        ret, frame = vid.read()
        #ret is bool for successful frame opening
        if not ret:
            break
        frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        frame = cv.resize(frame, (360,640))
        frame = cv.equalizeHist(frame)
        cv.imshow("Video",frame)
        if cv.waitKey(1) & 0xFF == 27:
            break

