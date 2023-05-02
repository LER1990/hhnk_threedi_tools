from pathlib import Path
from hhnk_research_tools.folder_file_classes.folder_file_classes import FileGDB

def ensure_file_path(filepath):
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
    if gdb.exists:
        if gpkg.exists and not overwrite:
            if verbose:
                print(f"Already exists: {gpkg.path}")
            return 
        else:
            if overwrite:
                gpkg.unlink_if_exists()
            if verbose:
                print(f"Write gpkg to {gpkg.path}")
            for layer in gdb.layers():
                if verbose:
                    print(f"    {layer}")
                gdf = gpd.read_file(gdb.path, layer=layer)

                gdf.to_file(gpkg.path, layer=layer, driver="GPKG")