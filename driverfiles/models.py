#!/usr/bin/python

import os
import md5
import utils
import re

class FileObject(object):
    """Generic object representing a file"""

    def __init__(self, fileloc):
        self.fileloc = fileloc        

    def get_filename(self):
        arr = os.path.split(self.fileloc)
        return arr[len(arr)-1]

    def get_loc(self):
        return self.fileloc

    def get_contents(self):
        return utils.read_file(self.fileloc)

    def get_md5(self):
        fh = open(self.fileloc)
        try:
            md5sum = utils.md5_for_file(fh)
            fh.close()
            return md5sum
        except Exception, e:
            fh.close()
            raise e

    def get_filesize(self):
        return os.path.getsize(self.fileloc) 

class BinaryFile(FileObject):
    """Generic object representing a binary file"""
    pass

class UserspaceRPM(BinaryFile):

    patterns = [r'(?P<component_name>([a-z][\w]+[\-]*)+)-(?P<version>[0-9\.\-]+)\.(?P<arch>\w+)\.rpm',
                r'(?P<component_name>([a-z][\w]+[\-]*)+)-v(?P<version>[0-9\.\-]+).(?P<arch>\w+)\.rpm'
               ]

    def __init__(self, fileloc):
        match = None

        for pattern in self.patterns:
            regex = re.compile(pattern)
            match = regex.match(fileloc)

            if match:
                break
            
        if not match:
            raise Exception("Error: could not match filename '%s' with regexs '%s'" % (fileloc, self.patterns))

        self.attrs = match
        return super(UserspaceRPM, self).__init__(fileloc)

    def get_name(self):
        return self.attrs.group('component_name')

    def get_version(self):
        return self.attrs.group('version')

    def get_arch(self):
        return self.attrs.group('arch')

class DriverRPM(UserspaceRPM):
    """Generic object representing an RPM"""

    patterns = [r'(?P<component_name>\w+)-modules-(?P<kernel>\w+)-(?P<kernel_version_major>[0-9a-z\.]+)-(?P<kernel_version_minor>[0-9a-z\.]+)-(?P<version>[0-9a-z\.\-\_]+)\.(?P<arch>\w+)\.rpm',
               ]

    def get_kernel(self):
        return self.attrs.group('kernel')

    def get_kernel_version(self):
        return "%s-%s" % (self.attrs.group('kernel_version_major'), self.attrs.group('kernel_version_minor'))


class DriverISO(BinaryFile):
    """Driver Disk ISO Object"""
    pass

class DriverRepoPackage(object):
    """Represent a package of ISO, source and metadata
    for a particular driver disk spin in a driverdisks.hg
    package."""

    pattern = r'kb-(?P<ctx>CTX[0-9]+)\-(?P<kernel_version>.*)$'

    def __init__(self, dirloc):
        self.dirloc = dirloc

        # Obtain the dirname
        self.dirname = os.path.basename(self.dirloc)

        # Parse directory name
        regex = re.compile(self.pattern)
        self.attrs = regex.match(self.dirname)

        # Find the ISO file in the driver repo
        iso_files = utils.find_files(self.dirloc, "*.iso")
        if len(iso_files) > 1:
            raise Exception("Error: more than one file found! (%s)" % iso_files)
        if not iso_files:
            raise Exception("Error: could not find any ISOs in directory %s" % self.dirloc)

        self.driver_iso = DriverISO(iso_files[0])

        # Find the repo metadata file
        metadata_files = utils.find_files(self.dirloc, "*.metadata.md5")

        if len(metadata_files) > 1:
            raise Exception("Error: more than one metadata files returned! (%s)" % metadata_files)
        if not metadata_files:
            raise Exception("Error: could not find any metadata files")

        self.metadata_file = FileObject(metadata_files[0])

        # Find RPM info file
        rpminfo_files = utils.find_files(self.dirloc, "*.rpminfo")
        if len(rpminfo_files) > 1:
            raise Exception("Error: more than one rpminfo file returned! (%s)" % rpminfo_files)
        if not rpminfo_files:
            raise Exception("Error: could not find any rpminfo files")

        self.rpminfo_file = FileObject(rpminfo_files[0])

        # Find the ZIP file
        zip_files = utils.find_files(self.dirloc, "*.zip")
        if len(zip_files) > 1:
            raise Exception("Error: more than on zip fil returned! (%s)" % zip_files)
        if not zip_files:
            raise Exception("Error: could not find any zip files")

        self.zip_file = FileObject(zip_files[0])

    def get_kernel_version(self):
        """Return the kernel version for which the disk 
        was created"""
        if not self.attrs.group('kernel_version'):
            raise Exception("Error: cannot match directory '%s' against regex '%s'" % (self.dirname, pattern))
        return self.attrs.group('kernel_version')

    def get_iso(self):
        return self.driver_iso

    def get_zip(self):
        return self.zip_file

    def get_ctx(self):
        return self.attrs.group('ctx')

    def get_metadata_file(self):
        return self.metadata_file

    def get_rpms(self):
        driver_rpms = []
        userspace_rpms = []
        for line in self.rpminfo_file.get_contents().split('\n'):
            arr = line.split()
            if not arr:
                #Empty line, skip
                continue
            rpm_filename = os.path.basename(arr[len(arr)-1])

            # Discriminate between RPMs based on whether its labelled like a driver module
            if '-modules-' in rpm_filename:
                driver_rpms.append(DriverRPM(rpm_filename)) 
            else:
                userspace_rpms.append(UserspaceRPM(rpm_filename))
        return driver_rpms, userspace_rpms


    def get_components(self):
        comps = {}
        driver_rpms, userspace_rpms = self.get_rpms()
        for rpm in driver_rpms + userspace_rpms:
            comps[rpm.get_name()] = rpm.get_version()
        return comps 
