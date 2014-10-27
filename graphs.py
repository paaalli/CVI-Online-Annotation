import pickle, yaml
from numpy import random, mean, std, sqrt
from matplotlib.pylab import figure

cubamFile = '../cubam/demo/results/bluebirds-rates.pickle'
numTrial = 60

cvi20 = yaml.load(open('trialWrk=20.yaml'))
cvi16 = yaml.load(open('trialWrk=16.yaml'))
cviPT = yaml.load(open('PTWrk=20.yaml'))


cubamRates = pickle.load(open(cubamFile))
cvi20Rates = []
cvi20Erbs = []
worker20List = []
worker20Erbs = []
cvi16Rates = []
cvi16Erbs = []
worker16List = []
worker16Erbs = []
cviPTRates = []
cviPTErbs = []
workerPTList = []
workerPTErbs = []

confs = sorted(list(cvi20.keys()))

for conf in confs:
	cvi20Rates.append(1-cvi20[conf][0])
	cvi20Erbs.append(cvi20[conf][1])
	worker20List.append(cvi20[conf][2])
	worker20Erbs.append(cvi20[conf][3])
	

confs = sorted(list(cvi16.keys()))
for conf in confs:	
	cvi16Rates.append(1-cvi16[conf][0])
	cvi16Erbs.append(cvi16[conf][1])
	worker16List.append(cvi16[conf][2])
	worker16Erbs.append(cvi16[conf][3])

	
confs = sorted(list(cviPT.keys()))
for conf in confs:	
	cviPTRates.append(1-cviPT[conf][0])
	cviPTErbs.append(cviPT[conf][1])
	workerPTList.append(cviPT[conf][2])
	workerPTErbs.append(cviPT[conf][3])




exps = [('signal', 'NIPS 2010'), ('majority', 'majority'), ('bias', 'Dawid & Skene')]
numWkrList = sorted(cubamRates[exps[0][0]].keys())
fig = figure(1, (5.5,3)); fig.clear(); ax = fig.add_subplot(1,1,1)
for (expt, legname) in exps:
    rates = [mean(cubamRates[expt][nw]) for nw in numWkrList]
    erbs = [std(cubamRates[expt][nw])/sqrt(numTrial) for nw in numWkrList]
    ax.errorbar(numWkrList, rates, yerr=erbs, lw=1)

ax.errorbar(worker20List, cvi20Rates, yerr=cvi20Erbs, xerr=worker20Erbs, label = 'CVI20', lw=1)
ax.errorbar(worker16List, cvi16Rates, yerr=cvi16Erbs, xerr=worker16Erbs, label = 'CVI16', lw=1)
ax.errorbar(workerPTList, cviPTRates, yerr=cviPTErbs, xerr=workerPTErbs, label = 'PTCVI20', lw=1)
ax.set_xlabel('number of annotators', fontsize=16)
ax.set_ylabel('error rate', fontsize=16)
ax.set_title('subsampled bluebirds data', fontsize=18)
ax.set_xlim(2, 22)
ax.set_ylim(0.0, .4)
ax.set_xticks([4, 8, 12, 16, 20])
ax.legend(loc=1)
fig.savefig('results.pdf')