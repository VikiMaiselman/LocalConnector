from abc import abstractmethod
from typing import List
from enum import Enum
from pydantic.v1 import BaseModel as PydanticBaseModel


class AuthenticationStatus(Enum):
    SUCCEEDED = 'SUCCEEDED'
    FAILED = 'FAILED'


class BaseModel(PydanticBaseModel):
    class Config:
        arbitrary_types_allowed = True


class BaseConnector(BaseModel):
    connection_id: str
    connection_name: str = ""
    description: str = ""

    @abstractmethod
    def connect_to_source(self) -> AuthenticationStatus:
        """
        Authenticate with the specific source.
        """
        raise NotImplementedError("Subclasses must implement the connect_to_source function.")

    @abstractmethod
    def get_last_modification_time(self, remote_file_path: str) -> float:
        """
        Get last file modification time.
        :param remote_file_path: file path
        """
        raise NotImplementedError("Subclasses must implement the get_last_modification_time function.")

    def get_connection_details(self) -> dict:
        """
        Get all the connection details from the DB: host, port, username, password etc.
        """
        pass

    @abstractmethod
    def get_directory_tree(self, remote_dir: str = ".", include_files: bool = False,
                           include_directories: bool = True) -> List[str]:
        """
        Get the directory tree in the specific source.
        :param include_directories: include directories in the result.
        :param include_files: include files, that are not directories, in the result.
        """
        raise NotImplementedError("Subclasses must implement the get_directory_tree function.")

    def remove_local_file(self, _id: str):
        """ Remove the copied file from the local directory"""
        raise NotImplementedError("Subclasses must implement the remove_file function.")

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download the file from the remote source path to the locat path"""
        raise NotImplementedError("Subclasses must implement the download_file function.")
