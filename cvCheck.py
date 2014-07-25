import yaml
from sklearn import svm, preprocessing
import cPickle
from numpy import exp, log, concatenate
from matplotlib import pyplot as plt

from CheckAnnotationModel import *

modelCheck = CheckAnnotationModel()


gtStream = open("bluebirds/gt.yaml", 'r')
groundTruth = yaml.load(gtStream)
labelStream = open("bluebirds/labels.yaml", 'r')
data = yaml.load(labelStream)
data = modelCheck.formatExamples(data)

dirName = 'data/bluebirds'
features = cPickle.load(open(dirName + '/featureVectors.pickle', 'r'))
scores = cPickle.load(open(dirName + '/scores.pickle', 'r'))
#print features

numTrials = 40

trialStat = []
probStat = []
correctStat = []

imgIDs = set(data.keys())
verifyIDs = set(random.sample(imgIDs, len(imgIDs)/2))

possibleTrainIDs = imgIDs - verifyIDs

#Can do this because all images have equal nr annotations
for numImg in range(10, len(possibleTrainIDs), 10):

    print "Number of img: " + str(numImg)
    avgProb = 0
    avgCorrect = 0

    trial = numTrials
    while trial > 0:

        print "Trial number: " + str(trial)
        y = []
        x = []

        linearSVC = svm.SVC(kernel = 'linear', probability = True)


        trainIDs = set(random.sample(possibleTrainIDs, numImg))

        #Making sure there are at least 2 cases of each class
        tmp = sum([groundTruth[i] for i in trainIDs])
        if (not (tmp >= 2 and tmp <= len(trainIDs) - 2)):
            continue

        #Getting data for training examples
        for imgID in trainIDs:
            y.append(groundTruth[imgID])
            x.append(features[str(imgID)])
            #print groundTruth[imgID]

        print "VALIDATION!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
        #min-max scaling, not sure whether to do here or in beginning
        #with all data.
        #minMaxScaler = preprocessing.MinMaxScaler()
        #x = minMaxScaler.fit_transform(x)

        linearSVC.fit(x,y)

        x = []
        y = []
        #Getting data for verification examples
        for imgID in verifyIDs:
            y.append(groundTruth[imgID])
            x.append(features[str(imgID)])
            #print groundTruth[imgID]

        #x = minMaxScaler.fit_transform(x)

        predProb = linearSVC.predict_proba(x)
        pred = [list(i).index(max(i)) for i in predProb]
        print predProb
        print zip(predProb, y)
        
        a = {}
        b = {}
        for i in range(len(pred)):
            a[i] = pred[i]
            b[i] = y[i]

        ratioCorrect = modelCheck.correctnessFactor(a,b)
        print ratioCorrect
        probTotal = exp(sum([log(max(p)) for p in predProb])) 

        avgProb += probTotal
        avgCorrect += ratioCorrect

        trial -= 1


    trialStat.append(numImg)
    probStat.append(avgProb/numTrials)
    correctStat.append(avgCorrect/numTrials)


print trialStat
print probStat
print correctStat

prob = plt.bar(trialStat, probStat, color = 'r')
plt.ylabel('Probabilities of images multiplied')
plt.xlabel('Number of training examples')
plt.savefig('data/cv/Probabilities.jpg')

corr = plt.bar(trialStat,correctStat)
plt.ylabel('Correctness of predictions')
plt.xlabel('Number of training examples')
plt.savefig('data/cv/Correctness.jpg')


