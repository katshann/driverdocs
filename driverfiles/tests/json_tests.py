import unittest
import os
from driverfiles import utils
from driverfiles import models


class BaseJsonTest(unittest.TestCase):
    """
    Test the driver repro decoder against a metadata file.
    """

    JSON_FILE = "data/sample-1.json"

    def setUp(self):
        self.directory = utils.create_temp_directory("test-directory")

        json_file_loc = "%s/%s" % (os.path.dirname(os.path.realpath(__file__)), self.JSON_FILE)
        fh = open(json_file_loc, 'r')
        json_data = fh.read()
        fh.close()

        utils.create_file(self.directory, "sample-1.0.json", data=json_data)

        self.drp = models.DriverRepoPackage(self.directory)

@unittest.skip("Needs work")
class TestDriverRepoPackageFromJson(BaseJsonTest):

    def test_get_kernel_version(self):
        kernel_ver = self.drp.get_kernel_version()
        print kernel_ver
        self.assertEqual(kernel_ver, "2.6.32.12-0.7.1.xs6.0.2.542.170665")

    def test_get_iso_filename(self):
        driver_iso = self.drp.get_iso()
        self.assertEqual("emulex-8.3.7.33-4.9.230.0-6.4.13.1-1-GA.iso", driver_iso.get_filename())

    def test_get_iso_md5(self):
        driver_iso = self.drp.get_iso()
        self.assertEqual("9110003b32fc8592f62f2292a9164d9d", driver_iso.get_md5())

    def test_get_iso_sha256(self):
        driver_iso = self.drp.get_iso()
        self.assertEqual("20c326976b5e53b7e028c25eebe24378", driver_iso.get_sha256())

    def test_get_zip_filename(self):
        zip_file = self.drp.get_zip()
        self.assertEqual("emulex-8.3.7.33-4.9.230.0-6.4.13.1-1-GA.zip", zip_file.get_filename())


class TestQlogicQla2xxxJson(BaseJsonTest):

    JSON_FILE = "data/qla2xxx-v8.07.00.18.66.5_k-1.json"


    def test_get_kernel_version(self):
        self.assertEqual("3.10.0+2", self.drp.get_kernel_version())

    def test_get_iso_filename(self):
        self.assertEqual("qla2xxx.iso", self.drp.get_iso().get_filename())

    def test_get_iso_md5(self):
        self.assertEqual("55ac0c4ac3000bff1a1ff90b6d96e3b9", self.drp.get_iso().get_md5())

    def test_get_iso_sha256(self):
        self.assertEqual("339bbe7e064dd3ae5d07f9ba6078703664000c145c710b3b625f6586fa09f4d9",
                        self.drp.get_iso().get_sha256())

    def test_get_metadata_md5(self):
        self.assertEqual("c6716bff6c01740fd2191d48a56788a2", self.drp.get_metadata_file().get_contents())

    def test_get_metadata_filename(self):
        self.assertEqual("qla2xxx.metadata.md5", self.drp.get_metadata_file().get_filename())

    def test_get_rpm_filenames(self):
        driver_rpms, _ = self.drp.get_rpms()
        rpm_filenames = [ rpm.get_filename() for rpm in driver_rpms]
        rpm_filenames.sort()
        self.assertEqual(["qla2xxx-3.10.0+2-modules-v8.07.00.18.66.5_k-1.x86_64.rpm",
                          "qla2xxx-modules-v8.07.00.18.66.5_k-1.x86_64.rpm"], rpm_filenames)


    def test_get_rpm_version(self):
        driver_rpms, _ = self.drp.get_rpms()
        for rpm in driver_rpms:
            self.assertEqual("v8.07.00.18.66.5_k", rpm.get_version())

    def test_get_rpm_name(self):
        driver_rpms, _ = self.drp.get_rpms()
        self.assertEqual("qla2xxx-modules", driver_rpms[0].get_name())
        self.assertEqual("qla2xxx-3.10.0+2-modules", driver_rpms[1].get_name())

    def test_get_rpm_modules(self):
        driver_rpms, _ = self.drp.get_rpms()
        module_rpms = [rpm for rpm in driver_rpms if rpm.get_modules()]
        self.assertEqual(len(module_rpms), 1)

        expected = [{"name": "qla2xxx", "version": "8.07.00.18.66.5-k"}, {"name": "tcm_qla2xxx"}]
        self.assertEqual(module_rpms[0].get_modules(), expected)

    def test_get_zip_filename(self):
        self.assertEqual("qla2xxx-v8.07.00.18.66.5_k-1.zip", self.drp.get_zip().get_filename())

    def test_get_zip_md5(self):
        self.assertEqual("fe4aa428ec710e4cbaa3206e62985356", self.drp.get_zip().get_md5())

    def test_get_zip_sha256(self):
        self.assertEqual("30ba37f2ecb410877ac758b672b3951853941adc55d39a8d235d56c6b73bc9a8", self.drp.get_zip().get_sha256())
