from sklearn.svm import SVC
import numpy as np

import cPickle

import random
from math import log, exp, sqrt, pow, pi

class AnnotationModel(object):

    #preTrain is a list of tuples for each image in the pretrain image set.
    #each tuple has a list of features and then the ground truth value for
    #that image.
    def __init__(self, dirName, stoppingRatio = '3', 
            mode = 'norm', preTrain = None, partTrain = None, pickBest = False, \
            cvCheck = False):
        
        self.dirName = dirName
        self.stoppingRatio = stoppingRatio

        assert (mode == 'norm' or mode == 'cv'), "Mode is either 'norm' or 'cv'"
        
        self.mode = mode
        self.partTrain = partTrain
        self.pickBest = pickBest
        self.cvCheck = cvCheck

        if (self.mode == 'cv'):
            self.features = cPickle.load(open(self.dirName + '/featureVectors.pickle', 'r'))
            self.scores = cPickle.load(open(self.dirName + '/scores.pickle', 'r'))
            self.svc = SVC(kernel = 'linear', probability = True, max_iter = 40)

            if preTrain:
                self.preTrain = preTrain
                self.svcFlag = True
            else:
                self.svcFlag = False

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

        completedExamples = dict()

        #predictions is a dictionary of lists with imageIDs as keys and
        #a key's value is a list with [probability, label prediction]
        predictions = self.optimiseProbability(labels, cvProb)

        for imgID in predictions:
            y = predictions[imgID][1]
            #py = p(y | xi, zi, vi)
            py = predictions[imgID][0]
            if (imgID in incompleteExamples and self.stoppingRatio < log(py/(1-py))):
                completedExamples[imgID] = y

            if imgID in insufficientExamples:
                insufficientExamples[imgID] = y

        return completedExamples

    def optimiseProbability(labels, cvProb = None):
        pass

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
        newCompletedExamples = dict()
        cvProb = None

        for imgID in incompleteExamples:
            labels[imgID] = {}


        for i in range(4):
            self.getOneNewWorkerLabelPerImage\
                    (incompleteExamples, insufficientExamples, labels)

        #Finishing partTrain amount of images first to train the computer vision 
        #algorithm with.
        if self.partTrain:
            assert(len(incompleteExamples) >= self.partTrain)
            self.__completePart(incompleteExamples,completedExamples, labels)
            #TEMPORARY, ONLY FOR cvCheck!
            if self.cvCheck:
                return completedExamples

        while len(incompleteExamples) != 0:


            #If no new examples have finished, no need to train/predict
            if (self.mode == 'cv' and (len(newCompletedExamples) != 0 or self.svcFlag)):
                tmp = sum([completedExamples[i] for i in completedExamples])
                
                #To train we need 2 classes(2 of each at least for training/validation)
                if ((tmp >= 2 and tmp <= (len(completedExamples) - 2)) or self.svcFlag):
                    self.trainComputerVision(completedExamples, imgIDx2ID)
                    cvProb = self.computerVisionPrediction(completedExamples, imgIDx2ID) 
        
            newCompletedExamples = self.getCompletedExamples(incompleteExamples, \
                    insufficientExamples, labels, cvProb)

            completedExamples.update(newCompletedExamples)


            for imgID in newCompletedExamples:

                del incompleteExamples[imgID]

            self.getOneNewWorkerLabelPerImage(incompleteExamples, \
                    insufficientExamples, labels)
 
        return [completedExamples, insufficientExamples, labels]


    def __completePart(self, incompleteExamples, completedExamples, labels):
        trainExamples = dict()

        if self.pickBest:
            trainSet = self.__getMostConfSet(labels)
        else:
            trainSet = random.sample(set(incompleteExamples), self.partTrain)

        for imgID in trainSet:
            trainExamples[imgID] = incompleteExamples[imgID]
            del incompleteExamples[imgID]

        while len(trainExamples) != 0:
            self.getOneNewWorkerLabelPerImage(trainExamples, completedExamples, labels)

        pred = self.optimiseProbability(labels)

        for imgID in completedExamples:
            completedExamples[imgID] = pred[imgID][1]

    def __getMostConfSet(self, labels):
        predictions = self.optimiseProbability(labels)
        trainIDs = set()


        predOne = []
        predZero = []
        for i in predictions:
            if predictions[i][1]:
                predOne.append((predictions[i][0], i))
            else:
                predZero.append((predictions[i][0], i))
        
        predOne.sort(reverse = True)
        predZero.sort(reverse = True)

        for i in range(min(len(predOne), len(predZero))):
            if len(trainIDs) == self.partTrain:
                break
            trainIDs.add(predOne.pop(0)[1])
            if len(trainIDs) == self.partTrain:
                break
            trainIDs.add(predZero.pop(0)[1])

        tmp = len(trainIDs)
        if len(predOne) == 0:
            for i in range(self.partTrain-tmp):
                trainIDs.add(predZero.pop(0)[1])
        elif len(predZero) == 0:
            for i in range(self.partTrain-tmp):
                trainIDs.add(predOne.pop(0)[1])

        # #For just the top conf predictions.
        # probImgTuples = [] 
        # for i in predictions:
        #     probImgTuples.append((predictions[i][0], i))
        # probImgTuples.sort(reverse = True)
        # for i in range(self.partTrain):
        #     trainIDs.add(probImgTuples[i][1])

        return trainIDs

    def trainComputerVision(self, completedExamples, imgIDx2ID):

        y = []
        x = []
        if self.svcFlag:
            for i in range(len(self.preTrain)):
                x.append(self.preTrain[i][0])
                y.append(self.preTrain[i][1])

        for imgIDx in completedExamples:
            imgID = imgIDx2ID[imgIDx]
            y.append(completedExamples[imgIDx])
            x.append(self.features[str(imgID)])

        self.svc.fit(x,y)


    #predict_proba returns a list of lists of length nrImg. Sublists have
    #probabilities for all possible values of ground truth.

    #For incomplete examples we use the SVC model to predict gt 
    #probabilities and for the examples that are completed we give image a
    #probability of 1.0 for all possible values of gt so that we have a 
    #list of all images in correct sampled order for cubam.

    #ATTENTION: When introducing non binary classes, change else sentence
    #to dimension of classes.
    def computerVisionPrediction(self, completedExamples, imgIDx2ID):

        features = cPickle.load(open(self.dirName + \
                '/featureVectors.pickle', 'r'))

        scores = cPickle.load(open(self.dirName + '/scores.pickle', 'r'))
        cvProb = []
        for imgIDx in imgIDx2ID:
            if imgIDx not in completedExamples:
                imgID = imgIDx2ID[imgIDx]
                cvProb.append(self.svc.predict_proba \
                    (self.features[str(imgID)])[0])
            #TODO: Should I insert the probabilities the images finished with?
            else:
                cvProb.append([0.5, 0.5])
       
        return cvProb


    def getOneNewWorkerLabelPerImage(self, incompleteExamples, \
            insufficientExamples, labels):
        for imgID in incompleteExamples:
            if len(incompleteExamples[imgID]) != 0:
                #workerKey = random.choice \
                #        (list(incompleteExamples[imgID].keys()))
                workerKey = min(incompleteExamples[imgID].keys())

                labels[imgID][workerKey] = \
                        incompleteExamples[imgID][workerKey]
                del incompleteExamples[imgID][workerKey]
            else:
                #print("Annotations available for image label " + str(imgID) + " are not sufficient to predict with confidence")
                insufficientExamples[imgID] = 0.0
        
        for x in insufficientExamples:
            if x in incompleteExamples:
                del incompleteExamples[x]
