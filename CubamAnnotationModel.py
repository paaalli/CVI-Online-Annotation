import cubam
import random


class CubamAnnotationModel():
    
    #stoppingRatio: stoppingRatio for sequential probability ratio test
    stoppingRatio = 15


    #flag = 0 or 1, 0 means we're getting annotations from an already labelled dataset
    #1 means we're getting annotations from MTTurk.
    def __init__(self, dirName, flag = 0):
        self.flag = flag
        self.dirName = dirName
        self.cubamDataFile = '%s/data.txt' % self.dirName


    # The function should determine whether we have enough confidence in ground truth predictions for any label to
    # stop the annotation process for that label. Confidence is measured with the Sequential probability ratio test using
    # the stoppingRatio variable.
    # http://en.wikipedia.org/wiki/Sequential_probability_ratio_test

    #U: getCompletedExamples(incompleteExamples,labels,v)
    #B: incompleteExamples: image data, dictionary of lists
    #   labels: crowd labels, dictionary of lists
    #
    #A: Returns a dictionary of images (list for each image) that we have enough confidence in ground truth prediction.

    def getCompletedExamples(self, incompleteExamples, labels):

        completeExamples = dict()

        #predictions is a dictionary of lists with imageIDs as keys and
        #a keys value is a list with [probability, label prediction]
        predictions = self.optimiseProbability(labels)
        for imgID in predictions:
            y = predictions[imgID][1]
            py = predictions[imgID][0]
            print py 
            if self.stoppingRatio < math.log(py/(1-py)):
                completeExamples[imgID] = y

        return completeExamples



    #The function takes the input of unlabelled examples and sends the examples through a pipe where images are only
    #given new annotations if the confidence level in their ground truth predictions are below a threshold. The function
    #asks for annotations for images continually until all image example predictions pass the confidence threshold.
    #(TO BE DONE): This function also uses a computer vision algorithm as an annotator and gives predictions with
    #confidence levels which can be supported or not by annotators.

    #MODEL CHECKING. This is the same function as 2 arguement crowdsourceLabels except that it does not include
    #computer vision and is used with datasets where we already have the groundtruth labels.
    #REFACTOR THIS SHIT.
    def crowdSourceLabels(self, incompleteExamples):

        completeExamples = dict()
        labels = dict()
        for imgID in incompleteExamples:
            labels[imgID] = {}
        #try:
        while len(incompleteExamples) != 0:

            labels = self.getOneNewWorkerLabelPerImage(incompleteExamples, labels)
            completedLabels = self.getCompletedExamples(incompleteExamples, labels)
            completeExamples.update(completedLabels)
            for imgID in completedLabels:
                del incompleteExamples[imgID]


        #except(AttributeError, TypeError):
        #    raise AssertionError('incompleteExamples must be a dictionary')

        return completeExamples, labels


    def optimiseProbability(self, labels):
        
        self.__saveData(labels)
        model = cubam.Binary1dSignalModel(filename = self.cubamDataFile)
        model.optimize_param()
        param = m.get_image_param()

        #Change the distribution from optimize_param() to probability
        #predictions = Dont know how, fak

        predictions = param

        for imgID in param:
            predictions[imgID][1] = int(param[imgID][0] > 0)

        return predictions 

    def __saveData(self, labels):

        
        fout = open(self.cubamDataFile, 'w')
        #temporary filewriting, gonna change cubam toolbox later.
        wkrIDs = set(wrkID for imgID in labels for wrkID in labels[imgID])
        total = sum(len(labels[imgID]) for imgID in labels)
        fout.write("%d %d %d\n" % (len(labels), len(wkrIDs), total))

        for imgID in labels:
            for wrkID in labels[imgID]:
                fout.write("%d %d %d\n" % (imgID, wrkID, labels[imgID][wrkID]))
        fout.close()

        
    def getOneNewWorkerLabelPerImage(self, incompleteExamples, labels):
        if self.flag:
            return self.__getLabelsFromMTTurk(incompleteExamples, labels)
        else:
            return self.__getLabelsFromDataset(incompleteExamples, labels)

    def __getLabelsFromMTTurk(self, incompleteExamples, labels):
        pass

    def __getLabelsFromDataset(self, incompleteExamples, labels):
        insufficientExamples = dict()

        #For every image in incompleteExampels we check whether there
        # are available annotations and if there are we select 
        # one label by random for each image.

        for imgID in incompleteExamples:

            #If there are available annotations left for imgID we choose a random worker
            #add his label to our labels, then delete it from incompleteExamples.
            #If no available annotations, mark the key for deletion and print
            #a statement letting the user know.

            if len(incompleteExamples[imgID]) != 0:
                workerKey = random.choice(list(incompleteExamples[imgID].keys()))
                labels[imgID][workerKey] = incompleteExamples[imgID][workerKey]
                del incompleteExamples[imgID][workerKey]
            else:
                print("Annotations available for image label " + str(imgID) + " are not sufficient to predict with confidence")
                insufficientExamples[imgID] = True
        
        #We delete the image IDs from incompleteExamples that have no further annotations available.
        for imgID in insufficientExamples:
            del incompleteExamples[imgID]

        return labels
