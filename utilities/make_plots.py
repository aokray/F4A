import numpy as np
import math
from matplotlib import rcParams
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from nptyping import NDArray
from typing import List

rcParams.update({"figure.autolayout": True})


def hellinger(p: NDArray, q: NDArray):
    # From https://nbviewer.jupyter.org/gist/Teagum/460a508cda99f9874e4ff828e1896862

    return math.sqrt(
        sum([(math.sqrt(p_i) - math.sqrt(q_i)) ** 2 for p_i, q_i in zip(p, q)]) / 2
    )


# This expects a dataset without the label
# Returns Hellinger Distance array
def make_plots(
    sample: NDArray,
    datasetName: str,
    feat_descs: List[str],
    sens_idx: int,
    p_value: int,
    u_value: int,
    p_label: int,
    u_label: int,
) -> None:
    # Protected indices
    p_idxs = np.where(sample[:, sens_idx] == p_value)[0]
    # Unprotected indices
    u_idxs = np.where(sample[:, sens_idx] == u_value)[0]

    # Collector array for the Hellinger distances
    hds = []
    scaler = MinMaxScaler()

    SMALL_SIZE = 14
    MEDIUM_SIZE = 24  # Title
    BIGGER_SIZE = 0

    plt.rc("font", size=SMALL_SIZE)  # controls default text sizes
    plt.rc("axes", titlesize=MEDIUM_SIZE)  # fontsize of the axes title
    plt.rc("axes", labelsize=MEDIUM_SIZE)  # fontsize of the x and y labels
    plt.rc("xtick", labelsize=MEDIUM_SIZE)  # fontsize of the tick labels
    plt.rc("ytick", labelsize=SMALL_SIZE)  # fontsize of the tick labels
    plt.rc("legend", fontsize=SMALL_SIZE)  # legend fontsize

    for i in np.arange(sample.shape[1]):
        scaled_samp = scaler.fit_transform(sample[:, i].reshape(-1, 1))
        feat_desc = feat_descs[i]
        # Density overlap plot. Commented out in preference for histograms
        # ax = sns.distplot(scaled_samp[u_idxs], hist=False, color='black', label=u_label)
        # ax = sns.distplot(scaled_samp[p_idxs], hist=False, color='b', label=p_label)

        # l1 = ax.lines[0]
        # l2 = ax.lines[1]

        # x1 = l1.get_xydata()[:,0]
        # y1 = l1.get_xydata()[:,1]
        # x2 = l2.get_xydata()[:,0]
        # y2 = l2.get_xydata()[:,1]

        # if x1 != [] and y1 != [] and x2 != [] and y2 != []:
        #     xmin = max(x1.min(), x2.min())
        #     xmax = min(x1.max(), x2.max())
        #     x = np.linspace(xmin, xmax, 100)
        #     y1 = np.interp(x, x1, y1)
        #     y2 = np.interp(x, x2, y2)
        #     y = np.minimum(y1, y2)

        #     # Fill the gap in the distributions' overlap
        #     ax.fill_between(x, y, color="green", alpha=0.3, hatch='/')
        fig, ax = plt.subplots()

        u_counts, bins = np.histogram(scaled_samp[u_idxs], np.linspace(0, 1, 50))
        p_counts, _ = np.histogram(scaled_samp[p_idxs], np.linspace(0, 1, 50))

        if i == 1:
            print(u_counts)
            print(p_counts)

        u = u_counts / len(scaled_samp[u_idxs])
        p = p_counts / len(scaled_samp[p_idxs])

        ax.hist(
            bins[:-1],
            bins,
            weights=u,
            label=u_label,
            edgecolor="black",
            ls="dashed",
            lw=0.5,
            fc=(1, 0, 0, 0.2),
        )
        ax.hist(
            bins[:-1],
            bins,
            weights=p,
            label=p_label,
            edgecolor="black",
            ls="dotted",
            lw=0.5,
            fc=(0, 0, 1, 0.2),
        )

        # hds.append(hellinger(u,p))

        plt.title("")
        plt.xlabel(feat_desc, fontsize=SMALL_SIZE + 2)
        plt.ylabel("Density", fontsize=SMALL_SIZE + 2)
        plt.xticks(fontsize=SMALL_SIZE)
        plt.yticks(fontsize=SMALL_SIZE)
        plt.xlim(-0.1, 1.1)

        plt.legend([u_label, p_label])

        plt.savefig(
            "static/" + str(datasetName) + "/" + str(datasetName) + str(i) + ".png",
            dpi=1000,
        )
        ax.clear()
        plt.clf()
        ax = None

    # return hds


# sample = np.loadtxt('../datasets/creditcarddefault.csv', delimiter=',')
# make_plots(sample, 'creditdefault', 'Amount of credit given, Gender, Education, Marital Status, Age, September 2005 Repayment status, August 2005 Repayment status, July 2005 Repayment status, June 2005 Repayment status, May 2005 Repayment status, April 2005 Repayment status, September 2005 Bill amount, August 2005 Bill amount, July 2005 Bill amount, June 2005 Bill amount, May 2005 Bill amount, April 2005 Bill amount, Amount Paid in September 2005, Amount Paid in August 2005, Amount Paid in July 2005, Amount Paid in June 2005, Amount Paid in May 2005, Amount Paid in April 2005'.split(','),
#             1, 1, 2, 'Female', 'Male'
#         )
