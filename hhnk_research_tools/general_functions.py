from pathlib import Path
from hhnk_research_tools.folder_file_classes.folder_file_classes import FileGDB
import geopandas as gpd
import sys
import importlib
import importlib.resources as pkg_resources  # Load resource from package
from uuid import uuid4


def ensure_file_path(filepath):
    #TODO add to file class? still needed?
    """
    Functions makes sure all folders in a given file path exist. Creates them if they don't.
    """
    try:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise e from None


def convert_gdb_to_gpkg(gdb:FileGDB, gpkg:FileGDB, overwrite=False, verbose=True):
    """Convert input filegdb to geopackage"""

    if gdb.exists():
        if check_create_new_file(output_file=gpkg, overwrite=overwrite):
            if verbose:
                print(f"Write gpkg to {gpkg}")
            for layer in gdb.available_layers():
                if verbose:
                    print(f"    {layer}")
                gdf = gpd.read_file(str(gdb), layer=layer)

                gdf.to_file(str(gpkg), layer=layer, driver="GPKG")


def check_create_new_file(output_file:str, overwrite:bool=False, input_files:list=[], allow_emptypath=False) -> bool:
    """
    Check if we should continue to create a new file. 

    output_file:
    overwrite: When overwriting is True the output_file will be removed.  
    input_files: if input files are provided the edit time of the input will be 
                 compared to the output. If edit time is after the output, it will
                 recreate the output.
    """
    create=False
    output_file = Path(str(output_file))

    #Als geen suffix (dus geen file), dan error
    if not allow_emptypath: #
        if not output_file.suffix:
            raise TypeError(f"{output_file} is not a file.")
    
    # Rasterize regions
    if not output_file.exists():
        create = True
    else:
        if overwrite:
            output_file.unlink()
            create=True

        if input_files:
            # Check edit times. To see if raster needs to be updated.
            output_mtime = output_file.stat().st_mtime

            for input_file in input_files:
                input_file = Path(input_file)
                if input_file.exists():
                    input_mtime = input_file.stat().st_mtime
                    
                    if input_mtime > output_mtime:
                        output_file.unlink()
                        create = True
                        break
    return create


def load_source(name: str, path: str):
    """
    Load python file as module. 
    
    Replacement for deprecated imp.load_source()
    Inspiration from https://github.com/cuthbertLab/music21/blob/master/music21/test/commonTest.py"""
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise FileNotFoundError(f'No such file or directory: {path!r}')
    if name in sys.modules:
        module = sys.modules[name]
    else:
        module = importlib.util.module_from_spec(spec)
        if module is None:
            raise FileNotFoundError(f'No such file or directory: {path!r}')
        sys.modules[name] = module
    spec.loader.exec_module(module)

    return module


def get_uuid(chars=8):
    """max chars = 36"""
    return str(uuid4())[:chars]


def get_pkg_resource_path(package_resource, name) -> Path:
    """return path to resource in a python package, so it can be loaded"""
    with pkg_resources.path(package_resource, name) as p:
        return p
    

class dict_to_class(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__