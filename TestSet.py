import random
import Annotation
import yaml

class CheckAnnotation:

    def __init__(self):
        pass


    def createSyntheticDataset(self, size):
        y = dict()
        x = dict()
        factorOfPositiveTruths = random.random()
        for i in range(0,size):
            x[i] = None
            if (random.random() < factorOfPositiveTruths):
                y[i] = 1
            else:
                y[i] = 0
        return [x,y]

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



def main():
    modelCheck = CheckAnnotation()
    model = Annotation.Annotation()
    [unlabelledExamples, groundTruth] = modelCheck.createSyntheticDataset(1000)
    [completedExamples, labels] = model.crowdsourceLabels(unlabelledExamples, groundTruth)
    print(modelCheck.correctnessFactor(completedExamples, groundTruth))
    print(modelCheck.annotationStatistics(labels))

if __name__ == "__main__":
    main()
