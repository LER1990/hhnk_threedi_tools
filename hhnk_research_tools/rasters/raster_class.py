import rioxarray as rxr
from osgeo import gdal
from hhnk_research_tools.folder_file_classes.file_class import File
from hhnk_research_tools.general_functions import check_create_new_file
from hhnk_research_tools.rasters.raster_metadata import RasterMetadata
import rasterio as rio
import xarray as xr
import numpy as np

CHUNKSIZE=4096
class RasterV2(File):
    def __init__(self, base, chunksize=CHUNKSIZE):
        super().__init__(base)

        self.chunksize = chunksize
        self._rxr = None
        self._metadata = None

    #DEPRECATED
    def deprecation_warn(self, txt):   
        return DeprecationWarning(f"Not available since 2024.2{txt}")
    
    @property
    def array(self):
        raise self.deprecation_warn()
    @property
    def _array(self):
        raise self.deprecation_warn()
    
    @property
    def _read_array(self):
        raise self.deprecation_warn()
    @property
    def get_array(self):
        raise self.deprecation_warn()
    @property
    def source(self):
        raise self.deprecation_warn(", use .open_gdal_source_read()")
    @property
    def source_set(self):
        raise self.deprecation_warn()

    @property
    def source_set(self):
        raise self.deprecation_warn()
    @property
    def band_count(self):
        raise self.deprecation_warn()
    @property
    def plot(self):
        #TODO rxr versie maken
        # plt.imshow(self._array)
        raise self.deprecation_warn()
    

    @property
    def metadata(self):
        if self._metadata is None:
            self._metadata = RasterMetadata.from_gdal_src(gdal_src=self.open_gdal_read())
        return self._metadata


    @property
    def nodata(self):
        return self.metadata.nodata

    @property
    def shape(self):
        return self.metadata.shape

    @property
    def pixelarea(self):
        return self.metadata.pixelarea

    # @property
    # def rxr(self):
    #     if self._rxr is None:
    #         self._rxr = rxr.open_rasterio(self.base, chunks={"x": self.chunksize, "y": self.chunksize})
    #     return self._rxr


    def open_gdal_read(self):
        """usage;
        with self.open_gdal_read() as gdal_src: doesnt work.
        just dont write it to the class, and it should be fine..
        """
        return gdal.Open(self.base, gdal.GA_ReadOnly)

    def open_gdal_write(self):
        """Open source with write access"""
        return gdal.Open(self.base, gdal.GA_Update)

    def open_rio_write(self):
        return rio.open(self.base, 'r+')
    

    def open_rxr(self, mask_and_scale=False):
        """Open raster as rxr.DataArray

        Parameters
        ----------
        mask_and_scale : bool, default=False
            Lazily scale (using the scales and offsets from rasterio) and mask.
        """
        rxr.open_rasterio(self.base, chunks={"x": self.chunksize, "y": self.chunksize}, masked=True, mask_and_scale=mask_and_scale)


    def overviews_build(self, factors:list=[16], resampling="average"):
        """Build overviews for faster rendering.
        documentation: https://gdal.org/programs/gdaladdo.html
        """
        with self.open_rio_write() as dst:
            dst.build_overviews(factors, getattr(rio.enums.Resampling, resampling))
            dst.update_tags(ns='rio_overview', resampling=resampling)

        #TODO this seems to give a nice result, can we incorparte it here somewhre or can rio do the same?
        # !gdaladdo -ro -r nearest --config COMPRESS_OVERVIEW ZSTD --config PREDICTOR_OVERVIEW 2 --config ZSTD_LEVEL_OVERVIEW 1 "C:\Users\Wietse\Documents\HHNK\playground\dem_schemer_hoog_zuid_compressed_v4.tif" 8 32

    
    def overviews_available(self):
        """Display available overviews on raster."""
        src = rio.open(self.base, "r")
        print([src.overviews(i) for i in src.indexes])

    def overviews_remove(self):
        """Remove overviews from raster"""
        ds = self.open_gdal_source_write()
        ds.BuildOverviews("NONE")
        ds = None

        print(f"Removed overviews: {self.view_name_with_parents(2)}")

    def statistics():


    # def generate_blocks:
    #     #TODO deze zou ook van een extent moeten werken, 
    #     #of vanaf een gdf.

    # def generate_blocks_geometry:
    #     # Twee opties: rxr + hrt   
    #     #Is er reden om dit niet te doen?
    


    #Bewerkingen
    def sum(self):
        """Calculate sum of raster"""
        raster_sum = 0
        #TODO Hoe rxr
        for window, block in self:
            block[block == self.nodata] = 0
            raster_sum += np.nansum(block)
        return raster_sum
    
        da = self.open_rxr()
        return da.values.sum()
    


    @classmethod
    def write(cls, raster_out:str, result: xr.DataArray, dtype:str="float32", scale_factor:float=None, chunksize:int=CHUNKSIZE):
        """
        used to create a raster.
        works both for rasters and gdf.

        from geocube.api.core import make_geocube
        out_grid = make_geocube(
            vector_data=grid_gpkg,
            resolution=(5, -5),
            fill=-9999
        )

        raster_out : str, Path, Raster
            output location
        result : xr.DataArray
            output array, either the result of an rxr calcultation or a dataframe turned into geocube 
        dtype : str
            output raster dtype
        scale_factor: float
            When saving as int, use a scale_factor to get back to original scale.
        chunksize : int
        
        """
        """Write a rxr result to file."""
        raster_out = cls(raster_out, chunksize=chunksize)

        if "float" in dtype:
            compress="LERC_DEFLATE"
        else:
            compress="ZSTD"

        result.rio.to_raster(
            raster_out.base,
            # chunks={"x": CHUNKSIZE, "y": CHUNKSIZE},
            chunks=True,
            # lock=threading.Lock(), #Use dask multithread
            lock=True,
            tiled=True,
            windowed=True, #If lock is False, window doesnt work.
            COMPRESS=compress, #gdal options
            PREDICTOR=2,#gdal options
            ZSTD_LEVEL=1,#gdal options
            MAX_Z_ERROR=0.001, #gdal options
            NUM_THREADS="ALL_CPUS",#gdal options
            dtype=dtype,
        )

        # Settings the scale_factor does not work with rioxarray. Update the result
        if scale_factor:
            with raster_out.open_rio_write() as src:
                src.scales = (scale_factor,)

        return raster_out

    @classmethod
    def build_vrt(cls, vrt_out:str, input_files: str|list,bounds=None, overwrite: bool=False, resolution="highest", bandlist=[1]):
        """Build vrt from input files.
        overwrite (bool)
        bounds (np.array): format should be; (xmin, ymin, xmax, ymax)
            if None will use input files.
        input_files (list): list of paths to input rasters
        resolution: "highest"|"lowest"|"average"
            instead of "user" option, provide a float for manual target_resolution
        bandList: doesnt work as expected, passing [1] works.
        """

        vrt_out = cls(vrt_out)

        if check_create_new_file(output_file=vrt_out, overwrite=overwrite):
            # Set inputfiles to list of strings.
            if type(input_files) != list:
                input_files = [str(input_files)]
            else:
                input_files = [str(i) for i in input_files]

            if type(resolution) in (float, int):
                kwargs = {}
                xRes = resolution
                yRes = resolution
                resolution = "user"
            else:
                xRes = None
                yRes = None

            # Check resolution of input files
            input_resolutions = []
            for r in input_files:
                r = cls(r)
                input_resolutions.append(r.metadata.pixel_width)
            if len(np.unique(input_resolutions)) > 1:
                raise Exception(
                    f"Multiple resolutions ({input_resolutions}) found in input_files. We cannot handle that yet."
                )

            # Build vrt
            vrt_options = gdal.BuildVRTOptions(
                resolution=resolution,
                separate=False,
                resampleAlg="nearest",
                addAlpha=False,
                outputBounds=bounds,
                bandList=bandlist,
                xRes=xRes,
                yRes=yRes,
            )
            ds = gdal.BuildVRT(destName=str(vrt_out), srcDSOrSrcDSTab=input_files, options=vrt_options)
            ds.FlushCache()
        return vrt_out
    
    #Bewerkingen
    # def sum_labels



    # def reproject




# #Calculator
# gdf_to_raster
# create_new_raster_file
# save_raster_array_to_tiff
# build_vrt -> losse functie
# create_meta_from_gdf
# dx_dy_between_rasters
# reproject -> as method under hrt.Raster
# hist_stats


