from pathlib import Path
import hhnk_research_tools as hrt


TEST_DIRECTORY = Path(__file__).parent.absolute() / "data"

OUTPUT_FOLDER = hrt.Folder(TEST_DIRECTORY/r"output", create=True)
OUTPUT_DIR = OUTPUT_FOLDER.pl
