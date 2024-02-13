import cv2
import os
import sys
import numpy as np

IMG_X = 1640
IMG_Y = 1232

YELLOW_MIN = np.array([15, 100, 100])
YELLOW_MAX = np.array([35, 255, 255])

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

def filter_contours_for_center(contours):
    x_min = IMG_X // 4
    x_max = IMG_X * 3 // 4
    filtered_contours = [cnt for cnt in contours if x_min <= cv2.moments(cnt)["m10"] / (cv2.moments(cnt)["m00"] + 1e-5) <= x_max]
    return filtered_contours


def trace_ball(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    canny = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    contours = filter_contours_for_center(contours)
    traced_img = img.copy()
    cv2.drawContours(traced_img, contours, -1, GREEN, 2)

    largest_area_contour = max(contours, key=cv2.contourArea)
    cv2.drawContours(traced_img, largest_area_contour, -1, RED, 8)
    largest_area_contour = max(contours, key=lambda x: cv2.arcLength(x, False))
    cv2.drawContours(traced_img, largest_area_contour, -1, BLUE, 6)
    largest_area_contour = max(contours, key=lambda x: cv2.boundingRect(x)[2] * cv2.boundingRect(x)[3])
    cv2.drawContours(traced_img, largest_area_contour, -1, YELLOW, 4)
    largest_area_contour = max(contours, key=lambda x: cv2.contourArea(x) / (cv2.contourArea(cv2.convexHull(x)) + 1e-5))
    cv2.drawContours(traced_img, largest_area_contour, -1, CYAN, 15)

    # M = cv2.moments(largest_area_contour)
    # if M["m00"] != 0:
    #     cx = int(M["m10"] / M["m00"])
    #     cy = int(M["m01"] / M["m00"])

    #     cv2.circle(traced_img, (cx, cy), 25, BLUE, -1)

def trace_ball_yellow(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    blurred = cv2.GaussianBlur(hsv, (5, 5), 0)

    masked = cv2.inRange(blurred, YELLOW_MIN, YELLOW_MAX)
    # masked = cv2.inRange(hsv, YELLOW_MIN, YELLOW_MAX)

    contours, _ = cv2.findContours(masked, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # cv2.drawContours(img, contours, -1, GREEN, 2)

    largest_area_contour = max(contours, key=cv2.contourArea)
    cv2.drawContours(img, largest_area_contour, -1, RED, 8)
    M = cv2.moments(largest_area_contour)
    if M["m00"] != 0:
        cx = int(M["m10"] / M["m00"])
        cy = int(M["m01"] / M["m00"])
        cv2.circle(img, (cx, cy), 25, BLUE, -1)
    return img
    # return masked

def trace_img_in_dir(src_dir, dest_dir):
    dir_num = 0
    for root, dirs, files in os.walk(src_dir):
        dest_root = os.path.join(dest_dir, os.path.relpath(root, src_dir))
        os.makedirs(dest_root, exist_ok=True)
        
        dir_num += 1
        for file_num, file in enumerate(files):

            if any(file.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png']):
                img_path = os.path.join(root, file)
                img = cv2.imread(img_path)
                # traced_frame = trace_ball(img)
                traced_frame = trace_ball_yellow(img)

                dest_path = os.path.join(dest_root, file)
                cv2.imwrite(dest_path, traced_frame)
                print("writing: ", dest_path)

if len(sys.argv) != 3:
    print("Usage: python extract_frames.py <frame_dir> <output_dir>")
    sys.exit(1)
input_dir = sys.argv[1]
output_dir = sys.argv[2]
trace_img_in_dir(input_dir, output_dir)
