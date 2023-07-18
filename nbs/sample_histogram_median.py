import numpy as np
import hhnk_research_tools as hrt

polder_raster : hrt.Raster
dem : hrt.Raster

blocks_df = polder_raster.generate_blocks()


hist = {}
for idx, block_row in blocks_df.iterrows():

    block_arr = dem._read_array(window=window_big)
    block_arr[nodatamask] = 0


    val, count = np.unique(block_arr, return_counts=True)
    for v,c in zip(val, count):
        if v not in hist.keys():
            hist[v] = c
        else:
            hist[v] += c
    else:
        hist = False

hrt.hist_stats(histogram=hist, 
               stat_type="median",
               ignore_keys=[0])