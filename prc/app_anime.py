'''
Created on 02.07.2019

@author: Mou Lin (moulin1024@gmail.com)

--------------------------------------------------------------------------------
app: create self-explained hdf5 output file
--------------------------------------------------------------------------------
'''

################################################################################
# IMPORT
################################################################################
import os, sys

from matplotlib import projections
import matplotlib.transforms as transforms
import fctlib
import app_post as post
import numpy as np
import h5py
import matplotlib.pyplot as plt
import matplotlib
from mpl_toolkits.axes_grid1 import make_axes_locatable
import h5py
import os.path
import math
import pandas as pd
from pathlib import Path
from matplotlib.pyplot import figure
from matplotlib import animation, rc
from mpl_toolkits.mplot3d import Axes3D
# import fatigue
# from skimage.measure import marching_cubes
import matplotlib.pyplot as plt
# from mpl_toolkits.mplot3d import Axes3D
# import cv2
# from pyevtk.hl import gridToVTK


################################################################################
# MAIN FONCTION
################################################################################
def anime(PATH, case_name):
    '''
    DEF:    post-processing for wireles.
    INPUT:  - case_name
    OUTPUT: - Statistics field: stat.h5
            - Instantanous field: animation.h5 
    '''
    case_path = fctlib.get_case_path(PATH, case_name)

    ############################################################################
    # INIT
    out_path = os.path.join(case_path, 'output')
    in_path = os.path.join(case_path, 'input')
    fctlib.test_and_mkdir(out_path)
    src_out_path = os.path.join(PATH['job'], case_name, 'src', 'output')
    src_inp_path = os.path.join(PATH['job'], case_name, 'src', 'input')

    ############################################################################
    # CONFIG
    print('extract config...')
    config = fctlib.get_config(case_path)

    ############################################################################
    # COMPUTE
    print('compute results...')
    print('Flow Fields:')
    print('Flow Fields:')

    space = post.get_space(config)
    time = post.get_time(config)

    if config['ta_flag'] > 0:
        result_3d = post.get_result_3d(src_inp_path,src_out_path, config)
        u_avg = result_3d['u_avg_c']
        v_avg = result_3d['v_avg_c']
        w_avg = result_3d['w_avg_c']

        u_std = result_3d['u_std_c']
        v_std = result_3d['v_std_c']
        w_std = result_3d['w_std_c']

        f = h5py.File(out_path+'/'+case_name+'_stat.h5','w')
        for key, value in config.items():
            f.attrs[key] = value

        f.create_dataset('x',data=space['x'])
        f.create_dataset('y',data=space['y'])
        f.create_dataset('z',data=space['z_c'])

        f.create_dataset('u_avg',data=u_avg )
        f.create_dataset('v_avg',data=v_avg)
        f.create_dataset('w_avg',data=w_avg)

        f.create_dataset('u_std',data=u_std)
        f.create_dataset('v_std',data=v_std)
        f.create_dataset('w_std',data=w_std)

        f.close

        mean_u = np.mean(np.mean(u_avg,axis=0),axis=0)
        print(mean_u[6])
        u_std = result_3d['u_std_c']
        
        mean_std = np.mean(np.mean(u_std,axis=0),axis=0)
        
        print(mean_std[6]/mean_u[6])


    if config['ts_flag'] > 0:

    
        f = h5py.File(out_path+'/'+case_name+'_flowfield.h5','w')

        t_count = (config['nsteps']-config['ts_tstart'])//100
        velo_data = np.zeros([t_count,config['nx'],config['ny'],3])
        for i in range(t_count):
            u = fctlib.load_3d(str(i).zfill(3)+'_ts_u', config['nx'],  config['ny'],  config['nz'], config['double_flag'], src_out_path)[:,:,:-1]
            v = fctlib.load_3d(str(i).zfill(3)+'_ts_v', config['nx'],  config['ny'],  config['nz'], config['double_flag'], src_out_path)[:,:,:-1]
            w = fctlib.load_3d(str(i).zfill(3)+'_ts_w', config['nx'],  config['ny'],  config['nz'], config['double_flag'], src_out_path)[:,:,:-1]

            fig = figure(figsize=(8,6),dpi=100)
            grid_ratio = (config['lz']/(config['nz']-1))/(config['lx']/config['nx'])
            print(i)
            plt.imshow(u[config['nx']//2,:,:].T,origin='lower',aspect=grid_ratio)
            plt.colorbar()
            plt.savefig(out_path+'/'+str(i).zfill(3)+'_flowfield_xz.png')
            plt.close()


            fig = figure(figsize=(8,6),dpi=100)
            grid_ratio = (config['lz']/(config['nz']-1))/(config['ly']/config['ny'])
            print(i)
            plt.imshow(u[:,config['ny']//2,:].T,origin='lower',aspect=grid_ratio)
            plt.colorbar()
            plt.savefig(out_path+'/'+str(i).zfill(3)+'_flowfield_yz.png')
            plt.close()
        

    if config['turb_flag'] > 0:
        turb_loc = pd.read_csv(case_path+"/input/turb_loc.dat")
        f = h5py.File(out_path+'/'+case_name+'_force.h5','w')
        for key, value in config.items():
            f.attrs[key] = value
        
        turb_force = post.get_turb(src_out_path, config)
        f.create_dataset('time',data=time['t'])
        f.create_dataset('fx',data=turb_force['fx'][:,:,:,:])
        f.create_dataset('ft',data=turb_force['ft'][:,:,:,:])
        f.create_dataset('moment_flap',data=turb_force['moment_flap'])
        f.create_dataset('moment_edge',data=turb_force['moment_edge'])
        f.create_dataset('phase',data=turb_force['phase'])
        f.create_dataset('inflow',data=turb_force['inflow'])

        f.close
        fig = figure(figsize=(12,4),dpi=300)
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)
        
        ax1.plot(turb_force['moment_flap'][:,0,0,0])
        ax2.plot(turb_force['inflow'][:,0,0,0])
        plt.savefig(out_path+'/force-inflow-time-series.png')