from picamera import PiCamera
from time import sleep

camera.resolution = (750, 750)

camera = PiCamera()

camera.start_preview()
sleep(10)
camera.stop_preview()

while True:
    print ("")

