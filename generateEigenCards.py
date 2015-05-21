import numpy as np
import cv2
import glob
import time
import cPickle as pickle

TRAINING_IMAGES_FOLDER = "pics/"
EIGENCARD_FOLDER = "eigencardStorage/"
NUM_EIGENCARDS = 10


start_time = time.time()

def getImgGray(filePath):
    return cv2.cvtColor(cv2.imread(filePath), cv2.COLOR_BGR2GRAY)

# Credit here: http://www.janeriksolem.net/2009/01/pca-for-images-using-python.html
def pca(X):
    
    
    # Principal Component Analysis
    # input: X, matrix with training data as flattened arrays in rows
    # return: projection matrix (with important dimensions first),
    # variance and mean
    #X = Y#np.copy(Y)
    

    # get dimensions
    num_data, dim = X.shape
    
    # center data
    mean_X = X.mean(axis=0)
    for i in range(num_data):
        X[i] -= mean_X

    if dim>100:
        print 'PCA - compact trick used'
        M = np.dot(X, X.T) #covariance matrix
        e,EV = np.linalg.eigh(M) #eigenvalues and eigenvectors

	# Sort eigen-values and vectors.
        ind = np.argsort(e)
        e = e[ind]
        EV = EV[:, ind]   # columns are eigenvectors corresponding to eigenvalues
        
        tmp = np.dot(X.T,EV).T #this is the compact trick
        V = tmp[::-1] #reverse since last eigenvectors are the ones we want
        EPSILON = 0.0001
        print "# of EIGENVALUES: ", len(e)
        for i in range(len(e)):
            if (np.abs(e[i]) < EPSILON):
                # eigenvalue is within rounding error of 0
                print "Rounded eigenvalue: ", e[i], " to 0!";
                e[i] = 0
        S = np.sqrt(e)[::-1] #reverse since eigenvalues are in increasing order
    else:
        print 'PCA - SVD used'
        U,S,V = linalg.svd(X)
        V = V[:num_data] #only makes sense to return the first num_data
        
    #return the projection matrix, the variance and the mean
    return V,S,mean_X




# Get all card images.
inputFileNames = glob.glob(TRAINING_IMAGES_FOLDER + "*.jpg")

# Will fail if there are no images. Assumes all images will have the same pixel size.
firstImage = cv2.imread(inputFileNames[0])
height, width = firstImage.shape[:2]

X = np.zeros((len(inputFileNames), height*width))

# Each image becomes one row in our big matrix.
for i in range(len(inputFileNames)):
    X[i] = getImgGray(inputFileNames[i]).flatten()

# Perform PCA
V, S, meanFlat = pca(X)

# Save the average image.
with open(EIGENCARD_FOLDER + "meanFlat.pkl", "wb+") as f:
    pickle.dump(meanFlat, f)

mean = meanFlat.reshape(height, width)
cv2.imwrite(EIGENCARD_FOLDER + "mean.jpg", mean)

# TODO: Find how many principal components we should use


# Get our list of eigencards
eigenCards = []

for i in range(NUM_EIGENCARDS):
    if (i < len(V)):
        mode = V[i].reshape(height, width)
        cv2.imwrite(EIGENCARD_FOLDER + "eigenCard%d.jpg" % i, mode)
        eigenCards.append(mode)
    else:
        print "We've run out of eigencards!"

print "WROTE OUT EIGENCARDS IN %0.3f SECONDS!" % (time.time() - start_time)
vector_time = time.time()

print "NOW SAVING PROJECTION VECTORS"

# Create our dictionary taking projection vectors -> card IDs
inputVectors = dict()
for i in range(len(inputFileNames)):
    fileName = inputFileNames[i]
    ID = fileName[fileName.find(TRAINING_IMAGES_FOLDER) + len(TRAINING_IMAGES_FOLDER) : fileName.find(".jpg")]
    flattenedImg = getImgGray(fileName).flatten() - meanFlat
    values = ()
    for eigenCard in eigenCards:
        projection = np.dot(eigenCard.flatten(), flattenedImg)
        values += (projection,)
    if (inputVectors.get(values) != None):
        print "ERROR: Two database cards have the same projection vector!"
    else:
        inputVectors[values] = ID



# Write our dictionary to a file
with open(EIGENCARD_FOLDER + "databaseVectors.data", "w+") as f:
    for key in inputVectors.keys():
        f.write(str(inputVectors[key]) + "," + str(key) + "\n")


print "DONE SAVING PROJECTION VECTORS IN %0.3f SECONDS!" % (time.time() - vector_time)
print "TOTAL TIME: %0.3f" % (time.time() - start_time)
