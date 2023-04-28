from pathlib import Path
import inspect


class File:
    def __init__(self, file_path):
        self.file_path = file_path
        self.pl = Path(file_path)

    @property
    def exists(self):
        if self.file_path == "":
            return False
        else:
            return self.pl.exists()

    @property
    def pl_if_exists(self):
        """return filepath if the file exists otherwise return None"""
        if self.exists:
            return self.pl
        else:
            return None

    @property
    def path_if_exists(self):
        """return filepath if the file exists otherwise return None"""
        if self.exists:
            return str(self.pl)
        else:
            return None

    @property
    def name(self):
        return self.pl.stem

    @property
    def path(self):
        return self.file_path

    def unlink_if_exists(self):
        """Remove file if it exists"""
        if self.exists:
            self.pl.unlink(missing_ok=False)

    def __str__(self):
        return self.file_path

    def __repr__(self):
        if self.exists:
            exists = "exists"
        else:
            exists = "doesn't exist"
        funcs = '.'+' .'.join([i for i in dir(self) if not i.startswith('__') and hasattr(inspect.getattr_static(self,i)
        , '__call__')])
        variables = '.'+' .'.join([i for i in dir(self) if not i.startswith('__') and not hasattr(inspect.getattr_static(self,i)
        , '__call__')])
        repr_str = f"""functions: {funcs}
variables: {variables}"""
        return f"""{self.name} @ {self.file_path} ({exists})
{repr_str}"""