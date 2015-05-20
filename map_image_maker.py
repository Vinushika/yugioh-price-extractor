import scipy.misc
import cv2
import numpy

##Turns image that has the white regions already marked
##into a MAP image by blacking out everything else
def make_MAP_image(image_name):
	img = cv2.imread(image_name)
	grayimg = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	black = numpy.where(grayimg != 255) #get all non-white
	grayimg[black] = 0 #numpy magic blacks out everything but our "correct" section
	extension = "." + image_name.split(".")[-1]
	scipy.misc.imsave(image_name.replace(extension,".png"),grayimg)
	##done
