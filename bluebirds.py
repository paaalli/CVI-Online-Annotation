import os, pickle
from numpy import random, mean, std, sqrt
from sklearn.svm import SVC
from matplotlib.pylab import figure
from copy import deepcopy

from CheckCubamAnnotationModel import *
from CubamAnnotationModel import *
from SimpleAnnotationModel import *

from cubam import Binary1dSignalModel, BinaryBiasModel
from cubam.utils import majority_vote, read_data_file

import time

#   fileName = 'bluebirds/labels.yaml'
dataDir = 'data/bluebirds'
debugDir = 'data/bluebirds/debug'

modelCheck = CheckCubamAnnotationModel()
modelCheck.createDir(dataDir)
modelCheck.createDir(debugDir)


simpleModel = SimpleAnnotationModel(dataDir)

#numWrkList = [2,4,6,8,10,12,14,16,18,20]
numWrkList = [20]
numTrial = 20

gtStream = open("bluebirds/gt.yaml", 'r')
groundTruth = yaml.load(gtStream)
labelStream = open("bluebirds/labels.yaml", 'r')
data = yaml.load(labelStream)

data = modelCheck.formatExamples(data)
features = cPickle.load(open(dataDir + '/featureVectors.pickle', 'r'))



cubamCVTCorrectRate = dict()
cubamCorrectRate = dict()
cubamNoCVCorrectRate = dict()
majCorrectRate = dict()
simpleCorrectRate = dict()

for numWkr in numWrkList:
    print "Generating trials for %d workers" % numWkr
    
    cubamCVTSumCorrect = 0.0
    cubamCVTAllSumCorrect = 0.0
    cubamAvgWorkers = 0.0

    cubamSumCorrect = 0.0
    cubamAllSumCorrect = 0.0
    cubamAvgWorkers = 0.0

    cubamNoCVSumCorrect = 0.0
    cubamNoCVAllSumCorrect = 0.0
    cubamNoCVAvgWorkers = 0.0

    majSumCorrect = 0.0

    simpleSumCorrect = 0.0
    simpleAllSumCorrect = 0.0
    simpleAvgWorkers = 0.0
    
    for i in range(numTrial):
        print i
        [incompleteExamples, imgIDx2ID, sampledGT] = \
        modelCheck.subSample(data, groundTruth, numWkr)
        #Cubam with CV pretrained 
        cvtFile = debugDir + 'tmpcvt.txt'

        cvtExamples = deepcopy(incompleteExamples)
        cvtGT = deepcopy(sampledGT)
        trainSet = random.sample(set(cvtExamples), 20)
        x = []
        y = []
        for i in trainSet:
            x.append(features[str(imgIDx2ID[i])])
            y.append(cvtGT[i])
            del cvtExamples[i]
            del cvtGT[i]


        svc = SVC(kernel = 'linear', probability = True, max_iter = 40)
        svc.fit(x,y)
        
        cubamModelCVT = CubamAnnotationModel(dataDir, stoppingRatio = 5, \
                debugFile = cvtFile)

        [cubamCompletedExamples, cubamInsufficientExamples, cubamLabels] = \
        cubamModelCVT.crowdSourceLabels(cvtExamples, imgIDx2ID)
        cubamCVTSumCorrect += modelCheck.correctnessFactor(cubamCompletedExamples, cvtGT)
        cubamCVTAllSumCorrect += \
        modelCheck.correctnessFactor(dict(cubamCompletedExamples.items() + cubamInsufficientExamples.items()), sampledGT)

        [cubamTotal, cubamCVTAvg] = modelCheck.annotationStatistics(cubamLabels)
        cubamCVTAvgWorkers += cubamCVTAvg

        #Cubam with CV      
        cvFile = debugDir + '/tmpcv.txt'
        cubamModel = CubamAnnotationModel(dataDir, stoppingRatio = 5, \
                debugFile = cvFile)

        [cubamCompletedExamples, cubamInsufficientExamples, cubamLabels] = \
        cubamModel.crowdSourceLabels(deepcopy(incompleteExamples), imgIDx2ID)
        cubamSumCorrect += modelCheck.correctnessFactor(cubamCompletedExamples, sampledGT)
        cubamAllSumCorrect += \
        modelCheck.correctnessFactor(dict(cubamCompletedExamples.items() + cubamInsufficientExamples.items()), sampledGT)

        [cubamTotal, cubamAvg] = modelCheck.annotationStatistics(cubamLabels)
        cubamAvgWorkers += cubamAvg


        #Cubam w/o CV
        noCvFile = debugDir + '/tmpnocv.txt'
        cubamModelNoCV = CubamAnnotationModel(dataDir, mode = 'norm', \
                stoppingRatio = 5, debugFile = noCvFile)

        [cubamNoCVCompletedExamples, cubamNoCVInsufficientExamples, cubamNoCVLabels] = \
                cubamModelNoCV.crowdSourceLabels(deepcopy(incompleteExamples), imgIDx2ID)
        cubamNoCVSumCorrect += modelCheck.correctnessFactor(cubamNoCVCompletedExamples, sampledGT)
        cubamNoCVAllSumCorrect += \
                modelCheck.correctnessFactor(dict(cubamNoCVCompletedExamples.items() + cubamNoCVInsufficientExamples.items()), sampledGT)
        [cubamNoCVTotal, cubamNoCVAvg] = modelCheck.annotationStatistics(cubamNoCVLabels)
        cubamNoCVAvgWorkers += cubamNoCVAvg

        debugFile = debugDir + '/Iteration%d.txt' % i
        f = open(debugFile, 'w')
        f.write('')
        f.close()

        fcv = open(cvFile, 'r')
        cv = fcv.readlines()
        fcv.close()     

        fnocv = open(noCvFile, 'r') 
        nocv = fnocv.readlines()
        fnocv.close()

        #Taking together info from both cubam runs. 
        f = open(debugFile, 'a')    
        
        for i in range(numWkr):

            f.write(cv[i] + nocv[2*i + 1] + cv[2*i + 1] + '\n')

        f = open(debugFile, 'a')
        gtStr = ''
        for i in dict(cubamCompletedExamples.items() + cubamInsufficientExamples.items()):
            gtStr += str(int(sampledGT[i])) + '       '


        f.write(gtStr + '\n\n\n')
        f.close()
        



