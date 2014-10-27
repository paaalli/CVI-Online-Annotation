from CheckAnnotationModel import *
import SimpleAnnotationModel


class CheckSimpleAnnotationModel(CheckAnnotationModel):


    def __init__(self):
        pass

    def createSyntheticDataset(self, size, lambdaf,nrLabels = 40):
        y = dict()
        x = dict()
        lambdafp = lambdaf[0]
        lambdafn = lambdaf[1]

        factorOfPositiveTruths = random.random()
        for i in range(0,size):
            if (random.random() < factorOfPositiveTruths):
                y[i] = 1
            else:
                y[i] = 0
            x[i] = {}
            for j in range(0,40):
                if y[i]:
                    if random.random() > lambdafn:
                        x[i][j] = 1
                    else:
                        x[i][j] = 0
                else:
                    if random.random() > lambdafp:
                        x[i][j] = 0
                    else:
                        x[i][j] = 1
        return [x,y]


    #Changing form of label data from dictionary with annotator id as key and labels as dictionary values to
    #dictionary of lists with image ids being keys and values are lists of corresponding labels.

    def formatRealDataset(self, data):

        availableLabels = dict()
        for i in data:
            for j in data[i]:
                if j in availableLabels:
                    availableLabels[j].append(data[i][j])
                else:
                    availableLabels[j] = [data[i][j]]
        return availableLabels

def main():

    #Checks for synthesized data
    lambdafp = 0.15
    lambdafn = 0.15
    lambdaf = [lambdafp, lambdafn]
    modelCheck = CheckSimpleAnnotationModel()
    [incompleteExamples, groundTruth] = modelCheck.createSyntheticDataset(1000,lambdaf)
    model = SimpleAnnotationModel.SimpleAnnotationModel(lambdaf)  
    [completedExamples, labels] = model.crowdSourceLabels(incompleteExamples)
    print(modelCheck.correctnessFactor(completedExamples, groundTruth))
    print(modelCheck.annotationStatistics(labels))




if __name__ == "__main__":
    main()
