import os

os.environ["BOTO_CONFIG"] = ".boto"

import boto
from boto.s3.key import Key
import sys
import time
import logging
import hashlib
from picamera import PiCamera
import RPi.GPIO as GPIO
import ds18b20
import segment

LOGGING     = True
VERBOSITY   = False
DEBUGGING   = True

if LOGGING:
	logging.basicConfig(filename='booth.log',level=logging.DEBUG)

def setup_GPIO():
	segment.TM1638_init()

def cleanup_GPIO():
	GPIO.cleanup()

def mydebugmsg(msg):
	if LOGGING:
		logging.debug(msg)
	if DEBUGGING:
		print (msg)
	return

def create_hash(file):
	BUF_SIZE = 65536  # lets read stuff in 64kb chunks!:

	md5 = hashlib.md5()

	with open(file, 'rb') as f:
		while True:
			data = f.read(BUF_SIZE)
			if not data:
				break
			md5.update(data)

	mydebugmsg("MD5: {0}".format(md5.hexdigest()))
	
	return md5.hexdigest()

#
# Upload the photo to S3 for later processing
#

def upload(name, path, temperature):
	
	mydebugmsg("uploading " + path)
	mydebugmsg("temperature = " + str(temperature))

	s3                  = boto.connect_s3()
	temp_bucket_name	= "temporary-incoming-images"
	temp_bucket 	    = s3.get_bucket(temp_bucket_name)
	
	image_hash = create_hash(path)
	new_image_name = str(image_hash) + ".jpg"
	
	mydebugmsg("hash = " + image_hash)
	mydebugmsg("new image name = " + new_image_name)
	mydebugmsg("path = " + path)

	key = temp_bucket.new_key(new_image_name)
	key.set_metadata ("temperature", str(temperature))
	key.set_metadata ("imagehash", str(image_hash))
	key.set_contents_from_filename(path)
	key.set_acl('public-read')

	return

#
# Main section of code
# loop around
# hit enter to take the photo
# hit x and enter to quit
#

camera = PiCamera()
camera.resolution = (1024, 768)

camera.start_preview()

counter = 1

# 
# Setup GPIO sensor for temperature & digital display
#

setup_GPIO()
current_temp = 0.0

while True:
		x = raw_input ("Hit Enter to take your picture\r\nEnter 'x' to quit")

		current_temp = ds18b20.ds18b20Read()
		segment.numberDisplay_dec(current_temp)

		if x == 'x':
				print ("Thank you and goodbye!")
				cleanup_GPIO()
				break

		image_name = "myphoto-" + str(counter) + ".jpg"
		image_path = "/home/pi/Desktop/" + image_name

		mydebugmsg("image_name = " + image_name)
		mydebugmsg("image_path = " + image_path)
		
		counter += 1

		camera.capture(image_path)
		upload(image_name, image_path, current_temp)

camera.stop_preview()
