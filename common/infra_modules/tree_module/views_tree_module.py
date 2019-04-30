import logging

from typing import Tuple, List, Dict, Union

from common.module import ViewModule, authenticate, AppException
from common.infra_tools.decorators import log_function
from common.infra_modules.tree_module import MODULE_NAME
from common.infra_modules.tree_module.model_tree_module import FileSystemElement
from common.infra_modules.tree_module.model_tree_module import TreeModuleException
from common.infra_modules.tree_module.model_tree_module import TreeModuleResponse, \
    SearchParameters, SearchParametersSchema, SearchResultSchema, SearchResultData, \
    RepositoriesResultSchema, RepositoriesResultData, \
    DirectoryFilesParameters, DirectoryFilesParametersSchema,  DirectoryTreeResultSchema, DirectoryFilesResultData


logger = logging.getLogger(MODULE_NAME)


@authenticate()
class DirectoryTreeModuleView(ViewModule):
    excluded_methods = ["get_directory_files_parameters", "get_directory_files_response_json", "get_repositories_response_json"]


    #get_directory_files
    @log_function(logger, print_result=False)
    def post(self) -> str:

        try:
            directory_files_parameters = self.get_directory_files_parameters()

            directory_files = self.app_module.get_directory_file_system_elements(directory_files_parameters)

            directory_files_response = self.app_module.get_directory_files_response(directory_files_parameters, directory_files)

        except TreeModuleException as directory_files_error:
            logger.exception("Error while retrieving directory files.")
            directory_files_response = directory_files_error.args[0]

        except:
            logger.exception("Unexpected error while retrieving directory files.")
            directory_files_response = {
                "status": "CODE_DIRECTORY_FILES_SERVER_ERROR",
                "message_id": "msg.directory_files.error.server",
                "result": {}
            }

        return self.get_directory_files_response_json(directory_files_response)


    #get_repositories
    @log_function(logger, print_result=False)
    def repositories(self) -> str:

        try:
            if self.app_module.cache_repositories is None:
                self.app_module.load_repositories()

            repositories_response = self.app_module.get_repositories_response()

        except TreeModuleException as repositories_error:
            logger.exception("Error while retrieving repositories.")
            repositories_response = repositories_error.args[0]

        except:
            logger.exception("Unexpected error while retrieving repositories.")
            repositories_response = {
                "status": "CODE_REPOSITORIES_SERVER_ERROR",
                "message_id": "msg.repositories.error.server",
                "result": {}
            }

        return self.get_repositories_response_json(repositories_response)


    def get_directory_files_parameters(self) -> Tuple[str]:

        invalid_directory_files_parameters_response = {
            "status": "CODE_INVALID_DIRECTORY_FILES_PARAMETERS_ERROR",
            "message_id": "msg.directory_files.error.invalid_parameters",
            "result": {}
        }

        try:
            directory_files_request_parameters = self.app_module.create_input(DirectoryFilesParameters, DirectoryFilesParametersSchema)
            repository_path = directory_files_request_parameters.repository_path
            actual_path = directory_files_request_parameters.actual_path
            directory_files_parameters = (repository_path, actual_path)

            if self.app_module.tuple_contains_none_values(directory_files_parameters):
                raise TreeModuleException(invalid_directory_files_parameters_response)

        except (AppException, TypeError):
            raise TreeModuleException(invalid_directory_files_parameters_response)

        return directory_files_parameters


    def get_directory_files_response_json(self, directory_files_response: Dict[str, Union[str, Dict[str, Union[str, int, List[FileSystemElement]]]]]) -> str:
        directory_files_result = directory_files_response.get("result")

        if not directory_files_result:
            directory_files_result_data = None
        else:
            directory_files_result_data = DirectoryFilesResultData(directory_files_result.get("repository_path"), directory_files_result.get("actual_path"), directory_files_result.get("number_of_results"), directory_files_result.get("directory_files_result"))

        return self.app_module.create_output(TreeModuleResponse, DirectoryTreeResultSchema, directory_files_result_data, directory_files_response.get("status"), msg=directory_files_response.get("message_id"))


    def get_repositories_response_json(self, repositories_response: Dict[str, Union[str, Dict[str, Union[int, List[FileSystemElement]]]]]) -> str:
        repositories_result = repositories_response.get("result")

        if not repositories_result:
            repositories_result_data = None
        else:
            repositories_result_data = RepositoriesResultData(repositories_result.get("number_of_repositories"), repositories_result.get("repositories"))

        return self.app_module.create_output(TreeModuleResponse, RepositoriesResultSchema, repositories_result_data, repositories_response.get("status"), msg=repositories_response.get("message_id"))


@authenticate()
class SearchModuleView(ViewModule):
    excluded_methods = ["get_search_parameters", "get_search_response_json"]


    #search
    @log_function(logger, print_result=False)
    def post(self) -> str:

        try:
            search_parameters = self.get_search_parameters()

            if not self.app_module.is_previous_search(search_parameters):
                self.app_module.search_files(search_parameters)
            else:
                self.app_module.refresh_times_searched(search_parameters)

            search_response = self.app_module.get_search_response(search_parameters)

        except TreeModuleException as search_error:
            logger.exception("Error while searching in file system.")
            search_response = search_error.args[0]

        except:
            logger.exception("Unexpected error while searching in file system.")
            search_response = {
                "status": "CODE_SEARCH_SERVER_ERROR",
                "message_id": "msg.search.error.server",
                "result": {}
            }

        return self.get_search_response_json(search_response)


    def get_search_parameters(self) -> Tuple[str]:

        invalid_search_parameters_response = {
            "status": "CODE_INVALID_SEARCH_PARAMETERS_ERROR",
            "message_id": "msg.search.error.invalid_parameters",
            "result": {}
        }

        try:
            search_request_parameters = self.app_module.create_input(SearchParameters, SearchParametersSchema)
            from_path = search_request_parameters.from_path
            text_to_search = search_request_parameters.text_to_search
            search_parameters = (from_path, text_to_search)

            if self.app_module.tuple_contains_none_values(search_parameters):
                raise TreeModuleException(invalid_search_parameters_response)

        except (AppException, TypeError):
            raise TreeModuleException(invalid_search_parameters_response)

        return search_parameters


    def get_search_response_json(self, search_response: Dict[str, Union[str, Dict[str, Union[str, bool, int, List[FileSystemElement]]]]]) -> str:
        search_result = search_response.get("result")

        if not search_result:
            search_result_data = None
        else:
            search_result_data = SearchResultData(search_result.get("from_path"), search_result.get("text_to_search"), search_result.get("is_search_finished"), search_result.get("number_of_results"), search_result.get("search_result"))

        return self.app_module.create_output(TreeModuleResponse, SearchResultSchema, search_result_data, search_response.get("status"), msg=search_response.get("message_id"))
