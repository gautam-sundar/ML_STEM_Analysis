import re
import numpy as np
import pandas as pd
from sklearn.utils import check_array
from sklearn.preprocessing import LabelEncoder
from scipy import sparse
from sklearn.base import BaseEstimator, TransformerMixin

def create_multicolumn(data):
    # get the columns names as a list for iteration purposes 
    data_columns = list(data.columns)

    # store the zero level indices as a list. Eg. ['Brief Description', 'Agency']
    level0 = []
    # store the first level indices as a list. If zero level index has only a single column
    # in the excel file then first level header will be an empty string '' otherwise if there are 
    # multiple columns under a zero level index the first level header will be 1, 2, 3...etc
    level1 = []


    for column_name in data_columns:
        # get rid of the prefix "A) " in "A) Brief Description" etc.
        column_name = re.sub(r'^\w+\)\s', '', column_name)
        # Algorithm
        # 1. If the column_name is not 'Unnamed...' then add column_name to level0 and a 
        # blank string '' to level1.
        #
        # 2. If the next column_name is also not 'Unnamed...' repeat step 1.
        #
        # 3. If the next column_name is 'Unnamed...' add the previously added column_name again
        # to level0. If the previously added item in level1 is a '' delete it and append the 
        # numbers 1 and 2. If the previously added item in level1 is not a '' increment the 
        # previously added item in level1 and add it to level1
        if column_name.startswith('Unnamed'):

            level0.append(level0[-1])
            if level1[-1] == '':
                level1.pop()
                level1.append(1)
                level1.append(2)
            else :
                level1.append(level1[-1] + 1)
        else:
            level0.append(column_name)
            level1.append('')

    return pd.MultiIndex.from_arrays([level0, level1])


class DataSelector(BaseEstimator, TransformerMixin):
    def __init__(self, columns=None):
        self.columns = columns
    
    def fit(self, X, y=None):        
        return self

    def transform(self, X):
        return X.loc[:, self.columns]


class MakeNumeric(BaseEstimator, TransformerMixin):
    def __init__(self, exclude=[]):
        self.exclude = exclude
   
    def fit(self, X, y=None):        
        return self
    def transform(self, X, y=None):
        return X.apply(lambda c: pd.to_numeric(c, errors='coerce') if c.name[0] not in self.exclude else c)


class FillNA(BaseEstimator, TransformerMixin):
    def __init__(self, fill_with=None):
        self.fill_with = fill_with

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):      
        return X.fillna(self.fill_with)

class CalculateFundingGrowth():
    def __init__(self, start_year=2008, end_year=2009):
        self.start_year = 2008
        self.end_year = 2009
    
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):      
        funding_growth_per_investment = np.divide(np.float64(np.subtract(X['Funding FY2009'], 
                                                                         X['Funding FY2008'])),
                                                  np.float64(X['Funding FY2008']), 
                                                 ) * 100
        
        funding_growth_overall = np.divide(np.sum(np.subtract(X['Funding FY2009'], 
                                                              X['Funding FY2008'])), 
                                           np.sum(X['Funding FY2008']),
                                          ) * 100
                                           
        funding_growth_table = pd.DataFrame(
            {'Funding Growth (%)': funding_growth_per_investment, 
             'Investment Name': X['Investment Name']
            }, 
            columns=["Investment Name", "Funding Growth (%)"],
	    )
                                           
        return funding_growth_table.append(pd.DataFrame(
            {'Funding Growth (%)': funding_growth_overall, 
             'Investment Name': "Overall"
	    }, 
            columns=["Investment Name", "Funding Growth (%)"],
            
            index = [1]
        ),
                                           ignore_index=True,
                                          )




