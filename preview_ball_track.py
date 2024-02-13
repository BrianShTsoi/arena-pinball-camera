import cv2
import numpy as np
from picamera2 import Picamera2

# SCREEN_X = 640
# SCREEN_Y = 480
SCREEN_X = 1640 
SCREEN_Y = 1232
GRID_ROWS = 6
GRID_COLS = 4

# BALL_COLOR_MIN = np.array([0, 0, 100])
# BALL_COLOR_MAX = np.array([180, 50, 255])
BALL_COLOR_MIN = np.array([15, 100, 100])
BALL_COLOR_MAX = np.array([35, 255, 255])
MIN_BALL_RADIUS = 10

WHITE = (255, 255, 255)
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
        return img, -1, -1
    cv2.drawContours(img, contours, -1, TURQUOISE, 2)

    cx = -1
    cy = -1
    largest_area_contour = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest_area_contour) > MIN_BALL_RADIUS:
        M = cv2.moments(largest_area_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
            cv2.circle(img, (cx, cy), MIN_BALL_RADIUS, GREEN, -1)
        cv2.drawContours(img, largest_area_contour, -1, RED, 8)

    return img, cx, cy
    # return masked


def add_frame_grids(img):
    spacing_x = img.shape[1] // (GRID_COLS)
    spacing_y = img.shape[0] // (GRID_ROWS)

    for i in range(1, GRID_COLS):
        x = i * spacing_x
        cv2.line(img, (x, 0), (x, img.shape[0]), MAGENTA, 1)  # thickness 1
    for i in range(1, GRID_ROWS):
        y = i * spacing_y
        cv2.line(img, (0, y), (img.shape[1], y), MAGENTA, 1)  # thickness 1

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (SCREEN_X, SCREEN_Y)}))
picam2.start()

while True:
    frame = picam2.capture_array()

    # Restructure to findContours & drawContours -> findBall & drawBall
    masked, x, y = trace_ball_in_frame(frame)

    add_frame_grids(masked)
    cv2.putText(masked, "{} {}".format(x, y), (25, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, WHITE, 2)

    cv2.imshow('Tracing Balls', masked)

    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()
