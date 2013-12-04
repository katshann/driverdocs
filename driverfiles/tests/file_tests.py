#!/usr/bin/env python
"""Unit tests for driver framework"""

import unittest
from driverfiles import models, utils

###### Unit Test Imports ######
import os


def assert_equal(ground_truth, value):
    """Check for equality between two objects"""

    if ground_truth != value:
        raise Exception("Assert Equal Fail: '%s' should equal '%s' but it doesn't." % (value, ground_truth))

def assert_in(value, search_list):
    """Assert that a provided value is in a given list"""

    if value not in search_list:
        raise Exception("Assert In Fail: Could not find object '%s' in list '%s'" % (value, search_list))

def assert_equal_len(lista, listb):

    if len(lista) != len(listb):
        raise Exception("Assert Equal Len Fail: Lists were different sizes. (%d, %d) ('%s', '%s')" % (len(lista), len(listb), lista, listb))    

##############################

class BinaryFileObjectsTests(unittest.TestCase):
    """Check md5 utils functions"""
    TEST_FILE = None
    RANDOM_DATA_SIZE = 100
    CREATED_FILES = []

    def setUp(self):
        self.FILENAME = "testbinaryfiles%s.txt" % utils.get_random_string(4)
        test_file = "/tmp/%s" % self.FILENAME
        self.TEST_FILE = test_file

        # Construct binary file with random data

        fh = open(self.TEST_FILE, "w")
        fh.write("This is a test message for for constructing a binary file: %s" % utils.get_random_string(self.RANDOM_DATA_SIZE))
        fh.close()

        self._generate_md5_file_for_binary()
        self._record_created(self.TEST_FILE)
        self._record_created("%s.md5" % self.TEST_FILE)

    def tearDown(self):
        for filename in self.CREATED_FILES:
            os.unlink(filename)

    def _record_created(self, filename):
        file_list = list(self.CREATED_FILES)
        file_list.append(filename)
        self.CREATED_FILES = file_list
    
    def _generate_md5_file_for_binary(self):
        # Generate MD5 of binary file - use system call
        call = ['/usr/bin/md5sum', self.TEST_FILE]
        self.md5_truth = utils.make_local_call(call).split()[0]
        fh = open("%s.md5" % self.TEST_FILE, 'w')
        fh.write(self.md5_truth)
        fh.close()

    def test_verify_md5(self):
        bf = models.BinaryFile(self.TEST_FILE)
        md5sum = bf.get_md5()
        assert_equal(self.md5_truth, md5sum)

    def test_verify_filename(self):
        bf = models.BinaryFile(self.TEST_FILE)
        filename = bf.get_filename()
        assert_equal(self.FILENAME, filename)

    def test_get_loc(self):
        bf = models.BinaryFile(self.TEST_FILE)
        file_loc = bf.get_loc()
        assert_equal(self.TEST_FILE, file_loc)
     

class TestDriverRPMFileObjects(unittest.TestCase):
    
    sample_data = {"file_loc": "bnx2x-modules-xen-2.6.32.12-0.7.1.xs6.0.2.542.170665-1.72.55-1.i386.rpm",
                   "driver": "bnx2x",
                   "driver_version": "1.72.55-1",
                   "kernel": "xen",
                   "arch": "i386",
                   "kernel_version": "2.6.32.12-0.7.1.xs6.0.2.542.170665"}


    def setUp(self):
        # Create a dummy file object for testing with
        self.rpm = models.DriverRPM(self.sample_data['file_loc'])
        
    def test_get_module(self):
        assert_equal(self.sample_data['driver'], self.rpm.get_name())

    def test_get_driver_version(self):
        assert_equal(self.sample_data['driver_version'], self.rpm.get_version())

    def test_get_kernel(self):
        assert_equal(self.sample_data['kernel'], self.rpm.get_kernel())

    def test_get_kernel_version(self):
        assert_equal(self.sample_data['kernel_version'], self.rpm.get_kernel_version())

    def test_get_arch(self):
        assert_equal(self.sample_data['arch'], self.rpm.get_arch())


