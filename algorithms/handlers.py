from typing import Callable, Tuple, List, Type
from nptyping import NDArray
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.base import TransformerMixin
from sklearn.metrics import accuracy_score

class ResultsHandlerException(Exception):
    pass

# Data handler accepts data paths and rejects them immediately if the paths don't exist/other problems exist
class DataHandler:
    def __init__(self, data_path: str, idxs_path: str, delimiter: str = ","):
        self.dataset: NDArray = None
        self.idxs: NDArray = None
        self.delimiter = delimiter
        self.data_path = data_path
        self.idxs_path = idxs_path

    @property
    def data_path(self):
        return self._data_path

    @data_path.setter
    def data_path(self, value: str):
        self._data_path = value
        self.dataset = np.loadtxt(value, delimiter = self.delimiter)

    @property
    def idxs_path(self):
        return self.idxs_path

    @idxs_path.setter
    def idxs_path(self, value):
        self._idxs_path = value
        self.idxs = np.loadtxt(value, delimiter = self.delimiter)
        self.idxs = self.idxs.astype(int)
        
        # Temporarily only take first 10 idx sets
        self.idxs = self.idxs[0:10]



class ResultsHandler:
    def __init__(
        self,
        # Requires a .fit() method to train the predictor, and a .predict() method to predict on new data
        predictor: object,
        data: DataHandler,
        sens_idx: int,
        # Explicity requires a tuple of 2 ints
        u_p_vals: Tuple[int, int],
        # Arbitrary length list of ints, no way to denote this otherwise (tmk)
        feats: List[int],
        # Requires a .fit() or .fit_transform() method to "train" the transformer, and a .transform() method to transform new data
        scaler: Type[TransformerMixin] = MinMaxScaler((0,1)),
        # Requires a .fit() or .fit_transform() method to "train" the transformer, and a .transform() method to transform new data
        transformer: Type[TransformerMixin] = None,
        needs_idxs: bool = False
    ):
        self.predictor = predictor
        self.data = data
        self.sens_idx = sens_idx
        self.u_p_vals = u_p_vals
        self.feats = feats
        self.scaler = scaler
        self.transformer = transformer
        self.needs_idxs = needs_idxs

    def get_results(self):
        if not hasattr(self.predictor, 'predict'):
            raise ResultsHandlerException(f'The given predictor {self.predictor.__class__.__name__} does not have a predict function.')

        if not hasattr(self.predictor, 'fit'):
            raise ResultsHandlerException(f'The given predictor {self.predictor.__class__.__name__} does not have a fit function.')

        if not hasattr(self.scaler, 'fit'):
            raise ResultsHandlerException(f'The given scaler {self.scaler.__class__.__name__} does not have a fit function.')

        if not hasattr(self.scaler, 'transform'):
            raise ResultsHandlerException(f'The given scaler {self.scaler.__class__.__name__} does not have a transform function.')

        if not hasattr(self.transformer, 'fit') and self.transformer is not None:
            raise ResultsHandlerException(f'The given transformer {self.transformer.__class__.__name__} does not have a fit function.')

        if not hasattr(self.transformer, 'transform') and self.transformer is not None:
            raise ResultsHandlerException(f'The given transformer {self.transformer.__class__.__name__} does not have a transform function.')

        # Predict
        all_idxs = np.arange(self.data.dataset.shape[0])
        accs = []
        sds = []
        rates = []
        eos = []
        u_ups = []
        u_downs = []
        p_ups = []
        p_downs = []

        u_value = self.u_p_vals[0]
        p_value = self.u_p_vals[1]

        sample = self.data.dataset[:,0:-1]
        all_feat_idxs = np.arange(sample.shape[1])
        label = self.data.dataset[:,-1]

        for idx_row in self.data.idxs:
            idx_row_test = np.setdiff1d(all_idxs, idx_row)
            sample_train = sample[idx_row]
            sample_test = sample[idx_row_test]

            self.scaler.fit(sample_train[:,np.setdiff1d(all_feat_idxs, self.sens_idx)])
            sample_train[:,np.setdiff1d(all_feat_idxs, self.sens_idx)] = self.scaler.transform(sample_train[:,np.setdiff1d(all_feat_idxs, self.sens_idx)])
            sample_test[:,np.setdiff1d(all_feat_idxs, self.sens_idx)] = self.scaler.transform(sample_test[:,np.setdiff1d(all_feat_idxs, self.sens_idx)])

            label_train = label[idx_row]
            label_test = label[idx_row_test]

            u_train_idxs = np.where(sample_train[:,self.sens_idx] == u_value)[0]
            p_train_idxs = np.where(sample_train[:,self.sens_idx] == p_value)[0]

            if self.feats is not None:
                sample_train = sample_train[:,self.feats]
                sample_test = sample_test[:,self.feats]

            if self.transformer is not None:
                self.transformer.fit(sample_train, u_train_idxs, p_train_idxs)
                sample_train = self.transformer.transform(sample_train)
                sample_test = self.transformer.transform(sample_test)

            if (self.needs_idxs):
                self.predictor.fit(sample_train, label_train, u_train_idxs, p_train_idxs)
            else:
                self.predictor.fit(sample_train, label_train)
            
            preds = self.predictor.predict(sample_test)

            u_test_idxs = np.where(sample[idx_row_test,self.sens_idx] == u_value)[0]
            p_test_idxs = np.where(sample[idx_row_test,self.sens_idx] == p_value)[0]

            acc = accuracy_score(label_test, preds)
            sd = np.abs(np.average(preds[p_test_idxs]) - np.average(preds[u_test_idxs]))

            # Calculation of equalized odds
            # UP class calculation
            # P(Y_hat = 1 | A = 0, Y=y) y \in {0,1} = |{Y_hat = 1 : A = 0} intersect  {Y = 1 : A = 0}| / |{Y = 1 : A = 0}| + (same with Y=0)
            up_one_pred_idxs = np.where(preds[u_test_idxs] == 1)[0]
            up_one_true_idxs = np.where(label_test[u_test_idxs] == 1)[0]
            up_zero_true_idxs = np.where(label_test[u_test_idxs] == 0)[0]
            up_tpr = (len(np.intersect1d(up_one_pred_idxs, up_one_true_idxs)) / len(up_one_true_idxs))
            up_fpr = (len(np.intersect1d(up_one_pred_idxs, up_zero_true_idxs)) / len(up_zero_true_idxs))
            up_eo = up_tpr + up_fpr

            # P class calculation
            p_one_pred_idxs = np.where(preds[p_test_idxs] == 1)[0]
            p_one_true_idxs = np.where(label_test[p_test_idxs] == 1)[0]
            p_zero_true_idxs = np.where(label_test[p_test_idxs] == 0)[0]
            p_tpr = (len(np.intersect1d(p_one_pred_idxs, p_one_true_idxs)) / len(p_one_true_idxs))
            p_fpr = (len(np.intersect1d(p_one_pred_idxs, p_zero_true_idxs)) / len(p_zero_true_idxs))
            p_eo = p_tpr + p_fpr

            eo = np.abs(up_eo - p_eo)

            # Get the number of unprotected classes predicted as the up/down class and the same for the protected class
            U_up = int(np.sum(preds[u_test_idxs] == 1))
            U_down = int(np.sum(preds[u_test_idxs] == 0))
            P_up = int(np.sum(preds[p_test_idxs] == 1))
            P_down = int(np.sum(preds[p_test_idxs] == 0))

            accs.append(acc)
            sds.append(sd)
            rates.append((up_tpr, up_fpr, p_tpr, p_fpr))
            eos.append(eo)
            u_ups.append(U_up)
            u_downs.append(U_down)
            p_ups.append(P_up)
            p_downs.append(P_down)
            
        return (np.average(accs), np.average(sds), np.average(eos) < 0.03, list(np.round(np.average(rates, axis=0), 5)), np.average(u_ups), np.average(u_downs), np.average(p_ups), np.average(p_downs))


