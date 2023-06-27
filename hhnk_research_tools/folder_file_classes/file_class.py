from pathlib import Path
import inspect


# class File(type(Path()), Path):
class File():
    def __init__(self, base):
        self.path = Path(base)


    @property
    def str(self):
        return str(self.path)


    def exists(self):
        """dont return true on empty path."""
        if self.path == ".":
            return False
        else:
            return self.path.exists()

    # @property
    # def path_if_exists(self) -> str:
    #     """return filepath if the file exists otherwise return None"""
    #     if self.exists():
    #         return str(self)
    #     else:
    #         return None

    # @property
    # def name(self):
    #     return self.stem



    def __repr__(self):
        # funcs = '.'+' .'.join([i for i in dir(self) if not i.startswith('__') and hasattr(inspect.getattr_static(self,i)
        # , '__call__')])
        # variables = '.'+' .'.join([i for i in dir(self) if not i.startswith('__') and not hasattr(inspect.getattr_static(self,i)
        # , '__call__')])
        repr_str = \
f"""{self.name} @ {self.path}
exists: {self.exists()}
type: {type(self)}
"""
# functions: {funcs}
# variables: {variables}
        return repr_str