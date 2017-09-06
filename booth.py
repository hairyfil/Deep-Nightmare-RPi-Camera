import os

os.environ["BOTO_CONFIG"] = ".boto"

import boto
from boto.s3.key import Key
import sys
import time
import logging
import hashlib
from picamera import PiCamera

LOGGING     = True
VERBOSITY   = False
DEBUGGING   = True

if LOGGING:
	logging.basicConfig(filename='booth.log',level=logging.DEBUG)

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

def upload(name, path):
	mydebugmsg("uploading " + path)

	s3                  = boto.connect_s3()
	temp_bucket_name  = "temporary_incoming_images"
	temp_bucket 	    = s3.get_bucket(temp_bucket_name)

	imagehash = create_hash(path)
	new_image_name = str(imagehash) + ".jpg"
	
	mydebugmsg("hash = " + imagehash)
	mydebugmsg("new image name = " + new_image_name)
	mydebugmsg("path = " + path)

	dest_bucket = temp_bucket.new_key(new_image_name)
	dest_bucket.set_contents_from_filename(path)
	dest_bucket.set_acl('public-read')

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

while True:
		x = raw_input ("Take my picture now!")

		if x == 'x':
				break

		image_name = "myphoto-" + str(counter) + ".jpg"
		image_path = "/home/pi/Desktop/" + image_name

		mydebugmsg("image_name = " + image_name)
		mydebugmsg("image_path = " + image_path)
		
		counter += 1

		camera.capture(image_path)
		upload(image_name, image_path)

camera.stop_preview()
