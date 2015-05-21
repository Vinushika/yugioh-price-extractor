import cPickle as pick
import MAPtrainer

classifier = MAPtrainer.get_classifier()
with open("classifier.pickle","wb+") as f:
	pick.dump(classifier,f)
