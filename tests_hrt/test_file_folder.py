# %%
# if __name__ == "__main__":
#     import set_local_paths  # add local git repos.

from pathlib import Path
import hhnk_research_tools.folder_file_classes.file_class as fcl

import importlib
importlib.reload(fcl)
import hhnk_research_tools as hrt

if __name__ == "__main__": #check if python is configed correctly
    print(hrt.__file__)
from tests_hrt.config import TEMP_DIR



# def test_file():
    
file_path = TEMP_DIR/f"test_{hrt.get_uuid()}.txt"


with open(file_path,"w") as f:

    f.write("test")


file = fcl.File(file_path)
file = fcl.File("")

file.exists()
# %%
