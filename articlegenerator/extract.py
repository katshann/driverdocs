#!/usr/bin/env python
"""Module for extracting article information from various data sources"""

from driverfiles.models import *

class ArticleDataSource(object):
    """A base class for obtaining data to fill out an article template"""

    data = {}

    def __init__(self, data=None):
        if data:
            self.data = data

    def export(self):
        return self.data

    def __add__(self, x):
        new_dict = dict(self.data.items() + x.export().items())
        return ArticleDataSource(new_dict)

class DriverRepoDataSource(ArticleDataSource):

    def __init__(self, loc):
        self.loc = loc
        super(DriverRepoDataSource, self).__init__()

    def get_inspector(self):
        return DriverRepoPackage(self.loc)

    def collect(self):
        drp = self.get_inspector()
        data_rec = {}

        # Get ISO information
        iso = drp.get_iso()
        data_rec['iso'] = {
                            'filename': iso.get_filename(),
                            'md5': iso.get_md5(),
                            'sha256': iso.get_sha256(),
                          }

        # Get Zip file information
        zip_file = drp.get_zip()
        data_rec['zip'] = {
                            'filename': zip_file.get_filename(),
                            'md5': zip_file.get_md5(),
                            'sha256': zip_file.get_sha256(),
                          }

        # Get kernel version
        data_rec['kernel_version'] = drp.get_kernel_version()

        metadata = drp.get_metadata_file()
        # Get metadata file
        data_rec['metadata_file'] = {
                                      'filename': metadata.get_filename(),
                                      'data': metadata.get_contents(),
                                    }

        # Get RPM information
        rpm_data = []

        driver_rpms, userspace_rpms = drp.get_rpms()
        for rpm in driver_rpms + userspace_rpms:
            rpm_rec = {
                        'module_name': rpm.get_name(),
                        'version': rpm.get_version(),
                        'filename': rpm.get_filename(),
                      }

            if 'get_kernel' in dir(rpm):
                rpm_rec['kernel'] = rpm.get_kernel()

            rpm_data.append(rpm_rec)

        data_rec['rpms'] = rpm_data

        # Get driver information
        driver_data = []

        xen_rpms = []
        xen_rpms = [rpm for rpm in driver_rpms if rpm.get_kernel() == "xen"]
        for rpm in xen_rpms:
            driver_rec = {'name': rpm.get_name(), 'version': rpm.get_version()}
            driver_data.append(driver_rec)

        data_rec['drivers'] = driver_data

        self.data = data_rec

