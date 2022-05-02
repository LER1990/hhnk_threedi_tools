# -*- coding: utf-8 -*-
"""
Created on Mon May  2 15:07:15 2022

@author: chris.kerklaan
"""
import xarray
NC_LAYERS = [
    "Mesh2D_vol",
    "Mesh2D_ucy",
    "Mesh2D_ucy",
    "Mesh2D_ucx",
    "Mesh2D_u1",
    "Mesh2D_su",
    "Mesh2D_s1",
    "Mesh2D_rain",
    "Mesh2D_q_sss",
    "Mesh2D_q_lat",
    "Mesh2D_q_",
    "Mesh2D_au",
    "Mesh2DCountour_y",
    "Mesh2DCountour_x",
    "Mesh1D_vol",
    "Mesh1D_su",
    "Mesh1D_s1",
    "Mesh1D_rain",
    "Mesh1D_q_pump",
    "Mesh1D_q_lat",
    "Mesh1D_q",
    "Mesh1D_breach_width",
    "Mesh1D_breach_depth",
    "Mesh1D_au",
    ]
CONVERT = {
    "volume_2d": "Mesh2D_vol",
    "waterlevel_2d": "Mesh2D_s1",
    "volume_1d": "Mesh1D_vol",
    "waterlevel_1d": "Mesh1D_s1"
    }



class GridEdit:
    """ edit the netcdf file based on ids of the grid"""
    
    def __init__(self, result_3di_path):
        self.ds = xarray.load_dataset(result_3di_path)
    
    def set_value(self, table, timestep, node_id, value):
        """ Sets a value for a node id in a certain table
            params:
                table: Can be volume_2d, waterlevel_2d, volume_1d, waterlevel_1d
        """
        self.ds[CONVERT[table]][timestep][node_id] = value
        
    def set_timeseries(self, table, node_id, values):
        """ sets complete timeseries for a single node_id"""
        self.ds[CONVERT[table]][:,node_id] = values 
        
        
    # def set_values(self, table, timestep, values):
    #     """ Set all nodes for a certain timestep"""
        
    #     self.df[CONVERT[table]][timestep][node_id] = value
        
    def write(self, path):
        self.ds.to_netcdf(path)
        