class CategoricalEncoder(BaseEstimator, TransformerMixin):
    """Encode categorical features as a numeric array.
    The input to this transformer should be a matrix of integers or strings,
    denoting the values taken on by categorical (discrete) features.
    The features can be encoded using a one-hot aka one-of-K scheme
    (``encoding='onehot'``, the default) or converted to ordinal integers
    (``encoding='ordinal'``).
    This encoding is needed for feeding categorical data to many scikit-learn
    estimators, notably linear models and SVMs with the standard kernels.
    Read more in the :ref:`User Guide <preprocessing_categorical_features>`.
    Parameters
    ----------
    encoding : str, 'onehot', 'onehot-dense' or 'ordinal'
        The type of encoding to use (default is 'onehot'):
        - 'onehot': encode the features using a one-hot aka one-of-K scheme
          (or also called 'dummy' encoding). This creates a binary column for
          each category and returns a sparse matrix.
        - 'onehot-dense': the same as 'onehot' but returns a dense array
          instead of a sparse matrix.
        - 'ordinal': encode the features as ordinal integers. This results in
          a single column of integers (0 to n_categories - 1) per feature.
    categories : 'auto' or a list of lists/arrays of values.
        Categories (unique values) per feature:
        - 'auto' : Determine categories automatically from the training data.
        - list : ``categories[i]`` holds the categories expected in the ith
          column. The passed categories are sorted before encoding the data
          (used categories can be found in the ``categories_`` attribute).
    dtype : number type, default np.float64
        Desired dtype of output.
    handle_unknown : 'error' (default) or 'ignore'
        Whether to raise an error or ignore if a unknown categorical feature is
        present during transform (default is to raise). When this is parameter
        is set to 'ignore' and an unknown category is encountered during
        transform, the resulting one-hot encoded columns for this feature
        will be all zeros.
        Ignoring unknown categories is not supported for
        ``encoding='ordinal'``.
    Attributes
    ----------
    categories_ : list of arrays
        The categories of each feature determined during fitting. When
        categories were specified manually, this holds the sorted categories
        (in order corresponding with output of `transform`).
    Examples
    --------
    Given a dataset with three features and two samples, we let the encoder
    find the maximum value per feature and transform the data to a binary
    one-hot encoding.
    >>> from sklearn.preprocessing import CategoricalEncoder
    >>> enc = CategoricalEncoder(handle_unknown='ignore')
    >>> enc.fit([[0, 0, 3], [1, 1, 0], [0, 2, 1], [1, 0, 2]])
    ... # doctest: +ELLIPSIS
    CategoricalEncoder(categories='auto', dtype=<... 'numpy.float64'>,
              encoding='onehot', handle_unknown='ignore')
    >>> enc.transform([[0, 1, 1], [1, 0, 4]]).toarray()
    array([[ 1.,  0.,  0.,  1.,  0.,  0.,  1.,  0.,  0.],
           [ 0.,  1.,  1.,  0.,  0.,  0.,  0.,  0.,  0.]])
    See also
    --------
    sklearn.preprocessing.OneHotEncoder : performs a one-hot encoding of
      integer ordinal features. The ``OneHotEncoder assumes`` that input
      features take on values in the range ``[0, max(feature)]`` instead of
      using the unique values.
    sklearn.feature_extraction.DictVectorizer : performs a one-hot encoding of
      dictionary items (also handles string-valued features).
    sklearn.feature_extraction.FeatureHasher : performs an approximate one-hot
      encoding of dictionary items or strings.
    """

    def __init__(self, encoding='onehot', categories='auto', dtype=np.float64,
                 handle_unknown='error'):
        self.encoding = encoding
        self.categories = categories
        self.dtype = dtype
        self.handle_unknown = handle_unknown

    def fit(self, X, y=None):
        """Fit the CategoricalEncoder to X.
        Parameters
        ----------
        X : array-like, shape [n_samples, n_feature]
            The data to determine the categories of each feature.
        Returns
        -------
        self
        """

        if self.encoding not in ['onehot', 'onehot-dense', 'ordinal']:
            template = ("encoding should be either 'onehot', 'onehot-dense' "
                        "or 'ordinal', got %s")
            raise ValueError(template % self.handle_unknown)

        if self.handle_unknown not in ['error', 'ignore']:
            template = ("handle_unknown should be either 'error' or "
                        "'ignore', got %s")
            raise ValueError(template % self.handle_unknown)

        if self.encoding == 'ordinal' and self.handle_unknown == 'ignore':
            raise ValueError("handle_unknown='ignore' is not supported for"
                             " encoding='ordinal'")

        X = check_array(X, dtype=np.object, accept_sparse='csc', copy=True)
        n_samples, n_features = X.shape

        self._label_encoders_ = [LabelEncoder() for _ in range(n_features)]

        for i in range(n_features):
            le = self._label_encoders_[i]
            Xi = X[:, i]
            if self.categories == 'auto':
                le.fit(Xi)
            else:
                valid_mask = np.in1d(Xi, self.categories[i])
                if not np.all(valid_mask):
                    if self.handle_unknown == 'error':
                        diff = np.unique(Xi[~valid_mask])
                        msg = ("Found unknown categories {0} in column {1}"
                               " during fit".format(diff, i))
                        raise ValueError(msg)
                le.classes_ = np.array(np.sort(self.categories[i]))

        self.categories_ = [le.classes_ for le in self._label_encoders_]

        return self

    def transform(self, X):
        """Transform X using one-hot encoding.
        Parameters
        ----------
        X : array-like, shape [n_samples, n_features]
            The data to encode.
        Returns
        -------
        X_out : sparse matrix or a 2-d array
            Transformed input.
        """
        X = check_array(X, accept_sparse='csc', dtype=np.object, copy=True)
        n_samples, n_features = X.shape
        X_int = np.zeros_like(X, dtype=np.int)
        X_mask = np.ones_like(X, dtype=np.bool)

        for i in range(n_features):
            valid_mask = np.in1d(X[:, i], self.categories_[i])

            if not np.all(valid_mask):
                if self.handle_unknown == 'error':
                    diff = np.unique(X[~valid_mask, i])
                    msg = ("Found unknown categories {0} in column {1}"
                           " during transform".format(diff, i))
                    raise ValueError(msg)
                else:
                    # Set the problematic rows to an acceptable value and
                    # continue `The rows are marked `X_mask` and will be
                    # removed later.
                    X_mask[:, i] = valid_mask
                    X[:, i][~valid_mask] = self.categories_[i][0]
            X_int[:, i] = self._label_encoders_[i].transform(X[:, i])

        if self.encoding == 'ordinal':
            return X_int.astype(self.dtype, copy=False)

        mask = X_mask.ravel()
        n_values = [cats.shape[0] for cats in self.categories_]
        n_values = np.array([0] + n_values)
        indices = np.cumsum(n_values)

        column_indices = (X_int + indices[:-1]).ravel()[mask]
        row_indices = np.repeat(np.arange(n_samples, dtype=np.int32),
                                n_features)[mask]
        data = np.ones(n_samples * n_features)[mask]

        out = sparse.csc_matrix((data, (row_indices, column_indices)),
                                shape=(n_samples, indices[-1]),
                                dtype=self.dtype).tocsr()
        if self.encoding == 'onehot-dense':
            return out.toarray()
        else:
            return out
