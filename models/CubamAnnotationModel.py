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
    def __init__(self, dirName, stoppingRatio = 5, mode = 'cv', flag = 0, \
                debugFile = None, preTrain = None, partTrain = None, \
                pickBest = False, cvCheck = False):
        
        self.flag = flag
        self.cubamDataFile = '%s/data.txt' % dirName

        super(CubamAnnotationModel, self).__init__(dirName, stoppingRatio, mode, \
                preTrain, partTrain, pickBest, cvCheck)

        self.file = None
        self.debugFile = None

        if debugFile:
            self.debugFile = debugFile
            f = open(self.debugFile, 'w')
            f.write('')
            f.close()


    def optimiseProbability(self, labels, cvProb = None):
        
        self.__saveData(labels)
        model = Binary1dSignalModel(filename = self.cubamDataFile)
        if cvProb:
            model.optimize_param(numIter=15) 
            model.optimize_param_cv(cvProb, numIter=15)
        else:
            model.optimize_param()
            
        combProb = model.get_image_prob()

        if self.debugFile:                
            #String vectors to print to html file. Shows probabilities of p(z=1|..)
            cvStr = ''
            combStr = ''
            for imgID in combProb:
                if cvProb:
                    cvStr += "%0.2f   " % cvProb[imgID][1]
                else:
                    cvStr += "5.00   "
                combStr += "%0.2f   " % combProb[imgID][0]

            f = open(self.debugFile, 'a')
            f.write(cvStr + '\n' + combStr +
             '\n')
            f.close()

        #If xi > 0.5 we estimate that the label is y == 1, otherwise  y == 0
        #and fix the probability to represent p(z=0|x)
        #We append the label estimation to the x value.
        predictions = combProb

        for imgID in predictions:
            if predictions[imgID][0] > 0.5:
                predictions[imgID].append(1)
            else:
                predictions[imgID][0] = 1 - predictions[imgID][0]
                predictions[imgID].append(0)
        

        return predictions



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
