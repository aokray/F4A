import os
import numpy as np
from utilities.dbUtils import connect
from utilities.make_plots import make_plots
from typing import Dict


def check_graphs_exist(dataset_shortname: str) -> bool:
    dir_name = "static/" + dataset_shortname
    if os.path.isdir(dir_name):
        return len(os.listdir(dir_name)) > 0
    else:
        return False


def on_startup() -> None:
    all_data_shortnames = connect("SELECT dataset_shortname FROM datasets;")

    for d in all_data_shortnames:
        if not check_graphs_exist(d[0]):
            all = connect(
                "SELECT dataset_path, dataset_featnames, dataset_upvals, dataset_sensidx, dataset_sensnames, dataset_shortname FROM datasets WHERE dataset_shortname = '"
                + d[0]
                + "'"
            )[0]

            path = all[0]
            featnames = all[1]
            featnames = [x.strip() for x in featnames.split(",")]
            upvals = all[2]
            sensidx = all[3]
            sensnames = all[4]
            shortname = all[5]

            data = np.loadtxt(path, delimiter=",")
            sample = data[:, 0:-1]

            sens_attr = [x.strip() for x in sensnames.split(",")]
            if not os.path.exists(os.path.join("static/", shortname)):
                os.makedirs(os.path.join("static/", shortname))

            make_plots(
                sample,
                shortname,
                featnames,
                sensidx - 1,
                upvals[1],
                upvals[0],
                sens_attr[1],
                sens_attr[0],
            )


def parse_webtexts(select_str: str) -> Dict:
    ret_dict = {}
    for row in select_str:
        ret_dict[row[0]] = row[1]

    return ret_dict
