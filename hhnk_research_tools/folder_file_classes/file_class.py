from pathlib import Path
import inspect


# class File(type(Path()), Path):
class File():
    def __init__(self, base):
        self.path = Path(base)


    @property
    def base(self):
        # return str(self.path)
        return self.path.as_posix()


    def exists(self):
        """dont return true on empty path."""
        if self.base == ".":
            return False
        else:
            return self.path.exists()


    def __repr__(self):
        funcs = '.'+' .'.join([i for i in dir(self) if not i.startswith('__') and hasattr(inspect.getattr_static(self,i)
        , '__call__')])
        variables = '.'+' .'.join([i for i in dir(self) if not i.startswith('__') and not hasattr(inspect.getattr_static(self,i)
        , '__call__')])
        repr_str = \
f"""{self.path.name} @ {self.path}
exists: {self.exists()}
type: {type(self)}
functions: {funcs}
variables: {variables}
"""
        return repr_str