
# %%

if __name__ == "__main__":
    import set_local_paths  # add local git repos.

from pathlib import Path
import numpy as np

import geopandas as gpd
import hhnk_research_tools as hrt
from tests_hrt.config import TEST_DIRECTORY, TEMP_DIR

# %%
class TestRasterFunctions():

    gdf = gpd.read_file(TEST_DIRECTORY/r"area_test.gpkg")
    meta=hrt.create_meta_from_gdf(gdf=gdf, res=40)


    def test_gdf_to_raster_and_reproject(self):
        output_raster = hrt.Raster(TEMP_DIR/f"gdf_to_raster_{hrt.get_uuid()}.tif")
        #gdf_to_raster
        arr = hrt.gdf_to_raster(gdf=self.gdf,
                          value_field="id",
                          raster_out=output_raster.path,
                          nodata=-9999,
                          metadata=self.meta,
                          read_array=True)

        assert arr.shape == (2, 2)

        #reproject
        output_raster_reproject = hrt.Raster(output_raster.path.with_stem(f"reproject_{hrt.get_uuid()}"))
        hrt.reproject(src=output_raster,
                      target_res=20,
                      output_path=output_raster_reproject.path)
        assert output_raster_reproject.metadata.pixel_width == 20


    def test_gdf_to_raster_mem(self):
        arr = hrt.gdf_to_raster(gdf=self.gdf,
                          value_field="id",
                          raster_out="",
                          nodata=-9999,
                          metadata=self.meta,
                          driver="MEM",
                          read_array=True)
        assert arr.shape == (2, 2)


    def test_save_raster_array_to_tiff_vrt(self):
        output_folder = hrt.Folder(TEMP_DIR/f"vrt_test", create=True)
        output_file = output_folder.full_path(f"save_raster_array_to_tiff_{hrt.get_uuid()}.tif")
        arr = np.array([[1,2],[2,3]])
        hrt.save_raster_array_to_tiff(output_file = output_file,
                                        raster_array=arr,
                                        nodata=-9999,
                                        metadata=self.meta,
                                        create_options=None,
                                        num_bands=1,
                                        overwrite=False,)
        assert output_file.exists()

        #Test vrt
        vrt_name = f"vrt_test_{hrt.get_uuid()}"
        vrt_path = output_folder.full_path(f"{vrt_name}.vrt")
        hrt.build_vrt(output_folder.path, vrt_name=vrt_name)

        assert vrt_path.exists()



if __name__ == "__main__":
    import inspect
    selftest = TestRasterFunctions()
    # self = selftest.raster
    self=selftest
    # Run all testfunctions
    for i in dir(selftest):
        if i.startswith('test_') and hasattr(inspect.getattr_static(selftest,i), '__call__'):
            print(i)
            getattr(selftest, i)()  

# %%
