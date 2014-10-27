import yaml
from sklearn import svm, preprocessing
import cPickle
from numpy import exp, log, concatenate, mean, std, sqrt
from matplotlib.pylab import figure
from time import *
from copy import deepcopy

from CubamAnnotationModel import *
from CheckAnnotationModel import *

modelCheck = CheckAnnotationModel()


#gtStream = open("bluebirds/gt.yaml", 'r')
gtStream = open("dhgroundTruth.yaml", 'r')
groundTruth = yaml.load(gtStream)
#labelStream = open("bluebirds/labels.yaml", 'r')
#data = yaml.load(labelStream)
#data = modelCheck.formatExamples(data)

#dirName = 'data/bluebirds'
dirName = 'data/dogshyenas'
features = cPickle.load(open(dirName + '/featureVectors.pickle', 'r'))
#scores = cPickle.load(open(dirName + '/scores.pickle', 'r'))
print len(features)
print len(groundTruth)

numTrials = 60
correctList = [0.9, 1]
#wrkList = [5,10,20]
wrkList = []
trialStat = []
probStat = {}
corrStat = {}
cubamStat = {}
for i in correctList:
    probStat[i] = {}
    probStat[i]['mean'] = []
    probStat[i]['std'] = []
    corrStat[i] = {}
    corrStat[i]['mean'] = []
    corrStat[i]['std'] = []

for j in wrkList:

    cubamStat['cv' + str(j)] = {}
    cubamStat['cv' + str(j)]['mean'] = []
    cubamStat['cv' + str(j)]['std'] = []
    #cubamStat[str(j)] = {}
    #cubamStat[str(j)]['mean'] = []
    #cubamStat[str(j)]['std'] = []

# cubamStat['cvPicked'] = {}
# cubamStat['cvPicked']['mean'] = []
# cubamStat['cvPicked']['std'] = []

imgIDs = set(groundTruth.keys())

for i in imgIDs:
    if not str(i) in features:
        print i
for numImg in range(10, 100, 10):

    print "Number of img: " + str(numImg)

    tmpCorr = {}
    tmpProb = {}
    for i in correctList:
        tmpCorr[i] = []
        tmpProb[i] = []

    for j in wrkList:
        tmpCorr[j] = []
        tmpProb[j] = []
    
    tmpCorr['cvPicked'] = []
    tmpProb['cvPicked'] = []

    trial = numTrials
    while trial > 0:

        #Random sampling verification/training data
        verifyIDs = set(random.sample(imgIDs, len(imgIDs)/2))
        #50% class 0 50% class 1 verification
        #bb = set([i for i in imgIDs if groundTruth[i]])
        #nobb = imgIDs-bb
        #verifyIDs = set(random.sample(bb, len(imgIDs)/4)).union \
        #        (set(random.sample(nobb, len(imgIDs)/4)))

        possibleTrainIDs = imgIDs - verifyIDs

        ###################################################################
        #Getting training examples from cubam by picking the images cubam
        #is most confident in.

        # linearSVC = svm.SVC(kernel = 'linear', probability = True)  

        # possibleTrainData = {}
        # for i in possibleTrainIDs:
        #     possibleTrainData[i] = data[i]

        # [incompleteExamples, imgIDx2ID, sampledGT] = \
        #     modelCheck.subSample(possibleTrainData, groundTruth, 20)


        # model = CubamAnnotationModel(dirName = dirName, stoppingRatio = 10, \
        #         partTrain = numImg, pickBest = True, cvCheck = True)

        # comp = model.crowdSourceLabels(incompleteExamples, imgIDx2ID)

        # tmp = sum([comp[i] for i in comp])    
        # #Making sure there are at least 2 cases of each class for both wrk and rate 
        # #runs.
        # if (not (tmp >= 2 and tmp <= (len(comp) - 2))):
        #     continue

        # x = []
        # y = []
        # for idx in comp:
        #     x.append(features[str(imgIDx2ID[idx])])
        #     y.append(comp[idx])

        # linearSVC.fit(x,y)  
        # x = []
        # y = []
        # #Getting data for verification examples
        # for imgID in verifyIDs:
        #     y.append(groundTruth[imgID])
        #     x.append(features[str(imgID)])

        # #x = minMaxScaler.fit_transform(x)

        # predProb = linearSVC.predict_proba(x)
        # pred = [list(i).index(max(i)) for i in predProb]

        # ratioCorrect = modelCheck.correctnessFactor(pred,y)
        # probTotal = exp(sum([log(max(p)) for p in predProb])) 

        # tmpProb['cvPicked'].append(probTotal)
        # tmpCorr['cvPicked'].append(ratioCorrect)



        ###################################################################

        #Setting up data for cubam with random images and sampled correct rate.

        trainIDs = set(random.sample(possibleTrainIDs, numImg))
        # tmp = sum([groundTruth[i] for i in trainIDs])    
        # #Making sure there are at least 2 cases of each class for both wrk and rate 
        # #runs.
        # if (not (tmp >= 2 and tmp <= (len(trainIDs) - 2))):
        #     continue

        # trainData = dict()
        # trainGT = dict()

        # for i in trainIDs:
        #     trainData[i] = data[i]        
        #     trainGT[i] = groundTruth[i]

        ####################################################################
        #Getting training examples from cubam, randomly.
        for wrk in wrkList:


            model = CubamAnnotationModel(dirName = dirName, stoppingRatio = 10, \
                    partTrain = numImg, cvCheck = True)

            linearSVC = svm.SVC(kernel = 'linear', probability = True)  

            [incompleteExamples, imgIDx2ID, sampledGT] = \
            modelCheck.subSample(trainData, trainGT, wrk)

            comp = model.crowdSourceLabels(incompleteExamples, imgIDx2ID)
            #part train puts all images in comp.

            x = []
            y = []
            for idx in comp:
                x.append(features[str(imgIDx2ID[idx])])
                y.append(comp[idx])

            linearSVC.fit(x,y)  
            x = []
            y = []
            #Getting data for verification examples
            for imgID in verifyIDs:
                y.append(groundTruth[imgID])
                x.append(features[str(imgID)])

            #x = minMaxScaler.fit_transform(x)

            predProb = linearSVC.predict_proba(x)
            pred = [list(i).index(max(i)) for i in predProb]

            ratioCorrect = modelCheck.correctnessFactor(pred,y)
            probTotal = exp(sum([log(max(p)) for p in predProb])) 

            tmpProb[wrk].append(probTotal)
            tmpCorr[wrk].append(ratioCorrect)

        ########################################################################
        #Simulating rate of correct training data
        for rate in correctList:
   

            #I know this results in different training sets, but we have so many 
            #trials I it shouldnt matter, also, I dont know how to do this different.         
            tmp = 0
            while not(tmp >= 2 and tmp <= len(trainIDs) - 2):
                possGT = {}
                for imgID in trainIDs:
                    if (random.random() <= rate):
                        possGT[imgID] = groundTruth[imgID]
                    else:
                        possGT[imgID] = int(not(groundTruth[imgID]))
                tmp = sum([possGT[i] for i in trainIDs])


            linearSVC = svm.SVC(kernel = 'linear', probability = True)   


            #Testing whether having almost equal number of classes in 
            #training data will have significant effect on results.
            #if (not (tmp >= len(trainIDs)*0.35 and tmp <= len(trainIDs)*0.65)):
            #    continue
            x = []
            y = []
            #Getting data for training examples
            for imgID in trainIDs:
                y.append(possGT[imgID])
                x.append(features[str(imgID)])
                #print groundTruth[imgID]


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
            ratioCorrect = modelCheck.correctnessFactor(pred,y)
            probTotal = exp(sum([log(max(p)) for p in predProb])) 
            tmpProb[rate].append(probTotal)
            tmpCorr[rate].append(ratioCorrect)

        trial -= 1
        print trial
        ########################################################################

    for rate in correctList:

        probStat[rate]['mean'].append(mean(tmpProb[rate]))
        probStat[rate]['std'].append(std(tmpProb[rate])/sqrt(numTrials))
        corrStat[rate]['mean'].append(mean(tmpCorr[rate]))
        corrStat[rate]['std'].append(std(tmpCorr[rate])/sqrt(numTrials))


    for wrk in wrkList:          
        cubamStat['cv' + str(wrk)]['mean'].append(mean(tmpCorr[wrk]))
        cubamStat['cv' + str(wrk)]['std'].append(std(tmpCorr[wrk])/sqrt(numTrials))

    #cubamStat['cvPicked']['mean'].append(mean(tmpCorr['cvPicked']))
    #cubamStat['cvPicked']['std'].append(std(tmpCorr['cvPicked'])/sqrt(numTrials))

    trialStat.append(numImg)



