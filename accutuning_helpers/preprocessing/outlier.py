from sklearn.base import BaseEstimator, TransformerMixin
from pandas.core.dtypes.common import is_numeric_dtype
import logging


class AccutuningOutlierBycol(BaseEstimator, TransformerMixin):
    def __init__(self, outlier_cols, outlier_strategy, outlier_threshold=None):
        self.outlier_cols = outlier_cols
        self.outlier_strategy = outlier_strategy
        self.outlier_threshold = outlier_threshold

    def fit(self, X, y=0, **fit_params):
        return self

    def transform(self, X, y=0):
        X_tr = X.copy()
        for col in self.outlier_cols:
            try:
                converting_col = X.loc[:, col]
            except KeyError:
                logging.critical(
                    'No such column name in the dataset - Outlier elimination'
                )
            else:
                if self.outlier_strategy == 'BOX_PLOT_RULE':
                    if is_numeric_dtype(converting_col):
                        q1 = converting_col.quantile(0.25)
                        q3 = converting_col.quantile(0.75)
                        IQR = q3 - q1
                        X_tr = X_tr[(X_tr[col] >= (q1 - 1.5 * IQR)) & (X_tr[col] <= (q3 + 1.5 * IQR))]
                        deleted = X_tr.shape[0] - sum((X_tr[col] >= (q1 - 1.5 * IQR)) & (X_tr[col] <= (q3 + 1.5 * IQR)))
                        logging.debug(f'AccutuningOutlierBycol: {deleted} rows deleted for column {col}')
                elif self.outlier_strategy == 'Z_SCORE':
                    if is_numeric_dtype(converting_col):
                        if self.outlier_threshold is None:
                            self.outlier_threshold = 3
                        z = (X_tr[col] - converting_col.mean()) / converting_col.std()
                        X_tr = X_tr[abs(z) <= self.outlier_threshold]
                        deleted = sum(abs(z) > self.outlier_threshold)
                        logging.debug(f'AccutuningOutlierBycol: {deleted} rows deleted for column {col}')
                else:
                    logging.critical(
                        'Not a proper method'
                    )
        return X_tr