class TestDriverRepoPackage(unittest.TestCase):
    

    sample_data = {"dir": "kb-CTX134278-2.6.32.12-0.7.1.xs6.0.2.553.170674xen",
                   "ctx": "CTX134278",
                   "kernel_version": "2.6.32.12-0.7.1.xs6.0.2.553.170674xen",
                   "drivers": {'bnx2x':'1.72.55-1'},
                   "iso": "bnx2x-1.72.55-XS602E007.iso",
                   "zip": "bnx2x-1.72.55-XS602E007.zip",
                   "hotfix": "XS602E007",
                   "metadata_md5": "d4a71bc7572354f0fdbcb78ae6165c0d",
                   "rpmdata": ['-rw-r--r-- 1 root root 823646 Sep 14 05:11 bnx2x-modules-kdump-2.6.32.12-0.7.1.xs6.0.2.553.170674-1.72.55-1.i386.rpm',
                               '-rw-r--r-- 1 root root 824401 Sep 14 05:10 bnx2x-modules-xen-2.6.32.12-0.7.1.xs6.0.2.553.170674-1.72.55-1.i386.rpm']
                   }

    def setUp(self):
        """Create a dummy directory for testing purposes"""
        self.directory = utils.create_temp_directory(self.sample_data['dir'])

        self.base_filename = self.sample_data['iso'].replace('.iso','')
 
        # Generate RPM Info Data
        rpminfo = '\n'.join(self.sample_data['rpmdata'])
    
        utils.create_file(self.directory, "%s.iso" % self.base_filename, checksums=['md5','sha256'])
        utils.create_file(self.directory, "%s.zip" % self.base_filename, checksums=['md5','sha256'])
        utils.create_file(self.directory, "%s.rpminfo" % self.base_filename, data=rpminfo)
        utils.create_file(self.directory, "%s.metadata.md5" % self.base_filename, data=self.sample_data['metadata_md5'])


    def test_get_kernel_version(self):
        drp = models.DriverRepoPackage(self.directory)
        kernel_ver = drp.get_kernel_version()        
        assert_equal(self.sample_data['kernel_version'], kernel_ver)
    
    def test_get_iso_name(self):
        drp = models.DriverRepoPackage(self.directory)
        iso = drp.get_iso()
        assert_equal(self.sample_data['iso'], iso.get_filename())
        
    def test_get_iso_md5(self):
        drp = models.DriverRepoPackage(self.directory)
        iso = drp.get_iso()
        fh = open(iso.get_loc())
        truth_md5 = utils.checksum_for_file(fh, 'md5')
        fh.close()
        assert_equal(truth_md5, iso.get_md5())

    def test_get_iso_sha256(self):
        drp = models.DriverRepoPackage(self.directory)
        iso = drp.get_iso()
        fh = open(iso.get_loc())
        truth_sha256 = utils.checksum_for_file(fh, 'sha256')
        fh.close()
        assert_equal(truth_sha256, iso.get_sha256())

    def test_get_zip(self):
        drp = models.DriverRepoPackage(self.directory)
        zip_file = drp.get_zip()
        assert_equal(self.sample_data['zip'], zip_file.get_filename())
    
    def test_get_metadata_md5(self):
        drp = models.DriverRepoPackage(self.directory)
        metadata_md5 = drp.get_metadata_file().get_contents()
        assert_equal(self.sample_data['metadata_md5'], metadata_md5)
        
    def test_verify_driver_versions(self):
        drp = models.DriverRepoPackage(self.directory)
        drpms_all, _ = drp.get_rpms()
        driver_rpms = [rpm for rpm in drpms_all if rpm.get_kernel() == 'xen']
        assert len(driver_rpms) == len(self.sample_data['drivers'].keys())
        for driver_rpm in driver_rpms:
            driver_name = driver_rpm.get_name()
            assert driver_name in self.sample_data['drivers'].keys()
            assert_equal(driver_rpm.get_version(), self.sample_data['drivers'][driver_name])

    def test_verify_rpm_names(self):
        drp = models.DriverRepoPackage(self.directory)
        driver_rpms, userspace_rpms = drp.get_rpms()
        
        # Define truth list
        rpm_names = [os.path.basename(rpm.split().pop()) for rpm in self.sample_data['rpmdata']]

        for driver_rpm in driver_rpms:
            assert_in(driver_rpm.get_filename(), rpm_names)

        for userspace_rpm in userspace_rpms:
            assert_in(userspace_rpm.get_filename(), rpm_names)

        # Check the total number of rpms is correct
        assert len(driver_rpms) + len(userspace_rpms) == len(rpm_names)


