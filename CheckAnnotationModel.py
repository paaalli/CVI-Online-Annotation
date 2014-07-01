import random
import yaml

#Abstract Base class for model checking

class CheckAnnotationModel():

    def __init__(self):
        pass

    def correctnessFactor(self, completedExamples, groundTruth):
        total = 0.0
        correct = 0.0
        for x in completedExamples:
            if completedExamples[x] == groundTruth[x]:
                correct += 1
            total += 1
        return correct/total

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