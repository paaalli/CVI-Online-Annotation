import os
from CheckAnnotationModel import *
from CubamAnnotationModel import *


class CheckCubamAnnotationModel(CheckAnnotationModel):


    def __init__(self):
        pass
            
    def createDir(self, dirName):
        if not os.path.exists(dirName): os.makedirs(dirName)



# modelCheck = CheckCubamAnnotationModel()
# modelCheck.createDir(dataDir)

# model = CubamAnnotationModel(dataDir

# #incompleteExamples is a dictionary with worker ids as keys
# #and the corresponding values are dictionaries with image ids as keys
# #and corresponding labels as values.
# incompleteExamples = modelCheck.formatExamples(yaml.load(open(fileName)))
# groundTruth = yaml.load(open('bluebirds/gt.yaml', 'r'))
# #used to subsample the data, used to try and get past segmentation fault.

# [incompleteExamples, groundTruth] = modelCheck.subSample(incompleteExamples, groundTruth)

# for id in incompleteExamples:
#     print len(incompleteExamples[id])

# [completedExamples, labels] = model.crowdSourceLabels(incompleteExamples)
# print(modelCheck.correctnessFactor(completedExamples, groundTruth))
# print(modelCheck.annotationStatistics(labels))    
