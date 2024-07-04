# %%

import inspect
from dataclasses import dataclass

import geopandas as gpd
import numpy as np

from hhnk_research_tools.general_functions import get_functions, get_variables


@dataclass
class RasterMetadataV2:
    """Metadata object of a raster. Resolution can be changed
    so that a new raster with another resolution can be created.

    Metadata can be created by supplying either:
    1. gdal_src
    2. res, bounds
    """

    georef: None
    x_res: int
    y_res: int
    projection: str = "EPSG:28992"

    @classmethod
    def from_gdal_src(cls, gdal_src):
        """

        Parameters
        ----------
        gdal_src : _type_
            hrt.Raster.open_gdal()
        """

        proj = gdal_src.GetProjection()

        proj_str = proj.split("AUTHORITY")[-1][2:-3].split('","')
        projection = f"{proj_str[0]}:{proj_str[1]}"  # TODO andere manier uit raster halen. rio??
        georef = gdal_src.GetGeoTransform()

        x_res = gdal_src.RasterXSize
        y_res = gdal_src.RasterYSize

        return cls(georef=georef, x_res=x_res, y_res=y_res, projection=projection)

    @classmethod
    def from_bounds(cls, bounds_dict, res: float, projection="EPSG:28992"):
        """_summary_

        Parameters
        ----------
        bounds_dict : dict
            bounds = {"minx":, "maxx":, "miny":, "maxy":}
        res : float
            resolution
        projection : str, default is "EPSG:28992"
            doesnt work on other projs.
        """

        georef = (int(np.floor(bounds_dict["minx"])), res, 0.0, int(np.ceil(bounds_dict["maxy"])), 0.0, -res)
        x_res = int((int(np.ceil(bounds_dict["maxx"])) - int(np.floor(bounds_dict["minx"]))) / res)
        y_res = int((int(np.ceil(bounds_dict["maxy"])) - int(np.floor(bounds_dict["miny"]))) / res)
        return cls(georef=georef, x_res=x_res, y_res=y_res, projection=projection)

    def from_gdf(cls, gdf: gpd.GeoDataFrame, res: float):
        """Create metadata that can be used in raster creation based on gdf bounds.
        Projection is 28992 default, only option.
        """
        bounds = gdf.bounds

        # Metadata input vars
        projection = gdf.crs
        georef = (int(np.floor(bounds["minx"].min())), res, 0.0, int(np.ceil(bounds["maxy"].max())), 0.0, -res)
        x_res = int((int(np.ceil(bounds["maxx"].max())) - int(np.floor(bounds["minx"].min()))) / res)
        y_res = int((int(np.ceil(bounds["maxy"].max())) - int(np.floor(bounds["miny"].min()))) / res)

        return cls(georef=georef, x_res=x_res, y_res=y_res, projection=projection)

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

    # TODO deprecated. Remove in future release.
    @property
    def bounds_dl(self):
        """Lizard v3 bounds"""
        raise Exception("use .bbox instead. lizard v4 api no longer supports bounds_dl")
        return {
            "west": self.x_min,
            "south": self.y_min,
            "east": self.x_max,
            "north": self.y_max,
        }

    @property
    def bbox(self):
        """Lizard v4 bbox; str(x1, y1, x2, y2)"""
        return f"{self.x_min}, {self.y_min}, {self.x_max}, {self.y_max}"

    @property
    def bbox_gdal(self):
        """Gdal takes bbox as list, for instance in vrt creation."""
        return [self.x_min, self.y_min, self.x_max, self.y_max]

    @property
    def shape(self):
        return [self.y_res, self.x_res]

    @property
    def pixelarea(self):
        return abs(self.georef[1] * self.georef[5])

    def _update_georef(self, resolution: float):
        """Update georef with new resolution"""

        def res_str(georef_i):
            """Make sure negative values are kept."""
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
            self.x_res = int((resolution_current / resolution_new) * self.x_res)
            self.y_res = int((resolution_current / resolution_new) * self.y_res)
            self.georef = self._update_georef(resolution_new)
            print(f"updated metadata resolution from {resolution_current}m to {resolution_new}m")
        else:
            raise Exception(
                f"New resolution ({resolution_new}) can currently only be smaller than old resolution ({resolution_current})"
            )

    def __repr__(self):
        repr_str = f"""functions: {get_functions(self)}
variables: {get_variables(self)}"""

        return f""".projection : {self.projection} 
.georef : {self.georef}
.bounds : {self.bounds}
.pixel_width : {self.pixel_width}
----
{repr_str}"""

    def __getitem__(self, item):
        """Metadata was a dict previously. This makes it that items from
        the class can be accessed like a dict.
        """
        return getattr(self, item)
