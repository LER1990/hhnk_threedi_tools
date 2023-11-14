# %%
import geopandas as gpd
import numpy as np
import pytest

import hhnk_research_tools as hrt
from tests_hrt.config import TEMP_DIR, TEST_DIRECTORY


class TestRasterFunctions:
    @pytest.fixture(scope="class")
    def gdf(self):
        gdf = gpd.read_file(TEST_DIRECTORY / r"area_test.gpkg")
        return gdf

    @pytest.fixture(scope="class")
    def metadata(self, gdf):
        meta = hrt.create_meta_from_gdf(gdf=gdf, res=40)
        return meta

    def test_meta(self, metadata):
        assert metadata.bounds == [133613, 133693, 500677, 500757]

    def test_gdf_to_raster_and_reproject(self, gdf, metadata):
        output_raster = hrt.Raster(TEMP_DIR / f"gdf_to_raster_{hrt.get_uuid()}.tif")
        # gdf_to_raster
        arr = hrt.gdf_to_raster(
            gdf=gdf, value_field="id", raster_out=output_raster.path, nodata=-9999, metadata=metadata, read_array=True
        )

        assert arr.shape == (2, 2)

        # reproject
        output_raster_reproject = hrt.Raster(output_raster.path.with_stem(f"reproject_{hrt.get_uuid()}"))
        hrt.reproject(src=output_raster, target_res=20, output_path=output_raster_reproject.path)
        assert output_raster_reproject.metadata.pixel_width == 20

    def test_gdf_to_raster_mem(self, gdf, metadata):
        arr = hrt.gdf_to_raster(
            gdf=gdf, value_field="id", raster_out="", nodata=-9999, metadata=metadata, driver="MEM", read_array=True
        )
        assert arr.shape == (2, 2)

    def test_save_raster_array_to_tiff_vrt(self, metadata):
        output_folder = hrt.Folder(TEMP_DIR / f"vrt_test", create=True)
        output_file = output_folder.full_path(f"save_raster_array_to_tiff_{hrt.get_uuid()}.tif")
        arr = np.array([[1, 2], [2, 3]])
        hrt.save_raster_array_to_tiff(
            output_file=output_file,
            raster_array=arr,
            nodata=-9999,
            metadata=metadata,
            create_options=None,
            num_bands=1,
            overwrite=False,
        )
        assert output_file.exists()

        # Test vrt
        vrt_name = f"vrt_test_{hrt.get_uuid()}"
        vrt_path = output_folder.full_path(f"{vrt_name}.vrt")
        hrt.build_vrt(output_folder.path, vrt_name=vrt_name)

        assert vrt_path.exists()


def test_raster_calculator():
    raster_depth = hrt.Raster(TEST_DIRECTORY / r"depth_test.tif")
    raster_lu = hrt.Raster(TEST_DIRECTORY / r"landuse_test.tif")
    raster_out = hrt.Raster(TEMP_DIR / f"rastercalc_{hrt.get_uuid()}.tif")

    def run_window(block):
        block_out = block.blocks["lu"]

        # Nodatamasks toepassen
        block_out[block.masks_all] = 0
        return block_out

    calc = hrt.RasterCalculatorV2(
        raster_out=raster_out,
        raster_paths_dict={
            "depth": raster_depth,
            "lu": raster_lu,
        },
        nodata_keys=["lu"],
        mask_keys=["depth", "lu"],
        metadata_key="depth",
        custom_run_window_function=run_window,
        output_nodata=0,
        min_block_size=4096,
        verbose=True,
    )

    calc.run(overwrite=False)

    assert raster_out.sum() == 261581


if __name__ == "__main__":
    import inspect

    selftest = TestRasterFunctions()
    # self = selftest.raster
    self = selftest
    # Run all testfunctions

    # gdf = self.gdf()
    # metadata = self.metadata()
    # for i in dir(selftest):
    #     if i.startswith('test_') and hasattr(inspect.getattr_static(selftest,i), '__call__'):
    #         print(i)
    #         getattr(selftest, i)()

    test_raster_calculator()

# %%
