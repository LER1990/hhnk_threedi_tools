from pathlib import Path
import os
import inspect
import glob
import fiona
import geopandas as gpd
import hhnk_research_tools as hrt
from hhnk_research_tools.folder_file_classes.file_class import File

# Third-party imports
from threedigrid.admin.gridadmin import GridH5Admin
from threedigrid.admin.gridresultadmin import GridH5ResultAdmin

#TODO refactor en alle classes los behandelen.


class Folder:
    """Base folder class for creating, deleting and see if folder exists"""

    def __init__(self, base, create=False):
        self.base = base
        self.pl = Path(base)  # pathlib path

        self.files = {}
        self.olayers = {}
        self.space = "\t\t\t\t"
        self.isfolder = True
        if create:
            self.create(parents=False)

    @property
    def structure(self):
        return ""

    @property
    def content(self):
        return os.listdir(self.base)

    @property
    def path(self):
        return self.base

    @property
    def name(self):
        return self.pl.stem

    @property
    def folder(self):
        return os.path.basename(self.base)

    @property
    def exists(self):
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
    def show(self):
        print(self.__repr__())

    def create(self, parents=False):
        """Create folder, if parents==False path wont be
        created if parent doesnt exist."""
        if not parents:
            if not self.pl.parent.exists():
                print(f"{self.path} not created, parent doesnt exist.")
                return
        self.pl.mkdir(parents=parents, exist_ok=True)

    def find_ext(self, ext):
        """finds files with a certain extension"""
        return glob.glob(self.base + f"/*.{ext}")

    def full_path(self, name):
        """returns the full path of a file or a folder when only a name is known"""
        if "/" in name:
            return str(self.pl) + name
        else:
            return str(self.pl / name)

    def add_file(self, objectname, filename, ftype="file"):
        """ftype options = ['file', 'filegdb', 'raster', 'sqlite'] """
        # if not os.path.exists(self.full_path(filename)) or
        if filename in [None, ""]:
            filepath = ""
        else:
            filepath = self.full_path(filename)

        if ftype == "file":
            new_file = File(filepath)
        elif ftype == "filegdb":
            new_file = FileGDB(filepath)
        elif ftype == "raster":
            new_file = hrt.Raster(filepath)
        elif ftype == "sqlite":
            new_file = Sqlite(filepath)

        self.files[objectname] = new_file
        setattr(self, objectname, new_file)

    def add_layer(self, objectname, layer):
        self.olayers[objectname] = layer
        setattr(self, objectname, layer)

    def __str__(self):
        return self.base

    def __repr__(self):
        funcs = '.'+' .'.join([i for i in dir(self) if not i.startswith('__') and hasattr(inspect.getattr_static(self,i), '__call__')]) #getattr resulted in RecursionError. https://stackoverflow.com/questions/1091259/how-to-test-if-a-class-attribute-is-an-instance-method
        variables = '.'+' .'.join([i for i in dir(self) if not i.startswith('__') and not hasattr(inspect.getattr_static(self,i)
                , '__call__')])
        repr_str = f"""functions: {funcs}
variables: {variables}"""
        return f"""{self.name} @ {self.path}
Exists: {self.exists}
        Folders:\t{self.structure}
        Files:\t{list(self.files.keys())}
        Layers:\t{list(self.olayers.keys())}
{repr_str}
                """
    




class FileGDB(File):
    def __init__(self, file_path):
        super().__init__(file_path)

    def load(self, layer=None):
        if layer == None:
            layer = input("Select layer:")
        return gpd.read_file(self.file_path, layer=layer)

    def layers(self):
        """Return available layers in file gdb"""
        return fiona.listlayers(self.file_path)

#TODO deprecated, gis.raster ipv deze gebruiken.
# class Raster(File):
#     def __init__(self, raster_path):
#         super().__init__(raster_path)

#     def load(self, return_array=True):
#         if self.exists:
#             self.array, self.nodata, self.metadata = hrt.load_gdal_raster(
#                 raster_source=self.file_path, return_array=return_array
#             )
#             return self.array, self.nodata, self.metadata
#         else:
#             print("Doesn't exist")


class Sqlite(File):
    def __init__(self, file_path):
        super().__init__(file_path)

    def connect(self):
        if os.path.exists(self.path):
            return hrt.create_sqlite_connection(self.path)
        else:
            return None


class ThreediResult(Folder):
    """Use .grid to get GridH5ResultAdmin and .admin to get GridH5Admin"""

    def __init__(self, base):
        super().__init__(base)

        # Files
        self.add_file("grid_path", "results_3di.nc")
        self.add_file("admin_path", "gridadmin.h5")

    @property
    def grid(self):
        return GridH5ResultAdmin(self.admin_path.file_path, self.grid_path.file_path)

    @property
    def admin(self):
        return GridH5Admin(self.admin_path.file_path)