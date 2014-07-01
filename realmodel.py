   
    # The function should determine whether we have enough confidence in ground truth predictions for any label to
    # stop the annotation process for that label. Confidence is measured with the Sequential probability ratio test using
    # the stoppingRatio variable.
    # http://en.wikipedia.org/wiki/Sequential_probability_ratio_test

    #U: getCompletedExamples(incompleteExamples,labels,v)
    #B: incompleteExamples: image data, dictionary of lists
    #   labels: crowd labels, dictionary of lists
    #   v: cv prediction, dictionary
    #
    #A: Returns a dictionary of images (list for each image) that we have enough confidence in ground truth prediction.
    def getCompletedExamples(self, incompleteExamples,labels,v):
        pass





   #The function takes the input of unlabelled examples and sends the examples through a pipe where images are only
    #given new annotations if the confidence level in their ground truth predictions are below a threshold. The function
    #asks for annotations for images continually until all image example predictions pass the confidence threshold.
    #(TO BE DONE): This function also uses a computer vision algorithm as an annotator and gives predictions with
    #confidence levels which can be supported or not by annotators.

    #U: crowdsourceLabels(incompleteExamples)
    #B: incompleteExamples is a dictionary of lists
    #A: returns a dictionary of ground truth predictions with key values corresponding to the key values in
    #   incompleteExamples
    def crowdsourceLabels(self, incompleteExamples):

        #w = 0
        #TODO: intialize CV prediction
        #cvPredictions = dict()

        completeExamples = dict()
        labels = dict()
        try:
            while len(incompleteExamples) != 0:
                #TODO: get CV predictions

                #for x in incompleteExamples:
                #    cvPredictions = cvPredictions.update(computerVisionPrediction(x,w))
                #completedLabels = getCompletedExamples(incompleteExamples,labels,cvPredictions)


                completedLabels = self.getCompletedExamples(incompleteExamples, labels)

                completeExamples = completeExamples.update(completedLabels)

                for y in completedLabels:
                    del incompleteExamples[y]

                labels = self.getOneNewWorkerLabelPerImage(incompleteExamples, labels)

                #w = retrainComputerVision(completeExamples)

        except(AttributeError, TypeError):
            raise AssertionError('incompleteExamples must be a dictionary')

        return completeExamples


    #
    # #u: dictionary of unlabelled images
    # def getOneNewWorkerLabelPerImage(u):
    #
    # def computerVisionPrediction(x,w):
    #
    # #l: dictionary of labelled images
    # def retrainComputerVision(l):