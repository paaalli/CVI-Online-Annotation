import random
from math import log, exp, sqrt, pow, pi

class AnnotationModel():


    # The function should determine whether we have enough confidence in ground truth predictions for any label to
    # stop the annotation process for tahat label. Confidence is measured with the Sequential probability ratio test using
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
        for imgID in incompleteExamples:
            y = predictions[imgID][1]
            #py = p(y | xi, zi, vi)
            py = predictions[imgID][0]
            if self.stoppingRatio < log(py/(1-py)):
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
        labels = self.getOneNewWorkerLabelPerImage(incompleteExamples, labels)
                
        try:
            while len(incompleteExamples) != 0:

                labels = self.getOneNewWorkerLabelPerImage(incompleteExamples, labels)
                completedLabels = self.getCompletedExamples(incompleteExamples, labels)
                completeExamples.update(completedLabels)

                for imgID in completedLabels:
                    del incompleteExamples[imgID]


        except(AttributeError, TypeError):
            raise AssertionError('incompleteExamples must be a dictionary')

        return completeExamples, labels
