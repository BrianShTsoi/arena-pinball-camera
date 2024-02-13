import cv2
from picamera2 import Picamera2

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (640, 480)}))
# picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (1640, 1232)}))
# picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888'}))
picam2.start()

while True:
    im = picam2.capture_array()
    cv2.imshow("Camera", im)

    # Check for user input (press 'q' to exit)
    if cv2.waitKey(1) == ord('q'):
        break

cv2.destroyAllWindows()

