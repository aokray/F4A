import numpy as np
from nptyping import NDArray

class LimitedAttributeEffectRegression():
    def __init__(self) -> None:
        self.w = None

    def fit(self, X, y, u_idxs, p_idxs) -> None:
        d = (np.average(X[u_idxs], axis = 0) - np.average(X[p_idxs], axis = 0)).reshape(-1,1)
        b = np.average(y[u_idxs]) - np.average(y[p_idxs])
        y = y.reshape(-1,1)

        self.w = np.linalg.inv(X.T @ X) @ X.T @ y - ((d.T @ np.linalg.inv(X.T @ X) @ X.T @ y - b) / (d.T @ np.linalg.inv(X.T @ X) @ d)) * np.linalg.inv(X.T @ X) @ d

    def predict(self, X) -> NDArray:
        preds = X @ self.w
        preds[preds < 0.5] = 0
        preds[preds >= 0.5] = 1

        return preds
