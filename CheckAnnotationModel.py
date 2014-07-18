import random
import yaml

#Abstract Base class for model checking

class CheckAnnotationModel():



    def __init__(self):
        pass

    def correctnessFactor(self, completedExamples, groundTruth):
        correct = 0.0
        total = 0
        for x in completedExamples:
            total = total + 1
            if completedExamples[x] == groundTruth[x]:
                correct += 1
        if total != 0:
            return (correct/total)
        else:
            return 0

    def annotationStatistics(self, labels):
        total = 0.0
        for x in labels:
            total += len(labels[x])
        avg = total/len(labels)
        return [total, avg]

    #B: uncompletedExamples is a dictionary of dictionaries with worker
    #ids as keys. For each key there is a corresponding dictionary with
    #img ids as keys and labels as values
    #
    #A: return a dictionary with img ids as keys and dictionaries as values
    #   where worker ids are keys and labels are values
    def formatExamples(self, uncompletedExamples):
    	formattedExamples = dict()
    	for workerID in uncompletedExamples:
    		for imgID in uncompletedExamples[workerID]:
    		 	if imgID in formattedExamples:
    		 		formattedExamples[imgID].update({workerID: int(uncompletedExamples[workerID][imgID])})
    		 	else:
    		 		formattedExamples[imgID] = {workerID: int(uncompletedExamples[workerID][imgID])}
   	
   	#dont understand, with correct indentation, the return statement is put inside the for loop,
   	#all my wot.

   	return formattedExamples

    #Changes imgIDs and workerIDs to numbers from 0...len instead of real
    #ids and gives only as many workers as nrWorkers specified
    def subSample(self, data, groundTruth, nrWorkers):
        
        wrkIDs = set(wrkID for imgID in data for wrkID in data[imgID])
        if (nrWorkers < len(wrkIDs)):
            wrkIDs = set(random.sample(wrkIDs, nrWorkers))
        wrkId2Idx = dict((id, idx) for (idx, id) in enumerate(wrkIDs))

        sampledData = dict()
        sampledGT = dict()
        imgIDx2ID = dict()
        for i, imgID in enumerate(data):
            sampledData[i] = dict()
            sampledGT[i] = groundTruth[imgID]
            imgIDx2ID[i] = imgID
            for wrkID in list(data[imgID]):
                if wrkID in wrkIDs:
                    sampledData[i][wrkId2Idx[wrkID]] = data[imgID][wrkID]

        return [sampledData, imgIDx2ID, sampledGT]

