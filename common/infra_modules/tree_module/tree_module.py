import os
import copy
import fnmatch
import threading

from typing import Tuple, List, Dict, Union

from common import config
from common.infra_modules.infra_module import InfraModule
from common.infra_modules.tree_module import MODULE_NAME
from common.infra_modules.tree_module.constants_tree_module import CacheMode, SearchMode
from common.infra_modules.tree_module.model_tree_module import TreeModuleException, FileSystemElement
from common.infra_modules.tree_module.views_tree_module import SearchModuleView
from common.infra_modules.tree_module.views_tree_module import DirectoryTreeModuleView


logger = config.get_log(MODULE_NAME)


class TreeModule(InfraModule):

    search_results = dict()
    cache_repositories = None


    def initialize(self):
        self.load_config_parameters()
        self.load_repositories()

        self.register_url(SearchModuleView, '/search')
        self.register_url(DirectoryTreeModuleView, '/directory_tree')


    def load_config_parameters(self) -> None:
        self.CACHE_MODE = CacheMode(int(self.module_config.get_value(MODULE_NAME, 'cache_mode')))
        self.SEARCH_MODE = SearchMode(int(self.module_config.get_value(MODULE_NAME, 'search_mode')))
        self.PRELOADED_CACHE_LEVELS = int(self.module_config.get_value(MODULE_NAME, 'preloaded_cache_levels'))


    def load_repositories(self) -> None:
        self.cache_repositories = dict()

        # TODO: obtener raiz de los repositorios desde bbdd (ahora mismo ponemos estos valores inventados)
        self.cache_repositories["/home/jmarin"] = dict()
        self.cache_repositories["/home/jmarin"]["/home/jmarin"] = FileSystemElement("/home/jmarin", "/home/jmarin", True, 0)
        self.cache_repositories["/usr/share"] = dict()
        self.cache_repositories["/usr/share"]["/usr/share"] = FileSystemElement("/usr/share", "/usr/share", True, 0)


    ################################################################################
    ############################## DIRECTORY FILES #################################
    ################################################################################


    def get_file_system_elements_from_cache(self, repository_path: str, file_system_elements_path: List[str]) -> List[FileSystemElement]:
        repository = self.cache_repositories.get(repository_path)

        return [repository[element_path] for element_path in file_system_elements_path]


    def get_new_file_system_element(self, directory_path: str, basename: str) -> FileSystemElement:
        full_element_path = os.path.join(directory_path, basename)

        is_directory = self.is_dir(full_element_path)
        size = 0
        if is_directory:
            try:
                size = os.path.getsize(full_element_path)
            except:
                logger.exception("Error getting file size: {}.".format(full_element_path))

        return FileSystemElement(directory_path, basename, is_directory, size)


    def generate_cache_n_levels_children(self, repository_path: str, actual_path: str, cache_levels_to_load: int) -> None:
        if cache_levels_to_load is not 0:
            file_system_elements_path = []

            cache_element = self.cache_repositories.get(repository_path).get(actual_path)
            directory_path = os.path.join(cache_element.path, cache_element.basename)

            all_files = []
            try:
                all_files = os.listdir(directory_path)
            except OSError:
                logger.exception("Error getting all files from {}".format(directory_path))

            for basename in all_files:
                full_element_path = os.path.join(directory_path, basename)
                file_system_element = self.get_new_file_system_element(directory_path, basename)
                self.cache_repositories[repository_path][full_element_path] = file_system_element
                file_system_elements_path.append(full_element_path)

                if self.is_dir(full_element_path):
                    self.generate_cache_n_levels_children(repository_path, full_element_path, cache_levels_to_load - 1)

            cache_element.add_children(file_system_elements_path)


    def get_directory_file_system_elements_from_cache(self, directory_files_parameters: Tuple[str]) -> List[FileSystemElement]:
        repository_path = directory_files_parameters[0]
        actual_path = directory_files_parameters[1]
        directory_path = os.path.join(repository_path, actual_path)

        cache_element = self.cache_repositories.get(repository_path).get(directory_path)

        if cache_element is None:
            raise TreeModuleException({
                "status": "CODE_INVALID_DIRECTORY_FILES_NODE_ERROR",
                "message_id": "msg.directory_files.error.invalid_cache_node",
                "result": {}
            })
        elif not cache_element.is_directory:
            raise TreeModuleException({
                "status": "CODE_INVALID_DIRECTORY_FILES_PATH_NODE_ERROR",
                "message_id": "msg.directory_files.error.invalid_cache_node",
                "result": {}
            })
        else:
            if cache_element.children is None:
                self.generate_cache_n_levels_children(repository_path, actual_path, self.PRELOADED_CACHE_LEVELS)

        return self.get_file_system_elements_from_cache(repository_path, cache_element.children)


    def get_directory_file_system_elements_on_demand(self, directory_files_parameters: Tuple[str]) -> List[FileSystemElement]:
        file_system_elements = []
        repository_path = directory_files_parameters[0]
        actual_path = directory_files_parameters[1]
        directory_path = os.path.join(repository_path, actual_path)

        all_files = []
        try:
            all_files = os.listdir(directory_path)
        except OSError:
            logger.exception("Error getting all files from {}".format(directory_path))

        for basename in all_files:
            file_system_element = self.get_new_file_system_element(directory_path, basename)
            file_system_elements.append(file_system_element)

        return file_system_elements


    def get_directory_files_response(self, directory_files_parameters: Tuple[str], directory_files: List[FileSystemElement]) -> Dict[str, Union[str, Dict[str, Union[str, int, List[FileSystemElement]]]]]:
        repository_path = directory_files_parameters[0]
        actual_path = directory_files_parameters[1]

        return {
            "status": "CODE_OK",
            "message_id": "msg.directory_files.ok",
            "result": {
                "repository_path": repository_path,
                "actual_path": actual_path,
                "number_of_results": len(directory_files),
                "directory_files_result": directory_files
            }
        }


    def get_directory_file_system_elements(self, directory_files_parameters: Tuple[str]) -> List[FileSystemElement]:
        actual_path = directory_files_parameters[1]
        if not self.is_dir(actual_path):
            raise TreeModuleException({
                "status": "CODE_INVALID_DIRECTORY_FILES_PATH_ERROR",
                "message_id": "msg.directory_files.error.invalid_actual_path",
                "result": {}
            })

        if self.CACHE_MODE is CacheMode.FROM_CACHE:
            directory_file_system_elements = self.get_directory_file_system_elements_from_cache(directory_files_parameters)
        else:  # CACHE_MODE is CacheMode.ON_DEMAND
            directory_file_system_elements = self.get_directory_file_system_elements_on_demand(directory_files_parameters)

        return directory_file_system_elements


    ################################################################################
    ############################ GET REPOSITORIES ##################################
    ################################################################################


    def get_repositories_response(self) -> Dict[str, Union[str, Dict[str, Union[int, List[FileSystemElement]]]]]:
        repositories = self.get_cache_repositories()

        return {
            "status": "CODE_OK",
            "message_id": "msg.repositories.ok",
            "result": {
                "number_of_repositories": len(repositories),
                "repositories": repositories
            }
        }


    def get_cache_repositories(self) -> List[FileSystemElement]:
        repositories = []

        for repository_path, repository in self.cache_repositories.items():
            repositories.append(repository.get(repository_path))

        return repositories


    def refresh_repositories(self) -> None:
        #los que no existan se eliminan, los que sean nuevos se añaden y los que sigan igual no se modifican
        pass


    ################################################################################
    ############################## SEARCH FILES ####################################
    ################################################################################


    def sort_search_results(self, search_results: List[FileSystemElement]) -> List[FileSystemElement]:
        temporal_search_result = copy.deepcopy(search_results)
        return sorted(temporal_search_result, key=FileSystemElement.get_full_path)


    def get_search_response(self, search_parameters: Tuple[str]) -> Dict[str, Union[str, Dict[str, Union[str, bool, int, List[FileSystemElement]]]]]:
        search_result = self.get_search_result(search_parameters)
        sorted_search = self.sort_search_results(search_result.get("items_found"))

        return {
            "status": "CODE_OK",
            "message_id": "msg.search.ok",
            "result": {
                "from_path": search_parameters[0],
                "text_to_search": search_parameters[1],
                "is_search_finished": search_result.get("is_search_finished"),
                "number_of_results": len(sorted_search),
                "search_result": sorted_search
            }
        }


    def refresh_times_searched(self, search_parameters: Tuple[str]) -> None:
        search_result = self.get_search_result(search_parameters)

        if search_result.get("is_search_finished"):
            search_result["times_searched"] += 1


    def text_contains_word(self, text: str, word: str) -> bool:
        return fnmatch.fnmatch(text.lower(), "".join(["*", word.lower(), "*"]))


    def set_search_finished(self, search_parameters: Tuple[str]) -> None:
        self.search_results[search_parameters].update({"is_search_finished": True})


    def save_file_system_searched_element(self, file_system_searched_element: FileSystemElement, search_parameters: Tuple[str]) -> None:
        self.search_results[search_parameters].get("items_found").append(file_system_searched_element)


    def search_files_in_scandir_mode_results(self, actual_base_path: str, search_parameters: Tuple[str]) -> None:
        if self.is_dir(actual_base_path):
            text_to_search = search_parameters[1]

            all_files = []
            try:
                all_files = os.scandir(actual_base_path)
            except OSError:
                logger.exception("Permission denied accessing file {}".format(actual_base_path))

            for entry in all_files:
                if entry.is_dir(follow_symlinks=False):
                    if self.text_contains_word(entry.name, text_to_search):
                        file_system_searched_element = FileSystemElement(actual_base_path, entry.name, True, 0)
                        self.save_file_system_searched_element(file_system_searched_element, search_parameters)

                    full_element_path = os.path.join(actual_base_path, entry.name)
                    self.search_files_in_scandir_mode_results(full_element_path, search_parameters)
                else:
                    if self.text_contains_word(entry.name, text_to_search):
                        size = 0
                        try:
                            size = entry.stat(follow_symlinks=False).st_size
                        except:
                            logger.exception("Error getting file size: {}.".format(entry.path))

                        file_system_searched_element = FileSystemElement(actual_base_path, entry.name, False, size)
                        self.save_file_system_searched_element(file_system_searched_element, search_parameters)


    def search_files_in_scandir_mode(self, *search_parameters) -> None:
        self.search_files_in_scandir_mode_results(search_parameters[0], search_parameters)
        self.set_search_finished(search_parameters)


    def search_files_in_walk_mode(self, *search_parameters) -> None:
        from_path = search_parameters[0]
        text_to_search = search_parameters[1]

        try:
            all_files = os.walk(from_path)
        except OSError:
            logger.exception("Error getting all files from {}".format(from_path))

        for directory_paths, directory_names, files in all_files:
            for directory_name in directory_names:
                if self.text_contains_word(directory_name, text_to_search):
                    file_system_searched_element = FileSystemElement(directory_paths, directory_name, True, 0)
                    self.save_file_system_searched_element(file_system_searched_element, search_parameters)

            for file_name in files:
                if self.text_contains_word(file_name, text_to_search):
                    full_element_path = os.path.join(directory_paths, file_name)
                    size = 0
                    try:
                        size = os.path.getsize(full_element_path)
                    except:
                        logger.exception("Error getting file size: {}.".format(full_element_path))

                    file_system_searched_element = FileSystemElement(directory_paths, file_name, False, size)
                    self.save_file_system_searched_element(file_system_searched_element, search_parameters)

        self.set_search_finished(search_parameters)


    def get_empty_search_result(self) -> Dict[str, Union[List[FileSystemElement], bool, int]]:
        return {
            "items_found": [],
            "is_search_finished": False,
            "times_searched": 0
        }


    def is_dir(self, path: str) -> bool:
        return os.path.isdir(path)


    def search_files(self, search_parameters: Tuple[str]) -> None:
        from_path = search_parameters[0]
        if not self.is_dir(from_path):
            raise TreeModuleException({
                "status": "CODE_INVALID_SEARCH_PATH_ERROR",
                "message_id": "msg.search.error.invalid_search_path",
                "result": {}
            })

        self.search_results[search_parameters] = self.get_empty_search_result()

        if self.SEARCH_MODE is SearchMode.OS_WALK:
            search_files_method = self.search_files_in_walk_mode
        else:  # SEARCH_MODE is SearchMode.OS_SCANDIR
            search_files_method = self.search_files_in_scandir_mode

        t = threading.Thread(target=search_files_method, args=search_parameters)
        t.start()


    def get_search_result(self, search_parameters: Tuple[str]) -> Dict[str, Union[List[FileSystemElement], bool, int]]:
        return self.search_results.get(search_parameters)


    def is_previous_search(self, search_parameters: Tuple[str]) -> bool:
        search_result = self.get_search_result(search_parameters)

        return search_result is not None


    def tuple_contains_none_values(self, n_tuple: Tuple[str]) -> bool:
        return any(map(lambda element: element is None, n_tuple))
