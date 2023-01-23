# %%
from osgeo import gdal, ogr
import numpy as np
import json
from hhnk_research_tools.variables import DEF_TRGT_CRS
from hhnk_research_tools.variables import GDAL_DATATYPE, GEOTIFF
from hhnk_research_tools.variables import GEOTIFF, GDAL_DATATYPE
from hhnk_research_tools.general_functions import ensure_file_path
from hhnk_research_tools.gis.raster import Raster, RasterMetadata
from pathlib import Path
import os


# Loading
def _get_array_from_bands(gdal_file, band_count, window, raster_source):
    try:
        if band_count == 1:
            band = gdal_file.GetRasterBand(1)
            if window is not None:
                raster_array = band.ReadAsArray(
                    xoff=window[0],
                    yoff=window[1],
                    win_xsize=window[2] - window[0],
                    win_ysize=window[3] - window[1],
                )
            else:
                raster_array = band.ReadAsArray()
            return raster_array
        elif band_count == 3:
            if window is not None:
                red_arr = gdal_file.GetRasterBand(1).ReadAsArray(
                    xoff=window[0],
                    yoff=window[1],
                    win_xsize=window[2] - window[0],
                    win_ysize=window[3] - window[1],
                )
                green_arr = gdal_file.GetRasterBand(2).ReadAsArray(
                    xoff=window[0],
                    yoff=window[1],
                    win_xsize=window[2] - window[0],
                    win_ysize=window[3] - window[1],
                )
                blue_arr = gdal_file.GetRasterBand(3).ReadAsArray(
                    xoff=window[0],
                    yoff=window[1],
                    win_xsize=window[2] - window[0],
                    win_ysize=window[3] - window[1],
                )
            else:
                red_arr = gdal_file.GetRasterBand(1).ReadAsArray()
                green_arr = gdal_file.GetRasterBand(2).ReadAsArray()
                blue_arr = gdal_file.GetRasterBand(3).ReadAsArray()
            raster_arr = np.dstack((red_arr, green_arr, blue_arr))
            return raster_arr
        else:
            raise ValueError(
                f"Unexpected number of bands in raster {raster_source} (expect 1 or 3)"
            )
    except Exception as e:
        raise e


def load_gdal_raster(raster_source, window=None, return_array=True, band_count=None):
    """
    Loads a raster (tif) and returns an array of its values, its no_data value and
    dict containing associated metadata
    returns raster_array, no_data, metadata
    """
    try:
        gdal_src = gdal.Open(raster_source)
        if gdal_src:
            if return_array:
                if band_count==None:
                    band_count = gdal_src.RasterCount
                raster_array = _get_array_from_bands(
                    gdal_src, band_count, window, raster_source
                )
            else:
                raster_array = None
            # are they always same even if more bands?
            no_data = gdal_src.GetRasterBand(1).GetNoDataValue()
            metadata = RasterMetadata(gdal_src=gdal_src)
            return raster_array, no_data, metadata
    except Exception as e:
        raise e


# Conversion
def _gdf_to_json(gdf, epsg=DEF_TRGT_CRS):
    try:
        gdf_json = json.loads(gdf.to_json())
        gdf_json["crs"] = {
            "type": "name",
            "properties": {"name": "urn:ogc:def:crs:EPSG::{}".format(epsg)},
        }
        gdf_json_str = json.dumps(gdf_json)
        return gdf_json_str
    except Exception as e:
        raise e


def _gdf_to_ogr(gdf, epsg=DEF_TRGT_CRS):
    """Create ogr instance of gdf"""
    try:
        gdf_json = _gdf_to_json(gdf, epsg)
        ogr_ds = ogr.Open(gdf_json)
        polygon = ogr_ds.GetLayer()
        return ogr_ds, polygon
    except Exception as e:
        raise e


def gdf_to_raster(
    gdf,
    value_field,
    raster_out,
    nodata,
    metadata,
    epsg=DEF_TRGT_CRS,
    driver=GEOTIFF,
    datatype=GDAL_DATATYPE,
    compression="DEFLATE",
    tiled="YES",
    read_array=True,
):
    """Dem is used as format raster. The new raster gets meta data from the DEM. A gdf is turned into ogr layer and is
    then rasterized.
    wsa.polygon_to_raster(polygon_gdf=mask_gdf[mask_type], valuefield='val', raster_output_path=mask_path[mask_type],
    nodata=0, meta=meta, epsg=28992, driver='GTiff')
    """
    try:
        ogr_ds, polygon = _gdf_to_ogr(gdf, epsg)
        # make sure folders exist
        if raster_out != '': #empty str when driver='MEM'
            ensure_file_path(raster_out)
        new_raster = create_new_raster_file(
            file_name=raster_out,
            nodata=nodata,
            meta=metadata,
            driver=driver,
            datatype=datatype,
        )
        gdal.RasterizeLayer(
            new_raster,
            [1],
            polygon,
            options=[
                f"ATTRIBUTE={value_field}",
                f"COMPRESS={compression}",
                f"TILED={tiled}",
            ],
        )
        if read_array:
            raster_array = new_raster.ReadAsArray()
            return raster_array
        else:
            return None
    except Exception as e:
        raise e


