import os
from CheckAnnotationModel import *
from CubamAnnotationModel import *


class CheckCubamAnnotationModel(CheckAnnotationModel):


    def __init__(self):
        pass
            
    def createDir(self, dirName):
        if not os.path.exists(dirName): os.makedirs(dirName)

    #Changes imgIDs and workerIDs to numbers from 0...len instead of real
    #ids.
    def subSample(self, data, groundTruth):
        
        wkrIDs = set(wrkID for imgID in data for wrkID in data[imgID])
        wkrId2Idx = dict((id, idx) for (idx, id) in enumerate(wkrIDs))

        for i, imgID in enumerate(data):
            data[i] = data.pop(imgID)
            groundTruth[i] = groundTruth.pop(imgID)
            for wrkID in list(data[i]):
                data[i][wkrId2Idx[wrkID]] = data[i].pop(wrkID)

        return [data, groundTruth]




def main():

    fileName = 'bluebirds/labels.yaml'
    dataDir = 'data/bluebirds'
    
    modelCheck = CheckCubamAnnotationModel()
    modelCheck.createDir(dataDir)

    model = CubamAnnotationModel(dataDir)
    
    #incompleteExamples is a dictionary with worker ids as keys
    #and the corresponding values are dictionaries with image ids as keys
    #and corresponding labels as values.
    incompleteExamples = modelCheck.formatExamples(yaml.load(open(fileName)))
    groundTruth = yaml.load(open('bluebirds/gt.yaml', 'r'))
    #used to subsample the data, used to try and get past segmentation fault.

    [incompleteExamples, groundTruth] = modelCheck.subSample(incompleteExamples, groundTruth)
    
    for id in incompleteExamples:
        print len(incompleteExamples[id])

    [completedExamples, labels] = model.crowdSourceLabels(incompleteExamples)
    print(modelCheck.correctnessFactor(completedExamples, groundTruth))
    print(modelCheck.annotationStatistics(labels))    




if __name__ == "__main__":
    main()
