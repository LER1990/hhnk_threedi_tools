# %%
import hhnk_research_tools as hrt
from tests_hrt.config import TEST_DIRECTORY

    
def test_raster_blocks():
    raster = hrt.Raster(TEST_DIRECTORY/r"depth_test.tif")


    for idx, block_row in raster.generate_blocks().iterrows():
        break

    block = hrt.RasterBlocks(window=block_row['window_readarray'],
                       raster_paths_dict={
                                "raster1" : raster,
                                "raster2" : raster,},
                       nodata_keys=["raster1"],
                       mask_keys=["raster2"],
                       )


    assert block.cont == True
    assert block.masks_all.shape == (160,160)

    block.blocks['raster1'][block.masks_all] = 0
    assert block.blocks['raster1'].sum() == 1826.1478


if __name__ == "__main__":
    test_raster_blocks()
