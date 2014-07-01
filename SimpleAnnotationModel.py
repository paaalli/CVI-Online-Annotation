import random
import math

# For binary classification, y is an element in {0,1}

class SimpleAnnotationModel():

    #lambdafp: p(z = 1 | y = -1, lambda)
    #lambdafn: p(z = -1 | y = 1, lambda)
    #lambdatp: p(z = 1 | y = 1, lambda)
    #lambdatn: p(z = -1 | y = -1, lambda)
    #pyx: p(y|x)

    lambdafp = 0.15
    lambdafn = 0.15
    lambdatp = 1 - lambdafn
    lambdatn = 1 - lambdafp

    #defining prior for p(y|x)
    pyx = 0.5

    #stoppingRatio: stoppingRatio for sequential probability ratio test
    stoppingRatio = 15


    def __init__(self, flag):
        self.flag = flag



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
        for imgID in incompleteExamples:
            #py = p(y | xi, zi, vi)
            [y,py]= self.optimiseProbability(labels[imgID])
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
    def crowdsourceLabels(self, incompleteExamples, groundTruthLabels):

        completeExamples = dict()
        labels = dict()
        try:
            while len(incompleteExamples) != 0:
                labels = self.getOneNewWorkerLabelPerImage(incompleteExamples, labels, groundTruthLabels)
                completedLabels = self.getCompletedExamples(incompleteExamples, labels)
                completeExamples.update(completedLabels)
                for y in completedLabels:
                    del incompleteExamples[y]


        except(AttributeError, TypeError):
            raise AssertionError('incompleteExamples must be a dictionary')

        return completeExamples, labels

    #MODEL CHECKING. This function uses a simple model to simulate annotators. Annotations are based on ground
    #truth labels and the probabilities lambdatp, lambatn, lambdafp, lambdafn (class variables). Since this model
    #uses ground truth label it is for testing purposes only.

    #For synthetic data, dataExamples are unlabelled, for real data, dataExampls are labelled.
    def getOneNewWorkerLabelPerImage(self, incompleteExamples, labels, groundTruthLabels):

        if self.flag == 1:
            labels = self.__getLabelsForSyntheticData(incompleteExamples, labels, groundTruthLabels)
        elif self.flag == 2:
            labels = self.__getLabelsForRealData(incompleteExamples, labels, groundTruthLabels)

        return labels

    def __getLabelsForRealData(self, incompleteExamples,labels,groundTruthLabels):
        insufficientExamples = dict()

        for x in incompleteExamples:
            if len(incompleteExamples[x]) != 0:
                labels = self.__addLabelToList(labels,x,incompleteExamples[x][0])
                del incompleteExamples[x][0]
            else:
                print("Annotations available for image label " + str(x) + " are not sufficient to predict with confidence")
                insufficientExamples[x] = True
        
        for x in insufficientExamples:
            del incompleteExamples[x]

        return labels


    def __getLabelsForSyntheticData(self, incompleteExamples, labels, groundTruthLabels):
        for x in incompleteExamples:
            if groundTruthLabels[x] == 1:
                if (random.random() < self.lambdatp):
                    labels = self.__addLabelToList(labels,x,1)
                else:
                    labels = self.__addLabelToList(labels,x,0)
            else:
                if (random.random() < self.lambdatn):
                    labels = self.__addLabelToList(labels,x,0)
                else:
                    labels = self.__addLabelToList(labels,x,1)
        return labels

    def __addLabelToList(self, labels, imageKey, label):
        if imageKey in labels:
            labels[imageKey].append(label)
        else:
            labels[imageKey] = [label]
        return labels


    #def getOneNewWorkerLabelPerImage(self,incompleteExamples, labels):
    #    pass

    #returns: y* = argmax(y) p(y|x)*PI(p(zij|y) for zi1..zin) / sigma(p(y'|x)*PI(p(zij|y') for zi1...zin) for all y),
    #         p(y*|x,z)
    #         p(!y*|x,z)
    #Model checking. For now only implements optimization of binary labels
    #imageLabels: list of labels for a certain image
    def optimiseProbability(self, imageLabels):

        p1 = self.pyx
        p2 = 1 - p1
        p3 = 1
        p4 = 1
        for i in range(0,len(imageLabels)):
            p3 *= self.__getConditional(imageLabels[i], 1)
            p4 *= self.__getConditional(imageLabels[i], 0)

        py1 = p1*p3
        py0 = p2*p4
        pSum = py1 + py0
        if (py1> py0):
            pyCond = py1 / pSum
            return [1,pyCond]
        else:
            pyCond = py0 / pSum
            return [0, pyCond]


    #returns the lambda probability value for given label and groundtruth
    def __getConditional(self, label, y):
        if (label == 1):
            if y == 1:
                return self.lambdatp
            else:
                return self.lambdafp
        else:
            if (y == 1):
                return self.lambdafn
            else:
                return self.lambdatn


