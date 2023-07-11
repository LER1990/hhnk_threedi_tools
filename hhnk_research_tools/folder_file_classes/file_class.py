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
        self.path = Path(base)


    @property
    def base(self):
        return self.path.as_posix()
    @property
    def name(self):
        return self.path.name
    


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


    def __repr__(self):
        repr_str = \
f"""{self.path.name} @ {self.path}
exists: {self.exists()}
type: {type(self)}
functions: {get_functions(self)}
variables: {get_variables(self)}
"""
        return repr_str