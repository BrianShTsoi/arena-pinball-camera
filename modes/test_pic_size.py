from picamera2 import Picamera2, Preview
import time
picam2 = Picamera2()

camera_config = picam2.create_preview_configuration({"format": "RGB888"})
picam2.configure(camera_config)
picam2.start()
time.sleep(2)
picam2.capture_file("testdefault.jpg")
picam2.stop()

camera_config = picam2.create_preview_configuration({"size": (1920, 1080), "format": "RGB888"})
picam2.configure(camera_config)
picam2.start()
time.sleep(2)
picam2.capture_file("test1920x1080.jpg")
picam2.stop()

camera_config = picam2.create_preview_configuration({"size": (3280, 2464), "format": "RGB888"})
picam2.configure(camera_config)
picam2.start()
time.sleep(2)
picam2.capture_file("test3280x2464.jpg")
picam2.stop()

camera_config = picam2.create_preview_configuration({"size": (1640, 1232), "format": "RGB888"})
picam2.configure(camera_config)
picam2.start()
time.sleep(2)
picam2.capture_file("test1640x1232.jpg")
picam2.stop()

camera_config = picam2.create_preview_configuration({"size": (640, 480), "format": "RGB888"})
picam2.configure(camera_config)
picam2.start()
time.sleep(2)
picam2.capture_file("test640x480.jpg")
picam2.stop()
