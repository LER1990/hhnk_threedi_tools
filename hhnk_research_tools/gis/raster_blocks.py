from dataclasses import dataclass
import numpy as np


@dataclass
class RasterBlocks:
    window: list
    raster_paths_dict: dict
    nodata_keys: list = None
    mask_keys: list = None

    """
    General function to load blocks of selected files with a given window.
    Also loads the masks and can check if a blcok is fully nodata, in which
    case it stopts loading.
    Input files should have the same extent, so make a vrt of them first if 
    they are not.

    for speed this class does not check if all inputs exist. This should still
    be these case.

    Input parameters
    window (list): [xmin, ymin, xmax, ymax]; same as row['windows_readarray']
    raster_paths_dict (dict): {key:hrt.Raster}, path items should be of type
        hrt.Raster.
    nodata_keys (list): the keys in raster_paths to check for all nodata values
        wont load other rasters if all values are nodata.
    mask_keys (list): list of keys to create a nodata mask for
    """
    
    def __post_init__(self):
        self.cont = True
        self.blocks = {}
        self.masks = {}

        try:
            for key in self.nodata_keys:
                self.blocks[key] = self.read_array_window(key)
                self.masks[key] = self.blocks[key]==self.raster_paths_dict[key].nodata

                if np.all(self.masks[key]):
                    """if all values in masks are nodata then we can break loading"""
                    self.cont = False
                    break
            
            #Load other rasters
            if self.cont:
                for key in self.raster_paths_dict:
                    if key not in self.blocks.keys():
                        self.blocks[key] = self.read_array_window(key)
                    if (key in self.mask_keys) and (key not in self.masks.keys()):
                        self.masks[key] = self.blocks[key]==self.raster_paths_dict[key].nodata
        except Exception as e:
            raise Exception("Something went wrong. Do all inputs exist?", e)

    def read_array_window(self, key):
        """read window from hrt.Raster"""
        return self.raster_paths_dict[key]._read_array(window=self.window)


    @property
    def masks_all(self):
        """Combine nodata masks"""
        return np.any([self.masks[i] for i in self.masks],0)

