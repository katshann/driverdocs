import unittest
from driverfiles.mock_models import *

from mock import Mock

from articlegenerator import extract

class ArticleDataSourceTests(unittest.TestCase):
    
    def test_addition(self):
        data_1 = {'one': '1','two': '2','three': '3'}
        data_2 = {'four': '4', 'five': '5', 'six': '6'}

        class_1 = extract.ArticleDataSource(data_1)
        class_2 = extract.ArticleDataSource(data_2)

        class_3 = class_1 + class_2

        # Verify all the data has been copied over
        data_dict = class_3.export()

        for k, v in data_1.iteritems():
            assert (data_dict[k] == v)

        for k, v in data_2.iteritems():
            assert (data_dict[k] == v)

        # validate the correct number of items

        assert ( len(data_dict) == (len(data_1) + len(data_2)) )


        
class DriverRepoDataSourceTests(unittest.TestCase):
    
    def setUp(self):
        self.drds = extract.DriverRepoDataSource('/tmp/test')

        mock_data = {
                        'kernel_version' : '2.3.52.x',
                        'iso': {
                                'filename': 'test.iso',
                                'fileloc': '/tmp/test.iso',
                                'data': 'fasdadsfgag',
                                'md5': 'md5summd5sum',
                                'sha256': 'sha256sumasdf',
                                'filesize': '12415',
                               },
                        'zip': {
                                'filename': 'test.zip',
                                'fileloc': '/tmp/test.zip',
                                'data': 'dummydata',
                                'md5': 'md5summd5sum1',
                                'sha256': 'sha256sumasdf',
                                'filesize': '59693',
                               },
                        'ctx': 'CTXTestNumber',
                        'metadata_file': {
                                           'filename': 'test.metadata.md5',
                                           'fileloc': '/tmp/test.metadata.md5',
                                           'data': '23523582358235235',
                                           'md5': 'asdfasdfasdf',
                                           'filesize': '124124',
                                         },
                        'driver_rpms': [
                                        {
                                          'filename':'test-rpm-1.rpm',
                                          'fileloc':'/tmp/test-rpm-1.rpm',
                                          'data': 'kahlfsadf',
                                          'md5': 'md5sumtestrpm1',
                                          'filesize': '2352354',
                                          'name': 'test-rpm-1',
                                          'version': '1.2.4',
                                          'arch': 'x86',
                                          'kernel': 'xen',
                                          'kernel_version': '2.3.52.x',
                                        },
                                        {
                                          'filename':'test-rpm-2.rpm',
                                          'fileloc':'/tmp/test-rpm-2.rpm',
                                          'data': 'kahasdfgf',
                                          'md5': 'md5sumtestrpm2',
                                          'filesize': '2323524',
                                          'name': 'test-rpm-2',
                                          'version': '1.2.4',
                                          'arch': 'x86',
                                          'kernel': 'xen',
                                          'kernel_version': '2.3.52.x',
                                        },
                                       ],
                        'userspace_rpms': [
                                            {
                                              'filename':'userspace-rpm.rpm',
                                              'fileloc':'/tmp/userspace-rpm.rpm',
                                              'data': 'kahassdgasdg',
                                              'md5': 'md5sumtestrpm3',
                                              'filesize': '2438821',
                                              'name': 'test-userspace-rpm',
                                              'version': '1.2.4',
                                              'arch': 'x86',
                                            },
                                          ],
                    }

        self.mock_data = mock_data
        mock_driver_repo = MockDriverRepoPackage(mock_data)
        self.drds.get_inspector = Mock(return_value=mock_driver_repo)
        self.drds.collect()
        self.exported_data = self.drds.export()

    def test_get_iso(self):
        data = self.exported_data
        mock_data = self.mock_data

        self.assertEqual(data['iso']['filename'], mock_data['iso']['filename'])
        self.assertEqual(data['iso']['md5'], mock_data['iso']['md5'])

        self.assertEqual(data['zip']['filename'], mock_data['zip']['filename'])
        self.assertEqual(data['zip']['md5'], mock_data['zip']['md5'])

        self.assertEqual(data['kernel_version'], mock_data['kernel_version'])
        self.assertEqual(data['metadata_file']['filename'], mock_data['metadata_file']['filename'])
        self.assertEqual(data['metadata_file']['data'], mock_data['metadata_file']['data'])

        #Verify RPM data
        assert len(mock_data['driver_rpms']) + \
               len(mock_data['userspace_rpms']) == len(data['rpms'])


        def equate_rec(reca, recb):
            shared_items = set(reca.items()) & set(recb.items())
            return len(shared_items) == len(reca) == len(recb)

        def find_rec(rec_list, rec):
            for rec_item in rec_list:
                if equate_rec(rec, rec_item):
                    return True

            return False

        for driver_rpm in mock_data['driver_rpms']:
            search_rec = {
                            'module_name': driver_rpm['name'],
                            'version': driver_rpm['version'],
                            'filename': driver_rpm['filename'],
                            'kernel': driver_rpm['kernel'],
                         }
            print data['rpms']
            assert find_rec(data['rpms'], search_rec)


        for userspace_rpm in mock_data['userspace_rpms']:
            search_rec = {
                            'module_name': userspace_rpm['name'],
                            'version': userspace_rpm['version'],
                            'filename': userspace_rpm['filename'],                
                         }
            assert find_rec(data['rpms'], search_rec)

               
if __name__ == "__main__":
    unittest.main()                
