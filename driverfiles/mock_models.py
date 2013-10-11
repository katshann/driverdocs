from driverfiles.models import *

class MockFileObject(FileObject):
    
    def __init__(self, rec):
        self.mock_rec = rec

    def get_filename(self):
        return self.mock_rec['filename']

    def get_loc(self):
        return self.mock_rec['fileloc']

    def get_contents(self):
        return self.mock_rec['data']

    def get_md5(self):
        return self.mock_rec['md5']

    def get_filesize(self):
        return self.mock_rec['filesize']


class MockBinaryFile(MockFileObject):
    pass

class MockUserspaceRPM(MockBinaryFile):
    
    def get_name(self):
        return self.mock_rec['name']

    def get_version(self):
        return self.mock_rec['version']

    def get_arch(self):
        return self.mock_rec['arch']


class MockDriverRPM(MockUserspaceRPM):
    
    def get_kernel(self):
        return self.mock_rec['kernel']

    def get_kernel_version(self):
        return self.mock_rec['kernel_version']


class MockDriverISO(MockBinaryFile):
    pass

class MockDriverRepoPackage(DriverRepoPackage):
    
    def __init__(self, data):
        self.mock_rec = data

    def get_kernel_version(self):
        return self.mock_rec['kernel_version']
        
    def get_iso(self):
        return MockDriverISO(self.mock_rec['iso'])
        
    def get_zip(self):
        return MockBinaryFile(self.mock_rec['zip'])
        
    def get_ctx(self):
        return self.mock_rec['ctx']   
    
    def get_metadata_file(self):
        return MockBinaryFile(self.mock_rec['metadata_file'])

    def get_rpms(self):
        driver_rpms = []
        for rpm_data in self.mock_rec['driver_rpms']:
            driver_rpms.append(MockDriverRPM(rpm_data))

        userspace_rpms = []
        for rpm_data in self.mock_rec['userspace_rpms']:
            userspace_rpms.append(MockUserspaceRPM(rpm_data))

        return driver_rpms, userspace_rpms












