import sys
import VisipediaAPI
from VisipediaAPI import *
import random
import fileinput
import yaml

IMAGE_DIR = "images"
RESULTS_FILE = "results.txt"
SANDBOX = 0

d = VisipediaConnection('Zo19m2hOAi1r0RYWV1Fv', '173.203.120.143', 1)

stream = file(IMAGE_DIR + '/hit_type_' + str(SANDBOX) + '.txt', 'r')
hit_type_id  = yaml.load(stream)

f = open(IMAGE_DIR + "/" + RESULTS_FILE, 'w')
results = VIS_field_array(d.find('image_assignments',
                                 { "hit_type_id" : hit_type_id, 'page_size' : 1000000 }))
for res in results:
    lab = int(res['answer'])
    f.write('%d %d %d\n' % (int(res['image-id']), int(res['worker-id']), lab))
f.close()