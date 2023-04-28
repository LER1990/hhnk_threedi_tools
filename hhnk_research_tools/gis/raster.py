# %%
from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
from scipy import ndimage
import os
import inspect
from shapely import geometry
from pathlib import Path

import hhnk_research_tools as hrt
from hhnk_research_tools.folder_file_classes.file_class import File



class Raster(File):
    def __init__(self, source_path, min_block_size=1024):
        super().__init__(source_path)
        self.source_path = source_path

        
        self.source_set=False #Tracks if the source exist on the system. 
        # self.source = True #calls self.source.setter(source_path)

        self._array = None
        self.min_block_size=min_block_size

    @property
    def array(self):
        if self._array  is not None:
            print('from memory')
            return self._array
        else:
            print('Array not loaded. Call Raster.get_array(window) first')
            return self._array

    @property
    def source_path(self):
        return self._source_path
    @source_path.setter
    def source_path(self, value):
        if type(value)==str:
            value = Path(value)
        self._source_path = value

    @array.setter
    def array(self, raster_array, window=None, band_nr=1):
        self._array = raster_array
        # self.source.GetRasterBand(band_nr).WriteArray(window[0],window[1],raster_array)

    def _read_array(self, band=None, window=None):
        """window=[x0, y0, x1, y1]--oud.
        window=[x0, y0, xsize, ysize]
        x0, y0 is left top corner!!"""
        if band == None:
            gdal_src = self.open_gdal_source()
            band = gdal_src.GetRasterBand(1) #TODO band is not closed properly

        if window is not None:
            # raster_array = band.ReadAsArray(
            #     xoff=int(window[0]),
            #     yoff=int(window[1]),
            #     win_xsize=int(window[2] - window[0]),
            #     win_ysize=int(window[3] - window[1]))

            raster_array = band.ReadAsArray(
                xoff=int(window[0]),
                yoff=int(window[1]),
                win_xsize=int(window[2]),
                win_ysize=int(window[3]))
        else:
            raster_array = band.ReadAsArray()

        band.FlushCache()  # close file after writing
        band = None

        return raster_array

    def get_array(self, window=None):
        try:
            gdal_src = self.open_gdal_source()
            if self.band_count == 1:
                raster_array = self._read_array(band=gdal_src.GetRasterBand(1), 
                                                window=window)

            elif self.band_count == 3:
                red_array = self._read_array(band=gdal_src.GetRasterBand(1), 
                                                window=window)
                green_array = self._read_array(band=gdal_src.GetRasterBand(2), 
                                                window=window)   
                blue_array = self._read_array(band=gdal_src.GetRasterBand(3), 
                                window=window)                                                                            

                raster_array = np.dstack((red_array, green_array, blue_array))
            else:
                raise ValueError(
                    f"Unexpected number of bands in raster {self.source_path} (expect 1 or 3)"
                )
            self._array = raster_array
            return raster_array

        except Exception as e:
            raise e from None


    @property
    def source(self):
        if not self.source_set:
            self.source=True #call source.setter
            return self.open_gdal_source()
        else:
            return self.open_gdal_source()
    @source.setter
    def source(self, value):
        """If source does not exist it will not be set.
        Bit clunky. But it should work that if it exists it will only be set once. 
        Otherwise it will not set.  """
        if os.path.exists(self.source_path): #cannot use self.exists here.
            #Needs to be first otherwise we end in a loop when settings metadata/nodata/band_count
            self.source_set=True 

            # self._source=gdal.Open(str(self.source_path), gdal.GA_ReadOnly)
            gdal_src = self.open_gdal_source()

            self._metadata = RasterMetadata(gdal_src=gdal_src)
            self._nodata = gdal_src.GetRasterBand(1).GetNoDataValue()
            self._band_count = gdal_src.RasterCount


    def open_gdal_source(self):
        """usage;
        with self.open_gdal_source() as gdal_src: doesnt work.
        just dont write it to the class, and it should be fine..
        """
        return gdal.Open(str(self.source_path), gdal.GA_ReadOnly)


    @property
    def exists(self):
        if self.source_set: #check this first for speed.
            return True
        else:
            path_exists = os.path.exists(self.source_path)
            if not self.source_set:
                if path_exists:
                    self.source #Set the source.      
            return path_exists


    @property
    def nodata(self):
        if self.exists:
            return self._nodata
        
    @property
    def band_count(self):
        if self.exists:
            return self._band_count

    @property
    def metadata(self):
        if self.exists:
            return self._metadata
        

    def plot(self):
        plt.imshow(self._array)


    @property
    def shape(self):
        return self.metadata.shape

    @property
    def pixelarea(self):
        return self.metadata.pixelarea


    def generate_blocks(self) -> pd.DataFrame:
        """Generate blocks with the blocksize of the band. 
        These blocks can be used as window to load the raster iteratively."""
        gdal_src = self.open_gdal_source()
        band = gdal_src.GetRasterBand(1)

        block_height, block_width = band.GetBlockSize()

        if (block_height < self.min_block_size) or (block_width < self.min_block_size):
            block_height=self.min_block_size
            block_width=self.min_block_size

        ncols = int(np.floor(band.XSize / block_width))
        nrows = int(np.floor(band.YSize / block_height))


        #Create arrays with index of where windows end. These are square blocks. 
        xparts = np.linspace(0, block_width*ncols, ncols+1).astype(int)
        yparts = np.linspace(0, block_height*nrows, nrows+1).astype(int)

        #If raster has some extra data that didnt fall within a block it is added to the parts here.
        #These blocks are not square.
        if block_width*ncols != self.shape[1]:
            xparts=np.append(xparts, self.shape[1])
            ncols+=1
        if block_height*nrows != self.shape[0]:
            yparts=np.append(yparts, self.shape[0])
            nrows+=1

        blocks_df = pd.DataFrame(index=np.arange(nrows*ncols)+1, columns=['ix', 'iy', 'window'])
        i = 0
        for ix in range(ncols):
            for iy in range(nrows):
                i += 1
                blocks_df.loc[i, :] = np.array((ix, iy, [xparts[ix], yparts[iy], xparts[ix+1], yparts[iy+1]]), dtype=object)

        blocks_df['window_readarray'] = blocks_df['window'].apply(lambda x: [int(x[0]), int(x[1]), int(x[2]-x[0]), int(x[3]-x[1])])

        band.FlushCache()  # close file after writing
        band = None

        self.blocks=blocks_df
        return blocks_df


    def _generate_blocks_geometry_row(self, window):
        minx=self.metadata.x_min
        maxy=self.metadata.y_max

        #account for pixel size
        minx += window[0] *self.metadata.pixel_width
        maxy += window[1] * self.metadata.pixel_height
        maxx = minx + window[2] *self.metadata.pixel_width
        miny = maxy + window[3] * self.metadata.pixel_height
        
        return geometry.box(minx=minx, miny=miny, maxx=maxx, maxy=maxy)
    
    def generate_blocks_geometry(self) -> gpd.GeoDataFrame:
        """Create blocks with shapely geometry"""
        self.generate_blocks()
        blocks_df =gpd.GeoDataFrame(self.blocks, geometry=self.blocks["window_readarray"].apply(self._generate_blocks_geometry_row), crs=self.metadata.projection)
        self.blocks = blocks_df
        return blocks_df

    def sum_labels(self, labels_raster, labels_index):
        """Calculate the sum of the rastervalues per label."""
        if labels_raster.shape != self.shape:
            raise Exception(f'label raster shape {labels_raster.shape} does not match the raster shape {self.shape}')

        accum = None

        for window, block in self:
            block[block==self.nodata] = 0
            block[pd.isna(block)] = 0

            block_label = labels_raster._read_array(window=window)

            #Calculate sum per label (region)
            result = ndimage.sum_labels(input=block,
                                    labels=block_label,
                                    index=labels_index) #Which values in labels to take into account.

            if accum is None:
                accum = result
            else:
                accum += result
        return accum


    def iter_window(self, min_block_size=None):
        """Iterate of the raster using blocks, only returning the window, not the values."""
        if not hasattr(self,'blocks'):
            if min_block_size is not None:
                 self.min_block_size = min_block_size
                
            _ = self.generate_blocks_geometry()

        for idx, block_row in self.blocks.iterrows():
            window=block_row['window_readarray']
            yield idx, window, block_row

    def to_file():
        pass

    def __iter__(self):
        if not hasattr(self,'blocks'):
            _ = self.generate_blocks()

        for idx, block_row in self.blocks.iterrows():
            window=block_row['window_readarray']
            block = self._read_array(window=window)
            yield window, block
            

    def __repr__(self):
        if self.exists:
            return f"""{self.__class__}
    Source: {self.source_path}, exists:{self.exists}
    Shape: {self.metadata.shape}
    Pixelsize: {self.metadata.pixel_width}"""
        else:
            return f"""{self.__class__}
    Source: {self.source_path}, exists:{self.exists}"""



    def create(self, metadata, nodata, overwrite=False):
        """Create empty raster
        metadata : RasterMetadata instance
        nodata: int
        """
        #Check if function should continue.
        cont=True
        if not overwrite and self.source_path.exists():
            cont=False

        if cont==True:
            print(f"creating output raster: {self.source_path}")
            target_ds = hrt.create_new_raster_file(file_name=str(self.source_path),
                                                    nodata=nodata,
                                                    meta=metadata,)
            target_ds = None
        else:
            print(f"output raster already exists: {self.source_path}")
        self.exists #Update raster now it exists


