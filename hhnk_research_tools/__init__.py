import hhnk_research_tools.variables as variables

from hhnk_research_tools.folder_file_classes.file_class import File

from hhnk_research_tools.gis.raster import Raster, RasterMetadata

import hhnk_research_tools.threedi as threedi

from hhnk_research_tools.threedi.read_api_file import (
    read_api_file
) 

from hhnk_research_tools.waterschadeschatter.wss_main import Waterschadeschatter

import hhnk_research_tools.waterschadeschatter.resources

from hhnk_research_tools.sql_functions import (
    sql_create_update_case_statement,
    sql_construct_select_query,
    create_sqlite_connection,
    sql_table_exists,
    execute_sql_selection,
    execute_sql_changes,
    sqlite_replace_or_add_table,
    sqlite_table_to_df,
    sqlite_table_to_gdf,
)

from hhnk_research_tools.dataframe_functions import (
    df_convert_to_gdf,
    df_add_geometry_to_gdf,
    gdf_write_to_geopackage,
    gdf_write_to_csv,
)

from hhnk_research_tools.general_functions import (
    ensure_file_path,
    convert_gdb_to_gpkg,
    check_create_new_file,
    load_source,
    get_uuid,
    get_pkg_resource_path,
)

from hhnk_research_tools.raster_functions import (
    load_gdal_raster,
    gdf_to_raster,
    create_new_raster_file,
    save_raster_array_to_tiff,
    build_vrt,
    create_meta_from_gdf,
    dx_dy_between_rasters,
    RasterCalculator,
    reproject,
)


from hhnk_research_tools.folder_file_classes.folder_file_classes import (
    Folder,
    FileGDB,
    FileGDBLayer,
)
from hhnk_research_tools.folder_file_classes.sqlite_class import (
    Sqlite,
)

from hhnk_research_tools.folder_file_classes.threedi_schematisation import (
    ThreediSchematisation,
    ThreediResult,
    RevisionsDir,
)

# TODO how does this versioning work?
# Threedigrid version number is automatic updated with zest.releaser. Geopandas uses versioneer.py.
# the version number in setup.py is updated using the find_version()
__version__ = '2023.2'

__doc__ = """
General toolbox for loading, converting and saving serval datatypes.
"""
