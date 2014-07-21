import sys
import os

from copy import deepcopy

from pylab import imread, imshow, gray, mean
import cPickle


CAFFE_DIR = '/home/sbranson/caffe'
PROTO_FILE = '/models/imagenet_center.prototxt'
REFERENCE_FILE = '/models/caffe_reference_imagenet_model'
FINE_TUNE = ''
FEAT_NAME = 'fc6'

sys.path.append(CAFFE_DIR+"/python")
from caffe import imagenet

# Initialize CNN feature extractor
net = imagenet.ImageNetClassifier(CAFFE_DIR+PROTO_FILE, CAFFE_DIR+REFERENCE_FILE+FINE_TUNE, center_only=True)
net.caffenet.set_phase_test()
net.caffenet.set_mode_cpu()

# Extract features for "myImage.jpg" (do this for each image you want to extract features for)

scores = dict()
featureVectors = dict()

dirname = 'bluebirds/bluebird_images'
for filename in os.listdir(dirname):
	img = imread(dirname + '/' + filename)
	scores[filename[:-4]] = net.predict_preloaded(img)
	featureVectors[filename[:-4]] = deepcopy(net.feature(FEAT_NAME))

f = open('scores.pickle', 'w')
cPickle.dump(scores, f); f.close()

f = open('featureVectors.pickle', 'w')
cPickle.dump(featureVectors, f); f.close()
