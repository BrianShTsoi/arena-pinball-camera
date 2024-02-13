import cv2
import numpy as np
from picamera2 import Picamera2

# BALL_COLOR_MIN = np.array([0, 0, 100])
# BALL_COLOR_MAX = np.array([180, 50, 255])
BALL_COLOR_MIN = np.array([15, 100, 100])
BALL_COLOR_MAX = np.array([35, 255, 255])
MIN_BALL_RADIUS = 10

RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
YELLOW = (0, 255, 255)
CYAN = (255, 255, 0)
MAGENTA = (255, 0, 255)
ORANGE = (0, 165, 255)
PURPLE = (128, 0, 128)
PINK = (203, 192, 255)
TURQUOISE = (208, 224, 64)

def trace_ball_in_frame(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    masked = cv2.inRange(hsv, BALL_COLOR_MIN, BALL_COLOR_MAX)

    contours, _ = cv2.findContours(masked, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        # return masked
        return img
    cv2.drawContours(img, contours, -1, TURQUOISE, 2)

    largest_area_contour = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest_area_contour) > MIN_BALL_RADIUS:
        M = cv2.moments(largest_area_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.circle(img, (cx, cy), MIN_BALL_RADIUS, GREEN, -1)
        cv2.drawContours(img, largest_area_contour, -1, RED, 8)

    return img
    # return masked

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (1640, 1232)}))
picam2.start()

while True:
    frame = picam2.capture_array()
    masked = trace_ball_in_frame(frame)
    cv2.imshow('Tracing Balls', masked)

    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()
