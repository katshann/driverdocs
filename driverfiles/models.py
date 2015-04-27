#!/usr/bin/python

import os
from driverfiles import utils
import re
import json

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

    def _get_checksum(self, checksum):
        fh = open(self.fileloc)
        try:
            csum = utils.checksum_for_file(fh, checksum)
            fh.close()

            # Verify csum against value in csum file if exists
            cfile_loc = "%s.%s" % (self.get_loc(), checksum)
            if os.path.isfile(cfile_loc):
                fh = open(cfile_loc)
                data = fh.read()
                fh.close()
                assert csum in data

            return csum
        except Exception, e:
            fh.close()
            raise e

    def get_md5(self):
        return self._get_checksum('md5')

    def get_sha256(self):
        return self._get_checksum('sha256')

    def get_filesize(self):
        return os.path.getsize(self.fileloc)

class FakeFileObject(object):

    def __init__(self, data):
        self.data = data

    def get_filename(self):
        return self.data["filename"]

    def _get_checksum(self, checksum):
        return self.data[checksum]

    def get_contents(self):
        return self.data["contents"]

    def get_md5(self):
        return self._get_checksum("md5")

    def get_sha256(self):
        return self._get_checksum("sha256")


class FakeRPMObject(FakeFileObject):


    def get_type(self):
        return self.data["type"]

    def get_modules(self):
        return self.data["modules"]

    def get_name(self):
        return self.data["name"]

    def get_version(self):
        return self.data["version"]


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
        super(UserspaceRPM, self).__init__(fileloc)

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

    patterns = [
                 r'(?P<ticket>(\w)+\-[0-9]+)\-(?P<hotfix>(\w)+)\-(?P<kernel_version>.*)$',
                 r'(?P<ctx>CTX[0-9]+)\-(?P<hotfix>(\w)+)\-(?P<kernel_version>.*)$',
                 r'kb-(?P<ctx>CTX[0-9]+)\-(?P<kernel_version>.*)$',
               ]


    def __init__(self, dirloc):
        self.data = {}
        self.dirloc = dirloc

        # Obtain the dirname
        self.dirname = os.path.basename(self.dirloc)

        if self.find_json_metadata():
            self.data_load_from_json()
        else:
            self.legacy_data_load_from_files()

    def find_json_metadata(self):
        for f in os.listdir(self.dirloc):
            if f.endswith(".json"):
                return "%s/%s" % (self.dirloc, f)
        return None

    def data_load_from_json(self):
        fh = open(self.find_json_metadata(), 'r')
        json_data = fh.read()
        fh.close()

        jdata = json.loads(json_data)

        self.data["kernel_version"] = jdata["kernel_version"]

        driver_iso = FakeFileObject(jdata["iso"])
        self.data["driver_iso"] = driver_iso

        zip_file = FakeFileObject(jdata["zip"])
        self.data["zip_file"] = zip_file

        metadata_file = FakeFileObject(jdata["iso"]["metadata"])
        self.data["metadata_file"] = metadata_file

        driver_rpms = []
        userspace_rpms = []

        for rpm in jdata["rpms"]:

            rpm_file = FakeRPMObject(rpm)

            if rpm["type"] == "kernel":
                driver_rpms.append(rpm_file)
            else:
                userspace_rpms.append(rpm_file)

        self.data["driver_rpms"] = driver_rpms
        self.data["userspace_rpms"] = userspace_rpms

    def legacy_data_load_from_files(self):

        # Parse directory name
        self.attrs = None
        for pattern in self.patterns:
            regex = re.compile(pattern)
            self.attrs = regex.match(self.dirname)
            if self.attrs:
                # If we've found a match, go with that.
                break

        if not self.attrs:
            # None of the dir patterns were matched.
            raise Exception("Error: could not match directory '%s' to known pattern" % self.dirname)

        # Find the ISO file in the driver repo
        iso_files = utils.find_files(self.dirloc, "*.iso")
        if len(iso_files) > 1:
            raise Exception("Error: more than one file found! (%s)" % iso_files)
        if not iso_files:
            raise Exception("Error: could not find any ISOs in directory %s" % self.dirloc)

        self.data["driver_iso"] = DriverISO(iso_files[0])

        # Find the repo metadata file
        metadata_files = utils.find_files(self.dirloc, "*.metadata.md5")

        if len(metadata_files) > 1:
            raise Exception("Error: more than one metadata files returned! (%s)" % metadata_files)
        if not metadata_files:
            raise Exception("Error: could not find any metadata files")

        self.data["metadata_file"] = FileObject(metadata_files[0])

        # Find RPM info file
        rpminfo_files = utils.find_files(self.dirloc, "*.rpminfo")
        if len(rpminfo_files) > 1:
            raise Exception("Error: more than one rpminfo file returned! (%s)" % rpminfo_files)
        if not rpminfo_files:
            raise Exception("Error: could not find any rpminfo files")

        rpminfo_file = FileObject(rpminfo_files[0])

        # Find the ZIP file
        zip_files = utils.find_files(self.dirloc, "*.zip")
        if len(zip_files) > 1:
            raise Exception("Error: more than on zip fil returned! (%s)" % zip_files)
        if not zip_files:
            raise Exception("Error: could not find any zip files")
        self.data["zip_files"] = zip_files

        self.data["zip_file"] = FileObject(zip_files[0])

        self.data['kernel_version'] = self.attrs.group('kernel_version')

        # Initialise RPMs
        driver_rpms = []
        userspace_rpms = []
        for line in rpminfo_file.get_contents().split('\n'):
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

        self.data["driver_rpms"] = driver_rpms
        self.data["userspace_rpms"] = userspace_rpms

    def get_kernel_version(self):
        """Return the kernel version for which the disk
        was created"""
        return self.data["kernel_version"]

    def get_iso(self):
        return self.data["driver_iso"]

    def get_zip(self):
        return self.data["zip_file"]

    def get_metadata_file(self):
        return self.data["metadata_file"]

    def get_rpms(self):
        return self.data["driver_rpms"], self.data["userspace_rpms"]


    def get_components(self):
        comps = {}
        driver_rpms, userspace_rpms = self.get_rpms()
        for rpm in driver_rpms + userspace_rpms:
            comps[rpm.get_name()] = rpm.get_version()
        return comps
