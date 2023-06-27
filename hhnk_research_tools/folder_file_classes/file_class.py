from pathlib import Path
import inspect


class File(type(Path()), Path):
    def __init__(self, base):
        # super().__init__(base)
        self.path=base


    def exists(self):
        """monkeypatch exists, dont return true on empty path."""
        if self.path == "":
            return False
        else:
            return super().exists()



    # @property
    # def path_if_exists(self) -> str:
    #     """return filepath if the file exists otherwise return None"""
    #     if self.exists():
    #         return str(self)
    #     else:
    #         return None

    # @property
    # def name(self):
    #     return self.pl.stem



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