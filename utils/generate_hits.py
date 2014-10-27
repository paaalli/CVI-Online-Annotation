import sys
import VisipediaAPI
from VisipediaAPI import *
import yaml
import re
import fileinput
import random
import os.path

NUM_IMAGES_PER_HIT = 36
WORKERS_PER_HIT = 20
REWARD = 10
SANDBOX = 0
api_key_id = 6

# Assume you have directories of images "images/Mallard", "images/Indigo\ Bunting", "images/Ellipse",
# with corresponding wikipedia articles "http://en.wikipedia.org/wiki/Mallard", "http://en.wikipedia.org/wiki/Indigo_bunting",
# "http://en.wikipedia.org/wiki/Ellipse"
IMAGE_DIR = "images"
CLASS_NAMES = [ "tomatoes","bellpeppers"]
WIKI_NAMES = [ "Tomato","Bell_pepper"]
HIT_TYPE_IDENTIFIER = "Label Images Hit Type"


d = VisipediaConnection('Zo19m2hOAi1r0RYWV1Fv', '173.203.120.143')
# Upload images for a certain object class
def upload_images(image_dir, class_name, wiki_name):
    if not os.path.isfile(IMAGE_DIR + "/" + class_name + ".txt"):
        dirList=os.listdir(image_dir)
        images = []
        for fname in dirList:
            curr = {}
            curr['fname'] = str(fname)
            images.append(curr)
        article_id = VIS_id(d.create('wikipedia_articles', { 'wikipedia_article[title]' : wiki_name, 'wikipedia_article[lang]' : 'en' }))
        print 'art##############'
        print article_id
        print '##############'
        object_id = VIS_id(d.create('objs', { 'obj[name]' : class_name, 'obj[wikipedia_article_id]' : article_id }))
        print 'obj##########'
        print object_id
        print 'ids#############'
        ids = d.upload_image_directory(image_dir, object_id)
        print ids
        print len(ids)
        print '################'
        for i in range(0,len(ids)):
            images[i]['id'] = ids[i]
            print ids[i]
        
        fout = open(IMAGE_DIR + '/' + class_name + '.txt', 'w') 
        fout.write(VIS_str(images))
        fout.close()
    else:
        stream = file(IMAGE_DIR + "/" + class_name + ".txt", 'r')
        images = yaml.load(stream)
    
    return images


# All hits of all classes share the same hit type
def build_hit_type():
    if not os.path.isfile(IMAGE_DIR + '/hit_type_' + str(SANDBOX) + '.txt'):
        annotation_type_presence_id = VIS_field_array(d.find('annotation_types', {'name' : 'Bird Presence/Absence (Illustrations)' } ))[0]['id']
        annotation_type_version_presence_id = VIS_id(d.custom('latest', 'annotation_types', annotation_type_presence_id ))
        hit_type_normal_id = VIS_id(d.create('hit_types', {
            "hit_type[identifier]" : HIT_TYPE_IDENTIFIER,
            "hit_type[title]" : "Click on images of an object",
            "hit_type[description]" : "You will be shown a collection of images, and will click on the images that contain a particular type of object.",
            "hit_type[keywords]" : "images,labelling",
            "hit_type[reward]" : REWARD,
            "hit_type[assignment_duration]" : 600,
            "hit_type[auto_approval_delay]" : 129600,
            "hit_type[annotation_type_id]" : annotation_type_presence_id,
            "hit_type[api_key_id]" : api_key_id,
            "hit_type[sandbox]" : SANDBOX,
            "register" : 1}))
        fout = open(IMAGE_DIR + '/hit_type_' + str(SANDBOX) + '.txt', 'w')
        fout.write(VIS_str(hit_type_normal_id))
        fout.close()
    else:
        stream = file(IMAGE_DIR + '/hit_type_' + str(SANDBOX) + '.txt', 'r')
        hit_type_normal_id  = yaml.load(stream)
    return hit_type_normal_id


