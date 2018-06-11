import math

from IPython import display
from matplotlib import cm
from matplotlib import gridspec
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from sklearn import metrics
import tensorflow as tf
from tensorflow.python.data import Dataset

tf.logging.set_verbosity(tf.logging.ERROR)
pd.options.display.max_rows = 10
pd.options.display.float_format = '{:.1f}'.format

california_housing_dataframe = pd.read_csv("https://storage.googleapis.com/mledu-datasets/california_housing_train.csv", sep=",")

def preprocess_features(california_housing_dataframe):
  """Prepares input features from California housing data set.

  Args:
    california_housing_dataframe: A Pandas DataFrame expected to contain data
      from the California housing data set.
  Returns:
    A DataFrame that contains the features to be used for the model, including
    synthetic features.
  """
  selected_features = california_housing_dataframe[
    ["latitude",
     "longitude",
     "housing_median_age",
     "total_rooms",
     "total_bedrooms",
     "population",
     "households",
     "median_income"]]
  processed_features = selected_features.copy()
  # Create a synthetic feature.
  processed_features["rooms_per_person"] = (
    california_housing_dataframe["total_rooms"] /
    california_housing_dataframe["population"])
  return processed_features

def preprocess_targets(california_housing_dataframe):
  """Prepares target features (i.e., labels) from California housing data set.

  Args:
    california_housing_dataframe: A Pandas DataFrame expected to contain data
      from the California housing data set.
  Returns:
    A DataFrame that contains the target feature.
  """
  output_targets = pd.DataFrame()
  # Scale the target to be in units of thousands of dollars.
  output_targets["median_house_value"] = (
    california_housing_dataframe["median_house_value"] / 1000.0)
  return output_targets


training_examples = preprocess_features(california_housing_dataframe.head(12000))
training_examples.describe()

training_targets = preprocess_targets(california_housing_dataframe.head(12000))
training_targets.describe()

validation_examples = preprocess_features(california_housing_dataframe.tail(5000))
validation_examples.describe()

validation_targets = preprocess_targets(california_housing_dataframe.tail(5000))
validation_targets.describe()


plt.figure(figsize=(13, 8))

ax = plt.subplot(1, 2, 1)
ax.set_title("Validation Data")

ax.set_autoscaley_on(False)
ax.set_ylim([32, 43])
ax.set_autoscalex_on(False)
ax.set_xlim([-126, -112])
plt.scatter(validation_examples["longitude"],
            validation_examples["latitude"],
            cmap="coolwarm",
            c=validation_targets["median_house_value"] / validation_targets["median_house_value"].max())

ax = plt.subplot(1,2,2)
ax.set_title("Training Data")

ax.set_autoscaley_on(False)
ax.set_ylim([32, 43])
ax.set_autoscalex_on(False)
ax.set_xlim([-126, -112])
plt.scatter(training_examples["longitude"],
            training_examples["latitude"],
            cmap="coolwarm",
            c=training_targets["median_house_value"] / training_targets["median_house_value"].max())
_ = plt.plot()

def my_input_fn(features, targets, batch_size=1, shuffle=True, num_ephochs=None):
    features = {key:np.array(value) for key, value in dict(features).items()}
    ds = Dataset.from_tensor_slices((features, targets))
    ds = ds.batch(batch_size).repeat(num_ephochs)

    if shuffle:
        ds = ds.shuffle(10000)

    features, labels = ds.make_initializable_iterator().get_next()
    return features, labels

def construct_feature_columns(input_features):
    return set([tf.feature_column.numeric_column(my_feature) for my_feature in input_features])

def train_model(
        learnig_rate,
        steps,
        batch_size,
        training_examples,
        training_targets,
        validation_examples,
        validata_targets):
    periods = 10
    steps_per_period = steps / periods

    my_optimizer = tf.train.GradientDescentOptimizer(learnig_rate=learnig_rate)
    my_optimizer = tf.contrib.estimator.clip_gradients_by_norm(my_optimizer, 5.0)
    linear_regressor = tf.estimator.LinearRegressor(
        feature_columns=construct_feature_columns(training_examples),
        optimizer=my_optimizer
    )

    training_input_fn = lambda : my_input_fn(training_examples,
                                             training_targets['median_house_value'],
                                             batch_size=batch_size)
    predict_training_input_fn = lambda : my_input_fn(training_examples,
                                            training_targets['median_house_value'],
                                            num_ephochs=1,
                                            shuffle=False)
    predict_validation_input_fn = lambda : my_input_fn(validation_examples,
                                                       validata_targets['median_house_value'],
                                                       num_ephochs=1,
                                                       shuffle=False)
