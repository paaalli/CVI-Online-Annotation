import urllib
import pycurl
import StringIO
import zipfile
import os
import yaml
import glob
from xml.etree import ElementTree


class VisipediaConnection:
    
    def __init__(self, access_key, url = 'http://localhost:3000', verbosity = 1):
        self.base_url = url
        self.access_key = access_key
        self.verbosity = verbosity
        self.cookie_file_name = 'cookie.txt'
    
    # Generic function supporting HTTP POST, GET, PUT, DELETE requests 
    def http_connect(self, http_type, class_type, operation, id = None, params={}, files = None):
        if not operation:
            if id and id > 0:
                url = self.base_url + '/' + class_type + '/' + str(id) + '.xml'
            else:
                url = self.base_url + '/' + class_type + '.xml'
        elif id and id > 0:
            url = self.base_url + '/' + class_type + '/' + operation + '/' + str(id) + '.xml'
        else:
            url = self.base_url + '/' + class_type + '/' + operation + '.xml'
        return self.http_connect_url(http_type, url, params, files)

    def http_connect_url(self, http_type, url, params={}, files = None):
        if self.access_key:
            params['access_key'] = self.access_key
        args = urllib.urlencode(params)
        full_url = url + "?" + args if http_type != "POST" or files else url
        res = StringIO.StringIO();
        crl = pycurl.Curl()
        crl.setopt(pycurl.FOLLOWLOCATION, 1)
        crl.setopt(pycurl.COOKIEFILE, self.cookie_file_name)
        crl.setopt(pycurl.COOKIEJAR, self.cookie_file_name)
        crl.setopt(pycurl.CUSTOMREQUEST, http_type)
        if http_type == "POST" and not files:
            crl.setopt(pycurl.POSTFIELDS, args)
        elif files:
            crl.setopt(pycurl.HTTPPOST, files)
        crl.setopt(pycurl.URL, full_url)
        crl.setopt(pycurl.WRITEFUNCTION, res.write)
        crl.perform()
        status = crl.getinfo(pycurl.HTTP_CODE)
        crl.close()
        if status < 200 or status >= 300:
            print "HTTP " + http_type + " " + full_url + " returned " + str(status) + "\n" + res.getvalue()
            return None
        if self.verbosity > 0:
           print "HTTP " + http_type + " " + full_url + " returned " + str(status)
           if self.verbosity > 1:
               print res.getvalue()
        return res.getvalue()


    def show(self, class_type, id, params={}, files = None):
        return self.http_connect("GET", class_type, "show", id, params, files)

    def list(self, class_type, id, params={}, files = None):
        return self.http_connect("GET", class_type, "list", id, params, files)

    def find(self, class_type, params={}, files = None):
        return self.http_connect("GET", class_type, None, None, params, files)

    def create(self, class_type, params={}, files = None):
        return self.http_connect("POST", class_type, "create", None, params, files)

    def update(self, class_type, id, params={}, files = None):
        return self.http_connect("PUT", class_type, None, id, params, files)

    def delete(self, class_type, id, params={}, files = None):
        return self.http_connect("DELETE", class_type, None, id, params, files)

    def custom(self, operation, class_type, id=None, params={}, files = None):
        return self.http_connect("POST", class_type, operation, id, params, files)

    # Upload all .jpg or .png images in a directory, all of which are assumed to have object label obj_id
    def upload_image_directory(self, dir_name, obj_id):
        file_list = glob.glob(dir_name + "/*.jpg") + glob.glob(dir_name + "/*.jpeg")  + glob.glob(dir_name + "/*.JPEG") + glob.glob(dir_name + "/*.jpeg") +  glob.glob(dir_name + "/*.png")
        ids = []
        i = 0
        for file in file_list:
            ids.append(VIS_id(self.create('images', {'obj_id' : obj_id}, [ ("image[image]", VIS_file(file)) ])))
            i = i+1
        return ids



# helper function to extract the ID from an XML string
def VIS_id(xml):
    xml_obj = VIS_fields(xml)
    id = xml_obj['id'] if xml_obj and xml_obj.has_key('id') else None
    return id


# helper function to convert an xml response to a dictionary of fields
def VIS_fields(xml, name=None):
    print 'VIS##############'
    print xml
    print '##############'
    if not xml:
        print 'Error: xml is None'
        return
    retval = {}
    try:
        tree = ElementTree.XML(xml) if xml else None
    except Exception:
        print 'Error parsing xml ' + xml
        return
    if tree and (tree.tag == 'error' or tree.tag == 'errors'):
        print xml
    if tree and tree.tag == 'response':
        if name:
            tree = tree.find(name)
        else:
            tree = tree[0]
    if tree:
        for element in tree:
            retval[element.tag] = element.text
    else:
        print 'Error parsing xml ' + xml
    return retval

def VIS_field_array(xml, name=None):
    if not xml:
        print 'Error: xml is None'
        return
    retval = []
    try:
        tree = ElementTree.XML(xml) if xml else None
    except Exception:
        print 'Error parsing xml ' + xml
        return
    if tree and (tree.tag == 'error' or tree.tag == 'errors'):
        print xml
    if tree and tree.tag == 'response':
        if name:
            tree = tree.find(name)
        else:
            tree = tree[0]
    if tree:
        for element in tree:
            curr = {}
            retval.append(curr)
            for e in element:
                curr[e.tag] = e.text
    else:
        print 'Error parsing xml ' + xml
    return retval

# Use this to attach a file onto an HTTP request
def VIS_file(fname):
    return (pycurl.FORM_FILE, fname)

# Create a qualification structure from 3 parametrs
def VIS_qual(id, val, comparator):
    return { "qualification_id" : id, "comparator" : comparator, "value" : val }

# Output an array or hash as a string in YAML format
def VIS_str(a):
    return "---\n" + yaml.dump(a)

# Use this to attach a folder onto an HTTP request.  The folder contents are
# zipped up in a .zip file.  Excludes .svn folders and files ending with ~
def VIS_folder(folder_name):
    fname = 'tmp.zip'
    archive = zipfile.ZipFile(fname, 'w', compression=zipfile.ZIP_DEFLATED)
    root_len = len(os.path.abspath(folder_name))
    VIS_folder_helper(folder_name, archive, root_len)
    archive.close()
    return VIS_file(fname)

def VIS_folder_helper(folder_name, archive, root_len):
    for root, dirs, files in os.walk(folder_name):
        archive_root = os.path.abspath(root)[root_len:]
        for f in files:
            fullpath = os.path.join(root,f)
            archive_name = os.path.join(archive_root, f)
            if not ".svn" in fullpath and not fullpath.endswith("~"):
                archive.write(fullpath, archive_name, zipfile.ZIP_DEFLATED)
        for d in dirs:
            VIS_folder_helper(os.path.join(folder_name, d), archive, root_len)




