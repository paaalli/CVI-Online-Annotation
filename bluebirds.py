import os, pickle
from numpy import random, mean, std, sqrt
from matplotlib.pylab import figure
from copy import deepcopy

from CheckCubamAnnotationModel import *
from CubamAnnotationModel import *
from SimpleAnnotationModel import *

from cubam import Binary1dSignalModel, BinaryBiasModel
from cubam.utils import majority_vote, read_data_file

#   fileName = 'bluebirds/labels.yaml'
dataDir = 'data/bluebirds'

modelCheck = CheckCubamAnnotationModel()
modelCheck.createDir(dataDir)

cubamModel = CubamAnnotationModel(dataDir)
cubamModelNoCV = CubamAnnotationModel(dataDir, mode = 'norm')
simpleModel = SimpleAnnotationModel(dataDir)

#numWrkList = [2,4,6,8,10,12,14,16,18,20]
numWrkList = [20]
numTrial = 20

#Checks for real data
gtStream = open("bluebirds/gt.yaml", 'r')
groundTruth = yaml.load(gtStream)
labelStream = open("bluebirds/labels.yaml", 'r')
data = yaml.load(labelStream)

data = modelCheck.formatExamples(data)

cubamCorrectRate = dict()
cubamNoCVCorrectRate = dict()
majCorrectRate = dict()
simpleCorrectRate = dict()

for numWkr in numWrkList:
	print "Generating trials for %d workers" % numWkr
	
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

		#Cubam with CV
		[cubamCompletedExamples, cubamInsufficientExamples, cubamLabels] = \
		cubamModel.crowdSourceLabels(deepcopy(incompleteExamples), imgIDx2ID)
		cubamSumCorrect += modelCheck.correctnessFactor(cubamCompletedExamples, sampledGT)
		cubamAllSumCorrect += \
		modelCheck.correctnessFactor(dict(cubamCompletedExamples.items() + cubamInsufficientExamples.items()), sampledGT)

		[cubamTotal, cubamAvg] = modelCheck.annotationStatistics(cubamLabels)
		cubamAvgWorkers += cubamAvg

		#Cubam w/o CV
		[cubamNoCVCompletedExamples, cubamNoCVInsufficientExamples, cubamNoCVLabels] = \
		cubamModelNoCV.crowdSourceLabels(deepcopy(incompleteExamples), imgIDx2ID)
		cubamNoCVSumCorrect += modelCheck.correctnessFactor(cubamNoCVCompletedExamples, sampledGT)
		cubamNoCVAllSumCorrect += \
		modelCheck.correctnessFactor(dict(cubamNoCVCompletedExamples.items() + cubamNoCVInsufficientExamples.items()), sampledGT)

		[cubamNoCVTotal, cubamNoCVAvg] = modelCheck.annotationStatistics(cubamNoCVLabels)
		cubamNoCVAvgWorkers += cubamNoCVAvg

		#Simple model w/o CV
		[simpleCompletedExamples, simpleInsufficientExamples, simpleLabels] = \
		simpleModel.crowdSourceLabels(deepcopy(incompleteExamples), imgIDx2ID)
		simpleSumCorrect += modelCheck.correctnessFactor(simpleCompletedExamples, sampledGT)
		simpleAllSumCorrect += \
		modelCheck.correctnessFactor(dict(simpleCompletedExamples.items() + simpleInsufficientExamples.items()), sampledGT)

		[simpleTotal, simpleAvg] = modelCheck.annotationStatistics(simpleLabels)
		simpleAvgWorkers += simpleAvg

		#Majority vote
		majCompletedExamples = majority_vote(incompleteExamples.copy()) 
		majSumCorrect += modelCheck.correctnessFactor(majCompletedExamples, sampledGT)

	cubamCorrectRate[numWkr] = [cubamSumCorrect/numTrial, cubamAllSumCorrect/numTrial, cubamAvgWorkers/numTrial]
	cubamNoCVCorrectRate[numWkr] = [cubamNoCVSumCorrect/numTrial, cubamNoCVAllSumCorrect/numTrial, cubamNoCVAvgWorkers/numTrial]
	majCorrectRate[numWkr] = [majSumCorrect/numTrial, numWkr]
	simpleCorrectRate[numWkr] = [simpleSumCorrect/numTrial, simpleAllSumCorrect/numTrial, simpleAvgWorkers/numTrial]

print(cubamCorrectRate, cubamNoCVCorrectRate, majCorrectRate, simpleCorrectRate)







