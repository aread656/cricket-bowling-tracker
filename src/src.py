import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

def read_in_video(path):
    #reads the selected video
    vid1 = cv.VideoCapture(path)
    if not vid1.isOpened():
        print("Error: Video failed to open")
        exit()
    return vid1

def hsv_filter(img):
    hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
    lower = np.array([25,100,100])
    upper = np.array([40,255,255])
    hsv_mask = cv.inRange(hsv,lower,upper)
    return hsv_mask

def convolution2d(img,n=2):
    #provides a 2d convolution with an n*n kernel
    kernel = np.ones((n,n), np.float32)/(n**2)
    img = cv.filter2D(img,-1,kernel)
    return img

def get_background_image(vid):
    #creates background image and its histogram
    ret, frame = vid.read()
    assert ret is not False
    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    frame = cv.resize(frame, (720,1280))
    frame = cv.equalizeHist(frame)
    return frame

def background_subtraction(bkg,img,n=2):
    #use a static background image to detect objects
    #background does not include ball, so all frames
    #with ball in them shall return a detection
    difference = cv.absdiff(img,bkg)
    _,mask = cv.threshold(difference,30,255,cv.THRESH_BINARY)
    kernel = np.ones((n,n),np.uint8)
    mask = cv.morphologyEx(mask,cv.MORPH_OPEN,kernel)
    mask = cv.morphologyEx(mask,cv.MORPH_CLOSE,kernel)
    return mask

def create_cv_blob_detector():
    params = cv.SimpleBlobDetector_Params()
    params.filterByArea = False
    params.filterByCircularity = True
    params.minCircularity = 0.8
    return cv.SimpleBlobDetector_create(params)

def blob_detector():
    return 0

def process_video(vid,bkg):
    detector = create_cv_blob_detector()
    while True:
        ret, img = vid.read()
        #ret is bool for successful frame opening
        if not ret: break
        #image preprocessing
        img = cv.resize(img, (720,1280))
        hsv = hsv_filter(img)
        frame = convolution2d(img)
        frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        frame = cv.equalizeHist(frame)
        #background subtraction
        mask = background_subtraction(bkg,frame,3)
        mask = cv.bitwise_and(hsv,mask)
        kernel = np.ones((3,3),np.uint8)
        mask = cv.dilate(cv.dilate(mask,kernel),kernel)
        cv.imshow("Video",mask)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

if __name__ == "__main__":
    vid1 = read_in_video("data/07_02_26_1.mov")
    bgr_frame = convolution2d(get_background_image(vid1))
    process_video(vid1,bgr_frame)
    #at this stage, video is black/white segmented footage
    #next step is actual detection/labelling
    vid1.release()
    cv.destroyAllWindows()