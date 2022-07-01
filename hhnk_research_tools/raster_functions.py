from osgeo import gdal
import numpy as np
import json
from osgeo import ogr
from shapely.geometry import LineString
from hhnk_research_tools.variables import DEF_TRGT_CRS
from hhnk_research_tools.variables import GDAL_DATATYPE, GEOTIFF
from hhnk_research_tools.variables import GEOTIFF, GDAL_DATATYPE
from hhnk_research_tools.general_functions import ensure_file_path
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


def _get_gdal_metadata(gdal_file) -> dict:
    try:
        meta = {}
        meta["proj"] = gdal_file.GetProjection()
        meta["georef"] = gdal_file.GetGeoTransform()
        meta["pixel_width"] = meta["georef"][1]
        meta["x_min"] = meta["georef"][0]
        meta["y_max"] = meta["georef"][3]
        meta["x_max"] = meta["x_min"] + meta["georef"][1] * gdal_file.RasterXSize
        meta["y_min"] = meta["y_max"] + meta["georef"][5] * gdal_file.RasterYSize
        meta["bounds"] = [meta["x_min"], meta["x_max"], meta["y_min"], meta["y_max"]]
        # for use in threedi_scenario_downloader
        meta["bounds_dl"] = {
            "west": meta["x_min"],
            "south": meta["y_min"],
            "east": meta["x_max"],
            "north": meta["y_max"],
        }
        meta["x_res"] = gdal_file.RasterXSize
        meta["y_res"] = gdal_file.RasterYSize
        meta["shape"] = [meta["y_res"], meta["x_res"]]
        return meta
    except Exception as e:
        raise e


def load_gdal_raster(raster_source, window=None, return_array=True, band_count=None):
    """
    Loads a raster (tif) and returns an array of its values, its no_data value and
    dict containing associated metadata
    returns raster_array, no_data, metadata
    """
    try:
        gdal_file = gdal.Open(raster_source)
        if gdal_file:
            if return_array:
                if band_count==None:
                    band_count = gdal_file.RasterCount
                raster_array = _get_array_from_bands(
                    gdal_file, band_count, window, raster_source
                )
            else:
                raster_array = None
            # are they always same even if more bands?
            no_data = gdal_file.GetRasterBand(1).GetNoDataValue()
            metadata = _get_gdal_metadata(gdal_file)
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
            file_name,
            meta["x_res"],
            meta["y_res"],
            num_bands,
            datatype,
            options=[f"COMPRESS={compression}", f"TILED={tiled}"],
        )
        target_ds.SetGeoTransform(meta["georef"])
        _set_band_data(target_ds, num_bands, nodata)
        target_ds.SetProjection(meta["proj"])
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
    """create vrt from all rasters in a folder.
    bounds=(xmin, ymin, xmax, ymax)
    bandList doesnt work as expected."""
    output_path = os.path.join(raster_folder, f'{vrt_name}.vrt')
    
    if os.path.exists(output_path) and not overwrite:
        print(f'vrt already exists: {output_path}')
        return

    tifs_list = [os.path.join(raster_folder, i) for i in os.listdir(raster_folder) if i.endswith('.tif') or i.endswith('.tiff')]


    vrt_options = gdal.BuildVRTOptions(resolution='highest',
                                       separate=False,
                                       resampleAlg='nearest',
                                       addAlpha=False,
                                       outputBounds=bounds,
                                       bandList=bandlist,)
    ds = gdal.BuildVRT(output_path, tifs_list, options=vrt_options)
    ds.FlushCache()
    if not os.path.exists(output_path):
        print('Something went wrong, vrt not created.')



def create_meta(minx, maxx, miny, maxy, res, proj='epsg:28992') -> dict:
    """
    only works for epsg:28992. 
    example input:
    minx=113891
    maxy=535912
    maxx=120760
    miny=534177
    res=0.5
    """
    projections = {'epsg:28992':'PROJCS["Amersfoort / RD New",GEOGCS["Amersfoort",DATUM["Amersfoort",SPHEROID["Bessel 1841",6377397.155,299.1528128,AUTHORITY["EPSG","7004"]],TOWGS84[565.2369,50.0087,465.658,-0.406857,0.350733,-1.87035,4.0812],AUTHORITY["EPSG","6289"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4289"]],PROJECTION["Oblique_Stereographic"],PARAMETER["latitude_of_origin",52.15616055555555],PARAMETER["central_meridian",5.38763888888889],PARAMETER["scale_factor",0.9999079],PARAMETER["false_easting",155000],PARAMETER["false_northing",463000],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["X",EAST],AXIS["Y",NORTH],AUTHORITY["EPSG","28992"]]'}
    
    meta = {'proj': projections[proj],
         'georef': (int(np.floor(minx)), res, 0.0, int(np.ceil(maxy)), 0.0, -res),
         'pixel_width': res,
         'x_min': int(np.floor(minx)),
         'y_max': int(np.ceil(maxy)),
         'x_max': int(np.ceil(maxx)),
         'y_min': int(np.floor(miny))}
    meta = {**meta, 
          'x_res': int((meta['x_max']-meta['x_min'])/res),
         'y_res': int((meta['y_max']-meta['y_min'])/res)} 
    return meta
    
def create_meta_from_gdf(gdf, res) -> dict:
    """Create metadata that can be used in raster creation based on gdf bounds. 
    Projection is 28992 default, only option.""" 
    gdf_local=gdf.copy()
    gdf_local['temp'] = 0
    bounds = gdf_local.dissolve('temp').bounds.iloc[0]

    return create_meta(**bounds, res=res)