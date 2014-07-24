from sklearn.svm import SVC
import numpy as np

import cPickle

import random
from math import log, exp, sqrt, pow, pi

class AnnotationModel(object):

    def __init__(self, dirName, stoppingRatio, mode):
        
        self.dirName = dirName
        self. stoppingRatio = stoppingRatio

        assert (mode == 'norm' or mode == 'cv'), "Mode is either 'norm' or 'cv'"
        
        self.mode = mode

        if (self.mode == 'cv'):
            self.features = cPickle.load(open(self.dirName + '/featureVectors.pickle', 'r'))
            self.scores = cPickle.load(open(self.dirName + '/scores.pickle', 'r'))

    #stoppingRatio: stoppingRatio for sequential probability ratio test

    #mode: cv: Computer vision enabled
    #      norm: Model without computer vision


    # The function should determine whether we have enough confidence in ground truth predictions for any label to
    # stop the annotation process for tahat label. Confidence is measured with the Sequential probability ratio test using
    # the stoppingRatio variable.
    # http://en.wikipedia.org/wiki/Sequential_probability_ratio_test

    #U: getCompletedExamples(incompleteExamples,labels,v)
    #B: incompleteExamples: image data, dictionary of lists
    #   labels: crowd labels, dictionary of lists
    #
    #A: Returns a dictionary of images (list for each image) that we have enough confidence in ground truth prediction.

    def getCompletedExamples(self, incompleteExamples, insufficientExamples, labels, cvProb = None):

        completeExamples = dict()

        #predictions is a dictionary of lists with imageIDs as keys and
        #a key's value is a list with [probability, label prediction]
        predictions = self.optimiseProbability(labels, cvProb)

        for imgID in predictions:
            y = predictions[imgID][1]
            #py = p(y | xi, zi, vi)
            py = predictions[imgID][0]
            if (imgID in incompleteExamples and self.stoppingRatio < log(py/(1-py))):
                completeExamples[imgID] = y

            if imgID in insufficientExamples:
                insufficientExamples[imgID] = y

        return [completeExamples, insufficientExamples]

    #The function takes the input of unlabelled examples and sends the examples through a pipe where images are only
    #given new annotations if the confidence level in their ground truth predictions are below a threshold. The function
    #asks for annotations for images continually until all image example predictions pass the confidence threshold.
    #(TO BE DONE): This function also uses a computer vision algorithm as an annotator and gives predictions with
    #confidence levels which can be supported or notI by annotators.

   #REFACTOR THIS SHIT.
    def crowdSourceLabels(self, incompleteExamples, imgIDx2ID):
        
        assert(type(incompleteExamples) == dict and type(imgIDx2ID) \
            == dict), 'crowdSourceLabels inputs need to be dictionaries'

        insufficientExamples = dict()
        completedExamples = dict()
        labels = dict()
        oldCompleted = dict()
        cvProb = None

        for imgID in incompleteExamples:
            labels[imgID] = {}
        [insufficientExamples, labels] = self.getOneNewWorkerLabelPerImage \
                (incompleteExamples,insufficientExamples, labels)

        while len(incompleteExamples) != 0:

            [insufficientExamples, labels] = \
                    self.getOneNewWorkerLabelPerImage(incompleteExamples, \
                    insufficientExamples, labels)

            [newCompletedExamples, insufficientExamples] = \
                    self.getCompletedExamples(incompleteExamples, \
                    insufficientExamples, labels, cvProb)

            completedExamples.update(newCompletedExamples)


            for imgID in newCompletedExamples:

                del incompleteExamples[imgID]
 
            #If no new examples have finished, no need to train/predict
            if (self.mode == 'cv' and not len(newCompletedExamples) == 0):
                tmp = sum([completedExamples[i] for i in completedExamples])
                
                #To train we need 2 classes
                if (tmp >= 2 and tmp <= (len(completedExamples) - 2)):
                    model = self.trainComputerVision(completedExamples, \
                            imgIDx2ID)
                    cvProb = self.computerVisionPrediction(model, \
                            completedExamples, imgIDx2ID)
            

        return [completedExamples, insufficientExamples, labels]

    def trainComputerVision(self, completedExamples, imgIDx2ID):

        linearSVC = SVC(kernel = 'linear', probability = True, max_iter = 30)
        y = []
        x = []
        for imgIDx in completedExamples:
            imgID = imgIDx2ID[imgIDx]
            y.append(completedExamples[imgIDx])
            x.append(self.features[str(imgID)])

        linearSVC.fit(x,y)

        return linearSVC

    #predict_proba returns a list of lists of length nrImg. Sublists have
    #probabilities for all possible values of ground truth.

    #For incomplete examples we use the SVC model to predict gt 
    #probabilities and for the examples that are completed we give image a
    #probability of 1.0 for all possible values of gt so that we have a 
    #list of all images in correct sampled order for cubam.

    #ATTENTION: When introducing non binary classes, change else sentence
    #to dimension of classes.
    def computerVisionPrediction(self, model, completedExamples, imgIDx2ID):

        features = cPickle.load(open(self.dirName + \
                '/featureVectors.pickle', 'r'))

        scores = cPickle.load(open(self.dirName + '/scores.pickle', 'r'))
        cvProb = []
        for imgIDx in imgIDx2ID:
            if imgIDx not in completedExamples:
                imgID = imgIDx2ID[imgIDx]
                cvProb.append(model.predict_proba \
                    (self.features[str(imgID)])[0])
            #TODO: Should I insert the probabilities the images finished with?
            else:
                cvProb.append([0.5, 0.5])
       
        return cvProb


    def getOneNewWorkerLabelPerImage(self, incompleteExamples, \
            insufficientExamples, labels):


        for imgID in incompleteExamples:
            if len(incompleteExamples[imgID]) != 0:
                workerKey = random.choice \
                        (list(incompleteExamples[imgID].keys()))

                labels[imgID][workerKey] = \
                        incompleteExamples[imgID][workerKey]
                del incompleteExamples[imgID][workerKey]
            else:
                #print("Annotations available for image label " + str(imgID) + " are not sufficient to predict with confidence")
                insufficientExamples[imgID] = 0.0
        
        for x in insufficientExamples:
            if x in incompleteExamples:
                del incompleteExamples[x]

        return [insufficientExamples, labels]
