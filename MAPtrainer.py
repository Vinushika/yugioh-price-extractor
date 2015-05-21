import numpy as np
import glob
from scipy.misc import imread
import scipy.ndimage

training_images = []
training_masks = []
testing_images = []

train = glob.glob("newtest_images/* shrunk.jpg")
trainmask = glob.glob("newtest_images/* shrunk train.png")
for img in train:
    training_images.append(imread(img))
for img in trainmask:
    training_masks.append(imread(img,flatten=True))

#now define our bins (16x16x16)
stepsize = 16
bin_centers = np.arange(stepsize/2, 256, stepsize)
number_of_bin_centers = len(bin_centers)

#and create a storage for the bins
border_count = np.zeros((number_of_bin_centers,number_of_bin_centers,number_of_bin_centers))
nonborder_count = np.zeros((number_of_bin_centers,number_of_bin_centers,number_of_bin_centers))
#What's going to happen is that we're going to dump each pixel of the training images into these bins,
#depending on whether something is a border or not a border, based on the training maps. Then when we're done,
#the "classifier" is really just looking at whether there is more border than non-border in a particular bin.

for img_num in range(len(training_images)):
    height, width, colors = np.shape(training_images[img_num])
    #images are, for example, 800x533, but shape
    #is 533x800, so height,width,colors.
    for x in range(height):
        for y in range(width):
            #for every pixel in the image
            pixel = training_images[img_num][x,y,:]
            #get the bin value for the particular pixel
            bin_location = np.zeros(colors)
            for c in range(colors):
                #find the closest bin (minimize distance) to the pixel
                bin_location[c] = np.argmin(np.abs(pixel[c] - bin_centers))
                
            #now that we have the bin, check against the map image to tell whether it's a border
            if training_masks[img_num][x,y] > 0:
                border_count[bin_location[0],bin_location[1],bin_location[2]] += 1
            else:
                nonborder_count[bin_location[0],bin_location[1],bin_location[2]] += 1

bin_classifier = np.greater(border_count, nonborder_count)

#now list how many bins are border
bin_count = 0
for r in range(len(bin_classifier)):
    for g in range(len(bin_classifier[0])):
        for b in range(len(bin_classifier[0][0])):
            if bin_classifier[r][g][b]:
                bin_count += 1

##now we have the classifier. Below is how it works - commented because testing is undefined!!
binary_detection_images = [] #list of our output images

#for num_image in range(len(testing_images)):
#    height, width, colors = np.shape(testing_images[num_image])
#    binary_detection_images.append(np.zeros((height,width)))
#    for x in range(height):
#        for y in range(width):
#            pixel = testing_images[num_image][x,y,:]
#            bin_location = np.zeros(colors)
#            for c in range(colors):
#                #find the closest bin (minimize distance) to the pixel
#                bin_location[c] = np.argmin(np.abs(pixel[c] - bin_centers))
#                
#            #now that we have the bin, check whether the bin is cone
#            if (bin_classifier[bin_location[0],bin_location[1],bin_location[2]]):
#                binary_detection_images[num_image][x,y] = 255

#We don't need to do MORPH_CLOSE on them because we only want the edges.
