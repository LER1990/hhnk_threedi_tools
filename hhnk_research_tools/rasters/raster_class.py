import rioxarray as rxr
from osgeo import gdal
from hhnk_research_tools.folder_file_classes.file_class import File
class Raster(File):
    def __init__(self, base, chunksize=4096):
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


    def open_gdal_source_read(self):
        """usage;
        with self.open_gdal_source_read() as gdal_src: doesnt work.
        just dont write it to the class, and it should be fine..
        """
        return gdal.Open(self.base, gdal.GA_ReadOnly)

    def open_gdal_source_write(self):
        """Open source with write access"""
        return gdal.Open(self.base, gdal.GA_Update)
    

    def statistics():
    def metadata():


    def generate_blocks:
        #TODO deze zou ook van een extent moeten werken, 
        #of vanaf een gdf.

    def generate_blocks_geometry:
        # Twee opties: rxr + hrt   
        #Is er reden om dit niet te doen?
    



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


