from pathlib import Path
import inspect
import json


def get_functions(cls):
    funcs = '.'+' .'.join([i for i in dir(cls) if not i.startswith('__') 
                            and hasattr(inspect.getattr_static(cls,i)
                            , '__call__')])
    return funcs
def get_variables(cls):
    variables = '.'+' .'.join([i for i in dir(cls) if not i.startswith('__') 
                            and not hasattr(inspect.getattr_static(cls,i)
                            , '__call__')])
    return variables


# class File(type(Path()), Path):
class File():
    def __init__(self, base):
        self.path = Path(str(base))


    @property
    def base(self): #full path to file
        return self.path.as_posix()
    @property
    def name(self): #name with suffix
        return self.path.name
    @property
    def stem(self): #stem (without suffix)
        return self.path.stem
    @property
    def suffix(self):
        return self.path.suffix

    def read_json(self):
        if self.path.suffix==".json":
            return json.loads(self.path.read_text())
        else:
            raise Exception(f"{self.name} is not a json.")


    def exists(self):
        """dont return true on empty path."""
        if self.base == ".":
            return False
        else:
            return self.path.exists()
        
    @property
    def path_if_exists(self):
        """return filepath if the file exists otherwise return None"""
        if self.exists():
            return str(self.path)
        else:
            return None


    def __repr__(self):
        repr_str = \
f"""{self.path.name} @ {self.path}
exists: {self.exists()}
type: {type(self)}
functions: {get_functions(self)}
variables: {get_variables(self)}
"""
        return repr_str