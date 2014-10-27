import os
import yaml


tomatoeDir = 'tomatoes'
gt = {}
for filename in os.listdir(tomatoeDir):
	gt[filename[0:-4]] = True
	
pepperDir = 'bellpeppers'
for filename in os.listdir(pepperDir):
	gt[filename[0:-4]] = False
	
gtFile = open('tbpgroundTruth.yaml', 'w')
gtFile.write(yaml.dump(gt))