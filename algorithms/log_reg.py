from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import numpy as np

# hyperp can later be expanded to **kwargs
def testLR(data_path, idxs_path, feats, hyperp, sens_idx, u_value, p_value):
    data = np.loadtxt(data_path, delimiter=',')

    sample = data[:,0:-1]
    label = data[:,-1]

    sample_train = sample[:int(0.75 * sample.shape[0])+1]
    sample_test = sample[int(0.25 * sample.shape[0]):]

    label_train = label[:int(0.75 * sample.shape[0])+1]
    label_test = label[int(0.25 * sample.shape[0]):]

    if (feats != None):
        sample = sample[:,feats]

    lr = LogisticRegression(C=hyperp)
    lr.fit(sample_train, label_train)
    preds = lr.predict(sample_test)

    u_test_idxs = np.where(sample_test[:,sens_idx] == u_value)[0]
    p_test_idxs = np.where(sample_test[:,sens_idx] == p_value)[0]

    acc = accuracy_score(label_test, preds)
    sd = np.abs(np.average(preds[p_test_idxs]) - np.average(preds[u_test_idxs]))
    
    # Get the number of unprotected classes predicted as the up/down class and the same for the protected class
    U_up = int(np.sum(label_test[u_test_idxs] == 1))
    U_down = int(np.sum(label_test[u_test_idxs] == 0))
    P_up = int(np.sum(label_test[p_test_idxs] == 1))
    P_down = int(np.sum(label_test[p_test_idxs] == 0))

    return (acc, sd, U_up, U_down, P_up, P_down)
