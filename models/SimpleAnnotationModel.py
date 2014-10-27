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



    def __init__(self, dirName, lambdaf = [0.05, 0.05], stoppingRatio = 5, mode = 'cv'):

        self.lambdafp = lambdaf[0]
        self.lambdafn = lambdaf[1]
        self.lambdatp = 1 - self.lambdafn
        self.lambdatn = 1 - self.lambdafp


        super(SimpleAnnotationModel, self).__init__(dirName, stoppingRatio, mode)


   
    #returns: y* = argmax(y) p(y|x)*PI(p(zij|y) for zi1..zin) / sigma(p(y'|x)*PI(p(zij|y') for zi1...zin) for all y),
    #         p(y*|x,z)
    #         p(!y*|x,z)
    #Model checking. For now only implements optimization of binary labels
    #imageLabels: list of labels for a certain image

    #TODO: Work the cvProb into the probability.
    def optimiseProbability(self, labels, cvProb = None):

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


