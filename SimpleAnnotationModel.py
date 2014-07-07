import random
import math
from AnnotationModel import *
# For binary classification, y is an element in {0,1}

class SimpleAnnotationModel(AnnotationModel):

    #lambdafp: p(z = 1 | y = -1, lambda)
    #lambdafn: p(z = -1 | y = 1, lambda)
    #lambdatp: p(z = 1 | y = 1, lambda)
    #lambdatn: p(z = -1 | y = -1, lambda)
    #pyx: p(y|x)


    #defining prior for p(y|x)
    pyx = 0.5

    #stoppingRatio: stoppingRatio for sequential probability ratio test
    stoppingRatio = 15


    def __init__(self, lambdaf = [0.05, 0.05]):

        self.lambdafp = lambdaf[0]
        self.lambdafn = lambdaf[1]
        self.lambdatp = 1 - self.lambdafn
        self.lambdatn = 1 - self.lambdafp



    #MODEL CHECKING. This function uses a simple model to simulate annotators. Annotations are based on ground
    #truth labels and the probabilities lambdatp, lambatn, lambdafp, lambdafn (class variables). Since this model
    #uses ground truth label it is for testing purposes only.

    #For synthetic data, dataExamples are unlabelled, for real data, dataExampls are labelled.
    def getOneNewWorkerLabelPerImage(self, incompleteExamples, labels):

        insufficientExamples = dict()

        for imgID in incompleteExamples:
            if len(incompleteExamples[imgID]) != 0:
                workerKey = random.choice(list(incompleteExamples[imgID].keys()))
                labels[imgID][workerKey] = incompleteExamples[imgID][workerKey]
                del incompleteExamples[imgID][workerKey]
            else:
                print("Annotations available for image label " + str(imgID) + " are not sufficient to predict with confidence")
                insufficientExamples[imgID] = True
        
        for x in insufficientExamples:
            del incompleteExamples[x]

        return labels

   
    #returns: y* = argmax(y) p(y|x)*PI(p(zij|y) for zi1..zin) / sigma(p(y'|x)*PI(p(zij|y') for zi1...zin) for all y),
    #         p(y*|x,z)
    #         p(!y*|x,z)
    #Model checking. For now only implements optimization of binary labels
    #imageLabels: list of labels for a certain image
    def optimiseProbability(self, labels):

        predictions = {}
        p1 = self.pyx
        p2 = 1 - p1
        for imgID in labels:
            p3 = 1
            p4 = 1
            for wrkID in labels[imgID]:
                p3 *= self.__getConditional(labels[imgID][wrkID], 1)
                p4 *= self.__getConditional(labels[imgID][wrkID], 0)

            py1 = p1*p3
            py0 = p2*p4
            pSum = py1 + py0
            if (py1> py0):
                pyCond = py1 / pSum
                predictions[imgID] = [pyCond, 1]
            else:
                pyCond = py0 / pSum
                predictions[imgID] = [pyCond, 0]

        return predictions


    #returns the lambda probability value for given label and groundtruth
    def __getConditional(self, label, y):
        if (label == 1):
            if y == 1:
                return self.lambdatp
            else:
                return self.lambdafp
        else:
            if (y == 1):
                return self.lambdafn
            else:
                return self.lambdatn