#Figure for probabilities/number of training images
fig = figure(1, (5.5,3)); fig.clear(); ax = fig.add_subplot(1,1,1)
for i in probStat:
    ax.errorbar(trialStat, probStat[i]['mean'], yerr=probStat[i]['std'], \
            label=str(i), lw=3)

ax.set_ylabel('Probabilities of images multiplied')
ax.set_xlabel('Number of training examples')
ax.set_xlim(0,110)
ax.set_ylim(0.0,0.005)
ax.set_xticks([10,20,30,40,50])
ax.legend(loc=1)
fig.savefig('data/cv/Probabilities.jpg')


#Figure for correctness/number of training images
fig = figure(1, (5.5,3)); fig.clear(); ax = fig.add_subplot(1,1,1)
for i in corrStat:
    ax.errorbar(trialStat, corrStat[i]['mean'], yerr=corrStat[i]['std'], \
            label=str(i), lw=3)
#ax.errorbar(trialStat, cubamStat['cv20']['mean'], yerr=cubamStat['cv20']['std'], \
#        label='cubamCV', lw=3)
#ax.errorbar(trialStat, cubamStat['cvPicked']['mean'], \
#        yerr=cubamStat['cvPicked']['std'], label='cubamP', lw=3)


ax.set_ylabel('Correctness of predictions')
ax.set_xlabel('Number of training examples')
ax.set_xlim(0,110)
ax.set_ylim(0.4,1)
ax.set_xticks([10,20,30,40,50])
ax.legend(loc=4)
fig.savefig('data/cv/Correctness.jpg')

# #Figure for correctness of cubam/number of total workers/image
# fig = figure(1, (5.5,3)); fig.clear(); ax = fig.add_subplot(1,1,1)
# for i in cubamStat:
#     ax.errorbar(trialStat, cubamStat[i]['mean'], yerr=cubamStat[i]['std'], \
#             label=str(i), lw=1)

# ax.set_ylabel('Correctness of predictions')
# ax.set_xlabel('Number of training examples')
# ax.set_xlim(0,60)
# ax.set_ylim(0.4,0.9)
# ax.set_xticks([10,20,30,40,50])
# ax.legend(loc=4)
# fig.savefig('data/cv/CorrectnessWrk.jpg')
