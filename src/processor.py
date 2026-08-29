import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt

def capture_video(path:str) -> cv.VideoCapture:
    print("video capture begun")
    video = cv.VideoCapture(path)
    print("Video Captured")
    video.set(cv.CAP_PROP_POS_FRAMES,0)
    return video

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
    return background

def background_subtraction(image,background):
    background = np.uint8(cv.cvtColor(background,cv.COLOR_BGR2GRAY))
    image_difference = cv.absdiff(src1 = image, src2 = background)
    _, segmented_image = cv.threshold(image_difference,30,255,cv.THRESH_BINARY)
    return segmented_image

def plot_trajectory(trajectory):
    xs = [p[0] for p in trajectory]
    ys = [p[1] for p in trajectory]

    plt.figure(figsize=(10,5))
    plt.scatter(xs,ys,color="red",s=30,label="Ball detections",zorder=3)
    plt.plot(xs,ys,color="blue",linestyle="--",alpha=0.7,label="Delivery Trajectory")
    plt.gca().invert_yaxis()

    plt.title("Delivery Trajectory")
    plt.xlabel("Horizontal distance(pixels)")
    plt.ylabel("Height")
    plt.grid(True,linestyle=":",alpha=0.6)
    plt.legend()
    plt.show()

def process_video(path):
    prev_circle = None
    euclidean_dist = lambda x1,y1,x2,y2: (x1-x2)**2 + (y1-y2)**2
    trajectory = []

    print("video processing begun")
    video = capture_video(path)

    background_image = find_background_image(video)
    print("Background found")

    print("Video imported into processor")

    kernel = np.ones((3,3))
    stop_counter = 0
    while stop_counter < 3:
        ret, frame = video.read()
        if not ret: break

        grey_frame = cv.cvtColor(frame,cv.COLOR_BGR2GRAY)
        colour_frame = hsv_mask(frame)
        #blur_frame = cv.GaussianBlur(src = grey_frame,ksize = (15,15),sigmaX = 0)
        segmented_frame = background_subtraction(grey_frame,background_image)
        combined_frame = cv.bitwise_and(segmented_frame,colour_frame)
        combined_frame = cv.morphologyEx(combined_frame,cv.MORPH_OPEN,kernel)
        #combined_frame = cv.morphologyEx(combined_frame,cv.MORPH_CLOSE,kernel)
        _, segmented_frame = cv.threshold(cv.GaussianBlur(combined_frame,(25,25),0),120,255,cv.THRESH_BINARY)

        circles = cv.HoughCircles(image = combined_frame, method = cv.HOUGH_GRADIENT, 
                                  dp = 1.2, minDist = 100, param1 = 100, param2 = 10,
                                  minRadius = 0, maxRadius = 15)
        if circles is not None:
            circles = np.uint16(np.around(circles))
            chosen = None
            for circle in circles[0,:]:
                if chosen is None:
                    chosen = circle
                if prev_circle is not None:
                    if euclidean_dist(chosen[0],chosen[1],prev_circle[0],prev_circle[1]) >= euclidean_dist(circle[0],circle[1],prev_circle[0],prev_circle[1]):
                        chosen = circle
                    # if chosen circle is further to the right and upwards than prev_circle,
                    # increment stop_counter. Break when stop_counter > 3, reset if false
                    # further right = chosen[x] > prev[x], chosen[y] < prev[y]
                    if (chosen[0] > prev_circle[0] and chosen[1] < prev_circle[1]):
                        stop_counter += 1
                    else:
                        stop_counter = 0
            if chosen is not None:
                trajectory.append((int(chosen[0]),int(chosen[1])))
                cv.circle(img = frame, center = (chosen[0],chosen[1]), radius=1, color=(0,100,100),thickness=3)
                cv.circle(frame,(chosen[0],chosen[1]),chosen[2],(255,0,255),3)
                prev_circle = chosen
        cv.imshow("circles",frame)

        if cv.waitKey(1) & 0xFF == ord("q"): break
    plot_trajectory(trajectory)
    video.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    path = "data/25_04_26_1/IMG_7053(7).MOV"
    process_video(path)
    print("Success")