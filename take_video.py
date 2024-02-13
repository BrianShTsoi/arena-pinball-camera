import sys
from picamera2 import Picamera2

if len(sys.argv) < 2:
    print("Need vid name")
    sys.exit(1)
vidname = sys.argv[1]

picam2 = Picamera2()
picam2.configure(picam2.create_video_configuration(main={"format": 'RGB888', "size": (1640, 1232)}))
picam2.start_and_record_video(vidname, duration=5)