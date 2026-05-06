import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from delivery import Delivery

class Processor:
    #/////////////////////////////////
    #Video I/0
    #/////////////////////////////////
    def read_in_video(self,path):
        #reads the selected video
        vid1 = cv.VideoCapture(path)
        if not vid1.isOpened():
            print("Error: Video failed to open")
            exit()
        return vid1
    def get_background_image(self,vid):
        #creates background image and its histogram
        ret, frame = vid.read()
        assert ret is not False
        frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        frame = cv.resize(frame, (1280,720))
        frame = cv.equalizeHist(frame)
        return frame

    #///////////////////////////////////
    #Masks
    #///////////////////////////////////
    def sobelEdgeDetection(self,img):
        Gx = np.array([-1,0,1,-2,0,2,-1,0,1]).reshape([3,3])
        Gy = np.array([-1,-2,-1,0,0,0,1,2,1]).reshape([3,3])
        img_float = np.float32(img)
        edges_x = cv.filter2D(img_float,-1,Gy)
        edges_y = cv.filter2D(img_float,-1,Gx)
        magnitudes = cv.magnitude(edges_x,edges_y)
        return cv.convertScaleAbs(magnitudes)
    def hsv_filter(self,img):
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        lower = np.array([0,100,100])
        upper = np.array([80,255,255])
        hsv_mask = cv.inRange(hsv,lower,upper)
        return hsv_mask
    def background_subtraction(self,bkg,img,n=2):
        #use a static background image to detect objects
        #background does not include ball, so all frames
        #with ball in them shall return a detection
        difference = cv.absdiff(img,bkg)
        _,mask = cv.threshold(difference,30,255,cv.THRESH_BINARY)
        kernel = np.ones((n,n),np.uint8)
        mask = cv.morphologyEx(mask,cv.MORPH_OPEN,kernel)
        mask = cv.morphologyEx(mask,cv.MORPH_CLOSE,kernel)
        return mask
    
    #///////////////////////////////
    #Preprocessing
    #///////////////////////////////
    def gaussianBlur(self,img):
        kernel = np.array([
            1,  4,  6,  4,  1,
            4, 16, 24, 16,  4,
            6, 24, 36, 24,  6,
            4, 16, 24, 16,  4,
            1,  4,  6,  4,  1
        ], dtype=np.float32).reshape([5,5]) / 256.0
        return cv.filter2D(img,-1,kernel)
    def preprocess_image(self,img):
        frame = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        frame = self.gaussianBlur(frame)
        frame = cv.equalizeHist(frame)
        return frame
    def convolution2d(self,img,n=2):
        #provides a 2d convolution with an n*n kernel
        kernel = np.ones((n,n), np.float32)/(n**2)
        img = cv.filter2D(img,-1,kernel)
        return img
    
    #///////////////////////////////
    #Detection
    #///////////////////////////////
    def create_cv_blob_detector(self):
        params = cv.SimpleBlobDetector_Params()
        params.filterByArea = True
        params.minArea = 10
        params.maxArea = 200
        params.filterByColor = True
        params.blobColor = 255
        params.filterByCircularity = False
        #params.minCircularity = 0.6
        detector = cv.SimpleBlobDetector_create(params)
        return detector
    def blob_detector(self,img,detector,trajectory_array):
        keypoints = detector.detect(img)
        if len(keypoints)>0:
            kp = keypoints[0]
            x = int(kp.pt[0])
            y = int(kp.pt[1])
            trajectory_array.append((x,y))
        return keypoints, trajectory_array

    #//////////////////////////////
    #Trajectory
    #//////////////////////////////
    def transform_trajectory(self,traj):
        if not traj:
            return traj
        xs = [p[0] for p in traj]
        ys = [p[1] for p in traj]
        xs = [max(xs) - x for x in xs]
        ys = [max(ys) - y for y in ys]
        return list(zip(xs, ys))

    #///////////////////////////////
    #Processing Pipeline
    #///////////////////////////////
    def process_video(self,vid,bkg,plot=False,show=False):
        detector = self.create_cv_blob_detector()
        trajectory = []
        vid.set(cv.CAP_PROP_POS_FRAMES,0)
        while True:
            ret, img = vid.read()
            #ret is bool for successful frame opening
            if not ret: break
            #image preprocessing
            img = cv.resize(img, (1280,720))
            hsv = self.hsv_filter(img)
            frame = self.preprocess_image(img)
            #background subtraction
            mask = self.background_subtraction(bkg,frame,3)
            mask = cv.bitwise_and(hsv,mask)
            #sobel edge detection mask
            sobel = self.sobelEdgeDetection(frame)
            _,sobel_mask = cv.threshold(sobel,50,255,cv.THRESH_BINARY)
            mask = cv.bitwise_and(sobel_mask,mask)
            #dilate the segmented areas, as small area may make detection difficult
            kernel = np.ones((3,3),np.uint8)
            mask = cv.dilate(mask,kernel,iterations = 2)
            #detect blobs using cv.SimpleBlobDetector
            keypoints,trajectory= self.blob_detector(mask,detector,trajectory)
            #draw ball keypoint
            output = cv.drawKeypoints(img,keypoints,np.array([]),(0,0,255),
                                cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
            #draw trajectory line
            for i in range(1,len(trajectory)):
                cv.line(output,trajectory[i-1],trajectory[i],(255,255,0),2)
            #show video
            output = cv.flip(output,1)
            if show:
                cv.imshow("Video",output)
                if cv.waitKey(1) & 0xFF == ord('q'):
                    break
        trajectory = self.transform_trajectory(trajectory)
        if plot:
            print(trajectory)
            xs = [p[0] for p in trajectory]
            ys = [p[1] for p in trajectory]
            plt.scatter(xs, ys)
            plt.plot(xs, ys)
            plt.xlabel("Distance down pitch")
            plt.ylabel("Height")
            plt.title("Ball trajectory")
            plt.show()
        delivery = Delivery(trajectory)
        return delivery