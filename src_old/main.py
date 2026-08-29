import processor as pc
import cv2 as cv

if __name__ == "__main__":
    p = pc.Processor()
    vid1 = p.read_in_video("data/25_04_26_1/IMG_7053(3).MOV")
    bgr_frame = p.convolution2d(p.get_background_image(vid1))
    p.process_video(vid1,bgr_frame,True,True)
    vid1.release()
    cv.destroyAllWindows()