from cubam import Binary1dSignalModel, BinaryBiasModel
from cubam.utils import read_data_file

from AnnotationModel import *

import time

class CubamAnnotationModel(AnnotationModel):
    

    #bernoulli prior for py=1)
    beta = 0.5
    #theta^2 is the variance for the distribution of x
    theta = 0.8


    #flag = 0 or 1, 0 means we're getting annotations from an already labelled dataset
    #1 means we're getting annotations from MTTurk.
    def __init__(self, dirName, stoppingRatio = 5, mode = 'cv', flag = 0):
        
        self.flag = flag
        self.cubamDataFile = '%s/data.txt' % dirName

        super(CubamAnnotationModel, self).__init__(dirName, stoppingRatio, mode)



    def optimiseProbability(self, labels, cvProb = None):
        
        self.__saveData(labels)
        model = Binary1dSignalModel(filename = self.cubamDataFile)

        if(cvProb != None):
            model.optimize_param(numIter=15)
            model.optimize_param_cv(cvProb, numIter=15)
        else:
            model.optimize_param()

        x = model.get_image_param()
        #If xi > 0 we estimate that the label is y == 1, otherwise  y == 0
        #we append the label estimation to the x value.
        for imgID in x:
            x[imgID].append(int(x[imgID][0] > 0))

        predictions = self.__calcProbability(x)

        return predictions 

    #calculates probability for each distribution value of x.

    #p(z|x) = p(x|z)/(p(x|!z) + p(x|z)
    # where p(x|z) = exp(-(x-1)^2/(2*theta^2)/(sqrt(2pi)*theta)
    # and p(x|!z) = exp(-(x+1)^2/(2*theta^2)/(sqrt(2pi)*theta)
    def __calcProbability(self, x):
        
        for imgID in x:
            p1 = exp(-(pow(x[imgID][0] - 1, 2)/(2*pow(self.theta,2)))) \
                / (sqrt(2*pi)*0.8)

            p2 = exp(-(pow(x[imgID][0] + 1, 2)/(2*pow(self.theta,2)))) \
                / (sqrt(2*pi)*0.8)

            if x[imgID][1]:
                x[imgID][0] = p1/(p1+p2)
            else:
                x[imgID][0] = p2/(p1+p2)
        return x

    def __saveData(self, labels):

        
        fout = open(self.cubamDataFile, 'w')
        #temporary filewriting, gonna change cubam toolbox later.
        wkrIDs = set(wrkID for imgID in labels for wrkID in labels[imgID])
        total = self.getNrOfLabels(labels)
        fout.write("%d %d %d\n" % (len(labels), len(wkrIDs), total))

        for imgID in labels:
            for wrkID in labels[imgID]:
                fout.write("%d %d %d\n" % (imgID, wrkID, labels[imgID][wrkID]))
        fout.close()
        
    def getOneNewWorkerLabelPerImage(self, incompleteExamples, insufficientExamples, labels):
        if self.flag:
            return self.__getLabelsFromMTTurk(incompleteExamples, labels)
        else:
            return super(CubamAnnotationModel, self).getOneNewWorkerLabelPerImage(incompleteExamples, insufficientExamples, labels)

    def __getLabelsFromMTTurk(self, incompleteExamples, labels):
        pass

    def getNrOfLabels(self, data):
        return   sum(len(data[imgID]) for imgID in data)
