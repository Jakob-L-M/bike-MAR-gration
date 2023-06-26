import tensorflow as tf
import numpy as np
from sklearn.model_selection import train_test_split

from load_data_locally import get_data

def init_model(path):

    print('💾 loading model...')
    model = tf.keras.models.load_model(path)

    # Show the model architecture
    # print(model.summary())

    return model

def get_test_data(start_time, end_time, seed, test_size):
    print('🔨 building test data...')

    df = get_data()
    df = df[(df['timeId'] >= start_time) & (df['timeId'] <= end_time)]

    _, X, _, y = train_test_split(df, test_size=test_size, seed=seed)

    return X, y

def make_analysis_heatmap(X, y_diff, feature1, feature2, buckets1=None, buckets2=None):
    # heatmap where one axis is feature1 and the other feature2
    # The squares of the map display the |log2(1 + y) - log2(1 + y_pred)|^2
    # If a feature is numeric 10% quantiles will be used as steps
    # Labels should include quantile and value info
    return 0



model = init_model('models/model01.h5')
X, y = get_test_data(0, 9312890, 1234, 0.2)
y_pred = model.predict(X[:-4])
y_diff = y - y_pred

