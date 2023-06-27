from ML_Predictor import build_train_test_data, build_model
import numpy as np

from datetime import datetime as dt
from dateutil import tz




def make_analysis_heatmap(X, y_diff, feature1, feature2, buckets1=None, buckets2=None):
    # heatmap where one axis is feature1 and the other feature2
    # The squares of the map display the |log2(1 + y) - log2(1 + y_pred)|^2
    # If a feature is numeric 10% quantiles will be used as steps
    # Labels should include quantile and value info
    print(X[feature1].unique())
    print(X[feature2].unique())

    return 0



model = build_model('log_loss')
_, X, _, y, _, meta = build_train_test_data()
y_pred = model.predict(X)

meta['hour'] = meta['timeId'].apply(lambda x: dt.fromtimestamp(x*180, tz=tz.gettz('Europe / Berlin')).hour)

y_diff = np.round(y - y_pred)

make_analysis_heatmap(meta, y_diff, 'hour', 'description')

