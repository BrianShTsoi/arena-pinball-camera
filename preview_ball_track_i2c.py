import cv2
import numpy as np
from picamera2 import Picamera2
import pigpio
import atexit
import time
import sys

# FRAME_WIDTH = 640
# FRAME_HEIGHT  = 480
FRAME_WIDTH = 1640
FRAME_HEIGHT = 1232

GRID_ROWS = 6
GRID_COLS = 4
# GRID_WIDTH = SCREEN_WIDTH
# GRID_HEIGHT = SCREEN_HEIGHT
GRID_SIZE_FACTOR = 0.8
GRID_WIDTH = int(FRAME_WIDTH * GRID_SIZE_FACTOR)
GRID_HEIGHT = int(FRAME_HEIGHT * GRID_SIZE_FACTOR)
GRID_MARGIN_X = (FRAME_WIDTH - GRID_WIDTH) // 2
GRID_MARGIN_Y = (FRAME_HEIGHT - GRID_HEIGHT) // 2
GRID_CELL_WIDTH = GRID_WIDTH // (GRID_COLS)
GRID_CELL_HEIGHT = GRID_HEIGHT // (GRID_ROWS)

# BALL_COLOR_MIN = np.array([0, 0, 100]) # White
# BALL_COLOR_MAX = np.array([180, 50, 255]) # White
BALL_COLOR_MIN = np.array([15, 100, 100])  # Yellow
BALL_COLOR_MAX = np.array([35, 255, 255])  # Yellow
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

I2C_ADDR = 0x0A
pi = None
e = None
i2c_msg = ""
counter = 0


def find_contours_in_frame(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    masked = cv2.inRange(hsv, BALL_COLOR_MIN, BALL_COLOR_MAX)

    contours, _ = cv2.findContours(masked, cv2.RETR_EXTERNAL,
                                   cv2.CHAIN_APPROX_SIMPLE)
    return contours


def find_ball_in_frame(frame, contours):
    cx, cy = -1, -1
    largest_area_contour = max(contours, key=cv2.contourArea)
    if cv2.contourArea(largest_area_contour) > MIN_BALL_RADIUS:
        M = cv2.moments(largest_area_contour)
        if M["m00"] != 0:
            cx = int(M["m10"] / M["m00"])
            cy = int(M["m01"] / M["m00"])
    return largest_area_contour, cx, cy


def add_frame_grids(frame):
    for i in range(0, GRID_COLS + 1):
        x = i * GRID_CELL_WIDTH + GRID_MARGIN_X
        cv2.line(frame, (x, GRID_MARGIN_Y),
                 (x, FRAME_HEIGHT - GRID_MARGIN_Y), MAGENTA, 5)
    for i in range(0, GRID_ROWS + 1):
        y = i * GRID_CELL_HEIGHT + GRID_MARGIN_Y
        cv2.line(frame, (GRID_MARGIN_X, y),
                 (FRAME_WIDTH - GRID_MARGIN_X, y), MAGENTA, 5)


def generate_cells_coordinates():
    cells = []
    for i in range(0, GRID_COLS):
        for j in range(0, GRID_ROWS):
            x1 = i * GRID_CELL_WIDTH + GRID_MARGIN_X
            x2 = x1 + GRID_CELL_WIDTH
            y1 = j * GRID_CELL_HEIGHT + GRID_MARGIN_Y
            y2 = y1 + GRID_CELL_HEIGHT
            cells.append((x1, x2, y1, y2))
    return cells


def draw_cells_with_ball(frame, cells, x, y):
    ball_cell_index = -1
    for i, cell in enumerate(cells):
        x1, x2, y1, y2 = cell
        cv2.line(frame, (x1, y1), (x2, y1), MAGENTA, 5)
        cv2.line(frame, (x1, y2), (x2, y2), MAGENTA, 5)
        cv2.line(frame, (x1, y1), (x1, y2), MAGENTA, 5)
        cv2.line(frame, (x2, y1), (x2, y2), MAGENTA, 5)

        if x >= x1 and x <= x2 and y >= y1 and y <= y2:
            ball_cell_index = i

    if ball_cell_index != -1:
        x1, x2, y1, y2 = cells[ball_cell_index]
        cv2.line(frame, (x1, y1), (x2, y1), YELLOW, 5)
        cv2.line(frame, (x1, y2), (x2, y2), YELLOW, 5)
        cv2.line(frame, (x1, y1), (x1, y2), YELLOW, 5)
        cv2.line(frame, (x2, y1), (x2, y2), YELLOW, 5)


def i2c(id, tick):
    print("callback!")
    global pi

    s, b, d = pi.bsc_i2c(I2C_ADDR)
    print("s: ", bin(s))
    print("sent={} FR={} received={} [{}]".format(s >> 16, s & 0xfff, b, d))
    print(i2c_msg)
    pi.bsc_i2c(I2C_ADDR, i2c_msg)


def init_i2c():
    global pi
    global e
    pi = pigpio.pi()
    if not pi.connected:
        exit()

    e = pi.event_callback(pigpio.EVENT_BSC, i2c)
    pi.bsc_i2c(I2C_ADDR)  # Configure BSC as I2C slave
    atexit.register(shutdown_i2c)


def shutdown_i2c():
    global pi
    global e
    e.cancel()
    pi.bsc_i2c(0)  # Disable BSC peripheral
    pi.stop()


if __name__ == "__main__":
    init_i2c()
    cells = generate_cells_coordinates()

    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(
        main={"format": 'XRGB8888', "size": (FRAME_WIDTH, FRAME_HEIGHT)}))
    picam2.start()
    while True:
        frame = picam2.capture_array()

        x, y = -1, -1
        contours = find_contours_in_frame(frame)
        if contours:
            cv2.drawContours(frame, contours, -1, TURQUOISE, 2)
            ball_contour, x, y = find_ball_in_frame(frame, contours)
            cv2.drawContours(frame, ball_contour, -1, RED, 8)
            cv2.circle(frame, (x, y), MIN_BALL_RADIUS, GREEN, -1)

        draw_cells_with_ball(frame, cells, x, y)
        cv2.putText(frame, "{} {}".format(x, y), (25, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, WHITE, 2)

        i2c_msg = ":{}:{}".format(str(x).rjust(5), str(y).rjust(4))
        print("running")

        if sys.argv.__len__ == 2 and sys.argv[1] == "-c":
            cv2.namedWindow('Ball Tracking', cv2.WINDOW_NORMAL)
            # cv2.resizeWindow('Ball Tracking', 820, 616)
            cv2.setWindowProperty(
                "Ball Tracking",
                cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            cv2.imshow('Ball Tracking', frame)

        if cv2.waitKey(1) == ord('q'):
            break

        time.sleep(sys.float_info.min)  # need a small delay for i2c to work

    cv2.destroyAllWindows()