#       #Simple model w/o CV
#       [simpleCompletedExamples, simpleInsufficientExamples, simpleLabels] = \
#       simpleModel.crowdSourceLabels(deepcopy(incompleteExamples), imgIDx2ID)
#       simpleSumCorrect += modelCheck.correctnessFactor(simpleCompletedExamples, sampledGT)
#       simpleAllSumCorrect += \
#       modelCheck.correctnessFactor(dict(simpleCompletedExamples.items() + simpleInsufficientExamples.items()), sampledGT)

#       [simpleTotal, simpleAvg] = modelCheck.annotationStatistics(simpleLabels)
#       simpleAvgWorkers += simpleAvg

#       #Majority vote
#       majCompletedExamples = majority_vote(incompleteExamples.copy()) 
#       majSumCorrect += modelCheck.correctnessFactor(majCompletedExamples, sampledGT)

    cubamCVTCorrectRate[numWkr] = [cubamCVTSumCorrect/numTrial, cubamCVTAllSumCorrect/numTrial, cubamCVTAvgWorkers/numTrial]
    cubamCorrectRate[numWkr] = [cubamSumCorrect/numTrial, cubamAllSumCorrect/numTrial, cubamAvgWorkers/numTrial]
    cubamNoCVCorrectRate[numWkr] = [cubamNoCVSumCorrect/numTrial, cubamNoCVAllSumCorrect/numTrial, cubamNoCVAvgWorkers/numTrial]
#   majCorrectRate[numWkr] = [majSumCorrect/numTrial, numWkr]
#   simpleCorrectRate[numWkr] = [simpleSumCorrect/numTrial, simpleAllSumCorrect/numTrial, simpleAvgWorkers/numTrial]

# print(cubamCorrectRate, cubamNoCVCorrectRate, majCorrectRate, simpleCorrectRate)
print cubamCVTCorrectRate, cubamCorrectRate, cubamNoCVCorrectRate





