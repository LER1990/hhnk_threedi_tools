import datetime
import tempfile
import types
from dataclasses import dataclass

import numpy as np

import hhnk_research_tools as hrt


@dataclass
class RasterBlocks:
    """
    General function to load blocks of selected files with a given window.
    Also loads the masks and can check if a blcok is fully nodata, in which
    case it stopts loading.
    Input files should have the same extent, so make a vrt of them first if
    they are not. This is handled in RasterCalculator.

    For speed this class does not check if all inputs exist. This should still
    be the case.

    Parameters
    ----------
    window (list): [xmin, ymin, xsize, ysize]; same as row['windows_readarray']
    raster_paths_dict (dict): {key:hrt.Raster}, path items should be of type
        hrt.Raster.
    nodata_keys (list): the keys in raster_paths to check for all nodata values
        wont load other rasters if all values are nodata.
    mask_keys (list): list of keys to create a nodata mask for
    """

    window: list
    raster_paths_dict: dict[str : hrt.Raster]
    nodata_keys: list[str] = None
    mask_keys: list[str] = None

    def __post_init__(self):
        self.cont = True
        self.blocks = {}
        self.masks = {}

        try:
            for key in self.nodata_keys:
                self.blocks[key] = self.read_array_window(key)
                self.masks[key] = self.blocks[key] == self.raster_paths_dict[key].nodata

                if np.all(self.masks[key]):
                    # if all values in masks are nodata then we can break loading
                    self.cont = False
                    break

            # Load other rasters
            if self.cont:
                for key in self.raster_paths_dict:
                    if key not in self.blocks.keys():
                        self.blocks[key] = self.read_array_window(key)
                    if (key in self.mask_keys) and (key not in self.masks.keys()):
                        self.masks[key] = self.blocks[key] == self.raster_paths_dict[key].nodata
        except Exception as e:
            raise Exception("Something went wrong. Do all inputs exist?") from e

    def read_array_window(self, key):
        """Read window from hrt.Raster"""
        return self.raster_paths_dict[key]._read_array(window=self.window)

    @property
    def masks_all(self):
        """Combine nodata masks"""
        return np.any([self.masks[i] for i in self.masks], 0)


