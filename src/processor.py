import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import os
from delivery import Delivery
from db import save_delivery_to_db, init_db

def capture_video(path:str) -> cv.VideoCapture:
    print("video capture begun")
    video = cv.VideoCapture(path)
    print("Video Captured")
    fps = video.get(cv.CAP_PROP_FPS)
    print("Actual video FPS:", fps)
    video.set(cv.CAP_PROP_POS_FRAMES,0)
    return video, fps

def hsv_mask(img):
        hsv = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        lower = np.array([20,100,100])
        upper = np.array([80,255,255])
        return cv.inRange(hsv,lower,upper)

def find_background_image(vid:cv.VideoCapture):
    ret, background = vid.read()
    if not ret:
        print("No background image. Check file exists, and method called before other processing")
        return
    return cv.resize(background,(1920,1080))

def background_subtraction(image,background):
    background = np.uint8(cv.cvtColor(background,cv.COLOR_BGR2GRAY))
    image_difference = cv.absdiff(src1 = image, src2 = background)
    _, segmented_image = cv.threshold(image_difference,30,255,cv.THRESH_BINARY)
    return segmented_image

def convert_to_metres(trajectory, pitch_start_x=200, pitch_end_x=1920,pitch_length=12.0):
    pixels_to_metres_scale_factor: float = (pitch_length/abs(pitch_end_x-pitch_start_x))
    # iterate over all coordinate tuples in trajectory list
    # change each x & y value into metres
    new_trajectory = []
    y_ground_level: float = max(point[0][1] for point in trajectory)
    for point in trajectory:
        new_x = round((point[0][0]-pitch_start_x)*pixels_to_metres_scale_factor,3)
        new_y = round((y_ground_level-point[0][1])*pixels_to_metres_scale_factor,3)
        frame = point[1]
        new_trajectory.append(((new_x,new_y),frame))
    return new_trajectory

def plot_trajectory(trajectory,pitch_length=12.0):

    xs = [p[0][0] for p in trajectory]
    ys = [p[0][1] for p in trajectory]

    plt.figure(figsize=(10,5))
    plt.scatter(xs,ys,color="red",s=30,label="Ball detections",zorder=3)
    plt.plot(xs,ys,color="blue",linestyle="--",alpha=0.7,label="Delivery Trajectory")

    plt.xlim(0.0,pitch_length)
    plt.ylim(0.0,3.0)

    plt.title("Delivery Trajectory")
    plt.xlabel("Horizontal distance(metres)")
    plt.ylabel("Height")
    plt.grid(True,linestyle=":",alpha=0.6)
    plt.legend()
    plt.show()

def process_video(path, show=False):
    frame_count = 0
    prev_circle = None
    euclidean_dist: float = lambda x1,y1,x2,y2: ((x1-x2)**2 + (y1-y2)**2)**0.5
    trajectory: list[(int,int),int] | list[(float,float),int]= []

    print("video processing begun")
    video, fps = capture_video(path)

    background_image = find_background_image(video)
    print("Background found")

    print("Video imported into processor")

    kernel = np.ones((3,3))
    stop_counter = False
    while stop_counter == False:
        ret, frame = video.read()
        if not ret: break
        frame_count += 1
        frame = cv.resize(frame,(1920,1080))

        grey_frame = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
        colour_frame = hsv_mask(frame)
        segmented_frame = background_subtraction(grey_frame,background_image)
        combined_frame = cv.bitwise_and(segmented_frame,colour_frame)
        combined_frame = cv.morphologyEx(combined_frame,cv.MORPH_OPEN,kernel)
        _, segmented_frame = cv.threshold(cv.GaussianBlur(combined_frame,(25,25),0),120,255,cv.THRESH_BINARY)

        circles = cv.HoughCircles(image = combined_frame, method = cv.HOUGH_GRADIENT, 
                                  dp = 1.2, minDist = 100, param1 = 100, param2 = 10,
                                  minRadius = 0, maxRadius = 15)
        if circles is not None:
            circles = np.uint16(np.around(circles))
            chosen = None
            for circle in circles[0,:]:
                # go through all detections, find nearest to previous detection
                if chosen is None:
                    chosen = circle
                if prev_circle is not None:
                    if euclidean_dist(chosen[0],chosen[1],prev_circle[0],prev_circle[1]) >= euclidean_dist(circle[0],circle[1],prev_circle[0],prev_circle[1]):
                        chosen = circle
                    # if chosen circle is further to the right and upwards than prev_circle,
                    # increment stop_counter. Break when stop_counter > 3, reset if false
                    # further right = chosen[x] > prev[x], chosen[y] < prev[y]
                    if (chosen[0] > prev_circle[0]):
                        stop_counter = True
            if chosen is not None and not stop_counter:
                trajectory.append(((int(chosen[0]),int(chosen[1])),frame_count))
                cv.circle(img = frame, center = (chosen[0],chosen[1]), radius=1, color=(0,100,100),thickness=3)
                cv.circle(frame,(chosen[0],chosen[1]),chosen[2],(255,0,255),3)
                if prev_circle is not None:
                    cv.line(frame,(prev_circle[0],prev_circle[1]),(chosen[0],chosen[1]),(255,255,0), 3)
                prev_circle = chosen
        cv.namedWindow("Detections",cv.WINDOW_NORMAL)
        cv.resizeWindow("Detections",640,360)
        if show: cv.imshow("Detections",frame)

        if cv.waitKey(1) & 0xFF == ord("q"): break
    if len(trajectory) < 5:
        return None
    trajectory = convert_to_metres(trajectory)
    if show: plot_trajectory(trajectory)
    video.release()
    cv.destroyAllWindows()
    return Delivery(trajectory,fps)

if __name__ == "__main__":
    init_db()
    path = "data/29_08_26"
    if os.path.isfile(path):
        delivery = process_video(path,True)
        if delivery is not None:
            print(delivery)
            save_delivery_to_db(delivery,path)
            print("Success")
        else:
            print("Detection inadequate to calculate trajectory")
    elif os.path.isdir(path):
        files = [entry.path for entry in os.scandir(path) if os.path.isfile(entry)]
        for file in files:
            delivery = process_video(file,False)
            if delivery is not None:
                print(delivery)
                save_delivery_to_db(delivery,file)
                print("Success")
            else:
                print("Detection inadequate to calculate trajectory")