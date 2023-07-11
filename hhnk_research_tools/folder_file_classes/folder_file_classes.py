from pathlib import Path
import os
import inspect
import glob
import fiona
import geopandas as gpd
import hhnk_research_tools as hrt
from hhnk_research_tools.folder_file_classes.file_class import File, get_functions, get_variables
from hhnk_research_tools.folder_file_classes.sqlite_class import Sqlite
import types


#TODO refactor en alle classes los behandelen.


class Folder():
    """Base folder class for creating, deleting and see if folder exists"""

    def __init__(self, base, create=False):
        self.path = Path(base)

        self.files = {}
        self.olayers = {}
        self.space = "\t\t\t\t"
        self.isfolder = True
        if create:
            self.create(parents=False)


    @property
    def base(self):
        return self.path.as_posix()
    @property
    def name(self):
        return self.path.name

    @property
    def structure(self):
        return ""

    #TODO oude content gaf alleen namen terug, nu volledig Path naar file
    @property
    def content(self):
        return [i for i in self.path.glob("*")]
        #     if self.exists:
        #     return os.listdir(self.base)
        # else:
        #     return []


    #TODO name uitfaseren. dit is stem. 
    # @property
    # def name(self):
    #     return self.stem

    #TODO uitfaseren, dit is .path.name
    # @property
    # def folder(self):
    #     return self.path.name
        # return os.path.basename(self.base)

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

    #TODO uitfaseren, is dit nodig?
    @property
    def show(self):
        print(self.__repr__())


    def create(self, parents=False, verbose=False):
        """Create folder, if parents==False path wont be
        created if parent doesnt exist."""
        if not parents:
            if not self.path.parent.exists():
                if verbose:
                    print(f"{self.path} not created, parent does not exist.")
                return
        self.path.mkdir(parents=parents, exist_ok=True)


    def find_ext(self, ext):
        """finds files with a certain extension"""
        # return glob.glob(self.base + f"/*.{ext}")
        return self.path.glob(f"*.{ext}")


    #TODO uitzoeken of name met '/' start. Dat mag niet.
    #TODO return Folder or File object
    def full_path(self, name):
        """returns the full path of a file or a folder when only a name is known"""
        p = self.path / name
        if p.suffix == "":
            return Folder()
        else:
            return File(p)
        # return self.path / name

    #TODO ftype is niet meer. uit de suffix halen.
    def add_file(self, objectname, filename):
        """"""
        # if not os.path.exists(self.full_path(filename)) or
        if filename in [None, ""]:
            filepath = Path("")
        else:
            filepath = self.full_path(filename)

        if filepath.suffix in [".gdb", ".gpkg", ".shp"]:
            new_file = FileGDB(filepath)
        elif filepath.suffix in [".tif", ".tiff", ".vrt"]:
            new_file = hrt.Raster(filepath)
        elif filepath.suffix in [".sqlite"]:
            new_file = Sqlite(filepath)
        else:
            new_file = File(filepath)

        self.files[objectname] = new_file
        setattr(self, objectname, new_file)


    def unlink_contents(self, names=[], rmfiles=True, rmdirs=False):
        """unlink all content when names is an empty list. Otherwise just remove the names."""
        if not names:
            names=self.content
        for name in names:
            pathname = self.path / name
            try:
                if pathname.exists():
                    #FIXME rmdir is only allowed for empty dirs
                    #can use shutil.rmtree, but this can be dangerous, 
                    #not sure if we should support that here.
                    if pathname.is_dir():
                        if rmdirs:
                            pathname.rmdir()
                    else:
                        if rmfiles:
                            pathname.unlink()
            except Exception as e:
                print(pathname, e)


    def __str__(self):
        return str(self.path)


    def __repr__(self):
        repr_str = \
 f"""{self.path.name} @ {self.path}
Exists: {self.exists()}
type: {type(self)}
    Folders:\t{self.structure}
    Files:\t{list(self.files.keys())}
functions: {get_functions(self)}
variables: {get_variables(self)}"""
        return repr_str




class FileGDB(File):
    def __init__(self, base):
        super().__init__(base)

        self.layerlist=[]
        self.layers=types.SimpleNamespace() #empty class


    def load(self, layer=None):
        if layer == None:
            avail_layers = self.available_layers()
            if len(avail_layers) == 1:
                layer= avail_layers[0]
            else:
                layer = input(f"Select layer [{avail_layers}]:")
        return gpd.read_file(self.base, layer=layer)


    def add_layer(self, name:str):
        """Predefine layers so we can write output to that layer."""
        if name not in self.layerlist:
            new_layer = FileGDBLayer(name, parent=self)
            self.layerlist.append(name)
            setattr(self.layers, name, new_layer)


    def add_layers(self, names:list):
        """Add multiple layers"""
        for name in names:
            self.add_layer(name)


    def available_layers(self):
        """Return available layers in file gdb"""
        return fiona.listlayers(self.base)


    def __repr__(self):
        repr_str = \
f"""{self.path.name} @ {self.path}
exists: {self.exists()}
type: {type(self)}
functions: {get_functions(self)}
variables: {get_variables(self)}
layers (access through .layers): {self.layerlist}"""
        return repr_str



class FileGDBLayer():
    def __init__(self, name:str,  parent:FileGDB):
        self.name=name
        self.parent=parent

    def load(self):
        return gpd.read_file(self.parent.base, layer=self.name)