# Saving
def _set_band_data(data_source, num_bands, nodata):
    try:
        for i in range(1, num_bands + 1):
            band = data_source.GetRasterBand(i)
            band.SetNoDataValue(nodata)
            band.Fill(nodata)
            band.FlushCache()  # close file after writing
            band = None
    except Exception as e:
        raise e


def create_new_raster_file(
    file_name,
    nodata,
    meta,
    driver=GEOTIFF,
    datatype=GDAL_DATATYPE,
    compression="DEFLATE",
    num_bands=1,
    tiled="YES",
):
    """
    ONLY FOR SINGLE BAND
    Create new empty gdal raster using metadata from raster from sqlite (dem)
    driver='GTiff'
    driver='MEM'
    Compression:
    LZW - highest compression ratio, highest processing power
    DEFLATE
    PACKBITS - lowest compression ratio, lowest processing power
    """
    try:
        target_ds = gdal.GetDriverByName(driver).Create(
            str(file_name),
            meta.x_res,
            meta.y_res,
            num_bands,
            datatype,
            options=[f"COMPRESS={compression}", f"TILED={tiled}"],
        )
        target_ds.SetGeoTransform(meta.georef)
        _set_band_data(target_ds, num_bands, nodata)
        target_ds.SetProjection(meta.proj)
        return target_ds
    except Exception as e:
        raise e


def save_raster_array_to_tiff(
    output_file,
    raster_array,
    nodata,
    metadata,
    datatype=GDAL_DATATYPE,
    compression="DEFLATE",
    num_bands=1,
):
    """
    ONLY FOR SINGLE BAND

    input:
    output_file (filepath)
    raster_array (values to be converted to tif)
    nodata (nodata value)
    metadata (dictionary)
    datatype -> gdal.GDT_Float32
    compression -> 'DEFLATE'
    num_bands -> 1
    """
    try:
        target_ds = create_new_raster_file(
            file_name=output_file,
            nodata=nodata,
            meta=metadata,
            datatype=datatype,
            compression=compression,
        )  # create new raster
        for i in range(1, num_bands + 1):
            target_ds.GetRasterBand(i).WriteArray(raster_array)  # fill file with data
        target_ds = None
    except Exception as e:
        raise e

        
def build_vrt(raster_folder, vrt_name='combined_rasters', bandlist=[1], bounds=None, overwrite=False):
    #TODO check resolution of all rasters in folder. if not equal then no vrt.
    """create vrt from all rasters in a folder.
    bounds=(xmin, ymin, xmax, ymax)
    bandList doesnt work as expected."""
    output_path = os.path.join(raster_folder, f'{vrt_name}.vrt')
    
    if os.path.exists(output_path) and not overwrite:
        print(f'vrt already exists: {output_path}')
        return

    tifs_list = [os.path.join(raster_folder, i) for i in os.listdir(raster_folder) if i.endswith('.tif') or i.endswith('.tiff')]


    for r in tifs_list:
        if Raster(r).metadata.pixel_width==1:
            print(Path(r.source_path).stem)


    vrt_options = gdal.BuildVRTOptions(resolution='highest',
                                       separate=False,
                                       resampleAlg='nearest',
                                       addAlpha=False,
                                       outputBounds=bounds,
                                       bandList=bandlist,)
    ds = gdal.BuildVRT(output_path, tifs_list, options=vrt_options)
    ds.FlushCache()
    del tifs_list

    if not os.path.exists(output_path):
        print('Something went wrong, vrt not created.')


def create_meta_from_gdf(gdf, res) -> dict:
    """Create metadata that can be used in raster creation based on gdf bounds. 
    Projection is 28992 default, only option.""" 
    gdf_local=gdf.copy()
    gdf_local['temp'] = 0
    bounds_dict = gdf_local.dissolve('temp').bounds.iloc[0]
    return RasterMetadata(res=res, bounds_dict=bounds_dict)


def dx_dy_between_rasters(meta_big, meta_small):
    """create window to subset a large 2-d array with a smaller rectangle. Usage:
    shapes_array[dy_min:dy_max, dx_min:dx_max]
    window=create_array_window_from_meta(meta_big, meta_small)
    shapes_array[window]"""
    if meta_small.pixel_width != meta_big.pixel_width:
        raise Exception(f"""Input rasters dont have same resolution. 
                meta_big   = {meta_big.pixel_width}m
                meta_small = {meta_small.pixel_width}m""")

    dx_min = max(0, int((meta_small.x_min-meta_big.x_min)/meta_big.pixel_width))
    dy_min = int((meta_big.y_max-meta_small.y_max)/meta_big.pixel_width)

    if dx_min < 0:
        raise Exception(f"dx_min smaller than 0 ({dx_min})")
    if dy_min < 0:
        raise Exception(f"dy_min smaller than 0 ({dy_min})")

    dx_max = int(min(dx_min + meta_small.x_res, meta_big.x_res))
    dy_max = int(min(dy_min + meta_small.y_res, meta_big.y_res))
    return dx_min, dy_min, dx_max, dy_max


