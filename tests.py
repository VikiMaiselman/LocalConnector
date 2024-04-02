import os
import unittest
from unittest import mock
import logging

from local_connector import LocalFileConnector
from base_connector import AuthenticationStatus

class TestLocalConnector(unittest.TestCase):

    def setUp(self):
        self.localFC = LocalFileConnector(connection_id="local", connection_name="test_connection", description="test")
        self.logger = logging.getLogger('VikLog')


    def test_connect_to_source(self):
        self.assertIs(self.localFC.connect_to_source(), AuthenticationStatus.SUCCEEDED)
        self.assertIsNot(self.localFC.connect_to_source(), AuthenticationStatus.FAILED,  "could not connect to the source")


    def test_get_last_modification_time(self):
        valid_file_path = "/Users/viki_m/Desktop/projects/WiseryTask/doc.txt"
        invalid_file_path = "/Users/viki_m/Desktop/projects/WiseryTask/do.txt"
        valid_dir_path = "/Users/viki_m/Desktop/projects"

        result = self.localFC.get_last_modification_time(valid_file_path)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, float)

        result = self.localFC.get_last_modification_time(valid_dir_path)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, float)

        with self.assertRaises(FileNotFoundError):
            self.localFC.get_last_modification_time(invalid_file_path)
            self.assertLogs('VikLog', level='ERROR')

        # additional test case: 
        # call last_modified => modify file => call last_modified => result2 - result1 > 0 
        result = self.localFC.get_last_modification_time(valid_file_path)
        with open(valid_file_path, 'w') as file:
            file.write("modification added")
        
        result_2 = self.localFC.get_last_modification_time(valid_file_path)
        self.assertGreater(result_2, result)


    def test_get_connection_details(self):
        result = self.localFC.get_connection_details()
        self.assertIsInstance(result, dict)
        self.assertDictEqual({
            "host": "localhost",
            "port": 8000,
            "username": None,
            "password": None
        }, result)


    def test_download_file(self): 
        path_to_src_file_valid = "/Users/viki_m/Desktop/projects/WiseryTask/doc.txt"
        path_to_dest_file_valid =  "new_files/test_download.txt"
        path_to_src_file_invalid = "/Users/viki_m/Desktop/projects/WiseryTask/do.txt"

        # invalid src path
        result = self.localFC.download_file(path_to_src_file_invalid, path_to_dest_file_valid)
        self.assertFalse(result)

        # valid src path
        result = self.localFC.download_file(path_to_src_file_valid, path_to_dest_file_valid)
        self.assertTrue(result)

        # if file's permissions do not include write - returns False
        os.chmod(path_to_dest_file_valid, 0o001)
        result = self.localFC.download_file(path_to_src_file_valid, path_to_dest_file_valid)
        self.assertFalse(result)
        os.chmod(path_to_dest_file_valid, 0o777)


    @mock.patch('builtins.open')
    def test_download_file_mocked(self, mock_open_file): 
        path_to_src_file_valid = "./any/doc.txt"
        path_to_dest_file_valid =  "./any/new.txt"
    
        self.localFC.download_file(path_to_src_file_valid, path_to_dest_file_valid)
        mock_open_file.assert_called_with(path_to_dest_file_valid, 'w') and mock_open_file.assert_called_with(path_to_src_file_valid, 'r')


    @mock.patch('os.remove')
    def test_remove_local_file(self, mock_os_remove):
        path_to_file = "./new_files/test_download.txt"
        self.localFC.remove_local_file(path_to_file)

        mock_os_remove.assert_called_once_with(path_to_file)
        self.assertTrue(os.path.exists(path_to_file))


    def test_get_directory_tree(self):
        valid_path = "/Users/viki_m/Desktop/books"
        invalid_path = "/Users/viki_m/Desktop/book"

        # no files and no subdirs required, path valid
        result = self.localFC.get_directory_tree(valid_path, include_files=False, include_directories=False)
        self.assertEqual(len(result), 1)
        self.assertTrue(os.path.isdir(result[0]))
        self.assertIsInstance(result, list)

        # no files and no subdirs requested, path invalid
        with self.assertRaises(OSError):
            self.localFC.get_directory_tree(invalid_path)
            self.assertLogs('VikLog', level='ERROR')

        # files and subdirs requested
        result = self.localFC.get_directory_tree(valid_path, include_files=True, include_directories=True)
        self.assertGreater(len(result), 1)
        self.assertIsInstance(result, list)
        
        # no files, but subdirs requested
        result = self.localFC.get_directory_tree(valid_path, include_files=False, include_directories=True)
        self.assertGreater(len(result), 1)
        for dir in result:
            self.assertTrue(os.path.isdir(dir))
        self.assertIsInstance(result, list)

        # check for files w/o subdirs is harder as have to build the path for each file 

if __name__ == '__main__':
    unittest.main()


