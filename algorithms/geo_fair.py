import numpy as np
from sklearn.base import TransformerMixin
from nptyping import NDArray
from scipy.linalg import orth

# Data is assumed to be centered and scaled (0,1)
class GeometricFairRepresentation(TransformerMixin):
    def __init__(self, sens_idxs: NDArray, lmbda: float = 0):
        self.sens_idxs = sens_idxs
        self.lmbda = lmbda

    def fit(self, X: NDArray, u_idxs: NDArray, p_idxs: NDArray):
        # Doing nothing for the fit function is 1/2 workaround, 1/2 because no projection matrix is needed,
        # each different dataset (eg training/testing) gets its own
        pass

    def transform(self, X: NDArray):
        # ints passed to this function are ok, just have to handle them a little differently
        if isinstance(self.sens_idxs, int):
            orth_vecs = orth(X[:,self.sens_idxs].reshape(-1,1))
        else:
            orth_vecs = orth(X[:,self.sens_idxs])
        
        P = np.zeros((orth_vecs.shape[0], orth_vecs.shape[0]))
        for i in range(orth_vecs.shape[1]):
            P += orth_vecs[:,i].reshape(-1,1) @ orth_vecs[:,i].reshape(1,-1)

        R = (np.eye(P.shape[0]) - P) @ X

        for j in range(R.shape[1]):
            R[:,j] = R[:,j] + self.lmbda * (X[:,j] - R[:,j])

        return R
