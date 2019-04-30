# Tools for parsing

def get_app_version():
    with open('version.txt') as f:
        return ''.join(f.readlines())

def get_args_from_shell(t: tuple) -> tuple:
    """Recover arguments in the following format: ((a, b, c),)"""
    return t[0]

def striplist(l):
    """Strip all list elements"""
    return ([x.strip() for x in l])