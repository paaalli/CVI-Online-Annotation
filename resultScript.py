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
numWkr = 16
confList = [1,2.5,5,10,20] 
numTrial = 5
trainSize = 30

gtStream = open("bluebirds/gt.yaml", 'r')
groundTruth = yaml.load(gtStream)
labelStream = open("bluebirds/labels.yaml", 'r')
data = yaml.load(labelStream)

data = modelCheck.formatExamples(data)
features = cPickle.load(open(dataDir + '/featureVectors.pickle', 'r'))


cubamCVPCorrectRate = dict()
cubamCVTCorrectRate = dict()
cubamCorrectRate = dict()
cubamNoCVCorrectRate = dict()
majCorrectRate = dict()
simpleCorrectRate = dict()

#for numWkr in numWrkList:
for conf in confList:
    print "Generating trials for %d workers, %d conf" % (numWkr, conf)
    
    cubamCVPAllSumCorrect = []
    cubamCVPAvgWorkers = []

    cubamCVTSumCorrect = []
    cubamCVTAllSumCorrect = []
    cubamCVTAvgWorkers = []

    cubamSumCorrect = []
    cubamAllSumCorrect = []
    cubamAvgWorkers = []

    cubamNoCVSumCorrect = []
    cubamNoCVAllSumCorrect = []
    cubamNoCVAvgWorkers = []

    majSumCorrect = []

    simpleSumCorrect = []
    simpleAllSumCorrect = []
    simpleAvgWorkers = []
    
    for i in range(numTrial):
        #Notes: Stopping ratio of 3 corresponds to a ~95% probability of an event.
        print i

        #Shuffling the data so that the last 20 items in subsamped examples are
        #random between iterations. (Taking last 20 off to pretrain.)
        tmpData = deepcopy(data)
        tmpGT = deepcopy(groundTruth)

        #Using this subset both for pretrained cubam as well as solving x images
        #first and using them for training.
        trainSet = random.sample(set(tmpData), trainSize)
        cvpData = dict()
        cvpGT = dict()
        cvtX = []
        cvtY = []
        for k in trainSet:
            cvpData[k] = tmpData[k]
            cvpGT[k] = tmpGT[k]

            cvtX.append(features[str(k)])
            cvtY.append(groundTruth[k])
            del tmpData[k]
            del tmpGT[k]


        [incompleteExamples, imgIDx2ID, sampledGT] = \
        modelCheck.subSample(tmpData, tmpGT, numWkr)
        
        #Cubam, solving for x images first and using them to train CV.
        # cvpFile2 = debugDir + '/tmpcvp2.txt'
        # cvpFile1  =  debugDir + '/tmpcvp1.txt'

        # # [cvpExamples, cvpImgIDx2ID, cvpSampledGT] = \
        # # modelCheck.subSample(cvpData, cvpGT, numWkr)

        # # cubamModelCVP = CubamAnnotationModel(dataDir, stoppingRatio = 999999, \
        # #        debugFile = cvpFile1, mode = 'norm')
        
        # # [tmppppp,trainExamples,tmpLabels] = cubamModelCVP.crowdSourceLabels(cvpExamples, \
        # #        cvpImgIDx2ID)       

        # # tmpCorr = modelCheck.correctnessFactor(trainExamples, cvpSampledGT)
        # # [tmpTotal, tmpAvg] = modelCheck.annotationStatistics(tmpLabels)
       
        # # cvpX = []
        # # cvpY = []
        # # for cvpImgIDx in trainExamples:
        # #    cvpX.append(features[str(cvpImgIDx2ID[cvpImgIDx])])
        # #    cvpY.append(trainExamples[cvpImgIDx])

        # cubamModelCVP = CubamAnnotationModel(dataDir, stoppingRatio = conf, \
        #         debugFile = cvpFile2, partTrain = trainSize)
      
        # [cubamCompletedExamples, cubamInsufficientExamples, cubamCVPLabels] = \
        # cubamModelCVP.crowdSourceLabels(deepcopy(incompleteExamples), imgIDx2ID)

        # cvpCorr = modelCheck.correctnessFactor( \
        #         dict(cubamCompletedExamples.items() + \
        #         cubamInsufficientExamples.items()), sampledGT)

        # #print tmpCorr, cvpCorr
        # print cvpCorr
        # #cubamCVPAllSumCorrect.append((cvpCorr*(len(data)-trainSize) + tmpCorr*trainSize)\
        # #        /len(data))
        # cubamCVPAllSumCorrect.append(cvpCorr)

        # [cubamTotal, cubamCVPAvg] = modelCheck.annotationStatistics(cubamCVPLabels)
        # #cubamCVPAvgWorkers.append((cubamCVPAvg*(len(data)-trainSize) + \
        # #        tmpAvg*trainSize)/len(data))
        # cubamCVPAvgWorkers.append(cubamCVPAvg)
        # print cubamCVPAvgWorkers 


        # #Cubam with CV pretrained 
        cvtFile = debugDir + '/tmpcvt.txt'
        
        cubamModelCVT = CubamAnnotationModel(dataDir, stoppingRatio = conf, \
                debugFile = cvtFile, preTrain = zip(cvtX,cvtY))

        [cubamCompletedExamples, cubamInsufficientExamples, cubamCVTLabels] = \
        cubamModelCVT.crowdSourceLabels(deepcopy(incompleteExamples), imgIDx2ID)
        cubamCVTSumCorrect.append(modelCheck.correctnessFactor(cubamCompletedExamples, \
                sampledGT))
        
        cvtCorrect = modelCheck.correctnessFactor(dict(cubamCompletedExamples.items() \
                + cubamInsufficientExamples.items()), sampledGT)
 
        print cvtCorrect
        cubamCVTAllSumCorrect.append(cvtCorrect)
        
        [cubamTotal, cubamCVTAvg] = modelCheck.annotationStatistics(cubamCVTLabels)
        cubamCVTAvgWorkers.append(cubamCVTAvg)

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
        cubamNoCVSumCorrect.append(modelCheck.correctnessFactor \
                (cubamNoCVCompletedExamples, sampledGT))
        cubamNoCVAllSumCorrect.append( \
                modelCheck.correctnessFactor(dict(cubamNoCVCompletedExamples.items() \
                + cubamNoCVInsufficientExamples.items()), sampledGT))
        [cubamNoCVTotal, cubamNoCVAvg] = modelCheck.annotationStatistics(cubamNoCVLabels)
        cubamNoCVAvgWorkers.append(cubamNoCVAvg)





        #Taking together info from all cubam runs. 

        # fcvp = open(cvpFile1, 'r')
        # cvp1 = fcvp.readlines()
        # fcvp.close()
        # fcvp = open(cvpFile2, 'r')
        # cvp2 = fcvp.readlines()

        fcvt = open(cvtFile, 'r')
        cvt = fcvt.readlines()
        fcvt.close()


        fcv = open(cvFile, 'r')
        cv = fcv.readlines()
        fcv.close()     

        fnocv = open(noCvFile, 'r') 
        nocv = fnocv.readlines()
        fnocv.close()


        debugFile = debugDir + '/Iteration%d.txt' % i
        f = open(debugFile, 'w')
        f.write('')
 
        #Range - 2, because we dont optimize for the first 3 annotations, and we 
        #optimise after the last one. so 2 missing.
        for j in range(numWkr-2):

            f.write(cv[2*j] + cv[2*j+1] + nocv[2*j+1] + cvt[2*j] + cvt[2*j+1] + '\n')
        #    f.write(cvp1[2*j+1] + cvp2[] )
        #    f.write(nocv[2*j+1] + cvt[2*j] + cvt[2*j+1] + '\n')
        gtStr = ''
        for j in dict(cubamCompletedExamples.items() + cubamInsufficientExamples.items()):
             gtStr += "%0.2f   " % float(sampledGT[j])      
        f.write(gtStr)
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

 #  cubamCVPCorrectRate[conf] = [mean(cubamCVPAllSumCorrect), \
 #           std(cubamCVPAllSumCorrect)/sqrt(numTrial), mean(cubamCVPAvgWorkers), \
 #           std(cubamCVPAvgWorkers)/sqrt(numTrial)]
    cubamCVTCorrectRate[conf] = [mean(cubamCVTAllSumCorrect), \
            std(cubamCVTAllSumCorrect)/sqrt(numTrial), mean(cubamCVTAvgWorkers), \
            std(cubamCVTAvgWorkers)/sqrt(numTrial)]
#   cubamCorrectRate[numWkr] = [cubamSumCorrect/numTrial, cubamAllSumCorrect/numTrial, cubamAvgWorkers/numTrial]
#   cubamNoCVCorrectRate[numWkr] = [cubamNoCVSumCorrect/numTrial, cubamNoCVAllSumCorrect/numTrial, cubamNoCVAvgWorkers/numTrial]
#   majCorrectRate[numWkr] = [majSumCorrect/numTrial, numWkr]
#   simpleCorrectRate[numWkr] = [simpleSumCorrect/numTrial, simpleAllSumCorrect/numTrial, simpleAvgWorkers/numTrial]

# print(cubamCorrectRate, cubamNoCVCorrectRate, majCorrectRate, simpleCorrectRate)
#print cubamCVTCorrectRate, cubamCorrectRate, cubamNoCVCorrectRate
#print cubamCVPCorrectRate, cubamCVTCorrectRate, cubamNoCVCorrectRate
#with open('PTWrk=%i.yaml' % numWkr, 'w') as f:
#    f.write(yaml.dump(cubamCVTCorrectRate))



