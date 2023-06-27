# %%  
from pathlib import Path
import shutil
import hhnk_research_tools as hrt

TEST_DIRECTORY = Path(__file__).parent.absolute() / "data"



# TEMP_DIR = TEST_DIRECTORY/r"temp"
# if TEMP_DIR.exists():
#     shutil.rmtree(TEMP_DIR)
TEMP_DIR = hrt.Folder(TEST_DIRECTORY/r"temp", create=True)

TEMP_DIR.unlink_contents()
TEMP_DIR = TEMP_DIR.path
for i in TEMP_DIR.iterdir():
    if i.is_dir:
        if "batch_test" in str(i):
            cont=True
        if "test_project_" in str(i):
            cont=True

        if cont:
            try:
                shutil.rmtree(i)
            except:
                pass
