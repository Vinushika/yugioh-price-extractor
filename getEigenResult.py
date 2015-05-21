import numpy as np
import cv2
import glob
import time
import MAPtrainer
import sys
import ast
import sortedcontainers
import cPickle as pickle

TRAINING_IMAGES_FOLDER = "testPics/"
INPUT_IMAGES_FOLDER = "./"
EIGENCARD_FOLDER = "eigencardStorage/"
NUM_EIGENCARDS = 9

start_time = time.time()

# For now, our input is just the Koala image.
inputImgName = glob.glob(INPUT_IMAGES_FOLDER + "koala.jpg")
eigenCardNames = [EIGENCARD_FOLDER + "eigenCard%d.jpg" % i for i in range(NUM_EIGENCARDS)] # Needs to be in order for vector projection matching.
eigenCards = [cv2.imread(fn, cv2.CV_LOAD_IMAGE_GRAYSCALE) for fn in eigenCardNames]

# Try to classify our card outline with a MAP classifier.

bin_classifier = MAPtrainer.get_classifier_pickle()
inputImage = [cv2.cvtColor(cv2.imread(fn), cv2.COLOR_BGR2RGB) for fn in inputImgName]
print "GOT CLASSIFIER, GONNA CLASSIFY"

classified_images = MAPtrainer.classify(inputImage, bin_classifier)
##Now you've got binary images!

#classified_images = [cv2.imread("classifier output.jpg", cv2.CV_LOAD_IMAGE_GRAYSCALE)]
print "MAP Classification completed in %0.3f!" % (time.time() - start_time)

inputOutline = classified_images[0]
cv2.imwrite("classifier output.jpg", inputOutline)
currH, currW = inputOutline.shape

# Get our bounding box around the card.
yIndices, xIndices = np.where(inputOutline == 255)
minX = np.min(xIndices)
minY = np.min(yIndices)
maxX = np.max(xIndices)
maxY = np.max(yIndices)

# Crop and resize our image.
inputImg = cv2.cvtColor(inputImage[0], cv2.COLOR_RGB2GRAY)
inputCropped = inputImg[minY:maxY, minX:maxX]
inputCropped = cv2.resize(inputCropped, eigenCards[0].shape[::-1])
cv2.imwrite("cropped koala.jpg", inputCropped)

# Get the projection vector for our input.
with open(EIGENCARD_FOLDER + "meanFlat.pkl", "rb+") as f: # Load the mean of all the database images.
    meanFlat = pickle.load(f)

flattenedInput = inputCropped.flatten() - meanFlat
inputVector = ()
for eigenCard in eigenCards:
    projection = np.dot(eigenCard.flatten(), flattenedInput)
    print "PROJECTION: ", projection
    inputVector += (projection,)

#print "INPUT VECTOR: " + str(inputVector)

# Load the dictionary of the projection vectors for all of the cards in the database.
databaseVectors = dict()
with open(EIGENCARD_FOLDER + "databaseVectors.data") as f:
    lines = f.readlines()
    for line in lines:
        firstSep = line.find(",")
        ID = line[:firstSep]
        tupleLine = line[firstSep+1:]
        if (tupleLine[0] != "("):
            print "ERROR TRYING TO READ DATABASE VECTORS FILE"
            sys.exit(0)
        vector = ast.literal_eval(tupleLine)
        databaseVectors[vector] = ID
print "RECONSTRUCTED THE VECTOR DATABASE!"

# Do MSE sorting to find the closest vector.
def MSE(v):
    dist = 0
    for i in range(len(v)):
        dist += ((inputVector[i] - v[i]) ** 2)
    print "MSE of ID: ", databaseVectors[v], " is: ", dist
    return dist

#print "ABOUT TO DO SORTING"
# Construct a sorted list using MSE sorting.
sortedVectors = sortedcontainers.SortedListWithKey(iterable=databaseVectors.keys(), key = lambda v: MSE(v))
#print "FINISHED SORTING"
# The list is sorted in increasing order, so the first element has the smallest MSE, therefore
# it is our match!
vectorMatch = sortedVectors[0]


# Get the card ID from that vector. That's our result!
ID = databaseVectors[vectorMatch]
print "RESULT ID: %s" % ID
print "TOTAL TIME: %0.3f" % (time.time() - start_time)
