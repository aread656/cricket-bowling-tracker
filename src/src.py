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
    frame = cv.resize(frame, (360,640))
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
    while True:
        ret, frame = vid.read()
        #ret is bool for successful frame opening
        if not ret:
            break
        frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        frame = cv.resize(frame, (360,640))
        frame = cv.equalizeHist(frame)
        frame = convolution2d(frame,2)
        mask = background_subtraction(bkg,frame,3)
        cv.imshow("Video",mask)
        if cv.waitKey(1) & 0xFF == 27:
            break

def background_subtraction(bkg,img,n=2):
    difference = cv.absdiff(img,bkg)
    _,mask = cv.threshold(difference,30,255,cv.THRESH_BINARY)
    kernel = np.ones((n,n),np.uint8)
    mask = cv.morphologyEx(mask,cv.MORPH_OPEN,kernel)
    mask = cv.morphologyEx(mask,cv.MORPH_CLOSE,kernel)
    return mask

if __name__ == "__main__":
    vid1 = read_in_video("data/07_02_26_1.mov")
    bgr_frame = convolution2d(get_background_image(vid1),2)
    process_video(vid1,bgr_frame)
    vid1.release()
    cv.destroyAllWindows()