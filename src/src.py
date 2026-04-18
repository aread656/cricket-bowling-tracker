import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
from delivery import Delivery

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
    params.filterByArea = True
    params.minArea = 5
    params.maxArea = 200
    params.filterByColor = True
    params.blobColor = 255
    params.filterByCircularity = False
    #params.minCircularity = 0.6
    detector = cv.SimpleBlobDetector_create(params)
    return detector

def blob_detector(img,detector,trajectory_array,ray_array,f,cx,cy):
    keypoints = detector.detect(img)
    if len(keypoints)>0:
        kp = keypoints[0]
        x = int(kp.pt[0])
        y = int(kp.pt[1])
        ray = calculate_ray_from_pixels(x,y,f,cx,cy)
        ray_array.append(ray)
        trajectory_array.append((x,y))
    return keypoints, trajectory_array, ray_array

#FOV of the camera, (cx,cy), focal length using formula

def projection_3d(rays,C,fps=60):
    positions = []
    for index,ray in enumerate(rays):
        t = index/fps
        scale = 5+(0.5*t)+(0.5*t**2)
        B = C+(scale*ray)
        positions.append(B)
    return np.array(positions)
def calculate_ray_from_pixels(x,y,f,cx,cy):
    xn = (x-cx)/f
    yn = (y-cy)/f
    ray = np.array([xn,-yn,1.0])
    #np.linalg.norm finds the vector size using the passed array
    #allows camera space direction vector to be returned
    ray = ray/np.linalg.norm(ray)
    return ray

def get_setup_variables(width=720,height=1280,fov=70):
    C = np.array([-1.0,1.0,-12.0])
    cx,cy = width/2,height/2
    f = width/(2*np.tan(np.deg2rad(fov)/2))
    return C,cx,cy,f

def process_video(vid,bkg,plot=False):
    detector = create_cv_blob_detector()
    trajectory = []
    rays = []
    vid.set(cv.CAP_PROP_POS_FRAMES,0)
    C,cx,cy,f = get_setup_variables()
    while True:
        ret, img = vid.read()
        #ret is bool for successful frame opening
        if not ret: break
        #image preprocessing
        img = cv.resize(img, (720,1280))
        hsv = hsv_filter(img)
        frame = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
        frame = convolution2d(frame)
        frame = cv.equalizeHist(frame)
        #background subtraction
        mask = background_subtraction(bkg,frame,3)
        #combine with HSV filter for more effective segmentation
        mask = cv.bitwise_and(hsv,mask)
        #dilate the segmented areas, as small area may make detection difficult
        kernel = np.ones((3,3),np.uint8)
        mask = cv.dilate(mask,kernel,iterations = 2)
        #detect blobs using cv.SimpleBlobDetector
        keypoints,trajectory,rays= blob_detector(mask,detector,trajectory,
                                             rays,f,cx,cy)
        #draw ball keypoint
        output = cv.drawKeypoints(img,keypoints,np.array([]),(0,0,255),
                               cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        #draw trajectory line
        for i in range(1,len(trajectory)):
            cv.line(output,trajectory[i-1],trajectory[i],(255,255,0),2)
        #show video
        cv.imshow("Video",output)
        if cv.waitKey(1) & 0xFF == ord('q'):
            break
    trajectory_3d = projection_3d(rays,C)
    if plot:
        print(trajectory)
        xs = [p[0] for p in trajectory]
        ys = [p[1] for p in trajectory]

        plt.scatter(xs, ys)
        plt.plot(xs, ys)

        plt.gca().invert_yaxis()
        plt.xlabel("Distance down pitch")
        plt.ylabel("Lateral Line")
        plt.title("Ball trajectory")
        plt.show()
    delivery = Delivery(trajectory_3d)
    print(trajectory_3d)
    return delivery

if __name__ == "__main__":
    vid1 = read_in_video("data/07_02_26_2.mov")
    bgr_frame = convolution2d(get_background_image(vid1))
    process_video(vid1,bgr_frame)
    #at this stage, video is black/white segmented footage
    #next step is actual detection/labelling
    vid1.release()
    cv.destroyAllWindows()