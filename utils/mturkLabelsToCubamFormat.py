
labelDir = "../data/tbp"
labels = dict()


with open(labelDir + "/tbp_labels.txt") as fp:
    for line in fp:
    	line = line.split()
    	wkrID = int(line[1])
    	imgID = int(line[0])
    	label = bool(line[2])
    	if wkrID in labels:
    		labels[wkrID].update({imgID:label})
    	else:
    		labels[wkrID] = {imgID:label}


print labels