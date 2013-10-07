#!/usr/bin/python
"""utils.py module"""

import hashlib
import subprocess
import string
import random
import os
import fnmatch

def get_random_string(length, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(length))

def create_temp_directory(dirname, base_dir="/tmp"):
    full_path = "%s/%s/%s" % (base_dir, get_random_string(5), dirname)
    os.makedirs(full_path)
    return full_path

def create_file(directory, filename, data=None, md5=False):
    file_loc = "%s/%s" % (directory, filename)
    file_h = open(file_loc, 'w')
    if data:
        file_h.write(data)
    file_h.close()

    # Now open the file for reading
    file_h = open(file_loc, 'r')
    
    if md5:
        md5sum = md5_for_file(file_h)
        fh = open("%s.md5" % file_loc, 'w')
        fh.write("%s %s" % (file_loc, md5sum))
        fh.close()

    file_h.close()

def md5_for_file(f, block_size=2**20):
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    return md5.hexdigest()    

def make_local_call(call):
    process = subprocess.Popen(call, stdout=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        return str(stdout).strip()
    else:
        raise Exception("Local Call Failure: %s" % stderr)

def find_files(basedir, pattern):
    """Find files in a specied directory using the provided pattern"""
    matches = []
    for root, dirs, filenames in os.walk(basedir):
        for filename in fnmatch.filter(filenames, pattern):
            matches.append(os.path.join(root, filename))
        for dirname in fnmatch.filter(dirs, pattern):
            matches.append(os.path.join(root, dirname))
    return matches

def read_file(fileloc):
    """Read the contents of a file and return to the caller"""
    fh = open(fileloc, 'r')
    try:
        data = fh.read()
        fh.close()
        return data
    except Exception, e:
        fh.close()
        raise e


    