class TestDriverRepoPackageEmulex(TestDriverRepoPackage):

    sample_data = {"dir": "kb-CTX132611-2.6.32.12-0.7.1.xs6.0.2.542.170665xen",
                   "ctx": "CTX132611",
                   "kernel_version": "2.6.32.12-0.7.1.xs6.0.2.542.170665xen",
                   "drivers": {'lpfc':'8.3.5.44.4p-1', 'be2net':'4.0.359.0-1'},
                   "iso": "emulex.iso",
                   "zip": "emulex.zip",
                   "hotfix": "GA",
                   "metadata_md5": "d6571d90382d7f97203fe97e22718c70",
                   "rpmdata": ['-rw-r--r-- 1 root root   44193 Mar  2 07:27 /root/emulex/package/be2net-modules-kdump-2.6.32.12-0.7.1.xs6.0.2.542.170665-4.0.359.0-1.i386.rpm',
                               '-rw-r--r-- 1 root root   44287 Mar  2 07:27 /root/emulex/package/be2net-modules-xen-2.6.32.12-0.7.1.xs6.0.2.542.170665-4.0.359.0-1.i386.rpm',
                               '-rw-r--r-- 1 root root 3155837 Mar  2 07:25 /root/emulex/package/elxocmcore-5.2.12.2-1.i386.rpm',
                               '-rw-r--r-- 1 root root    8873 Mar  2 07:25 /root/emulex/package/elxocmlibhbaapi-5.2.12.2-1.i386.rpm',
                               '-rw-r--r-- 1 root root  238950 Mar  2 07:28 /root/emulex/package/lpfc-modules-kdump-2.6.32.12-0.7.1.xs6.0.2.542.170665-8.3.5.44.4p-1.i386.rpm',
                               '-rw-r--r-- 1 root root  252628 Mar  2 07:28 /root/emulex/package/lpfc-modules-xen-2.6.32.12-0.7.1.xs6.0.2.542.170665-8.3.5.44.4p-1.i386.rpm'
                               ]
                   }

class TestDriverRepoPackageQla2xxx(TestDriverRepoPackage):

    sample_data = {"dir": "kb-CTX136466-2.6.32.12-0.7.1.xs6.0.2.587.170693xen",
                   "ctx": "CTX136466",
                   "kernel_version": "2.6.32.12-0.7.1.xs6.0.2.587.170693xen",
                   "drivers": {'qla2xxx':"8.04.00.02.55.6_k-1"},
                   "iso": "qla2xxx-8.04.00.02.55.6-k-XS602E021.iso",
                   "zip": "qla2xxx-8.04.00.02.55.6-k-XS602E021.zip",
                   "hotfix": "XS602E021",
                   "metadata_md5": "20c326976b5e53b7e028c25eebe24378",
                   "rpmdata": ['-rw-r--r-- 1 root root 460765 Feb 19 09:53 firmware-qlogic-qla2xxx-762-3.noarch.rpm',
                               '-rw-r--r-- 1 root root 186416 Feb 19 12:19 qla2xxx-modules-kdump-2.6.32.12-0.7.1.xs6.0.2.587.170693-8.04.00.02.55.6_k-1.i386.rpm',
                               '-rw-r--r-- 1 root root 186882 Feb 19 12:19 qla2xxx-modules-xen-2.6.32.12-0.7.1.xs6.0.2.587.170693-8.04.00.02.55.6_k-1.i386.rpm'
                               ]
                  }


