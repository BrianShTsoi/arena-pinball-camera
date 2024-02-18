import cv2
import numpy as np
from picamera2 import Picamera2

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
BALL_COLOR_MIN = np.array([15, 100, 100]) # Yellow
BALL_COLOR_MAX = np.array([35, 255, 255]) # Yellow
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
    # return masked, 0, 0

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
    for i in range(0, GRID_COLS + 1):
        x = i * GRID_CELL_WIDTH + GRID_MARGIN_X
        cv2.line(img, (x, GRID_MARGIN_Y), (x, FRAME_HEIGHT - GRID_MARGIN_Y), MAGENTA, 5)
    for i in range(0, GRID_ROWS + 1):
        y = i * GRID_CELL_HEIGHT + GRID_MARGIN_Y
        cv2.line(img, (GRID_MARGIN_X, y), (FRAME_WIDTH - GRID_MARGIN_X, y), MAGENTA, 5)

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

def draw_cells_with_ball(img, cells, x, y):
    ball_cell_index = -1
    for i, cell in enumerate(cells):
        x1, x2, y1, y2 = cell
        cv2.line(img, (x1, y1), (x2, y1), MAGENTA, 5) 
        cv2.line(img, (x1, y2), (x2, y2), MAGENTA, 5) 
        cv2.line(img, (x1, y1), (x1, y2), MAGENTA, 5)
        cv2.line(img, (x2, y1), (x2, y2), MAGENTA, 5)

        if x >= x1 and x <= x2 and y >= y1 and y <= y2:
            ball_cell_index = i

    if ball_cell_index != -1:
        x1, x2, y1, y2 = cells[ball_cell_index]
        cv2.line(img, (x1, y1), (x2, y1), YELLOW, 5) 
        cv2.line(img, (x1, y2), (x2, y2), YELLOW, 5) 
        cv2.line(img, (x1, y1), (x1, y2), YELLOW, 5)
        cv2.line(img, (x2, y1), (x2, y2), YELLOW, 5)
    

if __name__ == "__main__":
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (FRAME_WIDTH, FRAME_HEIGHT)}))
    picam2.start()

    cells = generate_cells_coordinates()
    while True:
        frame = picam2.capture_array()

        # # Restructure to findContours & drawContours -> findBall & drawBall
        # contours = detect_contours_in_frame()
        # drawContours(contours)
        # ball_contours, x, y = detect_ball_in_frame()
        # drawBall(ball_contours, x, y)

        masked, x, y = trace_ball_in_frame(frame)
        draw_cells_with_ball(masked, cells, x, y)

        cv2.putText(masked, "{} {}".format(x, y), (25, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, WHITE, 2)

        cv2.namedWindow('Ball Tracking', cv2.WINDOW_NORMAL)
        # cv2.resizeWindow('Ball Tracking', 820, 616)
        # cv2.setWindowProperty("Ball Tracking", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.imshow('Ball Tracking', masked)

        if cv2.waitKey(1) == ord('q'):
            break

    cv2.destroyAllWindows()
