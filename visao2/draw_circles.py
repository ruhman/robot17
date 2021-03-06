__author__      = "Daniel Ruhman, Marcelo Prado"


import cv2
import cv2.cv as cv
import numpy as np
from matplotlib import pyplot as plt
import time

# If you want to open a video, just change this path
#cap = cv2.VideoCapture('hall_box_battery.mp4')

# Parameters to use when opening the webcam.
cap = cv2.VideoCapture(0)
cap.set(cv.CV_CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv.CV_CAP_PROP_FRAME_HEIGHT, 480)

lower = 0
upper = 1

distance = 0
distanceText = ""
angle = 0

# Returns an image containing the borders of the image
# sigma is how far from the median we are setting the thresholds
def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)

    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
    (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cnts, key = cv2.contourArea)
    # return the edged image
    return edged, c

def distance_to_camera(knownWidth, focalLength, perWidth):
	# compute and return the distance from the maker to the camera
	return (knownWidth * focalLength) / perWidth

while(True):
    # Capture frame-by-frame
    #print("New frame")
    ret, frame = cap.read()

    # Convert the frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # A gaussian blur to get rid of the noise in the image
    blur = cv2.GaussianBlur(gray,(5,5),0)
    # Detect the edges present in the image
    bordas, c = auto_canny(blur)


    # find the contours in the edged image, keeping only the
    # largest ones, and initialize the screen contour
    # cnts = sorted(c, key = cv2.contourArea, reverse = True)[:5]
    # screenCnt = 0
    # # loop over the contours
    # for c in cnts:
    # 	# approximate the contour
    # 	peri = cv2.arcLength(c, True)
    # 	approx = cv2.approxPolyDP(c, 0.02 * peri, True)
    #
    # 	# if our approximated contour has four points, then we
    # 	# can assume that we have found our screen
    # 	if len(approx) == 4:
    # 		screenCnt = approx
    # 		break
    #
    # # show the contour (outline) of the piece of paper
    # cv2.drawContours(c, [screenCnt], -1, (0, 255, 0), 2)
    # cv2.imshow("Outline", c)

    circles = []

    # Obtains a version of the edges image where we can draw in color
    bordas_color = cv2.cvtColor(bordas, cv2.COLOR_GRAY2BGR)

    # HoughCircles - detects circles using the Hough Method. For an explanation of
    # param1 and param2 please see an explanation here http://www.pyimagesearch.com/2014/07/21/detecting-circles-images-using-opencv-hough-circles/
    circles=cv2.HoughCircles(bordas,cv.CV_HOUGH_GRADIENT,2,40,param1=50,param2=100,minRadius=5,maxRadius=60)
    if circles != None:
        circles = np.uint16(np.around(circles))
        KNOWN_DISTANCE = 25

# initialize the known object width, which in this case, the piece of
# paper is 11 inches wide
        KNOWN_WIDTH = 6.5

        focalLength = 519.230769231
        for i in circles[0,:]:
            if len(circles[0,:]) == 3:
                for j in c:
                    # returns ( center (x,y), (width, height), angle of rotation )
                    rect = cv2.minAreaRect(c)
                    box = cv2.cv.BoxPoints(rect)
                    box = np.int0(box)
                    cv2.drawContours(c,[box],0,(0,255,0),100)
                    angle = rect[2]
            else:
                distance = 'circles not found'
                break
            # draw the outer circle
            # cv2.circle(img, center, radius, color[, thickness[, lineType[, shift]]])
            cv2.circle(bordas_color,(i[0],i[1]),i[2],(0,255,0),2)
            # draw the center of the circle
            cv2.circle(bordas_color,(i[0],i[1]),2,(0,0,255),3)
            # focalLength = (135 * KNOWN_DISTANCE) / KNOWN_WIDTH
            # print focalLength
            distance = distance_to_camera(KNOWN_WIDTH, focalLength, i[2]*2)
            distanceText = "{0:.2f} cm".format(distance)


    # # Draw a diagonal blue line with thickness of 5 px
    # # cv2.line(img, pt1, pt2, color[, thickness[, lineType[, shift]]])
    # cv2.line(bordas_color,(0,0),(511,511),(255,0,0),5)
    #
    # # cv2.rectangle(img, pt1, pt2, color[, thickness[, lineType[, shift]]])
    # cv2.rectangle(bordas_color,(384,0),(510,128),(0,255,0),3)
    #
    # cv2.putText(img, text, org, fontFace, fontScale, color[, thickness[, lineType[, bottomLeftOrigin]]])
    font = cv2.FONT_HERSHEY_SIMPLEX

    text = ("{0}, {1} graus").format(distanceText, angle)
    cv2.putText(bordas_color,text,(0,50), font, 1.5,(255,255,255),2,cv2.CV_AA)
    # Display the resulting frame
    cv2.imshow('Detector de circulos',bordas_color)
    #print("No circles were found")
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