class RasterCalculatorV2:
    """
    Base setup for raster calculations. The input rasters defined in raster_paths_dict
    are looped over per block. Note that all input rasters should have the same extent.
    This can be achieved with .vrt if the original rasters do not have the same extent.
    For each block the custom_run_window_function will be run. This always takes a
    block as input and also returns the block. For example:

    def run_dem_window(block):
        block_out = block.blocks['dem']

        #Watervlakken ophogen naar +10mNAP
        block_out[block.blocks['watervlakken']==1] = 10

        block_out[block.masks_all] = nodata
        return block_out

    Parameters
    ----------
    raster_out (hrt.Raster): output raster location
    raster_paths_dict (dict[str : hrt.Raster]): these rasters will have blocks loaded.
    nodata_keys (list [str]): keys to check if all values are nodata, if yes then skip
    mask_keys (list[str]): keys to add to nodatamask
    metadata_key (str): key in raster_paths_dict that will be used to
        create blocks and metadata
    custom_run_window_function: function that does calculation with blocks.
        function takes block (hrt.RasterBlocks) and kwargs as input and must return block
    output_nodata (int): nodata of output raster
    min_block_size (int): min block size for generator blocks_df, higher is faster but
        uses more RAM.
    verbose (bool): print progress
    tempdir (hrt.Folder): pass if you want temp vrt's to be created a specific tempdir
    """

    def __init__(
        self,
        raster_out: hrt.Raster,
        raster_paths_dict: dict[str : hrt.Raster],
        nodata_keys: list[str],
        mask_keys: list[str],
        metadata_key: str,
        custom_run_window_function: types.MethodType,
        output_nodata: int = -9999,
        min_block_size: int = 4096,
        verbose: bool = False,
        tempdir: hrt.Folder = None,
    ):
        self.raster_out = raster_out
        self.raster_paths_dict = raster_paths_dict
        self.nodata_keys = nodata_keys
        self.mask_keys = mask_keys
        self.metadata_key = metadata_key
        self.custom_run_window_function = custom_run_window_function
        self.output_nodata = output_nodata
        self.min_block_size = min_block_size
        self.verbose = verbose

        # Local vars
        if tempdir is None:
            self.tempdir = raster_out.parent.full_path(f"temp_{hrt.current_time(date=True)}")
        else:
            self.tempdir = tempdir

        # If bounds of input rasters are not the same a temp vrt is created
        # The path to these files are stored here.
        self.raster_paths_same_bounds = self.raster_paths_dict.copy()

        # Filled when running
        self.blocks_df = None

    @property
    def metadata_raster(self) -> hrt.Raster:
        """Raster of which metadata is used to create output."""
        return self.raster_paths_dict[self.metadata_key]

    def verify(self, overwrite: bool) -> bool:
        """Verify if all inputs can be accessed and if they have the same bounds."""
        cont = True

        # Check if all input rasters have the same bounds
        bounds = {}
        for key, r in self.raster_paths_dict.items():
            if cont:
                if not isinstance(r, hrt.Raster):
                    raise TypeError(f"{key}:{r} in raster_paths_dict is not of type hrt.Raster")
                if not r.exists():
                    print(f"Missing input raster key: {key} @ {r}")
                    cont = False
                    continue
                bounds[key] = r.metadata.bounds

        # Check resolution
        if cont:
            vrt_keys = []
            for key, r in self.raster_paths_dict.items():
                if r.metadata.pixelarea > self.metadata_raster.metadata.pixelarea:
                    print(f"Resolution of {key} is not the same as metadataraster {self.metadata_key}, creating vrt")
                    self.create_vrt(key)
                    vrt_keys.append(key)
                if r.metadata.pixelarea < self.metadata_raster.metadata.pixelarea:
                    cont = False
                    raise NotImplementedError(
                        f"Resolution of {key} is smaller than metadataraster {self.metadata_key}, \
this is not implemented or tested if it works."
                    )

        # Check bounds, if they are not the same as the metadata_raster, create a vrt
        if cont:
            for key, r in self.raster_paths_dict.items():
                if r.metadata.bounds != self.metadata_raster.metadata.bounds:
                    # Create vrt if it was not already created in resolution check
                    if key not in vrt_keys:
                        self.create_vrt(key)

                    if self.verbose:
                        print(f"{key} does not have same extent as {self.metadata_key}, creating vrt")

        # Check if we should create new file
        if cont:
            cont = hrt.check_create_new_file(output_file=self.raster_out, overwrite=overwrite)
            if cont is False:
                if self.verbose:
                    print(f"output raster already exists: {self.raster_out.name} @ {self.raster_out.path}")

        return cont

    def create(self) -> bool:
        """Create empty output raster with metadata of metadata_raster"""
        if self.verbose:
            print(f"Creating output raster: {self.raster_out.name} @ {self.raster_out.path}")

        self.raster_out.create(metadata=self.metadata_raster.metadata, nodata=self.output_nodata)

    def create_vrt(self, raster_key: str):
        """Create vrt of input rasters with the extent of the metadata raster

        Parameters
        ----------
        raster_key (str) : key in self.raster_paths_dict to create vrt from.
        """
        input_raster = self.raster_paths_dict[raster_key]

        # Create temp output folder.
        self.tempdir.create()
        output_raster = self.tempdir.full_path(f"{input_raster.stem}.vrt")
        print(f"Creating temporary vrt; {output_raster.name} @ {output_raster}")

        output_raster.build_vrt(
            overwrite=True,
            bounds=self.metadata_raster.metadata.bbox_gdal,
            input_files=input_raster,
            resolution=self.metadata_raster.metadata.pixel_width,
        )

        self.raster_paths_same_bounds[raster_key] = output_raster

    def run(self, overwrite: bool = False, **kwargs):
        """Start raster calculation.

        Parameters
        ----------
        overwrite : bool, optional, by default False
            False -> if output already exists this will not run.
            True  -> remove existing output and continue
        **kwargs:
            extra arguments that can be passed to the custom_run_window_function
        """
        try:
            cont = self.verify(overwrite=overwrite)
            if cont:
                self.create()

            if cont:
                if self.verbose:
                    time_start = datetime.datetime.now()

                self.metadata_raster.min_block_size = self.min_block_size
                self.blocks_df = self.metadata_raster.generate_blocks()
                blocks_total = len(self.blocks_df)

                # Open output raster for writing
                gdal_src = self.raster_out.open_gdal_source_write()
                band_out = gdal_src.GetRasterBand(1)

                # Loop over generated blocks and do calculation per block
                for idx, block_row in self.blocks_df.iterrows():
                    window = block_row["window_readarray"]

                    # Load the blocks for the given window.
                    block = RasterBlocks(
                        window=window,
                        raster_paths_dict=self.raster_paths_same_bounds,
                        nodata_keys=self.nodata_keys,
                        mask_keys=self.mask_keys,
                    )

                    # The blocks have an attribute that can prevent further calculation
                    # if certain conditions are met. It is False when a raster in the
                    # nodata keys has all value as nodata. Output should be nodata as well
                    if block.cont:
                        # Calculate output raster block with custom function.
                        block_out = self.custom_run_window_function(block=block, **kwargs)

                        self.raster_out.write_array(array=block_out, window=window, band=band_out)

                        if self.verbose:
                            time_duration = hrt.time_delta(time_start)
                            print(f"{idx} / {blocks_total} ({time_duration}s) - {self.raster_out.name}", end="\r")

                # band_out.FlushCache()  # close file after writing, slow, needed?
                band_out = None
                if self.verbose:
                    print("\nDone")
            else:
                if self.verbose:
                    print(f"{self.raster_out.name} not created, .verify was false.")
        except Exception as e:
            band_out.FlushCache()
            band_out = None
            self.raster_out.unlink()
            raise e