class TestDriverRepoPackageQla2xxxNewPackaging(TestDriverRepoPackage):
    
    sample_data = {"dir": "QL-196-GA-2.6.32.43-0.4.1.xs1.6.10.734.170748xen",
                   "ctx": "",
                   "kernel_version": "2.6.32.43-0.4.1.xs1.6.10.734.170748xen",
                   "drivers": {'qla2xxx': "8.06.00.10.55.6_k-1"},
                   "iso": "qla2xxx-8.06.00.10.55.6-k-GA.iso",
                   "zip": "qla2xxx-8.06.00.10.55.6-k-GA.zip",
                   "hotfix": "GA",
                   "metadata_md5": "9110003b32fc8592f62f2292a9164d9d",
                   "rpmdata": ['-rw-r--r-- 1 root root 244587 Nov 18 08:09 qla2xxx-modules-kdump-2.6.32.43-0.4.1.xs1.6.10.734.170748-8.06.00.10.55.6_k-1.i386.rpm',
                               '-rw-r--r-- 1 root root 245258 Nov 18 08:09 qla2xxx-modules-xen-2.6.32.43-0.4.1.xs1.6.10.734.170748-8.06.00.10.55.6_k-1.i386.rpm'
                               ]
                  }


class TestDriverRepoPackageEmxSanibel(TestDriverRepoPackage):
    
    sample_data = {"dir": "CTX139408-GA-2.6.32.12-0.7.1.xs6.0.2.542.170665xen",
                   "ctx": "CTX139408",
                   "kernel_version": "2.6.32.12-0.7.1.xs6.0.2.542.170665xen",
                   "drivers": {'lpfc': '8.3.7.33-1', 'be2net': '4.9.230.0-1'},
                   "iso": "emulex-8.3.7.33-4.9.230.0-6.4.13.1-1-GA.iso",
                   "zip": "emulex-8.3.7.33-4.9.230.0-6.4.13.1-1-GA.zip",
                   "hotfix": "GA",
                   "metadata_md5": "3be6ed9465c6a9e80e80e23775b1e465",
                   "rpmdata": ['-rw-r--r-- 1 root root   56246 Nov  5 10:50 be2net-modules-kdump-2.6.32.12-0.7.1.xs6.0.2.542.170665-4.9.230.0-1.i386.rpm',
                               '-rw-r--r-- 1 root root   56213 Nov  5 10:50 be2net-modules-xen-2.6.32.12-0.7.1.xs6.0.2.542.170665-4.9.230.0-1.i386.rpm',
                               '-rw-r--r-- 1 root root 3334333 Oct 30 09:34 elxocmcore-6.4.13.1-1.i386.rpm',
                               '-rw-r--r-- 1 root root  313344 Oct 30 09:34 elxocmcorelibs-6.4.13.1-1.i386.rpm',
                               '-rw-r--r-- 1 root root    9274 Oct 30 09:34 elxocmlibhbaapi-6.4.13.1-1.i386.rpm',
                               '-rw-r--r-- 1 root root  299793 Nov  5 10:51 lpfc-modules-kdump-2.6.32.12-0.7.1.xs6.0.2.542.170665-8.3.7.33-1.i386.rpm',
                               '-rw-r--r-- 1 root root  299761 Nov  5 10:50 lpfc-modules-xen-2.6.32.12-0.7.1.xs6.0.2.542.170665-8.3.7.33-1.i386.rpm',
                              ]
    }



if __name__ == '__main__':
    unittest.main()


