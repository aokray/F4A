import os
import numpy as np
from utilities.dbUtils import connect
from utilities.make_plots import make_plots

def check_graphs_exist(dataset_shortname):
    dir_name =  'static/' + dataset_shortname
    if os.path.isdir(dir_name):
        return len(os.listdir(dir_name)) > 0
    else:
        return False

def on_startup():
    all_data_shortnames = connect('SELECT dataset_shortname FROM datasets;')

    for d in all_data_shortnames:
        if (not check_graphs_exist(d[0])):
            all = connect('SELECT dataset_path, dataset_featnames, dataset_upvals, dataset_sensidx, dataset_sensnames, dataset_shortname FROM datasets WHERE dataset_shortname = \'' + d[0] +'\'')[0]
            
            path = all[0]
            featnames = all[1]
            upvals = all[2]
            sensidx = all[3]
            sensnames = all[4]
            shortname = all[5]

            data = np.loadtxt(path, delimiter=',')
            sample = data[:,0:-1]
            
            sens_attr = [x.strip() for x in sensnames.split(',')]
            os.makedirs('static/' + shortname)
            make_plots(sample, shortname, featnames, sensidx-1, upvals[1], upvals[0], sens_attr[1], sens_attr[0])