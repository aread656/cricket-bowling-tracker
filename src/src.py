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

def convolution2d(img,n=2):
    #provides a 2d convolution with an n*n kernel
    kernel = np.ones((n,n), np.float32)/(n**2)
    img = cv.filter2D(img,-1,kernel)
    return img

def get_background_image(vid, show=False):
    #creates background image and its histogram
    ret, frame = vid.read()
    assert ret is not False
    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    frame = cv.resize(frame, (720,1280))
    frame = cv.equalizeHist(frame)
    hist, bins = np.histogram(frame.flatten(), 256,[0,256])
    cdf = hist.cumsum()
    cdf_normalised = cdf * float(hist.max())/cdf.max()
    if show:
        cv.imshow("Frame",frame)
        plt.plot(cdf_normalised, color = "b")
        plt.hist(frame.flatten(),256,[0,256],color="r")
        plt.xlim([0,256])
        plt.show()
    return frame

def process_video(vid,bkg):
    detector = create_cv_blob_detector()
    while True:
        ret, img = vid.read()
        #ret is bool for successful frame opening
        if not ret: break
        img = cv.resize(img, (720,1280))
        frame = convolution2d(img)
        frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        frame = cv.equalizeHist(frame)
        mask = background_subtraction(bkg,frame,3)
        trajectory = cv_blob_detector(mask,detector)
        for i in range(1,len(trajectory)):
            cv.line(img,trajectory[i-1], trajectory[i], (255,255,0), 3)
        cv.imshow("Video",img)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break

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
    param = cv.SimpleBlobDetector_Params()
    param.filterByArea = True
    #param.minArea = 30
    #param.maxArea = 50
    param.filterByCircularity = True
    param.minCircularity = 0.9
    param.maxCircularity = 1.0
    param.filterByInertia = False
    #param.minInertiaRatio = 0.6
    #param.maxInertiaRatio = 1.0
    param.filterByConvexity = False
    #param.minConvexity = 0.6
    #param.maxConvexity = 1.0
    detector = cv.SimpleBlobDetector_create(param)
    return detector

def cv_blob_detector(img,detector):
    keypoints = detector.detect(img)
    trajectory = []
    if not keypoints: return []

    for k in keypoints:
        x=int(k.pt[0])
        y=int(k.pt[1])
        r=int(k.size/2)
        trajectory.append((x,y))
        cv.circle(img,(x,y),r,(0,0,255),2)
    return trajectory

if __name__ == "__main__":
    vid1 = read_in_video("data/07_02_26_1.mov")
    bgr_frame = convolution2d(get_background_image(vid1))
    process_video(vid1,bgr_frame)
    #at this stage, video is black/white segmented footage
    #next step is actual detection/labelling
    vid1.release()
    cv.destroyAllWindows()