class Raster_calculator():
    """Make a custom calculation between two rasters by 
    reading the blocks and applying a calculation
    input raster should be of type hhnk_research_tools.gis.raster.Raster

    raster1: hrt.Raster -> big raster
    raster2: hrt.Raster -> smaller raster with full extent within big raster. Raster numbering is interchangeable as the scripts checks the bounds.
    raster_out: hrt.Raster -> output, doesnt need to exists. self.create also creates it.
    custom_run_window_function: function that takes window of small and big raster as input and does calculation with these arrays.
    customize below function for this, can take more inputs.

    def custom_run_window_function(self, window_small, window_big, band_out, **kwargs):
        #Customize this function with a calculation
        #Load windows
        block_big = self.raster_big._read_array(window=window_big)
        block_small = self.raster_small._read_array(window=window_small)

        #Calculate output
        block_out = None #replace with a calculation.

        # Write to file
        band_out.WriteArray(block_out, xoff=window_small[0], yoff=window_small[1])

    
    """
    def __init__(self, raster1, raster2, raster_out, custom_run_window_function, verbose=False):

        self.raster_big, self.raster_small = self._checkbounds(raster1, raster2) 
        self.raster_out = raster_out

        #dx dy between rasters.
        self.dx_min, self.dy_min = dx_dy_between_rasters(meta_big=self.raster_big.metadata, meta_small=self.raster_small.metadata)
        
        self.blocks_df = self.raster_small.generate_blocks()
        self.blocks_total = len(self.blocks_df)
        self.custom_run_window_function = custom_run_window_function
        self.verbose = verbose


    def _checkbounds(self, raster1, raster2):
        x1, x2, y1, y2=raster1.metadata.bounds
        xx1, xx2, yy1, yy2=raster2.metadata.bounds
        bounds_diff = x1 - xx1, y1 - yy1, xx2-x2, yy2 - y2 #subtract bounds
        check_arr = np.array([i<=0 for i in bounds_diff]) #check if values <=0

        #If all are true (or all false) we know that the rasters fully overlap. 
        if raster1.metadata.pixel_width != raster2.metadata.pixel_width:
            raise Exception("""Rasters do not have equal resolution""")

        if np.all(check_arr):
            #In this case raster1 is the bigger raster.
            return raster1, raster2
        elif np.all(~check_arr):
            #In this case raster2 is the bigger raster
            return raster2, raster1
        else:
            raise Exception("""Raster bounds do not overlap. We cannot use this.""")
        

    def create(self, overwrite=False, nodata=0):
        """Create empty output raster"""
        #Check if function should continue.
        cont=True
        if not overwrite and os.path.exists(self.raster_out.source_path):
            cont=False

        if cont==True:
            if self.verbose:
                print(f"creating output raster: {self.raster_out.source_path}")
            target_ds = create_new_raster_file(file_name=self.raster_out.source_path,
                                                    nodata=nodata,
                                                    meta=self.raster_small.metadata,)
            target_ds = None
        else:
            if self.verbose:
                print(f"output raster already exists: {self.raster_out.source_path}")


    def run(self, **kwargs):
        """loop over the small raster blocks, load both arrays and apply a custom function to it."""
        target_ds=gdal.Open(self.raster_out.source_path, gdal.GA_Update)
        band_out = target_ds.GetRasterBand(1)


        for idx, block_row in self.blocks_df.iterrows():
                #Load landuse 
                window_small=block_row['window_readarray']

                window_big = window_small.copy()
                window_big[0] += self.dx_min
                window_big[1] += self.dy_min

                self.custom_run_window_function(self=self, window_small=window_small, window_big=window_big, band_out=band_out, **kwargs)
                if self.verbose:
                    print(f"{idx} / {self.blocks_total}", end= '\r')
                # break
                
        band_out.FlushCache()  # close file after writing
        band_out = None
        target_ds = None


def reproject(src:Raster, target_res:float, output_path:str):
        """
        src : hrt.Raster
        output_path : str
        meta_new : hrt.core"""
        #https://svn.osgeo.org/gdal/trunk/autotest/alg/reproject.py
        # drv = gdal.GetDriverByName( 'GTiff' )
        # drv.Delete(output_path)

        src.metadata.update_resolution(target_res)

        src_ds = src.source
        dst_ds = create_new_raster_file(file_name=output_path,
                    nodata=src.nodata,
                    meta=src.metadata)

        gdal.ReprojectImage(src_ds, dst_ds, src_wkt='EPSG:28992')
        