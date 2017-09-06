from picamera import PiCamera

camera = PiCamera()
camera.resolution = (1024, 768)

camera.start_preview()

counter = 1

while True:
        x = raw_input ("Take my picture now!")

        if x == 'x':
                break

        pathname = "/home/pi/Desktop/myphoto-" + str(counter) + ".jpg"
        counter += 1
        camera.capture(pathname)

camera.stop_preview()
