# %%

import hhnk_research_tools as hrt
from tests_hrt.config import TEMP_DIR, TEST_DIRECTORY


def test_create_landuse_polder_clip():
    dem = hrt.Raster(TEST_DIRECTORY / r"lu_small.tif")
    landuse_name = "test_small"
    output_dir = TEMP_DIR
    landuse_hhnk = hrt.Raster(TEST_DIRECTORY / r"landuse_test.tif")

    #Create the tiff
    landuse_tif, created = hrt.create_landuse_polder_clip(
        dem=dem, landuse_name=landuse_name, output_dir=output_dir, landuse_hhnk=landuse_hhnk, overwrite=True
    )

    assert landuse_tif.sum() == 73343
    assert created is True

    #Check if it doesnt overwrite
    landuse_tif, created = hrt.create_landuse_polder_clip(
        dem=dem, landuse_name=landuse_name, output_dir=output_dir, landuse_hhnk=landuse_hhnk, overwrite=False
    )

    assert created is False


# %%
if __name__ == "__main__":
    test_create_landuse_polder_clip()
