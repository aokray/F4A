import numpy as np
from sklearn.decomposition import PCA
from sklearn.base import TransformerMixin
from nptyping import NDArray

class FairPCAException(Exception):
    pass

def _optProj(M: NDArray, d: int):
    p = PCA(d)
    p.fit(M)
    coeffs = p.components_.T
    P = coeffs @ coeffs.T

    return P

def _optApprox(M: NDArray, d: int):
    p = PCA(d)
    p.fit(M)
    coeffs = p.components_.T
    P = coeffs @ coeffs.T
    
    return M @ P

def _oracle(A: NDArray, m_A: int, B: NDArray, m_B: int, alpha: float, beta: float, d: int, w_1: float, w_2: float):
    # Help implementing this from https://github.com/samirasamadi/Fair-PCA/blob/master/mw.m
    ata = A.T @ A
    btb = B.T @ B

    vals = np.concatenate((np.sqrt((1/m_A) * w_1) * A,np.sqrt((1/m_B)*w_2) * B))

    P_0 = _optProj(vals, d)
    z_1 = (1/m_A)*(alpha - np.sum(ata * P_0))
    z_2 = (1/m_B)*(beta - np.sum(btb * P_0))

    return (P_0, z_1, z_2)

def _mw(A, B, d, eta, T):
    ata = A.T @ A
    btb = B.T @ B

    m_A = A.shape[0]
    m_B = B.shape[0]
    n = A.shape[1]

    A_hat = _optApprox(A, d)
    alpha = np.linalg.norm(A_hat, ord='fro') ** 2

    B_hat = _optApprox(B, d)
    beta = np.linalg.norm(B_hat, ord='fro') ** 2

    w_1 = 0.5
    w_2 = 0.5

    P = np.zeros((n,n))

    for t in range(T):
        P_temp, z_1, z_2 = _oracle(A, m_A, B, m_B, alpha, beta, d, w_1, w_2)

        w_1star = w_1 * np.exp(eta * z_1)
        w_2star = w_2 * np.exp(eta * z_2)

        w_1 = w_1star / (w_1star + w_2star)
        w_2 = w_2star / (w_1star + w_2star)

        P += P_temp

    P = (1/T) * P

    z_1 = 1/(m_A) * (alpha - np.sum(ata * P))
    z_2 = 1/(m_B) * (beta - np.sum(btb * P))
    z = max(z_1, z_2)

    P_last = P_temp
    zl_1 = 1/(m_A) * (alpha - np.sum(ata * P_last))
    zl_2 = 1/(m_B) * (beta - np.sum(btb * P_last))

    z_last = max(zl_1, zl_2)

    return (P, z, P_last, z_last)


class FairPCA(TransformerMixin):
    """

    Class implementing "The Price of Fair PCA: One Extra Dimension"s Fair PCA formulation
    in Python via the Multiplicative weights algorithm.

    Arguments:
        sens_idx: index of the sensitive variable (the variable that splits the data into 2 populations)
        u_value: value the unprotected class takes
        p_value: value the protected class takes
        d: desired rank of the newly projected data
        eta: weighting constant used to update weights in MW algorithm
        T: number of iterations to run MW algorithm

    """
    def __init__(self, d: int, eta: float = 20, T: int = 5):
        self.d = d
        self.eta = eta
        self.T = T
        self.P_smart = None

    def fit(self, X: NDArray, u_idxs: NDArray, p_idxs: NDArray):
        # The below implementation would throw errors because there is NO guarantee that the sensitive column is passed to this class
        # Now it's requred that u/p_idxs are passed to this class explicitly
        # u_idxs = np.where(X[:,self.sens_idx] == self.u_value)[0]
        # p_idxs = np.where(X[:,self.sens_idx] == self.p_value)[0]

        A = X[u_idxs]
        B = X[p_idxs]

        n = A.shape[1]

        if n != B.shape[1]:
            raise FairPCAException('A and B must be different populations within the same sample, number of features between A and B do not match.')

        if self.d >= n:
            raise FairPCAException('Desired rank d should be less than the true number of features "n"')

        P_smart = None
        P_fair, z, P_last, z_last = _mw(A, B, self.d, self.eta, self.T)

        if z < z_last:
            P_smart = P_fair
        else:
            P_smart = P_last

        # Return the project matrix "P_smart" (name from original Matlab code, I just liked it so I'm using it too)
        self.P_smart = P_smart

    def transform(self, X: NDArray):
        if self.P_smart is None:
            raise FairPCAException('The fit function must be called before calling the transform function.')

        return X @ self.P_smart