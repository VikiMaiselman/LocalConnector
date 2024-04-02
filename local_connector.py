import os
import logging
from typing import List
from functools import reduce

from base_connector import AuthenticationStatus
from base_connector import BaseConnector


############################   LOGGER CONFIG   ############################
logging.basicConfig(filename='./logger/error.log', level=logging.ERROR)
logger = logging.getLogger("VikLog")


############################   IMPLEMENTATION   ############################
class LocalFileConnector(BaseConnector):
    """
        This class provides an implementation for BaseConnector abstract class.
        It is used to connect to the local file system as a source.
    """

    def connect_to_source(self) -> AuthenticationStatus:
        """
        Authenticate with the specific source.
        """

        return AuthenticationStatus.SUCCEEDED

        
    def get_last_modification_time(self, remote_file_path: str) -> float:
        """
        Get last file modification time.
        :param remote_file_path: file path
        """

        try:
            timestamp: float = os.path.getmtime(remote_file_path)
        except FileNotFoundError as e: 
            logging.error('An error occurred: %s', str(e))
            raise
        except OSError as e:
            logging.error('File inaccessible: %s', str(e))
            raise

        return timestamp


    def get_connection_details(self) -> dict:
        """
        Get all the connection details from the DB: host, port, username, password etc.
        """

        return {
            "host": "localhost",
            "port": 8000,
            "username": None,
            "password": None
        }

   
    def get_directory_tree(self, remote_dir: str = ".", include_files: bool = False,
                           include_directories: bool = True) -> List[str]:
        """
        Get the directory tree in the specific source.
        :param remote_dir: path to the directory, default value: current directory
        :param include_directories: whether to include directories in the result.
        :param include_files: whether to include files, that are not directories, in the result.
        """

        try:
            if not os.path.exists(remote_dir):
                raise OSError("Path invalid")
        except OSError as e: 
            logging.error('An error occurred: %s', str(e))
            raise
        
        dir_tree_generator = os.walk(remote_dir, onerror=lambda e: OSError)

        if not include_files and not include_directories:
            return [remote_dir]            
        
        if not include_files and include_directories:
            return [dir_name for dir_name, *_ in dir_tree_generator]
            
        if include_files and not include_directories:
            result = [[*files] for _, _, files in dir_tree_generator]
            return list(reduce(lambda x, y: x + y, result, [remote_dir]))
    
        if include_files and include_directories:
            result = [[dir_name, *files] for dir_name, sub_dirs, files in dir_tree_generator]
            return list(reduce(lambda x, y: x + y, result, []))
           

    def remove_local_file(self, _id: str):
        """ 
        Remove the copied file from the local directory
        :param _id: for local fs it is the path to the file
        """

        try:
            os.remove(_id)
        except FileNotFoundError as e:
            logging.error('The file does not exist: %s', str(e))
            raise
        except OSError as e:
            logging.error('Provide a path to a file, not a directory: %s', str(e))
            raise


    def download_file(self, remote_path: str, local_path: str) -> bool:
        """
        Download the file from the remote source path to the locat path
        :param remote_path: path to file from the local fs
        :param local_path: path to new file created from the original one
        """

        try:
            with open(remote_path, 'r') as src, open(local_path, 'w') as dest:
                content = src.read()
                dest.write(content)
                return True
        except FileNotFoundError as e:
            logging.error('The file does not exist: %s', str(e))
            return False  
        except PermissionError as e:
            logging.error('The files do not have appropriate permissions: %s', str(e))
            return False
    
      
        
if __name__ == "__main__":
    pass
    # localFC = LocalFileConnector(connection_id="local", connection_name="test_connection", description="test")
    # print(localFC.get_directory_tree("/Users/viki_m/Desktop/books", include_files=True, include_directories=True))