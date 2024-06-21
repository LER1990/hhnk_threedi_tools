from xml.dom import NoDataAllowedErr
from fiona import Properties


class Raster(File):
    pass


    @property
    nodata

    def read_array(self):


    def source_read():

    def source_write():

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
build_vrt
create_meta_from_gdf
dx_dy_between_rasters
reproject -> as method under hrt.Raster
hist_stats


