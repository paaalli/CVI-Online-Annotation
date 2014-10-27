import random
import yaml

#Abstract Base class for model checking

class CheckAnnotationModel():



    def __init__(self):
        pass

    def correctnessFactor(self, completedExamples, groundTruth):
        assert(len(completedExamples) == len(groundTruth))
        assert(type(completedExamples) == type(groundTruth))

        if len(completedExamples) == 0:
            return 0

        if type(completedExamples) == list:
            return self.__correctnessFactorList(completedExamples, groundTruth)
        elif type(completedExamples) == dict:
            return self.__correctnessFactorDict(completedExamples, groundTruth)
        else:
            raise error('correctnessFactor requires input to be list or dict')

    def __correctnessFactorList(self, completedExamples, groundTruth):
        correct = 0.0
        total = 0
        for x in range(len(completedExamples)) :
            total += 1
            if completedExamples[x] == groundTruth[x]:
                correct += 1
        return correct/total

    def __correctnessFactorDict(self, completedExamples, groundTruth):
        correct = 0.0
        total = 0
        for x in completedExamples:
            total += 1
            if completedExamples[x] == groundTruth[x]:
                correct += 1
        return correct/total


    def annotationStatistics(self, labels):
        total = 0.0
        annImg = dict()
        for x in labels:
            total += len(labels[x])
            annImg[x] = len(labels[x])
        print annImg
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

    # #Changes imgIDs and workerIDs to numbers from 0...len instead of real
    # #ids and gives only as many workers as nrWorkers specified
    # def subSample(self, data, groundTruth, nrWorkers):
        
    #     wrkIDs = set(wrkID for imgID in data for wrkID in data[imgID])
    #     wrkId2Idx = dict((id, idx) for (idx, id) in enumerate(wrkIDs))

    #     sampledData = dict()
    #     sampledGT = dict()
    #     imgIDx2ID = dict()
    #     for i, imgID in enumerate(data):
    #         sampledData[i] = dict()
    #         sampledGT[i] = groundTruth[imgID]
    #         imgIDx2ID[i] = imgID
    #         #try: 
    #         imgWrkIDs =  random.sample(set(data[imgID]), nrWorkers)
    #         for wrkID in list(data[imgID]):
    #             if wrkID in imgWrkIDs:
    #                 sampledData[i][wrkId2Idx[wrkID]] = data[imgID][wrkID]
    #         #except Exception:
    #             #print "You can't use more annotations than are available"
    #     return [sampledData, imgIDx2ID, sampledGT]

    #ATTENTION: This is wrong (works for bluebirds set because all annotators annotate
    #all images). Using for now because right one gives seg faults. 
    #TODO: FIX CUBAM/save data function
    def subSample(self, data, groundTruth, nrWorkers):
        
        wrkIDs = set(wrkID for imgID in data for wrkID in data[imgID])
        if (nrWorkers < len(wrkIDs)):
            wrkIDs = random.sample(wrkIDs, nrWorkers)
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