class RasterMetadata():
    """Metadata object of a raster. Resolution can be changed
    so that a new raster with another resolution can be created.
    
    Metadata can be created by supplying either: 
    1. gdal_src
    2. res, bounds
    """
    def __init__(self, gdal_src=None, res=None, bounds_dict=None, proj='epsg:28992'):
        """gdal_src = gdal.Open(raster_source)
        bounds = {minx:, maxx:, miny:, maxy:}
        Projection only implemented for epsg:28992"""

        if gdal_src is not None:
            self.proj = gdal_src.GetProjection()
            self.georef = gdal_src.GetGeoTransform()

            self.x_res = gdal_src.RasterXSize
            self.y_res = gdal_src.RasterYSize

        elif res is not None and bounds_dict is not None:
            projections = {'epsg:28992':'PROJCS["Amersfoort / RD New",GEOGCS["Amersfoort",DATUM["Amersfoort",SPHEROID["Bessel 1841",6377397.155,299.1528128,AUTHORITY["EPSG","7004"]],TOWGS84[565.2369,50.0087,465.658,-0.406857,0.350733,-1.87035,4.0812],AUTHORITY["EPSG","6289"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4289"]],PROJECTION["Oblique_Stereographic"],PARAMETER["latitude_of_origin",52.15616055555555],PARAMETER["central_meridian",5.38763888888889],PARAMETER["scale_factor",0.9999079],PARAMETER["false_easting",155000],PARAMETER["false_northing",463000],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["X",EAST],AXIS["Y",NORTH],AUTHORITY["EPSG","28992"]]'}
            
            self.proj=projections[proj]
            self.georef = (int(np.floor(bounds_dict['minx'])), res, 0.0, int(np.ceil(bounds_dict['maxy'])), 0.0, -res)
            self.x_res = int((int(np.ceil(bounds_dict['maxx']))-int(np.floor(bounds_dict['minx'])))/res)
            self.y_res = int((int(np.ceil(bounds_dict['maxy']))-int(np.floor(bounds_dict['miny'])))/res)

        else:
            raise Exception('Metadata class called without proper input.')
    @property
    def pixel_width(self):
        return self.georef[1]

    @property
    def pixel_height(self):
        return self.georef[5]

    @property
    def x_min(self):
        return self.georef[0]

    @property
    def y_max(self):
        return self.georef[3]

    @property
    def x_max(self):
        return self.x_min + self.georef[1] * self.x_res

    @property
    def y_min(self):
        return self.y_max + self.georef[5] * self.y_res

    @property
    def bounds(self):
        return [self.x_min, self.x_max, self.y_min, self.y_max]

    @property
    def bounds_dl(self):
        return {
            "west": self.x_min,
            "south": self.y_min,
            "east": self.x_max,
            "north": self.y_max,
        }

    @property
    def shape(self):
        return [self.y_res, self.x_res]

    @property
    def pixelarea(self):
        return abs(self.georef[1] * self.georef[5])
    
    @property
    def projection(self):
        try:
            proj_str = self.proj.split('AUTHORITY')[-1][2:-3].split('","')
            return f"{proj_str[0]}:{proj_str[1]}"
        except:
            return None

    def _update_georef(self, resolution):
        def res_str(georef_i):
            """make sure negative values are kept."""
            if georef_i == self.pixel_width:
                return resolution
            if georef_i == -self.pixel_width:
                return -resolution
                
        georef_new = list(self.georef)
        georef_new[1] = res_str(georef_new[1])
        georef_new[5] = res_str(georef_new[5])
        return tuple(georef_new)


    def update_resolution(self, resolution_new):
        """Create new resolution metdata, only works for refining now."""
        resolution_current = self.pixel_width
        if (resolution_current / resolution_new).is_integer():
            self.x_res = int((resolution_current/resolution_new) *  self.x_res)
            self.y_res = int((resolution_current/resolution_new) *  self.y_res)
            self.georef = self._update_georef(resolution_new)
            print(f'updated metadata resolution from {resolution_current}m to {resolution_new}m')
        else:
            raise Exception(f'New resolution ({resolution_new}) can currently only be smaller than old resolution ({resolution_current})')

    def __repr__(self):
        funcs = '.'+' .'.join([i for i in dir(self) if not i.startswith('_') and hasattr(inspect.getattr_static(self,i), '__call__')]) #getattr resulted in RecursionError. https://stackoverflow.com/questions/1091259/how-to-test-if-a-class-attribute-is-an-instance-method
        variables = '.'+' .'.join([i for i in dir(self) if not i.startswith('__') and not hasattr(inspect.getattr_static(self,i)
                        , '__call__')])
        repr_str = f"""functions: {funcs}
variables: {variables}"""
        return f""".projection : {self.projection} 
.georef : {self.georef}
.bounds : {self.bounds}
.pixel_width : {self.pixel_width}
----
{repr_str}"""

    def __getitem__(self, item):
        """metadata was a dict previously. This makes it that items from
        the class can be accessed like a dict."""
        return getattr(self, item)


if __name__ == '__main__':
    dem_path = r"G:\02_Werkplaatsen\06_HYD\Projecten\HKC16015 Wateropgave 2.0\11. DCMB\hhnk-modelbuilder-master\data\fixed_data\DEM\DEM_AHN4_int.vrt"

    r=Raster(dem_path)
    print(r)

# %%
