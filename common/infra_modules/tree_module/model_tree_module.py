import os

from typing import List
from marshmallow import Schema, fields

from common.app_model import AppDataResult


class TreeModuleResponse(AppDataResult):

    def __init__(self, code: str, data: dict, msg: str = '', exception: Exception = None):
        AppDataResult.__init__(self, code, data, msg, exception)


class FileSystemElement(object):

    def __init__(self, path: str, basename: str, is_directory: bool, size: int) -> None:
        self.path = path
        self.basename = basename
        self.is_directory = is_directory
        self.size = size
        self.children = None

    def add_children(self, children: List[str]) -> None:
        self.children = children

    @staticmethod
    def get_path(self) -> str:
        return self.path

    @staticmethod
    def get_full_path(self) -> str:
        return os.path.join(self.path, self.basename)

    @staticmethod
    def get_basename(self) -> str:
        return self.basename

    @staticmethod
    def is_directory(self) -> bool:
        return self.is_directory

    @staticmethod
    def get_size(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return str(self.__dict__)


class DirectoryFilesParameters:

    def __init__(self, repository_path: str, actual_path: str) -> None:
        self.repository_path = repository_path
        self.actual_path = actual_path


class DirectoryFilesParametersSchema(Schema):
    repository_path = fields.Str()
    actual_path = fields.Str()


class DirectoryFilesResultData:
    def __init__(self, repository_path: str, actual_path: str, number_of_results: int,
                 directory_files_result: List[FileSystemElement]) -> None:
        self.repository_path = repository_path
        self.actual_path = actual_path
        self.number_of_results = number_of_results
        self.directory_files_result = directory_files_result


class FileSystemElementForDirectoryTreeSchema(Schema):
    basename = fields.Str()
    is_directory = fields.Bool()
    size = fields.Int()


class DirectoryTreeResultSchema(Schema):
    repository_path = fields.Str()
    actual_path = fields.Str()
    number_of_results = fields.Int()
    directory_files_result = fields.List(fields.Nested(FileSystemElementForDirectoryTreeSchema))


class RepositoriesResultData:

    def __init__(self, number_of_repositories: int, repositories: List[FileSystemElement]) -> None:
        self.number_of_repositories = number_of_repositories
        self.repositories = repositories


class RepositoriesResultSchema(Schema):
    number_of_repositories = fields.Int()
    repositories = fields.List(fields.Nested(FileSystemElementForDirectoryTreeSchema))


class SearchParameters:

    def __init__(self, from_path: str, text_to_search: str) -> None:
        self.from_path = from_path
        self.text_to_search = text_to_search


class SearchParametersSchema(Schema):
    from_path = fields.Str()
    text_to_search = fields.Str()


class SearchResultData:

    def __init__(self, from_path: str, text_to_search: str, is_search_finished: bool, number_of_results: int, search_result: List[FileSystemElement]) -> None:
        self.from_path = from_path
        self.text_to_search = text_to_search
        self.is_search_finished = is_search_finished
        self.number_of_results = number_of_results
        self.search_result = search_result


class FileSystemElementForSearchResultSchema(Schema):
    path = fields.Str()
    basename = fields.Str()
    is_directory = fields.Bool()
    size = fields.Int()


class SearchResultSchema(Schema):
    from_path = fields.Str()
    text_to_search = fields.Str()
    is_search_finished = fields.Bool()
    number_of_results = fields.Int()
    search_result = fields.List(fields.Nested(FileSystemElementForSearchResultSchema))


class TreeModuleException(Exception):

    def __init___(self, error_args):
        self.error_args = error_args
