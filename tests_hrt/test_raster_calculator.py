# %%
import pytest

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
    raster_small = hrt.Raster(TEST_DIRECTORY / r"lu_small.tif")
    raster_out = hrt.Raster(TEMP_DIR / f"rastercalc_{hrt.get_uuid()}.tif")

    def run_window(block):
        block_out = block.blocks["small_raster"]

        # Nodatamasks toepassen
        block_out[block.masks_all] = 0
        return block_out

    # Check error in nodata_keys and yesdata_dict
    with pytest.raises(UnboundLocalError):
        calc = hrt.RasterCalculatorV2(
            raster_out=raster_out,
            raster_paths_dict={
                "depth": raster_depth,
                "small_raster": raster_small,
            },
            nodata_keys=["depth"],
            mask_keys=["depth", "small_raster"],
            metadata_key="depth",
            custom_run_window_function=run_window,
            yesdata_dict={"depth": [-99]},
            output_nodata=0,
            min_block_size=4096,
            verbose=True,
            tempdir=hrt.Folder(TEMP_DIR / "temprasters"),
        )

        calc.run(overwrite=False)

    # Working calculator
    calc = hrt.RasterCalculatorV2(
        raster_out=raster_out,
        raster_paths_dict={
            "depth": raster_depth,
            "small_raster": raster_small,
        },
        nodata_keys=["depth"],
        mask_keys=["depth", "small_raster"],
        metadata_key="depth",
        custom_run_window_function=run_window,
        yesdata_dict={"small_raster": [-99]},
        output_nodata=0,
        min_block_size=4096,
        verbose=True,
        tempdir=hrt.Folder(TEMP_DIR / "temprasters"),
    )

    calc.run(overwrite=False)

    assert raster_out.sum() == 70914


# %%
if __name__ == "__main__":
    test_raster_blocks()
    test_raster_calculator()

# %%
self = calc
self.raster_out = hrt.Raster(TEMP_DIR / f"rastercalc_{hrt.get_uuid()}.tif")
from hhnk_research_tools.gis.raster_calculator import RasterBlocks

overwrite = True
kwargs = {}
import datetime

if True:
    try:
        cont = self.verify(overwrite=overwrite)
        if cont:
            self.create()

        if cont:
            if self.verbose:
                time_start = datetime.datetime.now()

            # Create blocks dataframe
            self.metadata_raster.min_block_size = self.min_block_size
            self.blocks_df = self.metadata_raster.generate_blocks()
            blocks_total = len(self.blocks_df)

            # Open output raster for writing
            gdal_src = self.raster_out.open_gdal_source_write()
            band_out = gdal_src.GetRasterBand(1)

            # Loop over generated blocks and do calculation per block
            for idx, block_row in self.blocks_df.iterrows():
                window = block_row["window_readarray"]

                # Load the blocks for the given window.
                block = RasterBlocks(
                    window=window,
                    raster_paths_dict=self.raster_paths_same_bounds,
                    nodata_keys=self.nodata_keys,
                    yesdata_dict=self.yesdata_dict,
                    mask_keys=self.mask_keys,
                )

                # The blocks have an attribute that can prevent further calculation
                # if certain conditions are met. It is False when a raster in the
                # nodata keys has all value as nodata. Output should be nodata as well
                if block.cont:
                    # Calculate output raster block with custom function.
                    block_out = self.custom_run_window_function(block=block, **kwargs)

                    self.raster_out.write_array(array=block_out, window=window, band=band_out)

                    if self.verbose:
                        print(
                            f"{idx} / {blocks_total} ({hrt.time_delta(time_start)}s) - {self.raster_out.name}",
                            end="\r",
                        )

            # band_out.FlushCache()  # close file after writing, slow, needed?
            band_out = None
            if self.verbose:
                print("\nDone")
        else:
            if self.verbose:
                print(f"{self.raster_out.name} not created, .verify was false.")
    except Exception as e:
        band_out.FlushCache()
        band_out = None
        self.raster_out.unlink()
        raise e
