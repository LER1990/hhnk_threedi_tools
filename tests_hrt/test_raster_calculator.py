# %%
import hhnk_research_tools as hrt
from tests_hrt.config import TEMP_DIR, TEST_DIRECTORY


def test_raster_blocks():
    """Test raster block loading"""
    raster = hrt.Raster(TEST_DIRECTORY / r"depth_test.tif")

    for idx, block_row in raster.generate_blocks().iterrows():
        break

    block = hrt.RasterBlocks(
        window=block_row["window_readarray"],
        raster_paths_dict={
            "raster1": raster,
            "raster2": raster,
        },
        nodata_keys=["raster1"],
        mask_keys=["raster2"],
    )

    assert block.cont is True
    assert block.masks_all.shape == (160, 160)

    block.blocks["raster1"][block.masks_all] = 0
    assert int(block.blocks["raster1"].sum()) == 1826


def test_raster_calculator():
    """Test raster calculator"""
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


# %%
if __name__ == "__main__":
    test_raster_blocks()
    test_raster_calculator()
