from CheckAnnotationModel import *
import SimpleAnnotationModel


class CheckSimpleAnnotationModel(CheckAnnotationModel):


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
    modelCheck = CheckSimpleAnnotationModel()
    model = SimpleAnnotationModel.SimpleAnnotationModel(1)
    [uncompletedExamples, groundTruth] = modelCheck.createSyntheticDataset(1000)
    [completedExamples, labels] = model.crowdsourceLabels(uncompletedExamples, groundTruth)
    print(modelCheck.correctnessFactor(completedExamples, groundTruth))
    print(modelCheck.annotationStatistics(labels))


    #Checks for real data
    gtStream = open("bluebirds/gt.yaml", 'r')
    groundTruth = yaml.load(gtStream)
    labelStream = open("bluebirds/labels.yaml", 'r')
    data = yaml.load(labelStream)

    model = SimpleAnnotationModel.SimpleAnnotationModel(2)
    availableLabels = modelCheck.formatRealDataset(modelCheck.formatExamples(data))
    print availableLabels
    [completedExamples, labels] = model.crowdsourceLabels(availableLabels, groundTruth)
    print(modelCheck.correctnessFactor(completedExamples, groundTruth))
    print(modelCheck.annotationStatistics(labels))




if __name__ == "__main__":
    main()
