import random
import math

# For binary classification, y is an element in {0,1}

class Annotation:

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
    stoppingRatio = 5


    def __init__(self):
        pass



    # The function should determine whether we have enough confidence in ground truth predictions for any label to
    # stop the annotation process for that label. Confidence is measured with the Sequential probability ratio test using
    # the stoppingRatio variable.
    # http://en.wikipedia.org/wiki/Sequential_probability_ratio_test

    #U: getCompletedExamples(unlabelledExamples,labels,v)
    #B: unlabelledExamples: image data, dictionary of lists
    #   labels: crowd labels, dictionary of lists
    #   v: cv prediction, dictionary
    #
    #A: Returns a dictionary of images (list for each image) that we have enough confidence in ground truth prediction.
    def getCompletedExamples(self, unlabelledExamples,labels,v):
        pass

    #Same as 3 arguement getCompletedExamples, except we omit the computer vision prediction.
    def getCompletedExamples(self, unlabelledExamples, labels):

        r = dict()
        for i in unlabelledExamples:
            #p = p(y | xi, zi, vi)
            [y,py, pnoty] = self.optimiseProbability(labels[i])

            if self.stoppingRatio < math.log(py/pnoty):
                r[i] = y

        return r


    #The function takes the input of unlabelled examples and sends the examples through a pipe where images are only
    #given new annotations if the confidence level in their ground truth predictions are below a threshold. The function
    #asks for annotations for images continually until all image example predictions pass the confidence threshold.
    #(TO BE DONE): This function also uses a computer vision algorithm as an annotator and gives predictions with
    #confidence levels which can be supported or not by annotators.

    #U: crowdsourceLabels(unlabelledExamples)
    #B: unlabelledExamples is a dictionary of lists
    #A: returns a dictionary of ground truth predictions with key values corresponding to the key values in
    #   unlabelledExamples
    def crowdsourceLabels(self, unlabelledExamples):

        #w = 0
        #TODO: intialize CV prediction
        #cvPredictions = dict()

        labelledExamples = dict()
        labels = dict()
        try:
            while len(unlabelledExamples) != 0:
                #TODO: get CV predictions

                #for x in unlabelledExamples:
                #    cvPredictions = cvPredictions.update(computerVisionPrediction(x,w))
                #completedLabels = getCompletedExamples(unlabelledExamples,labels,cvPredictions)


                completedLabels = self.getCompletedExamples(unlabelledExamples, labels)

                labelledExamples = labelledExamples.update(completedLabels)

                for y in completedLabels:
                    del unlabelledExamples[y]

                labels = self.getOneNewWorkerLabelPerImage(unlabelledExamples, labels)

                #w = retrainComputerVision(labelledExamples)

        except(AttributeError, TypeError):
            raise AssertionError('unlabelledExamples must be a dictionary')

        return labelledExamples

    #MODEL CHECKING. This is the same function as 2 arguement crowdsourceLabels except that it does not include
    #computer vision and is used with datasets where we already have the groundtruth labels.
    def crowdsourceLabels(self, unlabelledExamples, groundTruthLabels):

        labelledExamples = dict()
        labels = dict()
        try:
            while len(unlabelledExamples) != 0:

                labels = self.getOneNewWorkerLabelPerImage(unlabelledExamples, labels, groundTruthLabels)
                completedLabels = self.getCompletedExamples(unlabelledExamples, labels)
                labelledExamples.update(completedLabels)
                for y in completedLabels:
                    del unlabelledExamples[y]


        except(AttributeError, TypeError):
            raise AssertionError('unlabelledExamples must be a dictionary')

        return labelledExamples, labels

    #MODEL CHECKING. This function uses a simple model to simulate annotators. Annotations are based on ground
    #truth labels and the probabilities lambdatp, lambatn, lambdafp, lambdafn (class variables). Since this model
    #uses ground truth label it is for testing purposes only.
    def getOneNewWorkerLabelPerImage(self, unlabelledExamples, labels, groundTruthLabels):

        for x in unlabelledExamples:
            if groundTruthLabels[x] == 1:
                if (random.random() < Annotation.lambdatp):
                    labels = self.__addLabelToList(labels,x,1)
                else:
                    labels = self.__addLabelToList(labels,x,0)
            else:
                if (random.random() < Annotation.lambdatn):
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


    #def getOneNewWorkerLabelPerImage(self,unlabelledExamples, labels):
    #    pass

    #Model checking. For now only implements optimization of binary labels
    #imageLabels: list of labels for a certain image
    def optimiseProbability(self, imageLabels):


        py1 = self.__calcProbability(imageLabels, 1)
        py0 = self.__calcProbability(imageLabels, 0)
        if py1 > py0:
            return [1, py1, py0]
        else:
            return [0, py0, py1]

    #Model checking. Ignores the image itself.
    #returns y* = argmax(y) p(y|x)*PI(p(zij|y) for zi1..zin) / sigma(p(y'|x)*PI(p(zij|y') for zi1...zin) for all y)
    #ATTENTION: right now this is weird cause I calculate everything I need for all possible p(y|x,z,v) when I calculate
    #  each y. However, I want to keep the optimization function and the calcProbability function seperate
    #  for the future.
    #imageLabels: list of labels for a certain image
    #y: possible ground truth
    def __calcProbability(self, imageLabels, y):
        y2 = abs(y - 1)
        p1 = y * self.pyx + (1 - y) * (1 - Annotation.pyx)
        p2 = y2 * self.pyx + (1 - y2) * (1 - Annotation.pyx)
        p3 = 1
        p4 = 1
        for i in range(0,len(imageLabels)):
            p3 *= self.__getConditional(imageLabels[i], y)
            p4 *= self.__getConditional(imageLabels[i], y2)

        return (p1 * p3) / (p1 * p3 + p2 * p4)


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


                #
                # #u: dictionary of unlabelled images
                # def getOneNewWorkerLabelPerImage(u):
                #
                # def computerVisionPrediction(x,w):
                #
                # #l: dictionary of labelled images
                # def retrainComputerVision(l):