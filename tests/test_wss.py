
# %%

if __name__ == "__main__":
    import set_local_paths  # add local git repos.

from pathlib import Path
import importlib.resources as pkg_resources  # Load resource from package

import hhnk_research_tools as hrt


print(hrt.__file__)
from hhnk_research_tools.waterschadeschatter import wss_main
from tests.config import TEST_DIRECTORY

def test_wss():
        
        with pkg_resources.path(hrt.waterschadeschatter.resources, "cfg_lizard.cfg") as p:
            cfg_file = p.absolute().as_posix()
    
        landuse_file = TEST_DIRECTORY/'landuse_test.tif'
        depth_file = TEST_DIRECTORY/'depth_test.tif'
        output_file = hrt.Raster(TEST_DIRECTORY/r'output/schade_test.tif')


        wss_settings = {'inundation_period': 48, #uren
                        'herstelperiode':'10 dagen',
                        'maand':'sep',
                        'cfg_file':cfg_file,
                        'dmg_type':'gem'}
        
        # out_format = ["sum", "direct", "indirect"] 

        #Calculation
        self = wss_main.Waterschadeschatter(depth_file=depth_file, 
                                landuse_file=landuse_file, 
                                wss_settings=wss_settings,
                                )

        # Berkenen schaderaster
        self.run(output_raster=hrt.Raster(output_file), 
            calculation_type="sum", 
            verbose=True, 
            overwrite=False,
            )
        
        assert output_file.pl.exists()
        assert output_file.statistics() == {'min': 3.6e-05, 'max': 88.486397, 'mean': 19.272263, 'std': 31.117453}

        
# %%
if __name__ == "__main__":
    test_wss()
# %%
