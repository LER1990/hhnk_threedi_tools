import rioxarray as rxr
from osgeo import gdal
from hhnk_research_tools.folder_file_classes.file_class import File
import rasterio as rio

CHUNKSIZE=4096
class Raster(File):
    def __init__(self, base, chunksize=CHUNKSIZE):
        super().__init__(base)

        self.chunksize = chunksize
        self._rxr = None

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
    def nodata(self):
        return self.metadata.nodata

    @property
    def shape(self):
        return self.metadata.shape

    @property
    def pixelarea(self):
        return self.metadata.pixelarea

    @property
    def rxr(self):
        if self._rxr is None:
            self._rxr = rxr.open_rasterio(self.base, chunks={"x": self.chunksize, "y": self.chunksize})
        return self._rxr


    def open_gdal_read(self):
        """usage;
        with self.open_gdal_source_read() as gdal_src: doesnt work.
        just dont write it to the class, and it should be fine..
        """
        return gdal.Open(self.base, gdal.GA_ReadOnly)

    def open_gdal_write(self):
        """Open source with write access"""
        return gdal.Open(self.base, gdal.GA_Update)

    def open_rio_write(self):
        return rio.open(self.base, 'r+')
    
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
    def metadata():


    def generate_blocks:
        #TODO deze zou ook van een extent moeten werken, 
        #of vanaf een gdf.

    def generate_blocks_geometry:
        # Twee opties: rxr + hrt   
        #Is er reden om dit niet te doen?
    


    @classmethod
    def write(cls, raster_out, result, dtype="float32", scale_factor=None, chunksize=CHUNKSIZE):
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
            NUM_THREADS="ALL_CPUS",#gdal options
            dtype=dtype,
        )

        # Settings the scale_factor does not work with rioxarray. Update the result
        if scale_factor:
            with raster_out.open_rio_write() as src:
                src.scales = (scale_factor,)


    #Bewerkingen
    def sum_labels
    def build_vrt
        #TODO dit moet ook vanuit een folder kunnen/ een lijst van tifs
    def sum

    def reproject




#Calculator
gdf_to_raster
create_new_raster_file
save_raster_array_to_tiff
build_vrt -> losse functie
create_meta_from_gdf
dx_dy_between_rasters
reproject -> as method under hrt.Raster
hist_stats


