from enum import Enum


class CacheMode(Enum):
    ON_DEMAND = 1
    FROM_CACHE = 2


class SearchMode(Enum):
    OS_WALK = 1
    OS_SCANDIR = 2


class OrderSort(Enum):
    ASC = 1
    DESC = 2


class OrderBy(Enum):
    FULL_PATH = 1
    PATH = 2
    BASENAME = 3
    SIZE = 4
    DIRECTORY = 5
