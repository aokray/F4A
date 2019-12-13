import numpy as np
from matplotlib import rcParams
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

rcParams.update({'figure.autolayout': True})

# This expects a dataset without the label
def make_plots(sample, datasetName, feat_descs, sens_idx, p_value, u_value, p_label, u_label):
    # Protected indexes
    p_idxs = np.where(sample[:,sens_idx] == p_value)[0]
    # Unprotected indexes
    u_idxs = np.where(sample[:,sens_idx] == u_value)[0]

    SMALL_SIZE = 14
    MEDIUM_SIZE = 24 # Title
    BIGGER_SIZE = 0

    plt.rc('font', size=SMALL_SIZE)          # controls default text sizes
    plt.rc('axes', titlesize=MEDIUM_SIZE)     # fontsize of the axes title
    plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=MEDIUM_SIZE)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
    plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize

    for i in range(sample.shape[1]):
        feat_desc = feat_descs[i]
        ax = sns.distplot(sample[:,i][u_idxs], hist=False, color='black', label=u_label)
        ax = sns.distplot(sample[:,i][p_idxs], hist=False, color='b', label=p_label)

        l1 = ax.lines[0]
        l2 = ax.lines[1]

        x1 = l1.get_xydata()[:,0]
        y1 = l1.get_xydata()[:,1]
        x2 = l2.get_xydata()[:,0]
        y2 = l2.get_xydata()[:,1]


        xmin = max(x1.min(), x2.min())
        xmax = min(x1.max(), x2.max())
        x = np.linspace(xmin, xmax, 100)
        y1 = np.interp(x, x1, y1)
        y2 = np.interp(x, x2, y2)
        y = np.minimum(y1, y2)

        # Fill the gap in the distributions' overlap
        ax.fill_between(x, y, color="green", alpha=0.3, hatch='/')

        plt.title("")
        plt.xlabel(feat_desc, fontsize=SMALL_SIZE+2)
        plt.ylabel('Density', fontsize=SMALL_SIZE+2)
        plt.xticks(fontsize=SMALL_SIZE)
        plt.yticks(fontsize=SMALL_SIZE)

        plt.legend(handles=[l1, l2])

        plt.savefig('static/' + str(datasetName) +  '/' + str(datasetName) + str(i) + '.png', figsize=(19.2, 10.8), dpi=1000)
        ax.clear()
        plt.clf()