# An annotation instance contains custom instructions for a particular image class
def build_annotation_instance(class_name, wiki_name, pos_exemplars, neg_exemplars):
    if not os.path.isfile(IMAGE_DIR + '/' + class_name + '_inst_' + str(SANDBOX) + '.txt'):
        annotation_type_presence_id = VIS_field_array(d.find('annotation_types', {'name' : 'Bird Presence/Absence (Illustrations)' } ))[0]['id']
        annotation_type_version_presence_id = VIS_id(d.custom('latest', 'annotation_types', annotation_type_presence_id ))
         
        wikipedia_url = "http://en.wikipedia.org/wiki/" + wiki_name
        instructions = '\'<div id="brief" class="infobox"><p>Click on thumbnails of the class <b>' + class_name + '</b>.</p></div>' + \
            '<div id="examples" class="infobox">  <center>' + \
            '    <h1>Examples</h1>    <table>      <tr>'
        for im in pos_exemplars:

          instructions += '<td class="imgcell selected"><img height=150 src="' + 'http://s3.amazonaws.com/visipedia/images/' + im['id'] + '/small.jpg"><br><center>' + class_name + '</center></td>'
        for im in neg_exemplars:
          instructions += '<td class="imgcell"><img height=150 src="' + 'http://s3.amazonaws.com/visipedia/images/' + im['id'] + '/small.jpg"><br><center>Not a ' + class_name + '</center></td>'
        instructions += '</tr></table></div>\''
        params = VIS_str({"object_name" : ("'" + class_name + "'"),\
                          "wikipedia_url" : "'" + wikipedia_url + "'",\
                          "instructions" : instructions, "randomize_order" : "true"})
        inst_id = VIS_id(d.create('annotation_instances',
                              { 'annotation_instance[annotation_type_version_id]' : annotation_type_version_presence_id,
                                'annotation_instance[name]' : class_name,
                                'annotation_instance[parameters]' : params  
                                }))
        fout = open(IMAGE_DIR + '/' + class_name + '_inst_' + str(SANDBOX) + '.txt', 'w')
        fout.write(str(inst_id))
        fout.close()
    else:
        stream = file(IMAGE_DIR + '/' + class_name + '_inst_' + str(SANDBOX) + '.txt', 'r')
        inst_id = yaml.load(stream)
    return inst_id


# Divide images for a given class into multiple hits
def build_hits(images, class_name, inst_id, hit_type_id):
    if not os.path.isfile(IMAGE_DIR + '/' + class_name + '_hits_' + str(SANDBOX) + '.txt'):
        random.shuffle(images)
        num = 0
        hits = []
        while num < len(images):  
            image_ids_str = '['
            image_thumbs_str = '['
            for i in range(0, min(NUM_IMAGES_PER_HIT,len(images)-num)):
                if i > 0:
                    image_ids_str += ", "
                    image_thumbs_str += ', '
                image_ids_str += str(images[num]['id'])
                image_thumbs_str += '"http://s3.amazonaws.com/visipedia/images/' + str(images[num]['id']) + '/thumb.jpg"'
                num = num+1
            image_ids_str += ']' 
            image_thumbs_str += ']' 
            
            params = VIS_str({"image_ids" : image_ids_str, "image_thumbs" : image_thumbs_str})
            hit_id = VIS_id(d.create('hits',
                                { "hit[hit_type_id]" : hit_type_id,
                                  "hit[annotation_instance_id]" : inst_id,
                                  "hit[lifetime]" : 259200,
                                  "hit[max_assignments]" : WORKERS_PER_HIT,
                                  "hit[parameters]" : params,
                                  "hit[meta]" : "",
                                  "register" : 1 }))
            hits.append(hit_id)
        
        fout = open(IMAGE_DIR + '/' + class_name + '_hits_' + str(SANDBOX) + '.txt', 'w')
        fout.write(VIS_str(hits))
        fout.close()
    else:
        stream = file(IMAGE_DIR + '/' + class_name + '_hits_' + str(SANDBOX) + '.txt', 'r')
        hits = yaml.load(stream)
    return hits



images = []
images_neg = []
insts = []

# Upload images for each class
for i in range(len(CLASS_NAMES)):
    images.append(upload_images(IMAGE_DIR + "/" + CLASS_NAMES[i], CLASS_NAMES[i], WIKI_NAMES[i]))

# For each class, choose a set of negative examples, currently set to images from all other classes
for i in range(len(CLASS_NAMES)):
    images_neg.append([])
    for j in range(len(CLASS_NAMES)):
        if i != j:
            images_neg[i] += images[j]

# Contains custom instructions for each class
for i in range(len(CLASS_NAMES)):
    insts.append(build_annotation_instance(CLASS_NAMES[i], WIKI_NAMES[i], images[i][0:2], images_neg[i][0:2]))

## Build MTurk HITs
#hit_type_id = build_hit_type()
#for i in range(len(CLASS_NAMES)):
#    build_hits(images[i] + images_neg[i], CLASS_NAMES[i], insts[i], hit_type_id)

#Build MTurk HITs only for first class name
hit_type_id = build_hit_type()
build_hits(images[0] + images_neg[0], CLASS_NAMES[0], insts[0], hit_type_id)
