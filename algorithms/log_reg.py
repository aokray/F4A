from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import MinMaxScaler
import numpy as np

scaler = MinMaxScaler()

# hyperp can later be expanded to **kwargs
def testLR(data_path, idxs_path, feats, hyperp, sens_idx, u_value, p_value):
    data = np.loadtxt(data_path, delimiter=',')
    idxs = np.loadtxt(idxs_path, delimiter=',')
    idxs = idxs - 1
    idxs = idxs.astype(int)

    # Get a subset of idxs
    train_idxs = idxs[0:5]
    all_idxs = np.arange(data.shape[0])
    accs = []
    sds = []
    u_ups = []
    u_downs = []
    p_ups = []
    p_downs = []

    sample = data[:,0:-1]
    all_feat_idxs = np.arange(sample.shape[1])
    sample[:,np.setdiff1d(all_feat_idxs, sens_idx)] = scaler.fit_transform(sample[:,np.setdiff1d(all_feat_idxs, sens_idx)])
    label = data[:,-1]

    for idx_row in train_idxs:
        idx_row_test = np.setdiff1d(all_idxs, idx_row)
        sample_train = sample[idx_row]
        sample_test = sample[idx_row_test]

        label_train = label[idx_row]
        label_test = label[idx_row_test]

        if feats != None:
            sample_train = sample_train[:,feats]
            sample_test = sample_test[:,feats]

        lr = LogisticRegression(max_iter = 1000, **hyperp)
        lr.fit(sample_train, label_train)
        preds = lr.predict(sample_test)

        u_test_idxs = np.where(sample[idx_row_test,sens_idx] == u_value)[0]
        p_test_idxs = np.where(sample[idx_row_test,sens_idx] == p_value)[0]

        acc = accuracy_score(label_test, preds)
        sd = np.abs(np.average(preds[p_test_idxs]) - np.average(preds[u_test_idxs]))
        
        # Get the number of unprotected classes predicted as the up/down class and the same for the protected class
        U_up = int(np.sum(preds[u_test_idxs] == 1))
        U_down = int(np.sum(preds[u_test_idxs] == 0))
        P_up = int(np.sum(preds[p_test_idxs] == 1))
        P_down = int(np.sum(preds[p_test_idxs] == 0))

        accs.append(acc)
        sds.append(sd)
        u_ups.append(U_up)
        u_downs.append(U_down)
        p_ups.append(P_up)
        p_downs.append(P_down)

    return (acc, sd, np.average(u_ups), np.average(u_downs), np.average(p_ups), np.average(p_downs))
